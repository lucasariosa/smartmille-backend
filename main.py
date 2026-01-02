from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Pedido(BaseModel):
    area: str
    cidade: str
    publico: str
    tipo: str
    estilo: str

@app.get("/")
def home():
    return {"status": "SmartMille personalizado rodando"}

@app.post("/gerar-conteudo")
def gerar_conteudo(pedido: Pedido):

    prompt = f"""
Você é um advogado atuante em {pedido.area}, com atuação na região de {pedido.cidade}.
Seu público-alvo principal é {pedido.publico}.

Crie um conteúdo jurídico no formato de {pedido.tipo}, pensado para ser usado
como PEÇA VISUAL (imagem ou vídeo curto com texto em motion).

Diretrizes obrigatórias:
- linguagem clara e acessível ao público leigo
- frases curtas e objetivas
- texto organizado em blocos
- tom {pedido.estilo}
- conteúdo educativo e informativo
- não prometer resultados
- não mencionar valores ou honorários
- respeitar o Código de Ética da OAB

Estrutura do conteúdo:
TÍTULO (impactante e informativo)
BLOCOS DE TEXTO (3 a 5 frases curtas)
FECHAMENTO (autoridade e orientação geral)

Não use emojis.
Não escreva como legenda.
Escreva como texto pronto para ser colocado diretamente em uma peça visual.
"""

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    texto = resposta.output_text.strip()

    return {
        "resultado": texto
    }
