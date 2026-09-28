from typing import Dict

from fastapi import FastAPI

from app.routers import produto, usuario

# Criando o App
app = FastAPI()

app.include_router(produto.router)
app.include_router(usuario.router)

MENSAGEM_HOME: str = "Bem-vindo à API de Recomendação de Produtos"

# Iniciando o servidor


@app.get("/")
def home() -> Dict[str, str]:
    global MENSAGEM_HOME
    return {"mensagem": MENSAGEM_HOME}
