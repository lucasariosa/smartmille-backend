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
    tipo: str  # introducao | definicao | conclusao


def extrair_texto(response):
    """
    Extrai texto de forma segura da API Responses
    """
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text.strip()

    if hasattr(response, "output") and response.output:
        for item in response.output:
            if "content" in item:
                for c in item["content"]:
                    if c.get("type") == "output_text":
                        return c.get("text", "").strip()

    return ""


@app.post("/gerar-carrossel")
async def gerar_carrossel(req: CarouselRequest):
    start_time = time.time()
    print("➡️ Requisição recebida:", req.tema)

    try:
        print("🧠 Gerando textos...")

        prompt = f"""
        Você é um especialista em copywriting jurídico focado em captação.

        Gere um carrossel com 2 slides para Instagram.

        Perfil:
        - Área: {req.area}
        - Público-alvo: {req.publico}
        - Tipo de conteúdo: {req.tipo}

        Regras:
        - Linguagem profissional
        - Frases completas
        - Ortografia e pontuação corretas
        - Slide 1: dor ou pergunta
        - Slide 2: autoridade + CTA
        - CTA obrigatório:
          "Contato: {req.nome} – WhatsApp: {req.contato}"

        Tema:
        "{req.tema}"

        Retorne SOMENTE JSON válido:
        {{
          "slides": [
            {{ "headline": "Pergunta ou dor", "texto": "Texto do slide 1" }},
            {{ "headline": "Autoridade e solução", "texto": "Texto do slide 2 com CTA" }}
          ]
        }}
        """

        # Tentamos até 2 vezes obter JSON válido
        data = None

        for tentativa in range(2):
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            texto = extrair_texto(response)

            if texto:
                try:
                    data = json.loads(texto)
                    break
                except Exception as e:
                    print(f"⚠️ JSON inválido (tentativa {tentativa+1})")

        if not data:
            raise Exception("Não foi possível gerar JSON válido")

        print("✅ Textos gerados")

        slides_finais = []

        for i, slide in enumerate(data["slides"], start=1):
            print(f"🖼️ Gerando imagem {i}...")

            img_response = client.images.generate(
                model="gpt-image-1",
                prompt="""
                Imagem institucional profissional.
                Escritório corporativo vazio ou prédio empresarial.
                Estilo financeiro, elegante, moderno.
                SEM pessoas.
                SEM texto.
                """,
                size="1024x1536"
            )

            slides_finais.append({
                "headline": slide["headline"],
                "texto": slide["texto"],
                "imagem": img_response.data[0].b64_json
            })

        print(f"🏁 Finalizado em {round(time.time() - start_time, 2)}s")
        return {"slides": slides_finais}

    except Exception as e:
        print("❌ ERRO NO BACKEND:", str(e))
        return {
            "erro": "Falha ao gerar carrossel",
            "detalhe": str(e)
        }
