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
| **Microserviço & Quality Gate (`src/api/`, `tests/`)** | FastAPI + Pydantic v2 (`extra="forbid"`), **`26/26 PASSED`** no `pytest` (`ruff` & `mypy` limpos), endpoint `/metrics` e imagem Docker multi-stage (**`515 MB` Content Size**) |
| **Observabilidade (`monitoring/`)** | Endpoint `GET /metrics` (`prometheus-client`) coletado pelo **Prometheus** (`:9090`, scrape `5s`) + dashboard **Grafana** (`:3000`, `10` painéis de SLA, 422 e *drift*) |
| **IaC & Dados em Nuvem (`infra/`, `.dvc/`)** | **Terraform** (`11` recursos no Estágio 1: `S3`, `ECR`, `IAM OIDC`, `App Runner`) + **DVC + S3** versionando `~180 MiB` em `.parquet` (`dvc-store/`) |
| **MLflow Remoto (`Dockerfile.mlflow`, `mlops`)** | Backend **PostgreSQL 16** + **Amazon S3** (`mlflow-artifacts/`, `17` objetos / `~2,49 MiB`), `run_id = 6490c396b0e04147b156bedb0c8af9f7` |

> Os metadados completos e o checksum SHA-256 do modelo campeão estão auditados em [`models/enem_model_card.json`](models/enem_model_card.json).

---

## 🏗️ Arquitetura Desacoplada por Planos e Estrutura do Repositório

1. **Etapa 1 & Plano Offline (`notebooks/01` a `06`, `DVC + S3`, `PostgreSQL + MLflow`):** Investigação estrutural, EDA (`2023`), seleção parcimoniosa, mapeamento semântico SBERT, consolidação histórica em *chunks* (versionada via **DVC + S3**) e treinamento escalável com rastreamento remoto no **MLflow Server 3.17.2 (`PostgreSQL 16 + S3`)**.
2. **Etapa 2 & Plano Online/Observabilidade (`src/api/`, `monitoring/`, `infra/`, `.github/workflows/deploy.yml`):** API REST FastAPI com `/metrics`, dashboard **Prometheus + Grafana**, container multi-stage com `uv`, infraestrutura declarativa **Terraform** (`S3`, `ECR`, `IAM OIDC`, `AWS App Runner`) e esteira CI/CD no GitHub Actions (`quality-gate-ci` com `SHA-256 + ruff + mypy + 26 pytest` $\rightarrow$ `docker-smoke-test` $\rightarrow$ `deploy-aws` condicional via OIDC).

```text
enem/
├── .dvc/                          # Configuração do remoto DVC apontando para s3://.../dvc-store
├── .github/workflows/deploy.yml   # CI/CD: Quality Gate (SHA-256 + ruff + mypy + 26 pytest), Smoke Test e deploy AWS
├── data/processed/                # Contratos JSON, ponteiros .dvc e bases Parquet (armazenadas no S3 via DVC)
├── docs/                          # Guias passo a passo, estudos (Fases 1–3), diagramas e roteiros de slides
├── infra/                         # Terraform (IaC FinOps em 2 estágios: S3, ECR, IAM OIDC e AWS App Runner)
├── media/                         # Diagramas arquiteturais, infográficos MLOps e figuras (nb06_figuras/)
├── models/                        # Artefato campeão (enem.pkl, enem_xgboost.ubj) e Model Card JSON
├── monitoring/                    # Configurações do Prometheus (:9090) e dashboards provisionados do Grafana (:3000)
├── notebooks/                     # Esteira analítica completa (01 a 06)
├── scripts/download_microdados.sh # Download dos microdados públicos do INEP
├── src/api/                       # Microserviço FastAPI (main.py, model_loader.py, schemas.py, metrics.py)
├── tests/                         # Suíte de contrato HTTP, /metrics e paridade XGBoost (26 testes)
├── Dockerfile & Dockerfile.mlflow # Imagens Docker da API (515 MB) e do MLflow Tracking Server
├── docker-compose.yml             # API (:8000), profile "monitoring" (Prometheus/Grafana) e profile "mlops" (PG+MLflow)
├── pyproject.toml                 # Configuração unificada de Ruff e Mypy para Quality Gate
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
6. `notebooks/06_treinamento_modelo.ipynb` — Treinamento escalável, MLflow remoto (`PostgreSQL + S3`), validação OOT `2023`, TreeSHAP e exportação de `models/enem.pkl`.

---

## ☁️ Executando a Etapa 2 (Testes, API FastAPI, Docker, Observabilidade e MLflow)

### 1. Executar o Quality Gate Local (`26` testes + `ruff` + `mypy`)
```bash
pytest tests/ -v
ruff check src tests
mypy src/api tests
```

### 2. Subir a API Localmente (sem Docker)
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```
Acesse a documentação interativa Swagger em `http://localhost:8000/docs` e as métricas Prometheus em `http://localhost:8000/metrics`.

### 3. Subir Stacks Containerizadas com Docker Compose
```bash
# Apenas a API FastAPI (:8000)
docker compose up -d

# API + Observabilidade (Prometheus :9090 + Grafana :3000)
docker compose --profile monitoring up -d

# Tracking MLflow Remoto (PostgreSQL :5432 + MLflow Server :5000 -> Artifact Store S3)
docker compose --profile mlops up -d
```
Para encerrar os serviços:
```bash
docker compose --profile monitoring --profile mlops down
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
* [`docs/etapa-02-passo-a-passo.md`](docs/etapa-02-passo-a-passo.md) — Roteiro mestre de evolução MLOps e fechamento acadêmico do TCC.
* [`docs/estudos-futuros.md`](docs/estudos-futuros.md) — Análise arquitetural comparada (`Opção A + Cenário 1`) e alternativas tecnológicas por camada.
* [`docs/passo-a-passo-07-api-docker.md`](docs/passo-a-passo-07-api-docker.md) — Auditoria técnica da API FastAPI, testes, imagem Docker e pipeline CI/CD.
* [`docs/guia-estudo-observabilidade.md`](docs/guia-estudo-observabilidade.md) — Guia da Fase 1: `/metrics`, Prometheus e dashboard Grafana.
* [`docs/guia-estudo-terraform-dvc-s3.md`](docs/guia-estudo-terraform-dvc-s3.md) — Guia da Fase 2: IaC AWS (Terraform) e versionamento de datasets (DVC + S3).
* [`docs/guia-estudo-mlflow-postgresql-s3.md`](docs/guia-estudo-mlflow-postgresql-s3.md) — Guia da Fase 3: MLflow Tracking remoto (`PostgreSQL 16 + S3`) e reexecução do NB06.
* [`docs/onde-tudo-comeca.md`](docs/onde-tudo-comeca.md) — Histórico didático da fase inicial de ingestão/pipeline (arquivada na tag `archive/pre-faxina-2026-11`).
