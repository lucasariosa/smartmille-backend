from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI

app = FastAPI()

# CORS LIBERADO (TESTE DEFINITIVO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preflight OPTIONS (resolve Failed to fetch)
@app.options("/{path:path}")
def options_handler(path: str):
    return {}

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
Você é um advogado especialista em {pedido.area}, atuando em {pedido.cidade},
criando conteúdo para redes sociais voltado ao público {pedido.publico}.

Crie exatamente 3 textos curtos para um CARROSSEL JURÍDICO PRONTO PARA PUBLICAR:

Slide 1: Pergunta direta e chamativa
Slide 2: Explicação prática e clara
Slide 3: Orientação final ou definição objetiva

Regras:
- textos curtos e diretos
- linguagem profissional e acessível
- tom {pedido.estilo}
- não prometer resultados
- não mencionar valores
- respeitar o Código de Ética da OAB
- NÃO usar emojis

Assinatura (se houver) no Slide 3:
{assinatura}

Responda com 3 linhas, uma por slide.
"""

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt_texto
    )

    slides_texto = [
        l.strip() for l in resposta.output_text.split("\n") if l.strip()
    ][:3]

    imagens = []

    for texto in slides_texto:
        img = client.images.generate(
            model="gpt-image-1",
            prompt=f"""
Imagem vertical 4:5 para Instagram.
Fundo corporativo jurídico elegante.
Texto centralizado e legível:

"{texto}"

Sem pessoas, marcas ou logotipos.
""",
            size="1024x1280"
        )
        imagens.append(img.data[0].url)

    return {"slides": imagens}
