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
Você é um advogado especialista em {pedido.area}, atuando em {pedido.cidade},
criando conteúdo para redes sociais voltado ao público {pedido.publico}.

Crie exatamente 3 textos curtos para um CARROSSEL JURÍDICO PRONTO PARA PUBLICAR:

Slide 1: Pergunta direta e chamativa
Slide 2: Explicação prática e clara
Slide 3: Orientação final ou definição objetiva

Regras obrigatórias:
- textos curtos e diretos
- linguagem profissional e acessível
- tom {pedido.estilo}
- foco em autoridade e clareza
- conteúdo educativo
- não prometer resultados
- não mencionar valores ou honorários
- respeitar o Código de Ética da OAB
- NÃO escrever legenda
- NÃO usar emojis

Se houver assinatura institucional, inclua discretamente no Slide 3:
{assinatura}

Responda exatamente com 3 linhas, uma por slide.
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
Fundo elegante e corporativo relacionado à advocacia.
Estilo moderno, limpo e profissional.
Texto grande, centralizado e legível:

"{texto}"

Sem pessoas específicas, sem marcas, sem logotipos.
"""

        imagem = client.images.generate(
            model="gpt-image-1",
            prompt=prompt_imagem,
            size="1024x1280"
        )

        imagens.append(imagem.data[0].url)

    return {"slides": imagens}
