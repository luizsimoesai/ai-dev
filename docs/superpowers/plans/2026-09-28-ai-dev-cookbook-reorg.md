# Reorganização do ai-dev para taxonomia agnóstica de framework — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganizar o repositório `ai-dev` (raiz `/Users/luizsimoes/projetos/ai-dev`) de uma estrutura organizada por curso/provider para uma taxonomia por capacidade (`models/`, `patterns/`, `knowledge/`, `mcp/`, `tools/`, `_archive/`), com dependências isoladas por recipe e README raiz enxuto.

**Architecture:** Cada task move um grupo de pastas relacionadas via `git mv` (preserva histórico), ajusta arquivos de dependência/env quando uma pasta combinada é dividida em várias, e termina com uma verificação de árvore de arquivos + commit. Nenhum conteúdo técnico existente é reescrito — só movido, dividido em arquivos de config, ou arquivado.

**Tech Stack:** bash, git (mv/rm/add/commit), sem dependências novas.

**Spec:** `docs/superpowers/specs/2026-09-28-ai-dev-cookbook-reorg-design.md`

## Global Constraints

- Toda movimentação de arquivo/pasta rastreado usa `git mv`, nunca `mv` puro — exceção: `pyproject.toml` e `uv.lock` na raiz, que **não são rastreados pelo git** (confirmado via `git ls-files`, e listados em `.gitignore`), então são removidos com `rm` puro, não `git rm`.
- Nenhum conteúdo técnico de recipe existente é reescrito, melhorado ou traduzido — só movido.
- "Recipe-folha" para efeito de `requirements.txt`/`.env.example` próprio significa o nível de categoria/provider (ex: `models/openai/`, `tools/firecrawl/`), não cada subpasta numerada dentro dela — assim como no ai-cookbook, `models/openai/requirements.txt` cobre todas as subpastas numeradas de `models/openai/`. Não crie um `requirements.txt` por subpasta numerada a menos que um já exista ali (caso de `mcp/4-mcp-with-docker/requirements.txt`, usado pelo build do Docker, que permanece como está).
- Nomes de pastas/arquivos novos em inglês kebab-case. Conteúdo de arquivos existentes mantém o idioma original (não traduzir).
- Estrutura de topo final: `models/`, `patterns/`, `knowledge/`, `mcp/`, `tools/`, `_archive/`, mais `docs/`, `.gitignore`, `.python-version`, `README.md` na raiz (e `.venv/`, `.git/`, ignorados).

## Review Focus

- `git mv` de um diretório inteiro falha ou deixa arquivos órfãos se o diretório pai de destino ainda não existir — toda task cria o(s) diretório(s) pai com `mkdir -p` antes de qualquer `git mv`.
- Dividir um `requirements.txt`/`.env.example` combinado sem conferir contra os `import`s reais de cada pasta gera dependência sobrando ou faltando — a Task 3 (models/) já vem com a lista de imports levantada via `grep`; siga exatamente os pacotes listados ali.
- `pyproject.toml`/`uv.lock` na raiz não estão rastreados pelo git — usar `git rm` neles falha com "not under version control"; a Task 7 usa `rm` puro para os dois.
- Depois de `git mv` esvaziar uma pasta original (`api-models/`, `api-tools/`, `devops/`, `tutoriais/`, `mcp/tutorial_daveebbelaar/`), o diretório vazio continua no disco (git não rastreia diretórios) — cada task confirma com `find <dir> -type f` que não sobrou nenhum arquivo antes de rodar `rmdir <dir>`.
- O novo `README.md` raiz (Task 7) pode referenciar uma pasta que não existe mais ou usar um nome diferente do que as tasks anteriores realmente criaram — a Task 7 confere cada caminho citado no README com `test -d`/`test -f` antes de commitar.

---

### Task 1: Categoria `knowledge/`

**Files:**
- Move: `embeddings-fundamentals/` → `knowledge/embeddings/`
- Move: `document-parsing-fundamentals/` → `knowledge/document-parsing/`
- Move: `vector-database/` → `knowledge/vector-database/`
- Move: `nlp-fundamentals/` → `knowledge/nlp-fundamentals/`

**Interfaces:**
- Produces: `knowledge/embeddings/`, `knowledge/document-parsing/`, `knowledge/vector-database/`, `knowledge/nlp-fundamentals/` — caminhos que a Task 7 vai referenciar no README raiz.

- [ ] **Step 1: Conferir estado atual (precondição)**

```bash
cd /Users/luizsimoes/projetos/ai-dev
find embeddings-fundamentals document-parsing-fundamentals vector-database nlp-fundamentals -type f | sort
```

Esperado (exatamente estas linhas, em qualquer ordem):
```
document-parsing-fundamentals/README.md
embeddings-fundamentals/README.md
nlp-fundamentals/0_processamento_simbolico.py
nlp-fundamentals/1_ngramas.py
nlp-fundamentals/2_similaridade_morfologica.py
nlp-fundamentals/3_trnasformers.py
nlp-fundamentals/main.py
nlp-fundamentals/requirements.txt
vector-database/chromadb_vectordb/chromadb_ollama_embedding.py
vector-database/chromadb_vectordb/chromadb_tutorial.py
```

- [ ] **Step 2: Criar diretório pai e mover**

```bash
mkdir -p knowledge
git mv embeddings-fundamentals knowledge/embeddings
git mv document-parsing-fundamentals knowledge/document-parsing
git mv vector-database knowledge/vector-database
git mv nlp-fundamentals knowledge/nlp-fundamentals
```

- [ ] **Step 3: Verificar resultado**

```bash
find knowledge -type f | sort
for d in embeddings-fundamentals document-parsing-fundamentals vector-database nlp-fundamentals; do
  test -e "$d" && echo "AINDA EXISTE: $d" || echo "OK removido: $d"
done
```

Esperado: `find knowledge -type f` lista os mesmos 10 arquivos do Step 1 com o prefixo `knowledge/...` no lugar do nome antigo, e as 4 pastas antigas impressas como "OK removido".

- [ ] **Step 4: Commit**

```bash
git add -A
git status --short
git commit -m "$(cat <<'EOF'
Move recipes de conhecimento (embeddings, parsing, vector-db, NLP) para knowledge/

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Categoria `patterns/`

**Files:**
- Move: `rag-from-scratch/` → `patterns/rag-from-scratch/`
- Move: `prompt-engineering-fundamentals/` → `patterns/prompt-engineering/`

**Interfaces:**
- Produces: `patterns/rag-from-scratch/`, `patterns/prompt-engineering/`.

- [ ] **Step 1: Conferir estado atual**

```bash
cd /Users/luizsimoes/projetos/ai-dev
find rag-from-scratch prompt-engineering-fundamentals -type f | sort
```

Esperado:
```
prompt-engineering-fundamentals/README.md
rag-from-scratch/README.md
```

- [ ] **Step 2: Criar diretório pai e mover**

```bash
mkdir -p patterns
git mv rag-from-scratch patterns/rag-from-scratch
git mv prompt-engineering-fundamentals patterns/prompt-engineering
```

- [ ] **Step 3: Verificar resultado**

```bash
find patterns -type f | sort
test -e rag-from-scratch && echo "AINDA EXISTE" || echo "OK removido"
test -e prompt-engineering-fundamentals && echo "AINDA EXISTE" || echo "OK removido"
```

Esperado: `patterns/prompt-engineering/README.md` e `patterns/rag-from-scratch/README.md`, e ambas as pastas antigas "OK removido".

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
Move recipes agnósticas de padrão (RAG from scratch, prompt engineering) para patterns/

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Categoria `models/` (split de dependências por provider)

**Files:**
- Move: `api-models/openai-api/` → `models/openai/`
- Move: `api-models/anthropic-api/` → `models/anthropic/`
- Move: `api-models/ollama-api/` → `models/ollama/`
- Move: `api-models/README.md` → `models/openai/README.md` (o README só fala de links/API key da OpenAI)
- Remove (git rm): `api-models/requirements.txt`, `api-models/.env.example` (combinados, substituídos pelos arquivos por provider abaixo)
- Create: `models/openai/requirements.txt`, `models/anthropic/requirements.txt`, `models/ollama/requirements.txt`
- Create: `models/openai/.env.example`, `models/anthropic/.env.example`, `models/ollama/.env.example`

**Interfaces:**
- Produces: `models/openai/`, `models/anthropic/`, `models/ollama/` — cada um com seu próprio `requirements.txt` e `.env.example`.

Imports reais levantados via `grep` (usados para decidir o conteúdo dos `requirements.txt` abaixo):
- `openai-api/*.py`: `openai`, `python-dotenv`, `requests` (usado em `tools.py`)
- `anthropic-api/chatbot.py`: `anthropic`, `python-dotenv`, `arxiv`
- `ollama-api/*.py`: `ollama`, `python-dotenv`

- [ ] **Step 1: Conferir estado atual**

```bash
cd /Users/luizsimoes/projetos/ai-dev
find api-models -type f | sort
cat api-models/requirements.txt
cat api-models/.env.example
```

Esperado (arquivos):
```
api-models/.env.example
api-models/README.md
api-models/anthropic-api/chatbot.py
api-models/anthropic-api/papers/computers/papers_info.json
api-models/ollama-api/ollama_agent.py
api-models/ollama-api/ollama_chat.py
api-models/ollama-api/ollama_embeddings.py
api-models/ollama-api/ollama_websearch.py
api-models/openai-api/function-calling/0_function-calling.py
api-models/openai-api/function-calling/1_function_calling.py
api-models/openai-api/image-generation.py
api-models/openai-api/quickstart.py
api-models/openai-api/text-generation.py
api-models/openai-api/tools.py
api-models/requirements.txt
```

- [ ] **Step 2: Criar diretório pai e mover as pastas de provider + README**

```bash
mkdir -p models
git mv api-models/openai-api models/openai
git mv api-models/anthropic-api models/anthropic
git mv api-models/ollama-api models/ollama
git mv api-models/README.md models/openai/README.md
```

- [ ] **Step 3: Remover os arquivos combinados de dependência/env**

```bash
git rm api-models/requirements.txt api-models/.env.example
```

- [ ] **Step 4: Criar requirements.txt por provider**

```bash
cat > models/openai/requirements.txt <<'EOF'
python-dotenv
requests
openai
EOF

cat > models/anthropic/requirements.txt <<'EOF'
python-dotenv
arxiv
anthropic
EOF

cat > models/ollama/requirements.txt <<'EOF'
python-dotenv
ollama
EOF
```

- [ ] **Step 5: Criar .env.example por provider**

```bash
cat > models/openai/.env.example <<'EOF'
OPENAI_API_KEY=
EOF

cat > models/anthropic/.env.example <<'EOF'
ANTHROPIC_API_KEY=
EOF

cat > models/ollama/.env.example <<'EOF'
OLLAMA_API_KEY=
EOF
```

- [ ] **Step 6: Verificar que api-models/ ficou vazia e removê-la**

```bash
find api-models -type f
```

Esperado: nenhuma saída (vazio). Se aparecer algum arquivo, pare e investigue antes de continuar.

```bash
rmdir api-models
test -e api-models && echo "AINDA EXISTE" || echo "OK removido"
```

- [ ] **Step 7: Verificar árvore final de models/**

```bash
find models -type f | sort
cat models/openai/requirements.txt models/anthropic/requirements.txt models/ollama/requirements.txt
cat models/openai/.env.example models/anthropic/.env.example models/ollama/.env.example
```

Esperado: os arquivos `.py`/`.json` originais nos novos caminhos, mais os 3 `requirements.txt` e 3 `.env.example` criados nos Steps 4-5, mais `models/openai/README.md`.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
Divide api-models/ por provider em models/{openai,anthropic,ollama}/, com requirements.txt e .env.example próprios de cada um

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Categoria `mcp/` (arquiva curso de terceiro, promove recipes próprias)

`mcp/curso_mcp_deeplearningai/` é uma cópia de curso da DeepLearning.AI (notebooks, imagens, projeto com dados de papers) — vai para `_archive/`. `mcp/tutorial_daveebbelaar/` já segue a convenção de recipe numerada e autocontida (`1-server-setup`, `2-openai-sample`, `3-mcp-vs-function-calling`, `4-mcp-with-docker`) — promovemos essas 4 subpastas direto para `mcp/`, sem o wrapper de nome de curso, já que passam a ser as recipes oficiais de `mcp/` do projeto (nenhum conteúdo técnico é reescrito, só a pasta wrapper é removida).

**Files:**
- Move: `mcp/curso_mcp_deeplearningai/` → `_archive/mcp-courses/curso_mcp_deeplearningai/`
- Move: `mcp/tutorial_daveebbelaar/1-server-setup/` → `mcp/1-server-setup/`
- Move: `mcp/tutorial_daveebbelaar/2-openai-sample/` → `mcp/2-openai-sample/`
- Move: `mcp/tutorial_daveebbelaar/3-mcp-vs-function-calling/` → `mcp/3-mcp-vs-function-calling/`
- Move: `mcp/tutorial_daveebbelaar/4-mcp-with-docker/` → `mcp/4-mcp-with-docker/`
- Move: `mcp/tutorial_daveebbelaar/link.txt` → `mcp/link.txt` (mantém a atribuição da fonte original)
- Move: `mcp/.env.sample` → `mcp/.env.example`
- Keep as-is: `mcp/README.md`, `mcp/requirements.txt` (já cobrem as recipes numeradas que ficam em `mcp/`)

**Interfaces:**
- Produces: `mcp/1-server-setup/`, `mcp/2-openai-sample/`, `mcp/3-mcp-vs-function-calling/`, `mcp/4-mcp-with-docker/`, `_archive/mcp-courses/curso_mcp_deeplearningai/`.

- [ ] **Step 1: Conferir estado atual**

```bash
cd /Users/luizsimoes/projetos/ai-dev
find mcp -maxdepth 1
find mcp/curso_mcp_deeplearningai -type f | wc -l
find mcp/tutorial_daveebbelaar -type f | sort
```

Esperado para `mcp/tutorial_daveebbelaar`:
```
mcp/tutorial_daveebbelaar/1-server-setup/client-sse.py
mcp/tutorial_daveebbelaar/1-server-setup/client-stdio.py
mcp/tutorial_daveebbelaar/1-server-setup/server.py
mcp/tutorial_daveebbelaar/2-openai-sample/client-simple.py
mcp/tutorial_daveebbelaar/2-openai-sample/client.py
mcp/tutorial_daveebbelaar/2-openai-sample/data/kb.json
mcp/tutorial_daveebbelaar/2-openai-sample/server.py
mcp/tutorial_daveebbelaar/3-mcp-vs-function-calling/function-calling.py
mcp/tutorial_daveebbelaar/3-mcp-vs-function-calling/tools.py
mcp/tutorial_daveebbelaar/4-mcp-with-docker/Dockerfile
mcp/tutorial_daveebbelaar/4-mcp-with-docker/client.py
mcp/tutorial_daveebbelaar/4-mcp-with-docker/requirements.txt
mcp/tutorial_daveebbelaar/4-mcp-with-docker/server.py
mcp/tutorial_daveebbelaar/link.txt
```

- [ ] **Step 2: Arquivar o curso de terceiro**

```bash
mkdir -p _archive/mcp-courses
git mv mcp/curso_mcp_deeplearningai _archive/mcp-courses/curso_mcp_deeplearningai
```

- [ ] **Step 3: Promover as recipes de tutorial_daveebbelaar para mcp/**

```bash
git mv mcp/tutorial_daveebbelaar/1-server-setup mcp/1-server-setup
git mv mcp/tutorial_daveebbelaar/2-openai-sample mcp/2-openai-sample
git mv mcp/tutorial_daveebbelaar/3-mcp-vs-function-calling mcp/3-mcp-vs-function-calling
git mv mcp/tutorial_daveebbelaar/4-mcp-with-docker mcp/4-mcp-with-docker
git mv mcp/tutorial_daveebbelaar/link.txt mcp/link.txt
```

- [ ] **Step 4: Verificar que tutorial_daveebbelaar/ ficou vazia e removê-la**

```bash
find mcp/tutorial_daveebbelaar -type f
```

Esperado: nenhuma saída.

```bash
rmdir mcp/tutorial_daveebbelaar
```

- [ ] **Step 5: Padronizar o nome do arquivo de env**

```bash
git mv mcp/.env.sample mcp/.env.example
```

- [ ] **Step 6: Verificar árvore final de mcp/ e do archive**

```bash
find mcp -maxdepth 1 | sort
find mcp -type f | sort
find _archive/mcp-courses/curso_mcp_deeplearningai -type f | wc -l
```

Esperado para `find mcp -maxdepth 1`:
```
mcp
mcp/.env.example
mcp/1-server-setup
mcp/2-openai-sample
mcp/3-mcp-vs-function-calling
mcp/4-mcp-with-docker
mcp/README.md
mcp/link.txt
mcp/requirements.txt
```
E a contagem de arquivos em `_archive/mcp-courses/curso_mcp_deeplearningai` deve bater com a contagem do Step 1.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
Arquiva curso_mcp_deeplearningai e promove as recipes numeradas de tutorial_daveebbelaar para mcp/

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Categoria `tools/`

**Files:**
- Move: `api-tools/firecrawl-api/` → `tools/firecrawl/`
- Move: `api-tools/requirements.txt` → `tools/firecrawl/requirements.txt`
- Move: `api-tools/.env.sample` → `tools/firecrawl/.env.example`
- Move: `python-libraries/` → `tools/python-libraries/`
- Move: `devops/devops-docker/` → `tools/deployment/docker/`
- Move: `devops/google-cloud/` → `tools/deployment/google-cloud/`
- Move: `tutoriais/uv-guia/` → `tools/uv-guide/`

**Interfaces:**
- Produces: `tools/firecrawl/`, `tools/python-libraries/`, `tools/deployment/docker/`, `tools/deployment/google-cloud/`, `tools/uv-guide/`.

- [ ] **Step 1: Conferir estado atual**

```bash
cd /Users/luizsimoes/projetos/ai-dev
find api-tools python-libraries devops -type f | sort
find tutoriais/uv-guia -type f
```

Esperado:
```
api-tools/.env.sample
api-tools/firecrawl-api/firecrawl_quickstart.py
api-tools/requirements.txt
devops/devops-docker/.dockerignore
devops/devops-docker/Dockerfile
devops/devops-docker/README.md
devops/devops-docker/docker-compose.yaml
devops/google-cloud/README.md
python-libraries/html2text.py
python-libraries/requirements.txt
python-libraries/rich_markdown.py
tutoriais/uv-guia/uv-commands.gif
```

- [ ] **Step 2: Criar diretórios pai e mover**

```bash
mkdir -p tools/deployment
git mv api-tools/firecrawl-api tools/firecrawl
git mv api-tools/requirements.txt tools/firecrawl/requirements.txt
git mv api-tools/.env.sample tools/firecrawl/.env.example
git mv python-libraries tools/python-libraries
git mv devops/devops-docker tools/deployment/docker
git mv devops/google-cloud tools/deployment/google-cloud
git mv tutoriais/uv-guia tools/uv-guide
```

- [ ] **Step 3: Verificar que api-tools/ e devops/ ficaram vazias e removê-las**

```bash
find api-tools -type f
find devops -type f
```

Esperado: nenhuma saída para as duas.

```bash
rmdir api-tools
rmdir devops
```

(`tutoriais/` ainda tem `git-guia`, `github-cli`, `pyenv-guia` — não remover agora, isso é da Task 6.)

- [ ] **Step 4: Verificar árvore final de tools/**

```bash
find tools -type f | sort
```

Esperado: os mesmos arquivos do Step 1, nos novos caminhos (`tools/firecrawl/...`, `tools/python-libraries/...`, `tools/deployment/docker/...`, `tools/deployment/google-cloud/...`, `tools/uv-guide/uv-commands.gif`).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
Move ferramentas de apoio (firecrawl, python-libraries, deploy, uv-guide) para tools/

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Categoria `_archive/` (conteúdo não-IA)

**Files:**
- Move: `python-tutorial/` → `_archive/python-tutorial/`
- Move: `tutoriais/git-guia/` → `_archive/dev-tutorials/git-guia/`
- Move: `tutoriais/github-cli/` → `_archive/dev-tutorials/github-cli/`
- Move: `tutoriais/pyenv-guia/` → `_archive/dev-tutorials/pyenv-guia/`

**Interfaces:**
- Produces: `_archive/python-tutorial/`, `_archive/dev-tutorials/`.

- [ ] **Step 1: Conferir estado atual**

```bash
cd /Users/luizsimoes/projetos/ai-dev
find python-tutorial -type f | wc -l
find tutoriais -maxdepth 1
```

Esperado para `tutoriais`: só `git-guia`, `github-cli`, `pyenv-guia` (uv-guia já saiu na Task 5).

- [ ] **Step 2: Criar diretório pai e mover**

```bash
mkdir -p _archive/dev-tutorials
git mv python-tutorial _archive/python-tutorial
git mv tutoriais/git-guia _archive/dev-tutorials/git-guia
git mv tutoriais/github-cli _archive/dev-tutorials/github-cli
git mv tutoriais/pyenv-guia _archive/dev-tutorials/pyenv-guia
```

- [ ] **Step 3: Verificar que tutoriais/ ficou vazia e removê-la**

```bash
find tutoriais -type f
```

Esperado: nenhuma saída.

```bash
rmdir tutoriais
test -e python-tutorial && echo "AINDA EXISTE" || echo "OK removido"
test -e tutoriais && echo "AINDA EXISTE" || echo "OK removido"
```

- [ ] **Step 4: Verificar contagem de arquivos no archive**

```bash
find _archive/python-tutorial -type f | wc -l
find _archive/dev-tutorials -type f | sort
```

A contagem de `_archive/python-tutorial` deve bater com o Step 1. `_archive/dev-tutorials` deve listar `git-guia/git.pdf`, `github-cli/github-cli.md`, `github-cli/github-cli.pdf`, `pyenv-guia/pyenv-guia.md`.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
Arquiva conteúdo não-IA (python-tutorial, guias gerais de dev) em _archive/

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Limpeza da raiz, novo README, auditoria final

**Files:**
- Remove (git rm): `main.py`
- Remove (rm puro, não rastreado): `pyproject.toml`, `uv.lock`
- Modify: `README.md` (reescrita completa)

**Interfaces:**
- Consumes: `models/`, `patterns/`, `knowledge/`, `mcp/`, `tools/`, `_archive/` — produzidos pelas Tasks 1-6. O README desta task só pode citar caminhos que essas tasks realmente criaram.

- [ ] **Step 1: Confirmar que pyproject.toml e uv.lock não são rastreados**

```bash
cd /Users/luizsimoes/projetos/ai-dev
git ls-files pyproject.toml uv.lock
```

Esperado: nenhuma saída (confirma que não estão no índice do git).

- [ ] **Step 2: Remover main.py (rastreado) e pyproject.toml/uv.lock (não rastreados)**

```bash
git rm main.py
rm pyproject.toml uv.lock
test -e main.py && echo "AINDA EXISTE" || echo "OK removido"
test -e pyproject.toml && echo "AINDA EXISTE" || echo "OK removido"
test -e uv.lock && echo "AINDA EXISTE" || echo "OK removido"
```

- [ ] **Step 3: Reescrever o README raiz**

```bash
cat > README.md <<'EOF'
### Introduction

This repository is a collection of practical, copy/paste-ready recipes for building AI systems — organized by concept, not by provider or framework, so the code stays easy to adapt regardless of which SDK or library you're using.

## Structure

- `models/` — direct usage of each provider (OpenAI, Anthropic, Ollama): what actually changes from SDK to SDK.
- `patterns/` — provider-agnostic patterns, like RAG from scratch and prompt engineering.
- `knowledge/` — embeddings, document parsing, vector databases, and NLP fundamentals.
- `mcp/` — Model Context Protocol recipes: server, client, and function-calling comparisons.
- `tools/` — supporting tooling: uv, deployment (Docker, Google Cloud), scraping, Python utilities.
- `_archive/` — content outside the scope of AI recipes (general Python/dev tutorials, third-party course copies), kept for reference.

Each leaf folder carries its own `requirements.txt` (and `.env.example` where relevant) — no shared dependency file across recipes.
EOF
```

- [ ] **Step 4: Conferir que todo caminho citado no README existe de fato**

```bash
for d in models patterns knowledge mcp tools _archive; do
  test -d "$d" && echo "OK: $d" || echo "FALTANDO: $d"
done
```

Esperado: as 6 linhas "OK: ...". Se alguma faltar, pare — significa que uma task anterior não terminou como esperado.

- [ ] **Step 5: Auditoria final da árvore**

```bash
find . -maxdepth 1 -not -path '.' -not -path './.git' -not -path './.venv' | sort
```

Esperado (nomes, ignorando `.DS_Store` se presente): `./.gitignore`, `./.python-version`, `./README.md`, `./_archive`, `./docs`, `./knowledge`, `./mcp`, `./models`, `./patterns`, `./tools`.

```bash
find . -type d -empty -not -path './.git*' -not -path './.venv*'
```

Esperado: nenhuma saída (nenhum diretório vazio esquecido).

```bash
git status --short
```

Confira que só aparecem as mudanças desta task (`README.md` modificado, `main.py` removido) — todo o resto já foi commitado nas tasks anteriores.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
Remove scaffold não usado da raiz (main.py, pyproject.toml, uv.lock) e reescreve o README com o índice da nova taxonomia

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
git log --oneline -8
```
