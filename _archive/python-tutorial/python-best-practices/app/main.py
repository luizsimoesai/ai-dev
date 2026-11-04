from typing import Dict

from fastapi import FastAPI

from app.routers import product, user

# Criando o App
app = FastAPI()

app.include_router(product.router)
app.include_router(user.router)

MENSAGEM_HOME: str = "Bem-vindo à API de Recomendação de Produtos"

# Iniciando o servidor


@app.get("/")
def home() -> Dict[str, str]:
    global MENSAGEM_HOME
    return {"mensagem": MENSAGEM_HOME}
