from typing import Dict, List

from fastapi import APIRouter, HTTPException

from app.routers.usuario import usuarios
from app.schemas.produto import CriarProduto, HistoricoCompras, Preferencias, Produto

router = APIRouter()

produtos: List[Produto] = []
contador_produto: int = 1

# Histórico de compras em memória
historico_de_compras: Dict[int, List[int]] = {}

# Rota para cadastrar produtos


@router.post("/produtos/", response_model=Produto)
def criar_produto(produto: CriarProduto) -> Produto:
    """Cadastra um novo produto.

    Args:
        produto (CriarProduto): Dados do produto a ser cadastrado.

    Returns:
        Produto: O produto criado com id gerado automaticamente.
    """
    global contador_produto
    novo_produto = Produto(id=contador_produto, **produto.model_dump())
    produtos.append(novo_produto)
    contador_produto += 1
    return novo_produto


# Rota para listar todos os produtos


@router.get("/produtos/", response_model=List[Produto])
def listar_produtos() -> List[Produto]:
    """Lista todos os produtos cadastrados.

    Returns:
        List[Produto]: Lista com todos os produtos cadastrados.
    """
    return produtos


# Rota para simular a criação do histórico de compras de um usuário


@router.post("/historico_compras/{usuario_id}")
def adicionar_historico_compras(
    usuario_id: int, compras: HistoricoCompras
) -> Dict[str, str]:
    """Adiciona ou atualiza o histórico de compras de um usuário.

    Args:
        usuario_id (int): ID do usuário.
        compras (HistoricoCompras): Lista de IDs dos produtos comprados.

    Returns:
        Dict[str, str]: Mensagem de confirmação da atualização.

    Raises:
        HTTPException: 404 se o usuário não for encontrado.
    """
    if usuario_id not in [usuario.id for usuario in usuarios]:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    historico_de_compras[usuario_id] = compras.produtos_ids
    return {"mensagem": "Histórico de compras atualizado"}


# Rota para recomendações de produtos


@router.post("/recomendacoes/{usuario_id}", response_model=List[Produto])
def recomendar_produtos(usuario_id: int, preferencias: Preferencias) -> List[Produto]:
    """Recomenda produtos com base no histórico de compras e preferências do usuário.

    Busca os produtos do histórico de compras do usuário e aplica filtros opcionais
    por categoria e tags. Filtros não informados são ignorados.

    Args:
        usuario_id (int): ID do usuário.
        preferencias (Preferencias): Preferências opcionais de categorias e tags
            para filtrar as recomendações.

    Returns:
        List[Produto]: Lista de produtos do histórico filtrados pelas preferências.
            Retorna lista vazia se nenhum produto corresponder aos filtros.

    Raises:
        HTTPException: 404 se o usuário não possuir histórico de compras.
    """
    if usuario_id not in historico_de_compras:
        raise HTTPException(
            status_code=404, detail="Histórico de compras não encontrado"
        )

    produtos_recomendados = []

    # Buscar produtos com base no histórico de compras do usuário

    produtos_recomendados = [
        produto
        for produto_id in historico_de_compras[usuario_id]
        for produto in produtos
        if produto.id == produto_id
    ]

    # Filtrar as recomendações com base nas preferências
    if preferencias.categorias:
        produtos_recomendados = [
            produto
            for produto in produtos_recomendados
            if produto.categoria in preferencias.categorias
        ]

    if preferencias.tags:
        produtos_recomendados = [
            produto
            for produto in produtos_recomendados
            if any(tag in preferencias.tags for tag in produto.tags)
        ]

    return produtos_recomendados
