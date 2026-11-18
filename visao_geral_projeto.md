# 🎓 Visão Geral do Projeto: Previsão de Notas do ENEM e Arquitetura de Dados

Este documento apresenta à banca avaliadora a arquitetura ponta a ponta do projeto, esclarecendo o papel da fase de pesquisa e modelagem histórica (Notebooks `01` a `06` — Etapa 1), o recorte censitário até `2023` (devido à ruptura estrutural da LGPD a partir de `2024`) e a engenharia de produtização em nuvem (Etapa 2).

---

## 🗺️ Mapa Completo de Documentação e Slides por Etapa do TCC

A tabela abaixo consolida a correspondência exata entre as **2 Grandes Etapas Arquiteturais** do projeto, os **Capítulos Sequenciais (`01` a `07`)**, os guias técnicos de execução (`passo-a-passo`) e os roteiros de slides para a defesa perante a banca (`slides`):

| Grande Etapa do Projeto | Capítulo / Escopo Técnico | Guia Técnico (`passo-a-passo`) | Roteiro de Slides para a Banca (`slides`) | Status |
| :--- | :--- | :--- | :--- | :---: |
| **ETAPA 1**<br>*(Laboratório, Seleção, NLP, Big Data 2014–2023 e Treino MLflow)* | **Cap. 01 e 02:** Ingestão e Análise Exploratória (EDA 2023) | Documentado no [`AGENT.md`](AGENT.md) (Seção 3.1/3.2) | [`docs/resumo-apresentacao-tcc-19-09-26.md`](docs/resumo-apresentacao-tcc-19-09-26.md) | ✅ Concluído |
| **ETAPA 1** | **Cap. 03:** Engenharia de Features e Homologação do `TARGET_M4` | [`docs/conclusoes_do_notebook_03.md`](docs/conclusoes_do_notebook_03.md) | **[`docs/slides-03.md`](docs/slides-03.md)** | ✅ Concluído |
| **ETAPA 1** | **Cap. 04:** Varredura Semântica Histórica com NLP/SBERT | Documentado no `04_varredura_semantica.ipynb` | **[`docs/slides-04.md`](docs/slides-04.md)** | ✅ Concluído |
| **ETAPA 1** | **Cap. 05:** Consolidação 2014–2023 (37,59M) e Downcasting | **[`docs/passo-a-passo-05.md`](docs/passo-a-passo-05.md)** | **[`docs/slides-05.md`](docs/slides-05.md)** | ✅ Concluído |
| **ETAPA 1** | **Cap. 06:** Treinamento Escalável XGBoost + MLflow + SHAP (`enem.pkl`) | **[`docs/passo-a-passo-06.md`](docs/passo-a-passo-06.md)** | **[`docs/slides-06.md`](docs/slides-06.md)** | ✅ Concluído |
| **ETAPA 2**<br>*(API FastAPI, Pytest, Docker e CI/CD AWS)* | **Cap. 07:** Produtização da API REST, Testes de Contrato, Docker e GitHub Actions | **[`docs/passo-a-passo-07-api-docker.md`](docs/passo-a-passo-07-api-docker.md)** | **[`docs/slides-07.md`](docs/slides-07.md)** | ✅ Concluído |

---

## 🔬 Etapa 1: Laboratório Científico, Big Data e Modelagem (Notebooks `01` a `06`)

1. **`01_investigacao_estrutural.ipynb`:** Reconhecimento estrutural dos CSVs brutos do INEP, checagem de colunas, tipos e layout.
2. **`02_eda.ipynb` (Análise Exploratória):** Limpeza metodológica de 2023 (`enem_2023_eda_purificado.parquet`), análise bivariada demográfica e cálculo de tamanho de efeito (*Cohen's d*).
3. **`03_engenharia_features.ipynb` (Engenharia e Seleção):** Definição do alvo **`TARGET_M4`** (média das 4 provas objetivas da TRI, Alfa de Cronbach = `0,865`) e seleção parcimoniosa das **6 features de elite** (`contrato_features_modelagem.json`).
4. **`04_varredura_semantica.ipynb` (Harmonização por NLP):** Uso de *Sentence Transformers (SBERT)* para mapear os dicionários históricos (`schema_mapping_historico.json`), homologando a janela **2014–2023** (*Década de Ouro*) e identificando a ruptura estrutural a partir de `2024`.
5. **`05_consolidacao_historica.ipynb` (Big Data 2014–2023):** Leitura em *chunks* de 500 mil linhas dos 10 CSVs brutos (`56,57M` inscritos varridos $\rightarrow$ **`37.593.629` elegíveis**), deflação em Salários Mínimos, harmonização ordinal e *downcasting* para `15 bytes/linha` (`enem_2014_2023_consolidado.parquet`).
6. **`06_treinamento_modelo.ipynb` (Treinamento, MLflow, SHAP e OOT):** Competição `Dummy` vs. `Ridge` vs. `RandomForest` vs. `XGBoost`, eleição do **`XGBRegressor`** campeão no Holdout de `7,52M` ($R^2 = 0{,}33780$, $\text{RMSE} = 57{,}7439\text{ pts}$), **Validação *Out-of-Time* Interna (`2014–2022 -> 2023`, $R^2 = 0{,}31842$)**, explicabilidade via **TreeSHAP** e exportação de [`models/enem.pkl`](models/enem.pkl) + [`models/enem_model_card.json`](models/enem_model_card.json).

---

## 🔒 Por Que o Recorte Censitário Encerra em 2023 (Barreira LGPD 2024–2025)

A partir da edição de **2024**, por adequação à **Lei Geral de Proteção de Dados (LGPD)**, o INEP deixou de publicar os microdados em tabela única por inscrito e separou participantes (`PARTICIPANTES`) e notas (`RESULTADOS`) sem chave de ligação (`NU_INSCRICAO` ausente para cruzamento e ordenação independente). Em **2025**, tampouco existe tabela pareável com notas.

Como ficou comprovada a impossibilidade técnica e intencional de unir as duas tabelas CSV de `2024` e `2025`, o processamento dessas edições foi **retirado do escopo do projeto**, preservando a integridade científica da base `2014–2023` e comprovando a generalização temporal do modelo através da **Validação *Out-of-Time* Interna sobre os `2.678.264` candidatos integrais de `2023`**.

---

## ☁️ Etapa 2: Produtização, Testes de Contrato, Docker e CI/CD na AWS

O objetivo final de MLOps é entregar o modelo como um serviço (*Model as a Service*):

1. **Microserviço REST (`src/api/`):** A API **FastAPI** carrega [`models/enem.pkl`](models/enem.pkl) e [`models/enem_model_card.json`](models/enem_model_card.json), valida estritamente as 6 variáveis de entrada via **Pydantic v2** (`extra="forbid"`, bloqueando variáveis proibidas como `NU_ANO`) e expõe `/health`, `/info`, `/predict` e `/predict/batch`.
2. **Suíte de Testes (`tests/`):** Testes automatizados validam integridade `SHA-256`, contratos HTTP, limites psicométricos e paridade exata de inferência com o estimador `XGBRegressor`.
3. **Containerização FinOps (`Dockerfile`):** Build *multi-stage* com `uv`, `requirements-api.txt` enxuto (`515 MB` Content Size), biblioteca OpenMP (`libgomp1`) e usuário sem privilégios de `root` (`appuser`).
4. **CI/CD GitHub Actions (`.github/workflows/deploy.yml`):** Esteira automatizada em 3 jobs (`quality-gate-ci` $\rightarrow$ `docker-smoke-test` $\rightarrow$ `deploy-aws` para **Amazon ECR** e **AWS App Runner** com trava FinOps condicional).
