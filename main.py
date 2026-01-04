from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import random

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CarouselRequest(BaseModel):
    tema: str

HEADLINE_FONTS = ["Anton", "Playfair Display", "Novecento"]
BODY_FONTS = ["Abel", "Montserrat", "Poppins", "Nunito"]

def build_image_prompt(tema: str, headline: str, body_text: str) -> str:
    headline_font = random.choice(HEADLINE_FONTS)
    body_font = random.choice(BODY_FONTS)

    return f"""
Create a premium editorial-style social media image.

Theme: {tema}

MAIN HEADLINE:
"{headline}"

Design rules for headline:
- Use the font {headline_font}
- Headline must be LARGE, dominant, and centered or slightly offset
- Highlight up to TWO important words in ALL CAPS
- Apply subtle shadow or elegant glow around the letters
- Choose a refined color that fits the theme (no neon, no childish tones)
- Headline must NOT look like default system fonts

SUPPORTING TEXT:
"{body_text}"

Design rules for supporting text:
- Use font {body_font}
- Place text fluidly (bottom-left, center, or bottom-right)
- Text must sit inside a semi-transparent box (~10% opacity)
- Box should feel minimal, modern, and sophisticated

GENERAL STYLE:
- Typography-driven design
- Clean, modern, premium aesthetic
- Professional advertising look
- No clutter
- No small unreadable text
- No default or amateur layouts
"""

@app.post("/gerar-carrossel")
def gerar_carrossel(data: CarouselRequest):
    tema = data.tema

    # Textos (podem vir de LLM depois, aqui está estável)
    headline_1 = f"O segredo do {tema} eficiente"
    body_1 = f"Entenda como aplicar {tema} com mais clareza e resultado."

    headline_2 = f"{tema}: o que realmente importa"
    body_2 = f"Evite erros comuns e tome decisões mais inteligentes."

    prompts = [
        build_image_prompt(tema, headline_1, body_1),
        build_image_prompt(tema, headline_2, body_2),
    ]

    images = []

    for prompt in prompts:
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        images.append(result.data[0].url)

    return {
        "images": images
    }

@app.get("/health")
def health():
    return {"status": "ok"}
