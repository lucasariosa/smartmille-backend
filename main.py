from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS - permite chamadas do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
