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

@app.post("/gerar-carrossel")
async def gerar_carrossel(req: CarouselRequest):
    start_time = time.time()
    print("➡️ Requisição recebida:", req.tema)

    try:
        print("🧠 Gerando textos...")

        prompt = f"""
        Gere um carrossel com 2 slides para um profissional liberal
        (advogado, médico, contador), com linguagem profissional e objetiva.

        Tema: "{req.tema}"

        Retorne SOMENTE JSON válido, sem explicações, sem markdown:
        {{
          "slides": [
            {{ "texto": "Texto do slide 1" }},
            {{ "texto": "Texto do slide 2" }}
          ]
        }}
        """

        text_response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        raw_text = text_response.output_text.strip()
        data = json.loads(raw_text)

        print("✅ Textos gerados com sucesso")

        slides_finais = []

        for i, slide in enumerate(data["slides"], start=1):
            print(f"🖼️ Gerando imagem {i}...")
            img_start = time.time()

            img_response = client.images.generate(
                model="gpt-image-1",
                prompt=f"""
                Imagem institucional, limpa, profissional,
                estilo corporativo, formato 4:5,
                para Instagram, relacionada ao texto:
                "{slide['texto']}"
                """,
                size="1024x1536"
            )

            print(f"✅ Imagem {i} gerada em {round(time.time() - img_start, 2)}s")

            slides_finais.append({
                "texto": slide["texto"],
                "imagem": img_response.data[0].b64_json
            })

        print(f"🏁 Processo finalizado em {round(time.time() - start_time, 2)}s")

        return {"slides": slides_finais}

    except Exception as e:
        print("❌ ERRO NO BACKEND:", str(e))
        return {
            "erro": "Falha ao gerar carrossel",
            "detalhe": str(e)
        }
