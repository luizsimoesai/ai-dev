# Reorganização do ai-dev para taxonomia agnóstica de framework

## Contexto e objetivo

O repositório `ai-dev` hoje mistura três coisas no mesmo nível: recipes de IA
(RAG, embeddings, MCP, chamadas a provider), tutoriais gerais de Python/git
sem relação com IA, e uma organização de `api-models/` por SDK de provider
em vez de por conceito. Isso vai contra o modelo do
[ai-cookbook](https://github.com/daveebbelaar/ai-cookbook), a referência
que o usuário quer seguir: lá a navegação é por *capacidade* (`agents/`,
`patterns/`, `knowledge/`, `mcp/`, `tools/`), o provider só aparece como
detalhe dentro de `models/`, e cada recipe-folha é autocontida (dependências
próprias, progressão numerada).

Objetivo desta mudança: reorganizar `ai-dev` para essa mesma filosofia, sem
traduzir conteúdo existente e sem reescrever recipes que já funcionam —
apenas mover, dividir dependências, e arquivar o que não é escopo de
cookbook de IA.

## Estado atual (resumo do diagnóstico)

- `api-models/{openai-api,anthropic-api,ollama-api}/` — organizado por SDK,
  não por conceito; um único `requirements.txt` compartilhado pelas três
  subpastas.
- `rag-from-scratch/`, `prompt-engineering-fundamentals/`,
  `embeddings-fundamentals/`, `document-parsing-fundamentals/`,
  `vector-database/`, `nlp-fundamentals/` — recipes/conceitos agnósticos,
  já soltos na raiz, sem categoria comum.
- `mcp/curso_mcp_deeplearningai/` e `mcp/tutorial_daveebbelaar/` — cópias
  integrais de cursos de terceiros, não recipes escritas pelo projeto.
- `api-tools/firecrawl-api/`, `python-libraries/` — wrappers de
  ferramentas de apoio (scraping, output no terminal), não são "recipe de
  IA" nem "modelo".
- `devops/{devops-docker,google-cloud}/` — infra de deploy.
- `tutoriais/{git-guia,github-cli,pyenv-guia,uv-guia}/` — guias de
  ferramentas de dev, a maioria genérica (não específica de IA).
- `python-tutorial/` — OOP, SOLID, sync/async: conteúdo de Python puro,
  fora do escopo de um cookbook de IA.
- `pyproject.toml` raiz (só declara `fastapi`, não usado por nenhuma
  recipe) + `uv.lock` + `main.py` (scaffold vazio do `uv init`) — não
  refletem o projeto real.
- Idioma: maioria do conteúdo em inglês nos nomes, mas `python-tutorial/`
  e parte de `tutoriais/` estão em português.

## Taxonomia alvo

Estrutura de topo, espelhando as categorias do ai-cookbook que fazem
sentido para o conteúdo que este repositório já tem:

```
models/       # uso direto de cada provider — o que muda de SDK pra SDK
patterns/     # padrões agnósticos de provider (RAG, prompt engineering)
knowledge/    # embeddings, vector-db, document parsing, NLP fundamentals
mcp/          # recipes próprias de MCP, numeradas
tools/        # ferramentas de apoio (uv, deploy, scraping, output)
_archive/     # conteúdo fora de escopo do cookbook de IA, preservado
```

### Mapeamento pasta a pasta

| Atual | Nova | Observação |
|---|---|---|
| `api-models/openai-api/` | `models/openai/` | |
| `api-models/anthropic-api/` | `models/anthropic/` | |
| `api-models/ollama-api/` | `models/ollama/` | |
| `rag-from-scratch/` | `patterns/rag-from-scratch/` | |
| `prompt-engineering-fundamentals/` | `patterns/prompt-engineering/` | |
| `embeddings-fundamentals/` | `knowledge/embeddings/` | |
| `document-parsing-fundamentals/` | `knowledge/document-parsing/` | |
| `vector-database/` | `knowledge/vector-database/` | |
| `nlp-fundamentals/` | `knowledge/nlp-fundamentals/` | |
| `mcp/curso_mcp_deeplearningai/` | `_archive/mcp-courses/curso_mcp_deeplearningai/` | cópia de curso, não é recipe do projeto |
| `mcp/tutorial_daveebbelaar/` | `_archive/mcp-courses/tutorial_daveebbelaar/` | idem |
| `mcp/` (recipes próprias) | `mcp/` | ver "Recipes novas de MCP" abaixo |
| `api-tools/firecrawl-api/` | `tools/firecrawl/` | |
| `python-libraries/` | `tools/python-libraries/` | |
| `devops/devops-docker/` | `tools/deployment/docker/` | |
| `devops/google-cloud/` | `tools/deployment/google-cloud/` | |
| `tutoriais/uv-guia/` | `tools/uv-guide/` | espelha `tools/uv-guide` do ai-cookbook |
| `tutoriais/git-guia/` | `_archive/dev-tutorials/git-guia/` | genérico, não específico de IA |
| `tutoriais/github-cli/` | `_archive/dev-tutorials/github-cli/` | idem |
| `tutoriais/pyenv-guia/` | `_archive/dev-tutorials/pyenv-guia/` | idem |
| `python-tutorial/` | `_archive/python-tutorial/` | Python puro, fora de escopo |
| `main.py`, `pyproject.toml`, `uv.lock` (raiz) | removidos | scaffold não usado; sem ambiente único a coordenar |

### Recipes novas de MCP

Como o conteúdo atual de `mcp/` é só cópia de curso, `mcp/` fica com uma
estrutura mínima criada do zero, no padrão numerado do ai-cookbook,
cobrindo o que os cursos arquivados ensinavam (server setup, client,
function calling vs. MCP). Escopo exato dessas recipes fica para o plano
de implementação decidir o nível de detalhe — o essencial aqui é que
`mcp/` não fique vazio nem seja só um redirecionamento para `_archive/`.

## Gestão de dependências

Cada recipe-folha (pasta final na árvore, ex: `models/openai/`,
`patterns/rag-from-scratch/`) ganha seu próprio `requirements.txt` mínimo,
igual ao ai-cookbook. Isso implica:

- Dividir `api-models/requirements.txt` (hoje compartilhado por
  openai/anthropic/ollama) em três arquivos, um por provider, cada um só
  com o que aquela pasta de fato importa.
- Mover `mcp/requirements.txt` para dentro das recipes novas de `mcp/`.
- `nlp-fundamentals/requirements.txt` e `python-libraries/requirements.txt`
  seguem para `knowledge/nlp-fundamentals/` e `tools/python-libraries/`
  sem alteração de conteúdo.
- `.env.example` / `.env.sample` de cada pasta viajam junto com a recipe,
  renomeados para `.env.example` (padroniza os dois nomes usados hoje).
- Sem `pyproject.toml`/`uv.lock` na raiz coordenando um ambiente único.

## Idioma e nomenclatura

Nenhum conteúdo existente é traduzido — cada arquivo mantém o idioma em
que já está escrito. Só os nomes de pastas/arquivos da nova taxonomia
seguem inglês kebab-case (convenção do ai-cookbook). Como a maior parte
dos nomes em português estava concentrada em `python-tutorial/` e
`tutoriais/`, que vão para `_archive/`, isso já resolve a maior parte da
mistura de idioma na árvore de pastas.

## README raiz

Reescrito curto (2-3 parágrafos), no espírito do ai-cookbook: o que é o
repositório, e um índice das categorias de topo (`models/`, `patterns/`,
`knowledge/`, `mcp/`, `tools/`, `_archive/`) com uma linha de descrição
cada. Sem inventar links externos (redes sociais, cursos, etc.) que o
usuário não pediu — isso é uma diferença deliberada do ai-cookbook, cujo
README é uma vitrine pessoal do autor.

## Mecânica de execução

- Todos os moves via `git mv`, para preservar histórico de cada arquivo.
- Ordem sugerida: (1) criar esqueleto de pastas novas, (2) mover recipes
  que não têm dependência cruzada (`knowledge/`, `patterns/`, `tools/`),
  (3) dividir e mover `api-models/` → `models/`, (4) tratar `mcp/`
  (arquivar cursos, criar recipes novas), (5) mover `devops/` →
  `tools/deployment/`, (6) arquivar `python-tutorial/` e o resto de
  `tutoriais/`, (7) remover `main.py`/`pyproject.toml`/`uv.lock` raiz,
  (8) reescrever `README.md` raiz.
- Depois de cada bloco de moves, checar se algum arquivo movido importa
  outro por caminho relativo dentro do próprio repo (a maioria dos scripts
  é standalone, mas vale conferir antes de fechar).
- Verificação final: `git status` limpo, árvore batendo com a tabela de
  mapeamento, nenhum arquivo órfão fora de `models/`, `patterns/`,
  `knowledge/`, `mcp/`, `tools/`, `_archive/` ou arquivos de config na
  raiz (`.gitignore`, `.python-version`, `README.md`).

## Fora de escopo

- Reescrever ou melhorar o conteúdo técnico de qualquer recipe existente.
- Traduzir conteúdo entre português e inglês.
- Criar recipes novas além do mínimo necessário para `mcp/` não ficar
  vazio.
- Configurar CI, testes automatizados, ou qualquer verificação além de
  conferência manual de que os arquivos foram movidos corretamente.

## Riscos

- Baixo: é uma reorganização de arquivos em um repositório pessoal, sem
  consumidores externos dependendo dos caminhos atuais. `git mv` preserva
  histórico e a operação é reversível via git caso algo saia errado.
