# API de Recomendação de Produtos

Este projeto é uma API criada com FastAPI para recomendação de produtos baseada no histórico de compras de usuários e preferências como categorias e tags.

## Funcionalidades

- **Criação de usuários**: Cadastro de novos usuários.
- **Cadastro de produtos**: Cadastro de produtos com nome, categoria e tags.
- **Histórico de compras**: Adicionar produtos ao histórico de compras de um usuário.
- **Recomendações de produtos**: Recomendação de produtos com base no histórico de compras e preferências do usuário.

## Tecnologias Utilizadas

- **Python 3.9+**
- **FastAPI**
- **Pydantic**
- **Uvicorn** (para rodar o servidor)
- **Pytest** (para testes automatizados)

## Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/uranolais/boas-praticas-python-curso01.git
   cd recomendacao-produtos
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual:**
   - No Windows:
     ```bash
     venv\Scripts\activate
     ```
   - No macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute o servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Acesse a documentação interativa da API:**
   Abra o navegador e acesse `http://127.0.0.1:8000/docs` para visualizar e testar as rotas da API.

## Estrutura do Projeto

```bash
.
├── app
│   ├── main.py              # Arquivo principal que inicia o FastAPI
│   ├── models               # Modelos Pydantic usados pela API
│   │   ├── models_produtos.py
│   │   └── models_usuarios.py
│   ├── routers              # Arquivos contendo os roteadores de usuários e produtos
│   │   ├── routers_produtos.py
│   │   └── routers_usuarios.py
├── tests
│   └── test_api.py          # Testes para a API
├── venv                     # Ambiente virtual
├── README.md                # Instruções sobre o projeto
└── requirements.txt         # Dependências do projeto
```

## Exemplos de Uso

### Criar um usuário:

- **POST /usuarios/**
  ```json
  {
    "nome": "Usuário Teste"
  }
  ```

### Criar um produto:

- **POST /produtos/**
  ```json
  {
    "nome": "Produto Teste",
    "categoria": "Eletrônicos",
    "tags": ["tecnologia", "novo"]
  }
  ```

### Adicionar histórico de compras:

- **POST /historico_compras/{usuario_id}**
  ```json
  {
    "produtos_ids": [1, 2]
  }
  ```

### Recomendação de produtos:

- **POST /recomendacoes/{usuario_id}**
  ```json
  {
    "categorias": ["Eletrônicos"],
    "tags": ["novo"]
  }
  ```

## Rodar os Testes

Para rodar os testes unitários:

```bash
pytest tests/
```

----
PEP8 - https://peps.python.org/pep-0008/


### Nomenclaturas (vscode F2)
- snake_case: usado para nomes de variáveis, funções e métodos;
- PascalCase: utilizado para nomes de classes;
- SCREAMING_SNAKE_CASE: reservado para constantes.

### Organização em pastas ( __init__.py )
- schemas
- routers

### Ordem dos Imports
- Bibliotecas padrão do python
- Importação de terceiros
- Importações locais do projeto

### Espaçamentos, Identação e Comentários
```bash
$ uv add ruff --dev
$ uv add mupy --dev
```

```
# pyproject.toml
[tool.ruff.lint]
select = ["E", "W", "F", "I"] 
```
- $ ruff check --fix
- $ ruff format
- $ mypy .

### Docstrings

### Tratamento de Erros
- HTTPException
- Em APIs FastAPI, o try/except é recomendado em situações específicas — não para fluxo normal de negócio (use HTTPException para isso). 
- try/except -> Operações de I/O, Parsing/conversão de dados externos, Integrações com serviços externos

### List Comprehensions


## Pytest

Testes unitártios. Verificam uma funcionalidade por vez.

Testes são reconhecidos com:
```python
def test_<nome_do_teste>:
  ...
```

- https://docs.pytest.org/en/stable/
- `assert` - verificação de condição
- https://fastapi.tiangolo.com/tutorial/testing/ -> uv add httpx


#### Pirâmide de Testes
A pirâmide de testes é um conceito que ilustra a estratégia de testes em um projeto de software, sugerindo a proporção ideal de diferentes tipos de testes. Ela é dividida em três camadas:

#### Testes Unitários (base da pirâmide): 
Estes testes validam as menores unidades do código, como funções ou métodos individuais. Eles são rápidos de executar, fáceis de escrever e devem compor a maior parte da suíte de testes, pois garantem que cada parte do código funcione isoladamente.

#### Testes de Integração (meio da pirâmide):
Estes testes verificam a interação entre diferentes módulos ou serviços. Eles são mais complexos que os testes unitários e garantem que os componentes do sistema funcionem juntos como esperado.

#### Testes de Aceitação / Funcionais / End-to-End (topo da pirâmide): 
Esses testes validam o sistema como um todo, garantindo que ele atenda aos requisitos do usuário. Eles costumam ser mais lentos e custosos, e, por isso, devem ser realizados com menos frequência em comparação com os testes das camadas inferiores.
