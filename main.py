from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import time

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
            if "content" in item:
                for c in item["content"]:
                    if c.get("type") == "output_text":
                        return c.get("text", "").strip()
    return ""


@app.post("/gerar-carrossel")
async def gerar_carrossel(req: CarouselRequest):
    print("➡️ Requisição recebida:", req.tema)
    start = time.time()

    try:
        prompt = f"""
        Você é um profissional liberal falando em PRIMEIRA PESSOA.

        Gere um carrossel com 2 slides para Instagram focado em captação.

        Regras obrigatórias:
        - SEM terceira pessoa
        - SEM mencionar "Dr.", "especialista", "ele", "ela"
        - Sempre usar "eu", "meu", "posso te ajudar"
        - Linguagem profissional, confiante e direta
        - Frases completas e bem pontuadas

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

        Retorne SOMENTE JSON:
        {{
          "slides": [
            {{ "headline": "...", "texto": "..." }},
            {{ "headline": "...", "texto": "..." }}
          ]
        }}
        """

        data = None

        for _ in range(2):
            resp = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )
            texto = extrair_texto(resp)
            if texto:
                try:
                    data = json.loads(texto)
                    break
                except:
                    pass

        if not data:
            raise Exception("Falha ao gerar texto")

        slides = []

        for slide in data["slides"]:
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

    except Exception as e:
        print("❌ ERRO:", str(e))
        return {"erro": "Falha ao gerar carrossel"}
