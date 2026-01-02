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

@app.post("/gerar-carrossel")
async def gerar_carrossel(req: CarouselRequest):
    start_time = time.time()
    print("➡️ Requisição recebida:", req.tema)

    try:
        print("🧠 Gerando textos...")

        prompt = f"""
        Você é um especialista em copywriting jurídico.

        Gere um carrossel com 2 slides para Instagram com foco em CAPTAÇÃO DE CLIENTES.

        Perfil:
        - Profissão: {req.area}
        - Público-alvo: {req.publico}
        - Tipo de conteúdo: {req.tipo}

        Regras obrigatórias:
        - Linguagem profissional e acessível
        - Frases completas
        - Inicial maiúscula
        - Pontuação correta
        - Tom institucional (nada de influencer)
        - Slide 1 deve gerar curiosidade ou dor
        - Slide 2 deve gerar autoridade e intenção de contato
        - O CTA deve conter:
          "Contato: {req.nome} – WhatsApp: {req.contato}"

        Tema central:
        "{req.tema}"

        Retorne SOMENTE JSON válido:
        {{
          "slides": [
            {{
              "headline": "Pergunta ou dor principal",
              "texto": "Texto curto e objetivo"
            }},
            {{
              "headline": "Autoridade e solução",
              "texto": "Texto explicativo + CTA completo"
            }}
          ]
        }}
        """

        text_response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        data = json.loads(text_response.output_text.strip())
        print("✅ Textos gerados")

        slides_finais = []

        for i, slide in enumerate(data["slides"], start=1):
            print(f"🖼️ Gerando imagem {i}...")

            img_response = client.images.generate(
                model="gpt-image-1",
                prompt="""
                Imagem institucional e profissional.
                Ambiente corporativo, escritório vazio moderno,
                prédios empresariais ou avenida financeira.
                Estilo Wall Street / Faria Lima.
                Fotografia realista.
                SEM pessoas.
                SEM texto na imagem.
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
        print("❌ ERRO:", str(e))
        return {
            "erro": "Falha ao gerar carrossel",
            "detalhe": str(e)
        }
