from typing import List

from fastapi import APIRouter

from app.schemas.usuario import Usuario

router = APIRouter()

usuarios: List[Usuario] = []
contador_usuario: int = 1


# Rota para cadastrar usuários


@router.post("/usuarios/", response_model=Usuario)
def criar_usuario(nome: str) -> Usuario:
    """Cadastra um novo usuário.

    Args:
        nome (str): Nome do usuário a ser cadastrado.

    Returns:
        Usuario: O usuário criado com id gerado automaticamente.
    """
    global contador_usuario
    novo_usuario = Usuario(id=contador_usuario, nome=nome)
    usuarios.append(novo_usuario)
    contador_usuario += 1
    return novo_usuario


# Rota para listar usuários


@router.get("/usuarios/", response_model=List[Usuario])
def listar_usuarios() -> List[Usuario]:
    """Lista todos os usuários cadastrados.

    Returns:
        List[Usuario]: Lista com todos os usuários cadastrados.
    """
    return usuarios
