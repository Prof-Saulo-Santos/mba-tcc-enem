# 📊 TCC MBA — Previsão de Desempenho no ENEM e Arquitetura MLOps

Projeto de Conclusão de Curso de MBA que integra **Sociologia Educacional** (investigação empírica do determinismo socioeconômico à luz de Pierre Bourdieu), **Ciência de Dados / Machine Learning em larga escala** e **Engenharia de MLOps ponta a ponta** sobre uma década de microdados públicos do ENEM (`2014–2023`).

---

## 🎯 Visão Geral do Projeto

* **Alvo Oficial (`TARGET_M4`):** Média aritmética simples das **4 provas objetivas calibradas pela TRI** (`NU_NOTA_CN`, `NU_NOTA_CH`, `NU_NOTA_LC` e `NU_NOTA_MT`), validada psicometricamente (**Alfa de Cronbach = `0,865`**) e blindada contra ruído subjetivo da Redação (escala TCT).
* **Esquadrão de Elite (`6` features parcimoniosas):**
  1. `RENDA_PER_CAPITA` *(salários mínimos por morador — `Q006 / Q005`)*
  2. `Q024` *(posse de computador no domicílio)*
  3. `TP_ANO_CONCLUIU` *(anos desde a conclusão do Ensino Médio, harmonizado em `[0, 9]`)*
  4. `TP_LINGUA` *(língua estrangeira: `0 = Inglês`, `1 = Espanhol`)*
  5. `TP_SEXO` *(sexo: `0 = Feminino`, `1 = Masculino`)*
  6. `Q002` *(escolaridade materna / mulher responsável, `0` a `7`)*
* **Recorte Censitário (`2014–2023`) e Barreira LGPD (`2024–2025`):** A harmonização semântica via NLP/SBERT (`paraphrase-multilingual-MiniLM-L12-v2`) homologou a janela `2014–2023` (*Década de Ouro*). A partir de `2024`, por adequação à LGPD, o INEP separou `PARTICIPANTES` e `RESULTADOS` sem chave identificadora de junção, encerrando o escopo censitário em `2023` e comprovando a generalização temporal por meio de **Validação *Out-of-Time* Interna (`2014–2022 -> 2023`)**.

---

## 🏆 Principais Resultados Homologados

| Marco / Artefato | Evidência Empírica Oficial |
| :--- | :--- |
| **Consolidação Histórica (`2014–2023`)** | `56.568.785` inscritos varridos $\rightarrow$ **`37.593.629` elegíveis** (`8` colunas, `15 bytes/linha`, **`153,17 MB`** em Parquet) |
| **Modelo Campeão (`XGBRegressor` `hist`)** | Holdout estratificado (`7.518.726` alunos): **$R^2 = 0{,}33780$** \| **$\text{RMSE} = 57{,}7439\text{ pts}$** \| **$\text{MAE} = 45{,}5904\text{ pts}$** |
| **Validação *Out-of-Time* (`2014–2022 -> 2023`)** | Safra cega de `2023` (`2.678.264` alunos): **$R^2 = 0{,}31842$** \| **$\text{RMSE} = 67{,}6232\text{ pts}$** \| $\text{MAE} = 52{,}8526\text{ pts}$ |
| **Explicabilidade (`TreeSHAP`, `N = 10.000`)** | Liderança de `RENDA_PER_CAPITA` (`18,483 pts` de `|SHAP|` médio / **`30,10%`** do impacto total) |
| **Microserviço & Testes (`src/api/`, `tests/`)** | FastAPI + Pydantic v2 (`extra="forbid"`), **`25/25 PASSED`** no `pytest` e imagem Docker multi-stage (**`515 MB` Content Size**) |

> Os metadados completos e o checksum SHA-256 do modelo campeão estão auditados em [`models/enem_model_card.json`](models/enem_model_card.json).

---

## 🏗️ Arquitetura em 2 Etapas e Estrutura do Repositório

1. **Etapa 1 — Laboratório Científico, NLP, Big Data e Modelagem (`notebooks/01` a `06`):** Investigação estrutural, EDA (`2023`), seleção parcimoniosa, mapeamento semântico SBERT, consolidação histórica em *chunks* e treinamento escalável com rastreamento no **MLflow** (`mlflow.db`).
2. **Etapa 2 — Produtização, Testes, Containerização e CI/CD (`src/api/`, `Dockerfile`, `.github/workflows/deploy.yml`):** API REST FastAPI, validação estrita anti-leakage (`HTTP 422`), container multi-stage com `uv` e esteira automatizada no GitHub Actions (`quality-gate-ci` $\rightarrow$ `docker-smoke-test` $\rightarrow$ `deploy-aws` condicional para Amazon ECR e AWS App Runner).

```text
enem/
├── .github/workflows/deploy.yml   # CI/CD: Quality Gate (SHA-256 + pytest), Docker Smoke Test e deploy AWS
├── data/processed/                # Contratos JSON canônicos e bases Parquet (não versionados no Git)
├── docs/                          # Guias passo a passo, diagramas e roteiros de slides
├── media/                         # Diagramas arquiteturais e figuras científicas (nb06_figuras/)
├── models/                        # Artefato campeão (enem.pkl, enem_xgboost.ubj) e Model Card JSON
├── notebooks/                     # Esteira analítica completa (01 a 06)
├── scripts/download_microdados.sh # Download dos microdados públicos do INEP
├── src/api/                       # Microserviço FastAPI (main.py, model_loader.py, schemas.py)
├── tests/                         # Suíte de contrato HTTP e paridade XGBoost (25 testes)
├── Dockerfile & docker-compose.yml# Containerização multi-stage FinOps (appuser não-root)
├── AGENT.md                       # Memória técnica e diretrizes operacionais do projeto
└── visao_geral_projeto.md         # Mapa de etapas, capítulos, guias e roteiros de defesa
```

---

## 🚀 Como Reconstruir o Ambiente (`uv` + Python 3.13)

O projeto utiliza **Python 3.13** (definido em `.python-version`). Mesmo que sua máquina não tenha o Python 3.13 instalado, o gerenciador **[`uv`](https://github.com/astral-sh/uv)** realiza o download e a configuração do ambiente de forma autônoma.

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
*(Alternativa caso já possua Python instalado: `pip install uv`)*

### 3. Criar e Ativar o Ambiente Virtual
```bash
uv venv
```
- **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\activate
  ```

### 4. Instalar as Dependências
- **Ambiente completo (Notebooks, NLP/SBERT, MLflow, SHAP e testes):**
  ```bash
  uv pip install -r requirements.txt
  ```
- **Ambiente enxuto apenas para servir a API FastAPI (produção/testes da Etapa 2):**
  ```bash
  uv pip install -r requirements-api.txt pytest httpx
  ```

---

## 📁 Dados (Microdados do ENEM)

Por padrão, os diretórios de dados brutos e processados (`data/raw/` e arquivos `.parquet` em `data/processed/`) não são versionados no Git devido ao volume dos microdados do INEP.

Para baixar as safras históricas em `data/raw/`:
```bash
bash scripts/download_microdados.sh
```
> **Nota:** O script contempla os links históricos de `2009` a `2025`, mas a série consolidada e modelada oficialmente pelo pipeline corresponde à janela **`2014–2023`** em razão da ruptura estrutural da LGPD a partir de `2024`.

---

## 🔬 Executando a Etapa 1 (Notebooks `01` a `06`)

Inicie o JupyterLab e execute os notebooks em ordem sequencial:
```bash
jupyter lab
```
1. `notebooks/01_investigacao_estrutural.ipynb` — Diagnóstico de layouts do INEP e detecção da ruptura em `2024`.
2. `notebooks/02_eda.ipynb` — Limpeza metodológica de `2023` (`212.386` concluintes), análise bivariada e *Cohen's d*.
3. `notebooks/03_engenharia_features.ipynb` — Criação de `RENDA_PER_CAPITA`, seleção do `TARGET_M4` e das 6 features (`data/processed/contrato_features_modelagem.json`).
4. `notebooks/04_varredura_semantica.ipynb` — Harmonização histórica via NLP/SBERT (`data/processed/schema_mapping_historico.json`).
5. `notebooks/05_consolidacao_historica.ipynb` — Consolidação decenal em *chunks* (`2014–2023`), deflação por Salário Mínimo e *downcasting* (`data/processed/contrato_consolidacao_2014_2023.json`).
6. `notebooks/06_treinamento_modelo.ipynb` — Treinamento escalável, MLflow, validação OOT `2023`, TreeSHAP e exportação de `models/enem.pkl`.

---

## ☁️ Executando a Etapa 2 (Testes, API FastAPI e Docker)

### 1. Executar a Suíte Automatizada de Testes (`25` testes)
```bash
pytest tests/ -v
```

### 2. Subir a API Localmente (sem Docker)
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```
Acesse a documentação interativa Swagger em `http://localhost:8000/docs`.

### 3. Subir a API Containerizada com Docker Compose
```bash
docker compose up -d
```
Para encerrar os serviços:
```bash
docker compose down
```

### 4. Exemplos de Chamadas aos Endpoints
- **Healthcheck e verificação SHA-256 (`GET /health`):**
  ```bash
  curl -s http://localhost:8000/health | python3 -m json.tool
  ```
- **Metadados e métricas oficiais (`GET /info`):**
  ```bash
  curl -s http://localhost:8000/info | python3 -m json.tool
  ```
- **Inferência individual (`POST /predict`):**
  ```bash
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"RENDA_PER_CAPITA": 1.5, "Q024": 1, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 0, "Q002": 4}'
  ```
- **Bloqueio Anti-Leakage (`NU_ANO` rejeitado com `HTTP 422`):**
  ```bash
  curl -i -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"RENDA_PER_CAPITA": 1.5, "Q024": 1, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 0, "Q002": 4, "NU_ANO": 2023}'
  ```

---

## 📚 Documentação de Referência

* [`visao_geral_projeto.md`](visao_geral_projeto.md) — Mapa completo das etapas, capítulos (`01` a `07`), guias técnicos e roteiros de slides.
* [`AGENT.md`](AGENT.md) — Guia arquitetural detalhado, métricas oficiais e regras operacionais do repositório.
* [`docs/passo-a-passo-07-api-docker.md`](docs/passo-a-passo-07-api-docker.md) — Auditoria técnica da API FastAPI, testes, imagem Docker e pipeline CI/CD.
* [`docs/onde-tudo-comeca.md`](docs/onde-tudo-comeca.md) — Histórico didático da fase inicial de ingestão/pipeline (arquivada na tag `archive/pre-faxina-2026-11`).
