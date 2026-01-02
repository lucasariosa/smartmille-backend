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


def extrair_texto_resposta(resp):
    """
    Extrai texto da API Responses de forma segura,
    independentemente do formato retornado.
    """
    # Caso padrão
    if hasattr(resp, "output_text") and resp.output_text:
        return resp.output_text.strip()

    # Caso estruturado
    if hasattr(resp, "output") and resp.output:
        for item in resp.output:
            if isinstance(item, dict) and "content" in item:
                for bloco in item["content"]:
                    if bloco.get("type") == "output_text":
                        return bloco.get("text", "").strip()

    return ""


@app.post("/gerar-carrossel")
async def gerar_carrossel(req: CarouselRequest):
    print("➡️ Requisição recebida:", req.tema)
    start = time.time()

    try:
        prompt = f"""
        Você é um copywriter jurídico especializado em captação de clientes.

        Gere um carrossel com 2 slides para Instagram.

        Perfil:
        - Área: {req.area}
        - Público-alvo: {req.publico}
        - Tipo de conteúdo: {req.tipo}

        Regras obrigatórias:
        - Linguagem profissional
        - Frases completas
        - Ortografia correta
        - Slide 1: pergunta ou dor
        - Slide 2: autoridade + CTA
        - CTA obrigatório:
          "Contato: {req.nome} | WhatsApp: {req.contato}"

        Tema:
        "{req.tema}"

        Retorne SOMENTE JSON válido:
        {{
          "slides": [
            {{ "headline": "...", "texto": "..." }},
            {{ "headline": "...", "texto": "..." }}
          ]
        }}
        """

        data = None

        # Retry controlado (2 tentativas)
        for tentativa in range(2):
            print(f"🧠 Gerando textos (tentativa {tentativa+1})...")
            resp = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            texto = extrair_texto_resposta(resp)

            if not texto:
                print("⚠️ Resposta vazia da IA")
                continue

            try:
                data = json.loads(texto)
                break
            except Exception as e:
                print("⚠️ JSON inválido:", texto)

        if not data:
            raise Exception("Falha ao obter JSON válido da IA")

        slides_finais = []

        for i, slide in enumerate(data["slides"], start=1):
            print(f"🖼️ Gerando imagem {i}...")

            img = client.images.generate(
                model="gpt-image-1",
                prompt="""
                Imagem institucional profissional.
                Escritório corporativo vazio, prédio empresarial,
                ambiente financeiro sofisticado.
                Estilo moderno.
                SEM pessoas.
                SEM texto.
                """,
                size="1024x1024"
            )

            slides_finais.append({
                "headline": slide["headline"],
                "texto": slide["texto"],
                "imagem": img.data[0].b64_json
            })

        print(f"🏁 Finalizado em {round(time.time() - start, 2)}s")

        return {"slides": slides_finais}

    except Exception as e:
        print("❌ ERRO NO BACKEND:", str(e))
        return {
            "erro": "Falha ao gerar carrossel",
            "detalhe": str(e)
        }
