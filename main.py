from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from openai import OpenAI

app = FastAPI()

# CORS simples e seguro para produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- MODELOS ----------
class PedidoTexto(BaseModel):
    area: str
    cidade: str
    publico: str
    estilo: str
    nome: str | None = None
    escritorio: str | None = None

class PedidoImagens(BaseModel):
    textos: List[str]

# ---------- HEALTH ----------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------- ETAPA 1: TEXTO (RÁPIDO) ----------
@app.post("/gerar-textos")
def gerar_textos(pedido: PedidoTexto):
    assinatura = ""
    if pedido.nome and pedido.escritorio:
        assinatura = f"{pedido.nome} – {pedido.escritorio}"
    elif pedido.nome:
        assinatura = pedido.nome
    elif pedido.escritorio:
        assinatura = pedido.escritorio

    prompt = f"""
Crie exatamente 2 textos curtos para um carrossel jurídico pronto para Instagram.

Contexto:
Área: {pedido.area}
Cidade: {pedido.cidade}
Público: {pedido.publico}
Tom: {pedido.estilo}

Formato:
Slide 1: Pergunta direta (dor)
Slide 2: Orientação clara (resposta)

Regras:
- linguagem profissional e acessível
- sem emojis
- sem promessas
- sem valores
- respeitar o Código de Ética da OAB

Assinatura (se houver) no slide 2:
{assinatura}

Responda com exatamente 2 linhas.
"""

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    textos = [l.strip() for l in resp.output_text.split("\n") if l.strip()][:2]

    return {"textos": textos}

# ---------- ETAPA 2: IMAGENS (PESADO) ----------
@app.post("/gerar-imagens")
def gerar_imagens(pedido: PedidoImagens):
    imagens = []

    for texto in pedido.textos:
        prompt_img = f"""
Imagem vertical 4:5 para Instagram.
Fundo corporativo jurídico elegante.
Estilo moderno, minimalista e profissional.
Texto grande, centralizado e legível:

"{texto}"

Sem pessoas, sem marcas, sem logotipos.
"""

        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt_img,
            size="1024x1280"
        )

        imagens.append(img.data[0].url)

    return {"imagens": imagens}
