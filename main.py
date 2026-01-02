from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import time
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class CarouselRequest(BaseModel):
    tema: str
    nome: str
    contato: str
    area: str
    publico: str
    tipo: str


def extrair_texto(resp):
    if hasattr(resp, "output_text") and resp.output_text:
        return resp.output_text.strip()

    if hasattr(resp, "output"):
        for item in resp.output:
            if isinstance(item, dict) and "content" in item:
                for c in item["content"]:
                    if c.get("type") == "output_text":
                        return c.get("text", "").strip()

    return ""


def limpar_json(texto: str) -> str:
    """
    Remove ```json ... ``` ou ``` ... ``` se existirem
    """
    texto = texto.strip()

    # remove ```json
    texto = re.sub(r"^```json\s*", "", texto, flags=re.IGNORECASE)
    # remove ```
    texto = re.sub(r"^```\s*", "", texto)
    texto = re.sub(r"\s*```$", "", texto)

    return texto.strip()


@app.post("/gerar-carrossel")
async def gerar_carrossel(req: CarouselRequest):
    print("➡️ Requisição recebida:", req.tema)
    start = time.time()

    prompt_base = f"""
Você é um profissional liberal falando em PRIMEIRA PESSOA.

Gere um carrossel com 2 slides para Instagram focado em captação.

Regras obrigatórias:
- SEM terceira pessoa
- SEM mencionar "Dr.", "especialista", "ele", "ela"
- Sempre usar "eu", "meu", "posso te ajudar"
- Linguagem profissional, confiante e direta

Estrutura:
- Slide 1: dor ou pergunta forte
- Slide 2: autoridade em primeira pessoa + CTA

CTA obrigatório no slide 2:
"Fale comigo:
{req.nome} | WhatsApp: {req.contato}"

Contexto:
- Área: {req.area}
- Público-alvo: {req.publico}
- Tipo de conteúdo: {req.tipo}

Tema:
"{req.tema}"

Retorne SOMENTE JSON válido no formato:
{{
  "slides": [
    {{ "headline": "...", "texto": "..." }},
    {{ "headline": "...", "texto": "..." }}
  ]
}}
"""

    data = None
    ultimo_texto = ""

    for tentativa in range(3):
        print(f"🧠 Gerando textos (tentativa {tentativa + 1})")

        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt_base if tentativa == 0 else (
                "O JSON anterior estava inválido. Retorne APENAS o JSON correto.\n\n"
                + prompt_base
            )
        )

        texto = extrair_texto(resp)
        ultimo_texto = texto

        if not texto:
            print("⚠️ Resposta vazia")
            continue

        texto_limpo = limpar_json(texto)

        try:
            data = json.loads(texto_limpo)
            break
        except Exception:
            print("⚠️ JSON inválido após limpeza")

    if not data:
        print("❌ TEXTO FINAL RECEBIDO:\n", ultimo_texto)
        raise Exception("Falha ao gerar texto")

    slides = []

    for i, slide in enumerate(data["slides"], start=1):
        print(f"🖼️ Gerando imagem {i}")

        img = client.images.generate(
            model="gpt-image-1",
            prompt="""
Imagem institucional profissional.
Escritório corporativo vazio ou prédio empresarial moderno.
Estilo elegante, sofisticado.
SEM pessoas.
SEM texto.
""",
            size="1024x1024"
        )

        slides.append({
            "headline": slide["headline"],
            "texto": slide["texto"],
            "imagem": img.data[0].b64_json
        })

    print(f"🏁 Finalizado em {round(time.time() - start, 2)}s")
    return {"slides": slides}
