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
    nome: str
    contato: str
    area: str
    publico: str
    tipo: str


@app.post("/gerar-carrossel")
async def gerar_carrossel(req: CarouselRequest):
    try:
        prompt = f"""
        Você é um copywriter jurídico especializado em anúncios de Instagram.

        Gere um carrossel com 2 slides focado em captação.

        Perfil:
        - Área: {req.area}
        - Público: {req.publico}
        - Tipo: {req.tipo}

        Regras:
        - Linguagem profissional
        - Texto claro e persuasivo
        - Ortografia correta
        - Slide 1: pergunta ou dor
        - Slide 2: autoridade + CTA
        - CTA obrigatório no slide 2:
          "Contato: {req.nome} | WhatsApp: {req.contato}"

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

        text_response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        data = json.loads(text_response.output_text.strip())

        slides = []

        for slide in data["slides"]:
            img = client.images.generate(
                model="gpt-image-1",
                prompt="""
                Imagem institucional profissional.
                Direito, finanças ou ambiente corporativo.
                Escritório vazio, objetos jurídicos ou cidade financeira.
                Estilo sofisticado, moderno.
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

        return {"slides": slides}

    except Exception as e:
        return {"erro": str(e)}
