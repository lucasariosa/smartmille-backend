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
        (advogado, médico, contador), tom profissional.

        Tema: "{req.tema}"

        Retorne SOMENTE JSON válido:
        {{
          "slides": [
            {{ "texto": "Texto do slide 1" }},
            {{ "texto": "Texto do slide 2" }}
          ]
        }}
        """

        text_response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt,
    response_format={"type": "json"}
)
