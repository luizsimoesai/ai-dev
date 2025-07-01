# --- EXEMPLO ---

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
