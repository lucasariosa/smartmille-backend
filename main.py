from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Pedido(BaseModel):
    area: str
    cidade: str
    publico: str
    estilo: str
    nome: str | None = None
    escritorio: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/gerar-carrossel")
def gerar_carrossel(pedido: Pedido):

    assinatura = ""
    if pedido.nome and pedido.escritorio:
        assinatura = f"{pedido.nome} – {pedido.escritorio}"
    elif pedido.nome:
        assinatura = pedido.nome
    elif pedido.escritorio:
        assinatura = pedido.escritorio

    # 🔹 SOMENTE TEXTO (sem imagem ainda)
    prompt = f"""
Crie exatamente 3 textos curtos para um carrossel jurídico.
Área: {pedido.area}
Cidade: {pedido.cidade}
Público: {pedido.publico}
Tom: {pedido.estilo}

Formato:
1) Pergunta
2) Explicação
3) Orientação final

Sem emojis.
Sem promessas.
Responda em 3 linhas.
Assinatura no slide 3 (se houver): {assinatura}
"""

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    slides = [
        l.strip()
        for l in resposta.output_text.split("\n")
        if l.strip()
    ][:3]

    return {
        "slides_texto": slides
    }
