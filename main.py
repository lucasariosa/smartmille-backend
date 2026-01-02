from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI

app = FastAPI()

# CORS para permitir chamadas do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente da OpenAI (usa a variável de ambiente)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Pedido(BaseModel):
    area: str
    tipo: str

@app.get("/")
def home():
    return {"status": "SmartMille com IA rodando"}

@app.post("/gerar-conteudo")
def gerar_conteudo(pedido: Pedido):

    prompt = f"""
Você é um advogado especialista em {pedido.area}.
Crie um conteúdo para {pedido.tipo}, com linguagem simples,
educativa e ética, voltada para o público leigo no Brasil.
Não faça promessas, não cite valores e respeite o código de ética da OAB.
"""

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    texto = resposta.output_text

    return {
        "resultado": texto
    }
