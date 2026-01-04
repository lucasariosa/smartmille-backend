from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import base64
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# CORS liberado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CarouselRequest(BaseModel):
    nome: str
    contato: str
    area: str
    publico: str
    tipo: str
    tema: str


@app.post("/gerar-carrossel")
def gerar_carrossel(data: CarouselRequest):

    tema = data.tema

    # ---- TEXTOS (simples e estáveis) ----
    slides_text = [
        {
            "headline": f"O que você precisa saber sobre {tema}",
            "texto": f"Entenda os principais pontos de {tema} e como isso pode impactar você."
        },
        {
            "headline": f"{tema}: atenção a estes detalhes",
            "texto": f"Evite erros comuns e tome decisões mais seguras sobre {tema}."
        }
    ]

    slides = []

    for slide in slides_text:

        prompt = f"""
Crie uma imagem editorial premium para redes sociais.

Tema: {tema}

A imagem deve ser limpa, elegante e profissional.
Sem textos visíveis na imagem.
Estilo fotográfico ou ilustrativo sofisticado.
Boa iluminação, alto contraste e composição moderna.
"""

        # ---- GERA IMAGEM ----
        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1536"
        )

        image_base64 = img.data[0].b64_json

        slides.append({
            "headline": slide["headline"],
            "texto": slide["texto"],
            "imagem": image_base64
        })

    return {
        "slides": slides
    }


@app.get("/health")
def health():
    return {"status": "ok"}
