from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import json

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
    try:
        prompt = f"""
        Gere um carrossel com 2 slides para Instagram sobre:
        "{req.tema}"

        Retorne SOMENTE JSON válido:
        {{
          "slides": [
            {{ "texto": "Texto do slide 1" }},
            {{ "texto": "Texto do slide 2" }}
          ]
        }}
        """

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            response_format={"type": "json"}
        )

        data = json.loads(response.output_text)

        slides_finais = []

        for slide in data["slides"]:
            img = client.images.generate(
                model="gpt-image-1",
                prompt=f"Imagem profissional, clean, formato 4:5, para Instagram sobre: {slide['texto']}",
                size="1024x1280"
            )

            slides_finais.append({
                "texto": slide["texto"],
                "imagem": img.data[0].b64_json
            })

        return {"slides": slides_finais}

    except Exception as e:
        return {"erro": f"Backend error: {str(e)}"}
