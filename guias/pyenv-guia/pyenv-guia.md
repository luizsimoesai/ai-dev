# pyenv
Ferramenta para gerenciar diferentes versões do Python no seu sistema:

---

### 🔧 **1. Ver versões do Python disponíveis para instalar**

```bash
pyenv install --list
```

Mostra todas as versões do Python que você pode instalar.

---

### 📥 **2. Instalar uma versão específica do Python**

```bash
pyenv install 3.10.12
```

Instala a versão 3.10.12 do Python (ou qualquer outra que você quiser).

---

### 📌 **3. Definir a versão global do Python (para todo o sistema)**

```bash
pyenv global 3.10.12
```

Define a versão do Python que será usada por padrão em todo o sistema.

---

### 📁 **4. Definir a versão do Python apenas para um projeto (diretório)**

```bash
pyenv local 3.11.4
```

Cria um arquivo `.python-version` no diretório atual para usar essa versão só naquele projeto.

---

### ❓ **5. Ver a versão do Python atualmente ativa**

```bash
pyenv version
```

Mostra qual versão do Python está sendo usada naquele momento.

---

### 🔍 **6. Ver todas as versões do Python instaladas com pyenv**

```bash
pyenv versions
```

Lista todas as versões do Python que você instalou com o pyenv.

---

### 🔄 **7. Atualizar a lista de versões disponíveis**

```bash
pyenv update
```

Atualiza o repositório de onde o pyenv busca novas versões do Python.

---