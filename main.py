python

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Pedido(BaseModel):
    area: str
    tipo: str

@app.get("/")
def home():
    return {"status": "Backend Smart Mille rodando"}

@app.post("/gerar-conteudo")
def gerar_conteudo(pedido: Pedido):
    return {
        "resultado": f"Conteúdo de exemplo sobre {pedido.area} para {pedido.tipo}"
    }
