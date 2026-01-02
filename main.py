from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


@app.post("/gerar-carrossel")
def gerar_carrossel(pedido: Pedido):

    assinatura = ""
    if pedido.nome and pedido.escritorio:
        assinatura = f"{pedido.nome} – {pedido.escritorio}"
    elif pedido.nome:
        assinatura = pedido.nome
    elif pedido.escritorio:
        assinatura = pedido.escritorio

    prompt_texto = f"""
Você é um advogado atuante em {pedido.area}, com atuação na região de {pedido.cidade}.
Seu público-alvo é {pedido.publico}.

Crie um conteúdo jurídico para CARROSSEL com EXATAMENTE 3 slides, obedecendo:

SLIDE 1 – PERGUNTA
SLIDE 2 – CONTEÚDO EXPLICATIVO
SLIDE 3 – DEFINIÇÃO OU ORIENTAÇÃO FINAL

Diretrizes obrigatórias:
- frases curtas
- linguagem clara e acessível
- tom {pedido.estilo}
- conteúdo educativo
- não prometer resultados
- não mencionar valores
- respeitar o Código de Ética da OAB

Se houver assinatura institucional, inclua de forma discreta no SLIDE 3:
{assinatura}

Responda EXATAMENTE com 3 linhas, uma por slide.
"""

    resposta_texto = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt_texto
    )

    slides_texto = [
        linha.strip()
        for linha in resposta_texto.output_text.split("\n")
        if linha.strip()
    ][:3]

    imagens = []

    for texto in slides_texto:
        prompt_imagem = f"""
Imagem vertical 4:5 para Instagram.
Fundo profissional e elegante relacionado à advocacia.
Estilo moderno, minimalista e corporativo.
Texto centralizado na imagem:

"{texto}"

Sem logotipos, sem pessoas identificáveis, sem marcas.
"""

        imagem = client.images.generate(
            model="gpt-image-1",
            prompt=prompt_imagem,
            size="1024x1280"
        )

        imagens.append(imagem.data[0].url)

    return {
        "slides": imagens
    }
