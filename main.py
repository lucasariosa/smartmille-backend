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

# Modelo de dados recebido do frontend
class Pedido(BaseModel):
    area: str
    cidade: str
    publico: str
    tipo: str
    estilo: str
    nome: str | None = None
    escritorio: str | None = None


@app.get("/")
def home():
    return {"status": "SmartMille backend ativo"}


@app.post("/gerar-conteudo")
def gerar_conteudo(pedido: Pedido):

    # Montar assinatura institucional (se existir)
    assinatura = ""
    if pedido.nome and pedido.escritorio:
        assinatura = f"{pedido.nome} – {pedido.escritorio}"
    elif pedido.nome:
        assinatura = pedido.nome
    elif pedido.escritorio:
        assinatura = pedido.escritorio

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
- respeitar rigorosamente o Código de Ética da OAB

Estrutura obrigatória do conteúdo:
TÍTULO
BLOCOS DE TEXTO (3 a 5 frases curtas)
FECHAMENTO

Regras adicionais:
- Não usar emojis
- Não escrever como legenda
- Não escrever como roteiro
- O texto deve estar pronto para ser aplicado diretamente em uma peça visual

Se houver assinatura institucional, inclua no FECHAMENTO de forma discreta:
{assinatura}
"""

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    texto_final = resposta.output_text.strip()

    return {
        "resultado": texto_final
    }
