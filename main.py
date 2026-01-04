from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# ========================
# CORS
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# MODELO DE ENTRADA
# ========================
class CarouselRequest(BaseModel):
    nome: str
    contato: str
    area: str
    publico: str
    tipo: str
    tema: str

# ========================
# ENDPOINT PRINCIPAL
# ========================
@app.post("/gerar-carrossel")
def gerar_carrossel(data: CarouselRequest):

    tema = data.tema.strip()

    # ---- TEXTOS (frontend controla tipografia e destaque) ----
    slides_text = [
        {
            "headline": f"Teve um atendimento médico negligenciado?",
            "texto": "Saiba seus direitos e entenda os pontos que exigem atenção."
        },
        {
            "headline": "Quando a negligência médica gera indenização",
            "texto": "Nem todo erro é indenizável. Conheça os critérios e evite decisões precipitadas."
        }
    ]

    slides = []

    for idx, slide in enumerate(slides_text):

        # ========================
        # PROMPT DE IMAGEM (BASE LIMPA)
        # ========================
        prompt = f"""
Create a premium editorial background image for a legal social media carousel.

ABSOLUTE RULES (DO NOT BREAK):
- NO people
- NO faces
- NO human silhouettes
- NO hands
- NO characters
- NO readable text
- NO stock photo look
- NO Canva-style layouts

THEME:
{tema}

STYLE:
- Minimalist, elegant, high-end
- Professional legal/editorial aesthetic
- Abstract elements, textures, architecture, light, shapes, symbols
- Neutral or sophisticated color palette
- Clean composition with empty space

COMPOSITION:
- Leave large empty areas for headline text
- Leave space for secondary text blocks
- Background must support typography overlay
- Balanced contrast for text readability

IMPORTANT:
This image will receive typography and UI overlays later.
Do NOT include any text or people.
"""

        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1536"  # formato vertical válido
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

# ========================
# HEALTHCHECK
# ========================
@app.get("/health")
def health():
    return {"status": "ok"}
