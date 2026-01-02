from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
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

    # Assinatura institucional
    assinatura = ""
    if pedido.nome and pedido.escritorio:
        assinatura = f"{pedido.nome} – {pedido.escritorio}"
    elif pedido.nome:
        assinatura = pedido.nome
    elif pedido.escritorio:
        assinatura = pedido.escritorio

    # 1️⃣ GERAR TEXTOS
    prompt_texto = f"""
Crie exatamente 3 textos curtos para um carrossel jurídico pronto para Instagram.

Contexto:
Área: {pedido.area}
Cidade: {pedido.cidade}
Público: {pedido.publico}
Tom: {pedido.estilo}

Formato:
Slide 1: Pergunta direta
Slide 2: Explicação clara
Slide 3: Orientação final

Regras:
- linguagem profissional e acessível
- sem emojis
- sem promessas
- sem valores
- respeitar o Código de Ética da OAB

Assinatura (se houver) no slide 3:
{assinatura}

Responda com exatamente 3 linhas.
"""

    resposta_texto = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt_texto
    )

    textos = [
        l.strip()
        for l in resposta_texto.output_text.split("\n")
        if l.strip()
    ][:3]

    # 2️⃣ GERAR IMAGENS (a partir dos textos)
    imagens = []

    for texto in textos:
        prompt_imagem = f"""
Imagem vertical 4:5 para Instagram.
Fundo corporativo jurídico elegante.
Estilo moderno, minimalista e profissional.
Texto grande, centralizado e legível:

"{texto}"

Sem pessoas, sem marcas, sem logotipos.
"""

        imagem = client.images.generate(
            model="gpt-image-1",
            prompt=prompt_imagem,
            size="1024x1280"
        )

        imagens.append(imagem.data[0].url)

    # 🎁 ENTREGA FINAL (produto)
    return {
        "imagens": imagens
    }
