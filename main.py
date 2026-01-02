from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import base64
import os

app = FastAPI()

# CORS liberado
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
def gerar_carrossel(req: CarouselRequest):
    try:
        # 1) Geração dos textos (2 slides)
        texto_prompt = f"""
        Gere um carrossel de Instagram com 2 slides sobre o tema:
        "{req.tema}"

        Retorne APENAS em JSON no formato:
        {{
          "slides": [
            {{ "texto": "Texto curto e direto para o slide 1" }},
            {{ "texto": "Texto curto e direto para o slide 2" }}
          ]
        }}
        """

        texto_resp = client.responses.create(
            model="gpt-4.1-mini",
            input=texto_prompt,
        )

        textos_json = eval(texto_resp.output_text)
        slides = textos_json["slides"]

        slides_finais = []

        # 2) Geração das imagens (4:5)
        for slide in slides:
            img_prompt = f"""
            Crie uma imagem clean, moderna e profissional para Instagram (formato 4:5),
            relacionada ao texto:
            "{slide['texto']}"

            Estilo minimalista, fundo claro, tipografia elegante.
            """

            img_resp = client.images.generate(
                model="gpt-image-1",
                prompt=img_prompt,
                size="1024x1280"  # 4:5
            )

            img_base64 = img_resp.data[0].b64_json

            slides_finais.append({
                "texto": slide["texto"],
                "imagem": img_base64
            })

        return {"slides": slides_finais}

    except Exception as e:
        return {"erro": str(e)}
