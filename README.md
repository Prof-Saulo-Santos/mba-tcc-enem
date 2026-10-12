# 📊 TCC MBA — Previsão de Desempenho no ENEM e Arquitetura MLOps

Projeto de Conclusão de Curso focado na previsão de notas do ENEM, análise de determinismo social e pipeline de MLOps automatizado.

---

## 🚀 Como Reconstruir e Rodar o Projeto em Qualquer Máquina

O projeto é configurado para rodar com **Python 3.13**.  
**Mesmo que a sua máquina NÃO tenha o Python 3.13 instalado**, o gerenciador **[`uv`](https://github.com/astral-sh/uv)** faz o download e configuração do Python 3.13 de forma 100% autônoma e portátil, sem exigir privilégios de administrador ou pacotes do sistema operacional.

### 1. Clonar o Repositório
```bash
git clone <URL_DO_REPOSITORIO>
cd enem
```

### 2. Instalar o `uv` (se ainda não tiver)
- **Linux / macOS:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
*(Ou, caso já possua qualquer versão de Python instalada, pode instalar via: `pip install uv`)*

### 3. Criar o Ambiente Virtual com Python 3.13
Graças ao arquivo `.python-version`, o `uv` reconhece e baixa o CPython 3.13 standalone automaticamente:
```bash
uv venv
```

### 4. Ativar o Ambiente Virtual
- **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows:**
  ```powershell
  .venv\Scripts\activate
  ```

### 5. Instalar as Dependências
Com o ambiente ativado, execute a instalação ultrarrápida com o `uv`:
```bash
uv pip install -r requirements.txt
```

---

## 📁 Dados (Microdados do ENEM)

Por padrão, a pasta `data/` não é versionada no Git devido ao tamanho dos microdados do INEP.

Para baixar as safras históricas necessárias:
```bash
bash scripts/download_microdados.sh
```

---

## 🧪 Execução dos Testes e Pipeline

- **Executar testes automatizados:**
  ```bash
  pytest tests/ -v
  ```

- **Iniciar Jupyter Notebook / JupyterLab:**
  ```bash
  jupyter lab
  ```
