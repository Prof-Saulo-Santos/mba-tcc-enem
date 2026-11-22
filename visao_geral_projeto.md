# 🎓 Visão Geral do Projeto: Previsão de Notas do ENEM e Arquitetura de Dados

Este documento apresenta à banca avaliadora a arquitetura ponta a ponta do projeto, esclarecendo o papel da fase de pesquisa e modelagem histórica (Notebooks `01` a `06` — Etapa 1), o recorte censitário até `2023` (devido à ruptura estrutural da LGPD a partir de `2024`) e a engenharia de produtização em nuvem (Etapa 2).

---

## 🗺️ Mapa Completo de Documentação e Slides por Etapa do TCC

A tabela abaixo consolida a correspondência exata entre as **2 Grandes Etapas Arquiteturais** do projeto, os **Capítulos Sequenciais (`01` a `07`)**, os guias técnicos de execução (`passo-a-passo`) e os roteiros de slides para a defesa perante a banca (`slides`):

| Grande Etapa do Projeto | Capítulo / Escopo Técnico | Guia Técnico (`passo-a-passo`) | Roteiro de Slides para a Banca (`slides`) | Status |
| :--- | :--- | :--- | :--- | :---: |
| **ETAPA 1**<br>*(Laboratório, Seleção, NLP, Big Data 2014–2023 e Treino MLflow)* | **Cap. 01 e 02:** Ingestão e Análise Exploratória (EDA 2023) | Documentado no [`AGENT.md`](AGENT.md) (Seção 3.1/3.2) | [`docs/resumo-apresentacao-tcc-19-09-26.md`](docs/resumo-apresentacao-tcc-19-09-26.md) *(legado; consolidar Cap. 01–02)* | ⚠️ Slides pendentes |
| **ETAPA 1** | **Cap. 03:** Engenharia de Features e Homologação do `TARGET_M4` | [`docs/conclusoes_do_notebook_03.md`](docs/conclusoes_do_notebook_03.md) | **[`docs/slides-03.md`](docs/slides-03.md)** | ✅ Concluído |
| **ETAPA 1** | **Cap. 04:** Varredura Semântica Histórica com NLP/SBERT | Documentado no [`notebooks/04_varredura_semantica.ipynb`](notebooks/04_varredura_semantica.ipynb) | **[`docs/slides-04.md`](docs/slides-04.md)** | ✅ Concluído |
| **ETAPA 1** | **Cap. 05:** Consolidação 2014–2023 (37,59M) e Downcasting | **[`docs/passo-a-passo-05.md`](docs/passo-a-passo-05.md)** | **[`docs/slides-05.md`](docs/slides-05.md)** | ✅ Concluído |
| **ETAPA 1** | **Cap. 06:** Treinamento Escalável XGBoost + MLflow + SHAP (`enem.pkl`) | **[`docs/passo-a-passo-06.md`](docs/passo-a-passo-06.md)** | **[`docs/slides-06.md`](docs/slides-06.md)** | ✅ Concluído |
| **ETAPA 2**<br>*(API FastAPI, Pytest, Docker e CI/CD AWS)* | **Cap. 07:** Produtização da API REST, Testes de Contrato, Docker e GitHub Actions | **[`docs/passo-a-passo-07-api-docker.md`](docs/passo-a-passo-07-api-docker.md)** | **[`docs/slides-07.md`](docs/slides-07.md)** *(atualizar na consolidação final)* | ✅ Concluído |
| **ETAPA 2 — EVOLUÇÕES MLOPS**<br>*(Fases 1 a 4 concluídas)* | **Fases 1–4:** Observabilidade (`Prometheus + Grafana`), `Terraform + DVC + S3`, `MLflow (PostgreSQL + S3)` e `Ruff + Mypy` no CI | **[`docs/etapa-02-passo-a-passo.md`](docs/etapa-02-passo-a-passo.md)** *(roteiro mestre)* | [`docs/guia-estudo-observabilidade.md`](docs/guia-estudo-observabilidade.md)<br>[`docs/guia-estudo-terraform-dvc-s3.md`](docs/guia-estudo-terraform-dvc-s3.md)<br>[`docs/guia-estudo-mlflow-postgresql-s3.md`](docs/guia-estudo-mlflow-postgresql-s3.md) | ✅ Concluído |

---

## 🔬 Etapa 1: Laboratório Científico, Big Data e Modelagem (Notebooks `01` a `06`)

1. **`01_investigacao_estrutural.ipynb`:** Reconhecimento estrutural dos CSVs brutos do INEP, checagem de colunas, tipos e layout.
2. **`02_eda.ipynb` (Análise Exploratória):** Limpeza metodológica de 2023 (`enem_2023_eda_purificado.parquet`), análise bivariada demográfica e cálculo de tamanho de efeito (*Cohen's d*).
3. **`03_engenharia_features.ipynb` (Engenharia e Seleção):** Definição do alvo **`TARGET_M4`** (média das 4 provas objetivas da TRI, Alfa de Cronbach = `0,865`) e seleção parcimoniosa das **6 features de elite** (`contrato_features_modelagem.json`).
4. **`04_varredura_semantica.ipynb` (Harmonização por NLP):** Uso de *Sentence Transformers (SBERT)* para mapear os dicionários históricos (`schema_mapping_historico.json`), homologando a janela **2014–2023** (*Década de Ouro*) e identificando a ruptura estrutural a partir de `2024`.
5. **`05_consolidacao_historica.ipynb` (Big Data 2014–2023):** Leitura em *chunks* de 500 mil linhas dos 10 CSVs brutos (`56,57M` inscritos varridos $\rightarrow$ **`37.593.629` elegíveis**), deflação em Salários Mínimos, harmonização ordinal e *downcasting* para `15 bytes/linha` (`enem_2014_2023_consolidado.parquet`, versionado no Amazon S3 via **DVC**).
6. **`06_treinamento_modelo.ipynb` (Treinamento, MLflow Remoto, SHAP e OOT):** Competição `Dummy` vs. `Ridge` vs. `RandomForest` vs. `XGBoost`, eleição do **`XGBRegressor`** campeão no Holdout de `7,52M` ($R^2 = 0{,}33780$, $\text{RMSE} = 57{,}7439\text{ pts}$), **Validação *Out-of-Time* Interna (`2014–2022 -> 2023`, $R^2 = 0{,}31842$)**, explicabilidade via **TreeSHAP**, registro no **MLflow (`PostgreSQL 16 + S3`, `run_id = 6490c396b0e04147b156bedb0c8af9f7`)** e exportação de [`models/enem.pkl`](models/enem.pkl) + [`models/enem_model_card.json`](models/enem_model_card.json).

---

## 🔒 Por Que o Recorte Censitário Encerra em 2023 (Barreira LGPD 2024–2025)

A partir da edição de **2024**, por adequação à **Lei Geral de Proteção de Dados (LGPD)**, o INEP deixou de publicar os microdados em tabela única por inscrito e separou participantes (`PARTICIPANTES`) e notas (`RESULTADOS`) sem chave de ligação (`NU_INSCRICAO` ausente para cruzamento e ordenação independente). Em **2025**, tampouco existe tabela pareável com notas.

Como ficou comprovada a impossibilidade técnica e intencional de unir as duas tabelas CSV de `2024` e `2025`, o processamento dessas edições foi **retirado do escopo do projeto**, preservando a integridade científica da base `2014–2023` e comprovando a generalização temporal do modelo através da **Validação *Out-of-Time* Interna sobre os `2.678.264` candidatos integrais de `2023`**.

---

## ☁️ Etapa 2: Produtização, Observabilidade, IaC e CI/CD na AWS

O objetivo final de MLOps é entregar o modelo como um serviço (*Model as a Service*) sob uma **Arquitetura Desacoplada por Planos (*Local-to-Cloud MLOps*)**:

1. **Microserviço REST & Observabilidade (`src/api/`, `monitoring/`):** A API **FastAPI** carrega [`models/enem.pkl`](models/enem.pkl) e [`models/enem_model_card.json`](models/enem_model_card.json), valida estritamente as 6 variáveis de entrada via **Pydantic v2** (`extra="forbid"`, bloqueando variáveis proibidas como `NU_ANO`) e expõe `/health`, `/info`, `/predict`, `/predict/batch` e `/metrics` (coletado pelo **Prometheus** e exibido em `10` painéis no **Grafana**).
2. **Quality Gate & Suíte de Testes (`tests/`, `pyproject.toml`):** **`26` testes automatizados** (`pytest`) somados a **`ruff`** e **`mypy`** validam linting, tipagem estática, integridade `SHA-256`, contratos HTTP, limites psicométricos, exposição `/metrics` e paridade exata de inferência com o estimador `XGBRegressor`.
3. **Containerização FinOps (`Dockerfile`, `Dockerfile.mlflow`, `docker-compose.yml`):** Build *multi-stage* com `uv`, `requirements-api.txt` enxuto (`515 MB` Content Size na API base), `libgomp1` e usuário `appuser` não-root, além de profiles dedicados para `monitoring` e `mlops` (`PostgreSQL 16 + MLflow Server 3.17.2 -> S3`).
4. **IaC (`infra/`), Dados (`DVC + S3`) e CI/CD (`.github/workflows/deploy.yml`):** **Terraform** provisiona `Amazon S3` (armazenamento unificado para `dvc-store/` e `mlflow-artifacts/`), `Amazon ECR`, `IAM OIDC` e `AWS App Runner` (em 2 estágios FinOps), integrados à esteira de 3 jobs (`quality-gate-ci` $\rightarrow$ `docker-smoke-test` $\rightarrow$ `deploy-aws`).

---

## 🗂️ Diagramas e Documentação Complementar

* **Diagramas Arquiteturais e Figuras (`media/`):** [`media/pipeline-1.jpg`](media/pipeline-1.jpg), [`media/pipeline-2.jpg`](media/pipeline-2.jpg), [`media/arquitetura_medalhao_parquet.png`](media/arquitetura_medalhao_parquet.png), [`media/fluxo_notebooks_parquet_json.png`](media/fluxo_notebooks_parquet_json.png), [`media/observabilidade_docker_prometheus_grafana.png`](media/observabilidade_docker_prometheus_grafana.png), [`media/infra_terraform_s3_dvc.png`](media/infra_terraform_s3_dvc.png), [`media/mlflow_postgresql_s3_fase3.png`](media/mlflow_postgresql_s3_fase3.png), [`media/qualidade_ci_documentacao_fase4.png`](media/qualidade_ci_documentacao_fase4.png), [`media/producao_ecr_apprunner.png`](media/producao_ecr_apprunner.png) e [`media/nb06_figuras/`](media/nb06_figuras/).
* **Guias, Estudos e Roteiros (`docs/`):** [`docs/etapa-02-passo-a-passo.md`](docs/etapa-02-passo-a-passo.md), [`docs/estudos-futuros.md`](docs/estudos-futuros.md), [`docs/como-testar.md`](docs/como-testar.md), [`docs/guia-estudo-observabilidade.md`](docs/guia-estudo-observabilidade.md), [`docs/guia-estudo-terraform-dvc-s3.md`](docs/guia-estudo-terraform-dvc-s3.md), [`docs/guia-estudo-mlflow-postgresql-s3.md`](docs/guia-estudo-mlflow-postgresql-s3.md), [`docs/fluxo_arquitetura_enem.md`](docs/fluxo_arquitetura_enem.md), [`docs/diagrama_deploy_aws.md`](docs/diagrama_deploy_aws.md), [`docs/diagrama_treinamento_mlflow.mmd`](docs/diagrama_treinamento_mlflow.mmd), [`docs/onde-tudo-comeca.md`](docs/onde-tudo-comeca.md) e [`docs/criacao-slides.md`](docs/criacao-slides.md) *(em revisão na Parte II para limpeza de referências legadas)*.
* **Guia Operacional e Contratos:** [`README.md`](README.md), [`AGENT.md`](AGENT.md) e [`models/enem_model_card.json`](models/enem_model_card.json).
