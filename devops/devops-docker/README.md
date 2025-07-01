# Docker

Docker é uma plataforma que permite empacotar, distribuir e executar aplicações em contêineres leves, isolados e portáteis.
  
- https://www.docker.com/
- https://hub.docker.com/
- https://docs.docker.com/reference/dockerfile/

### Dockerfile
O Dockerfile é um arquivo de configuração que contém instruções para criar uma imagem Docker personalizada, definindo o ambiente e os passos necessários para executar uma aplicação.

```Dockerfile
# Usa a imagem base do Python 3.13.5 com Alpine Linux
FROM python:3.13.5-alpine3.22

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia apenas o requirements.txt primeiro.
# Isso permite que o cache do Docker seja
# aproveitado: só reexecuta a instalação de
# dependências quando esse arquivo muda.
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do projeto
COPY . .

```

### .dockerignore

O arquivo .dockerignore lista padrões de arquivos e pastas que devem ser ignorados durante o build da imagem, evitando que conteúdos desnecessários sejam copiados para o contêiner e reduzindo o tamanho da imagem.

### docker-compose.yaml

O docker-compose.yaml é um arquivo de orquestração que descreve, em formato declarativo, como vários serviços Docker devem ser construídos, configurados e executados conjuntamente.

```docker 
services:
  app:
    image: fastapi_app
    build: .              # Constrói a imagem a partir do Dockerfile local
    container_name: fastapi_app
    command: sh -c "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"  # Servidor FastAPI
    env_file:
      - .env
    volumes:
      - .:/app            # Monta o código para hot-reload em desenvolvimento
    ports:
      - "8000:8000"       # Exponha a porta 8000
```

Exemplos de comandos: (não estão em ordem de execução, são apenas exemplos)
```bash
$ docker ps
$ docker ps -a
$ docker images

$ docker compose up --build
$ docker compose up -d
$ docker compose down
```