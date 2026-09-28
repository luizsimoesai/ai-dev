# GCP - Google Cloud Provider

### Criar um projeto no GCP

Criar um novo projeto no Google Cloud - https://console.cloud.google.com/

### Instalar a CLI gcloud

Linha de comando para rodas comandos do GCP no terminal. O Google Cloud CLI inclui as ferramentas de linha de comando , 'gcloude' e 'gsutil' - https://cloud.google.com/sdk/docs/install

```bash
$ gcloud version
```

### Autenticação no Google Cloud

```bash
$ gcloud auth login
```

### Escolher o projeto

```bash
$ gcloud config set project <project_id>
```

### Para rodar um container na nuvem de forma 'serverless'
Sem a criação de Virtual Machines. O Google que gerencia como escala.

```bash
$ gcloud run deploy --port=8000
```
Opções que serão aprensentadas:
- Escolher a pasta do projeto (Dockerfile) ou 'enter' se já estiver na pasta do projeto;
- Escolher o nome do serviço;
- Confirmar a instalação de outras APIs necessárias (Artifact Registry, etc);
- Escolher uma região: [32] southamerica-east1;
- Confirmar a criação de um Artifact Registry;
- Confirmar 'Allow unauthenticated invocations';

No final, será fornecido a URL do serviço.

### No GCP, entrar em Artifact Registry

Verificar a criação da imagem Docker no Google Cloud

### No GCP, entrar em Cloud Run

Informações sobre o deploy, métricas, logs.
