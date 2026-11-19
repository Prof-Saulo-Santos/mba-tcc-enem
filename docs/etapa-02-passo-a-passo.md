# 🧭 Guia de Continuidade — Evolução Etapa 2 (MLOps de Produção) e Fechamento do TCC

**Projeto:** TCC MBA — Predição de Desempenho no ENEM (`TARGET_M4`) e Arquitetura MLOps  
**Autor:** Saulo Santos  
**Ponto de Partida do Plano:** `77c01fc` (`main`) + alterações validadas da **Fase 1** (`Observabilidade`)  
**Última Atualização:** `19/11/2026`  
**Objetivo deste Documento:** Servir como **roteiro mestre (*handoff*)** registrando o que já foi concluído e validado e conduzindo, passo a passo junto com o Saulo, as próximas etapas até o fechamento final do TCC.

---

## 0. Regras Obrigatórias para o Agente de IA no Novo Chat

1. **Papel:** Atuar como **Professor Orientador de TCC de MBA**, especialista em Engenharia de Dados, Ciência de Dados / Machine Learning e MLOps.
2. **Leitura inicial obrigatória:** Antes de propor qualquer alteração, leia:
   * [`AGENT.md`](../AGENT.md)
   * [`visao_geral_projeto.md`](../visao_geral_projeto.md)
   * [`docs/estudos-futuros.md`](estudos-futuros.md)
   * Este guia [`docs/etapa-02-passo-a-passo.md`](etapa-02-passo-a-passo.md)
   * E inspecione os arquivos reais que serão modificados (`src/api/`, `tests/`, `.github/workflows/deploy.yml`, `docker-compose.yml`, `models/enem_model_card.json`).
3. **Colaboração passo a passo (proibida ação autônoma):**
   * **Nunca** edite arquivos, crie infraestrutura na AWS, instale pacotes ou reexecute notebooks sem antes explicar o porquê, apresentar opções/alternativas com prós e contras quando aplicável e **aguardar o aval explícito do Saulo**.
   * Ao concluir cada marco aprovado, informe que é hora de commitar e forneça os comandos `git add` e `git commit` prontos.
4. **Fidelidade absoluta aos fatos e idioma:** Responda sempre em **Português do Brasil**, citando exclusivamente arquivos, métricas e resultados observados diretamente no repositório.

---

## 1. Contexto Herdado (O Que Já Está Pronto no Commit `5841d7d`)

* **Etapa 1 (100% implementada e auditada):**
  * Notebooks [`01_investigacao_estrutural.ipynb`](../notebooks/01_investigacao_estrutural.ipynb) a [`06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb).
  * Alvo oficial `TARGET_M4` ($\alpha = 0{,}865$), 6 features do Esquadrão de Elite (`RENDA_PER_CAPITA`, `Q024`, `TP_ANO_CONCLUIU`, `TP_LINGUA`, `TP_SEXO`, `Q002`), consolidação de `37.593.629` elegíveis (`2014–2023`, `153,17 MB` Parquet), encerramento da série em `2023` pela barreira LGPD (`2024–2025`), modelo campeão `XGBRegressor` (Holdout `7,52M`: $R^2 = 0{,}33780$, $\text{RMSE} = 57{,}7439\text{ pts}$; OOT `2023`: $R^2 = 0{,}31842$; TreeSHAP liderado por `RENDA_PER_CAPITA` com `30,10%`).
  * Artefatos atuais em [`models/`](../models/): `enem.pkl` (`1,727 MB`, SHA-256 `114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f`), `enem_xgboost.ubj`, `enem_model_card.json` e `auditoria_holdout_por_ano_2014_2023.csv`.
  * *Ponto a evoluir:* atualmente o tracking do MLflow está em `sqlite:///mlflow.db` + `./mlruns`, os arquivos `.parquet` em `data/processed/` não usam DVC/S3, não há Terraform nem observabilidade Prometheus/Grafana.
* **Etapa 2 base (100% implementada e testada):**
  * Microserviço FastAPI em [`src/api/`](../src/api/) (`main.py`, `model_loader.py`, `schemas.py` com `extra="forbid"`).
  * `25` testes automatizados em [`tests/test_api_contract.py`](../tests/test_api_contract.py) e [`tests/test_model_inference.py`](../tests/test_model_inference.py).
  * [`Dockerfile`](../Dockerfile) *multi-stage* (`515 MB` Content Size, `appuser` não-root), [`docker-compose.yml`](../docker-compose.yml) e CI/CD em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).
* **Documentação base alinhada:** [`README.md`](../README.md), [`visao_geral_projeto.md`](../visao_geral_projeto.md), [`AGENT.md`](../AGENT.md) e [`docs/estudos-futuros.md`](estudos-futuros.md).

---

## 2. Decisão Arquitetural Aprovada a Implementar (`Opção A + Cenário 1`)

* **Classificação técnica para a banca:** **Arquitetura Desacoplada por Planos (*Decoupled Training & Serving Planes* / *Local-to-Cloud MLOps*)** — **não** classificar como *Hybrid Cloud* (segundo o NIST, workstation local com Docker/WSL2 não constitui nuvem privada corporativa).
* **Os 3 Planos:**
  1. **Plano Offline / Governança (Workstation Containerizada + Storage S3):** `PostgreSQL + MLflow Tracking Server + DVC` sob demanda em Docker, eliminando o `SQLite` e persistindo dados/artefatos no **Amazon S3**.
  2. **Plano Online / *Serving* (AWS via Terraform):** `Terraform` (`infra/`) provisiona **Amazon S3**, **Amazon ECR**, **IAM/OIDC** e **AWS App Runner**, servindo a API FastAPI de forma independente da máquina local.
  3. **Plano de Observabilidade (Cenário 1 — `Prometheus + Grafana`):** a API expõe `/metrics` (localmente e no App Runner) e containers `prometheus + grafana` consomem as métricas para validação e demonstração ao vivo (com registro explícito de que em operação 24/7 migraria para **AMP + AMG**).

---

## 3. Parte I — Roteiro Técnico de Execução (4 Fases)

```text
[✅ Fase 1: Prometheus + Grafana] ──> [⏸️ Estudo & Slides Fase 1] ──> [⏳ Fase 2: Terraform + S3 + DVC] ──> [⏳ Fase 3: MLflow PostgreSQL+S3 & NB06] ──> [⏳ Fase 4: CI Hardening + Docs]
```

### Fase 1 — Observabilidade na API (`Prometheus + Grafana`, Cenário 1) — ✅ CONCLUÍDA E VALIDADA (`19/11/2026`)
* **O que foi entregue e testado:**
  * [`src/api/metrics.py`](../src/api/metrics.py) + [`src/api/main.py`](../src/api/main.py): endpoint `GET /metrics` com `prometheus-client==0.26.0`, middleware HTTP sem explosão de cardinalidade (`route.path`, ignorando `/metrics`), `validation_exception_handler` separando rejeições `HTTP 422` (`extra_forbidden` vs. `domain_or_schema`) e métricas de ML (*Prediction Drift* de `TARGET_M4` e *Data Drift* de `RENDA_PER_CAPITA` + 5 categóricas).
  * [`requirements-api.txt`](../requirements-api.txt) e [`requirements.txt`](../requirements.txt): `prometheus-client==0.26.0` fixado.
  * [`tests/test_api_contract.py`](../tests/test_api_contract.py): adicionado `test_metrics_endpoint_and_observability_counters` (**`26/26 PASSED`** no `pytest` e **`ruff check`** limpo).
  * [`docker-compose.yml`](../docker-compose.yml) + `monitoring/`: serviços `prometheus` (`:9090`) e `grafana` (`:3000`) sob `profiles: ["monitoring"]`, [`prometheus.yml`](../monitoring/prometheus/prometheus.yml) (`scrape_interval: 5s`), provisioning automático de datasource e dashboard [`enem_api_observability.json`](../monitoring/grafana/provisioning/dashboards/enem_api_observability.json) (10 painéis).
  * [`media/observabilidade_docker_prometheus_grafana.png`](../media/observabilidade_docker_prometheus_grafana.png): infográfico `1920×1080` gerado e validado.
  * [`docs/guia-estudo-observabilidade.md`](guia-estudo-observabilidade.md): guia didático detalhado da Fase 1 para estudo, montagem de slides e preparação para sabatina.
* **Evidência em runtime (Docker Desktop/WSL em `19/11/2026`):** `docker compose --profile monitoring up -d --build` subiu os 3 containers; Prometheus validou `enem-api-local` (`http://enem-api:8000/metrics`) com estado **`1 / 1 up` (`UP`, `4ms`)** e o Data Source `Prometheus` foi confirmado no Grafana.

### ⏸️ Pausa Planejada Antes da Fase 2 — Estudo e Slides da Fase 1 (Próxima Ação Imediata)
* **Objetivo:** Antes de avançar para AWS/Terraform/DVC, o Saulo deseja **dominar intelectualmente** tudo o que foi implementado na Fase 1 (usando [`docs/guia-estudo-observabilidade.md`](guia-estudo-observabilidade.md)) e **produzir os slides explicativos dessa camada** (atualizando/complementando [`docs/slides-07.md`](slides-07.md) ou o roteiro da apresentação).
* **Ação pendente no Grafana:** rodar a pequena sequência de chamadas `POST /predict` (documentada na Seção 4 de `docs/guia-estudo-observabilidade.md`) para visualizar as curvas de `rate()` / *Drift* preenchidas no dashboard **`ENEM TARGET_M4 — Observabilidade & Drift (API FastAPI)`**.

### Fase 2 — Infraestrutura como Código (`Terraform`) + Versionamento de Dados (`DVC + S3`) — ⏳ PENDENTE
* **Objetivo:** Eliminar *ClickOps* na criação de recursos AWS e versionar os arquivos `.parquet` pesados fora do Git usando Amazon S3.
* **Impacto nos notebooks:** **Nenhum código Python alterado** (`02_eda` e `05_consolidacao` apenas têm suas saídas `.parquet` rastreadas via CLI do DVC).
* **Arquivos alvo:**
  * Nova pasta `infra/` (`providers.tf`, `variables.tf`, `main.tf`, `outputs.tf`, `terraform.tfvars.example`)
  * `.gitignore` (ignorar `.terraform/`, `*.tfstate*`, `.env`, caches locais do DVC)
  * `.dvc/` e arquivos `.dvc` para os Parquets em `data/processed/`
  * [`requirements.txt`](../requirements.txt) (inclusão de `dvc[s3]` — **não** colocar em `requirements-api.txt`)
  * [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) (se houver ajuste de variáveis/OIDC)
* **Passo a passo com o Saulo:**
  1. **Checklist prévio antes de qualquer comando AWS:**
     * Verificar credenciais CLI locais (`aws sts get-caller-identity`), região (`us-east-1`), nome único global para o bucket S3 e se o GitHub Actions usará **OIDC (`AWS_ROLE_TO_ASSUME`)** (recomendado) ou Access Keys.
     * Decidir com o Saulo se o `tfstate` do Terraform ficará local (fora do Git via `.gitignore`) ou em bucket S3 de estado.
  2. **Desenhar e aprovar os recursos do Terraform (`infra/`):**
     * **Amazon S3:** bucket privado com versionamento habilitado e *encryption at rest* (prefixos lógicos `dvc-store/` e `mlflow-artifacts/`).
     * **Amazon ECR:** repositório `enem-target-m4-api` com *scan on push* e *lifecycle policy* FinOps (expirar imagens antigas).
     * **IAM / OIDC:** role de acesso do AWS App Runner ao ECR e (se escolhido) provedor/role OIDC do GitHub Actions.
     * **AWS App Runner:** serviço apontando para a imagem do ECR, porta `8000`, `/health` check, variáveis `MODEL_PATH` / `MODEL_CARD_PATH` e limites mínimos de instância/concorrência (FinOps).
     * **`outputs.tf`:** URL do serviço App Runner, `service_arn` (`AWS_APPRUNNER_SERVICE_ARN`), URL do ECR e nome do bucket S3.
  3. **Executar `terraform init`, `terraform plan` e (após revisão explícita do Saulo) `terraform apply`**.
  4. **Configurar DVC (`dvc init` + `dvc remote add -d s3remote s3://<bucket>/dvc-store`):**
     * Rastrear `data/processed/enem_2023_eda_purificado.parquet` e `data/processed/enem_2014_2023_consolidado.parquet` e enviar via `dvc push`.
     * **⚠️ Atenção crítica de CI/CD:** O job `quality-gate-ci` e o `Dockerfile` em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) dependem de [`models/enem.pkl`](../models/enem.pkl) (`1,727 MB`) estar disponível imediatamente após `actions/checkout@v4` sem exigir credenciais AWS em Pull Requests. Portanto, **mantenha `models/enem.pkl` versionado no Git** e use o DVC para os datasets `.parquet` (ou só adicione `dvc pull` se optar explicitamente por alterar o CI).
  5. **Checkpoint Git:** propor commit de `infra/`, `.dvc/` e arquivos `.dvc`.

### Fase 3 — MLflow Tracking Remoto (`PostgreSQL + S3`) e Reexecução do Notebook 06
* **Objetivo:** Eliminar `sqlite:///mlflow.db` e `./mlruns`, passando a registrar parâmetros, métricas, gráficos, Model Card e modelo registrado em **PostgreSQL + Amazon S3**.
* **Impacto nos notebooks:**
  * **Notebooks `01` a `05`: zero alterações de código.**
  * **[`notebooks/06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb): único notebook alterado.**
* **Arquivos alvo:**
  * `docker-compose.yml` (ou `docker-compose.mlops.yml`) com serviços `postgres` e `mlflow-server` (conectado ao S3 via credenciais AWS em `.env` não versionado)
  * [`requirements.txt`](../requirements.txt) (`psycopg2-binary`, `boto3`)
  * [`notebooks/06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb) (`Bloco 1.5` na Célula 2, diagrama Mermaid na Célula 3 e notas textuais nas Células `0`, `1`, `18`, `19`)
  * Artefatos atualizados após reexecução: [`models/enem.pkl`](../models/enem.pkl), [`models/enem_xgboost.ubj`](../models/enem_xgboost.ubj), [`models/enem_model_card.json`](../models/enem_model_card.json), [`models/auditoria_holdout_por_ano_2014_2023.csv`](../models/auditoria_holdout_por_ano_2014_2023.csv)
* **Passo a passo com o Saulo:**
  1. Subir `postgres + mlflow-server` apontando `--backend-store-uri postgresql+psycopg2://...` e `--default-artifact-root s3://<bucket>/mlflow-artifacts`.
  2. Alterar `Bloco 1.5` de [`06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb) para ler `MLFLOW_TRACKING_URI` via `os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")` (removendo `sqlite:///mlflow.db` e `./mlruns`).
  3. **Reexecutar o Notebook 06 (com autorização prévia do Saulo, avisando que a execução completa leva ~35–45 minutos)**.
  4. **⚠️ Sincronização obrigatória pós-reexecução:** Conferir se o `sha256` de `models/enem.pkl` ou o `mlflow_run_id_campeao` mudaram em `models/enem_model_card.json`. Caso tenham mudado, atualizar de forma consistente:
     * `EXPECTED_MODEL_SHA256` em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml);
     * asserções de `sha256` / `run_id` / valor esperado em [`tests/test_api_contract.py`](../tests/test_api_contract.py) e [`tests/test_model_inference.py`](../tests/test_model_inference.py);
     * referências nos guias (`AGENT.md`, `README.md`, `docs/passo-a-passo-06.md`, `docs/passo-a-passo-07-api-docker.md`).
  5. Rodar `pytest tests/ -v` e testar o container Docker novamente. Após confirmar tudo no Postgres+S3, decidir com o Saulo se arquiva/remove `mlflow.db` e `mlruns/` locais.
  6. **Checkpoint Git:** propor commit da stack MLOps + NB06 atualizado + Model Card/artefatos.

### Fase 4 — Qualidade Estática no CI e Alinhamento Documental
* **Objetivo:** Reforçar governança de código no CI/CD e atualizar a documentação técnica antes da redação final.
* **Passos:**
  1. Avaliar com o Saulo a adição de `ruff` e `mypy` no job `quality-gate-ci` em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) (e corrigir eventuais apontamentos em `src/api/` e `tests/`).
  2. Atualizar [`README.md`](../README.md), [`AGENT.md`](../AGENT.md), [`visao_geral_projeto.md`](../visao_geral_projeto.md), [`docs/passo-a-passo-07-api-docker.md`](passo-a-passo-07-api-docker.md) e [`docs/diagrama_deploy_aws.md`](diagrama_deploy_aws.md) (que ainda cita *"esperando pelo momento que o INEP liberará os dados no futuro"*) para refletir a arquitetura final com `DVC + S3`, `MLflow (PostgreSQL + S3)`, `Terraform` e `Prometheus + Grafana`.
  3. **Checkpoint Git.**

---

## 4. Parte II — Fechamento Acadêmico do TCC (Após a Parte I)

### Passo 5 — Atualizar Integralmente a Dissertação ([`tcc_mba_saulo_santos.md`](../tcc_mba_saulo_santos.md) e `.docx`)
* **Situação atual:** O rascunho de `09/09/2026` (`409` linhas) ainda reflete a fase inicial (`2017–2025`, Airflow, `reader.py`/`harmonizer.py`, `JOIN` 2024/2025, Streamlit/Evidently) e salta da seção `4.6` direto para `### 5.2 Próximas Etapas`.
* **O que revisar e incorporar em conjunto com o Saulo:**
  1. Reescrever Resumo, Introdução, Problema e Objetivos alinhados ao projeto real: determinismo socioeconômico (Pierre Bourdieu) + esteira longitudinal `2014–2023` + MLOps em nuvem.
  2. Metodologia e Resultados da **Etapa 1**: EDA (`212.386`, *Cohen's d* em Matemática: Escola `1,079`, Raça `0,625`, Sexo `0,377`), Notebook 03 (`6` alvos TRI, `19 -> 6` features, `TARGET_M4` com $\alpha = 0{,}865$), SBERT (NB04), consolidação de `37.593.629` elegíveis em `15 bytes/linha` (NB05), justificativa formal da barreira LGPD em `2024–2025`, treinamento escalável `XGBRegressor` + OOT `2023` + TreeSHAP (NB06) e MLflow remoto (`PostgreSQL + S3`) + `DVC + S3`.
  3. Metodologia e Resultados da **Etapa 2**: FastAPI + Pydantic v2 (`extra="forbid"`), testes automatizados `pytest`, observabilidade (`Prometheus + Grafana`), containerização Docker multi-stage, GitHub Actions CI/CD e IaC com **Terraform** na AWS (S3, ECR, App Runner), incluindo discussão de **Arquitetura Desacoplada por Planos** e análise comparativa de tecnologias ([`docs/estudos-futuros.md`](estudos-futuros.md)).
  4. Estruturar corretamente **Conclusões / Considerações Finais** e **Trabalhos Futuros** (`Polars`/`DuckDB`, `LightGBM`/`CatBoost`, `Evidently AI`, `AMP`/`AMG`) e converter/sincronizar para `.docx` conforme norma da instituição.

### Passo 6 — Fechar e Consolidar os Slides Finais de Defesa (`15 a 20 minutos`)
* **Pendências já mapeadas:**
  1. Criar/cobrir os roteiros dos **Capítulos `01` e `02`** (substituindo o arquivo legado [`docs/resumo-apresentacao-tcc-19-09-26.md`](resumo-apresentacao-tcc-19-09-26.md)).
  2. Limpar divergências legadas em [`docs/criacao-slides.md`](criacao-slides.md) (menções à extinta Etapa 3 / `slides-08`, `29/29 PASSED`, valores divergentes de *Cohen's d* e SHAP) e alinhar [`docs/slides-03.md`](slides-03.md) aos números atuais do Notebook 03 (`6` alvos TRI, `19 -> 6` features, $R^2 = 0{,}3743 \rightarrow 0{,}3397$).
  3. Incorporar os novos slides de **Arquitetura Desacoplada (`DVC + S3`, `MLflow PostgreSQL + S3`, `Terraform`, `Prometheus + Grafana`)** vindos da Parte I.
  4. Consolidar tudo em um deck executivo enxuto (~16 a 18 slides principais para `15–20 min` + apêndice de backup para perguntas da banca).

### Passo 7 — Treino de Sabatina e Deploy Pontual na AWS para a Banca
* **Treino de Sabatina:** Simular arguição rigorosa cobrindo Bourdieu, TRI vs. TCT, interpretação de $R^2 \approx 0{,}34$, desvio de 2018 na TRI, barreira LGPD 2024–2025, escolha de *Single-Node Chunked Streaming* vs. Spark, *Decoupled Training & Serving Planes* (vs. *Hybrid Cloud*), proteção contra *Leakage* (`HTTP 422`) e monitoramento de drift/latência via Prometheus/Grafana.
* **Deploy FinOps ao vivo (se o Saulo optar):**
  1. Rodar `terraform apply` em `infra/` e confirmar secrets/vars no GitHub;
  2. Executar workflow `.github/workflows/deploy.yml` para publicar na AWS App Runner;
  3. Testar URL pública + `/metrics` coletado pelo Grafana + UI do MLflow;
  4. **Executar `terraform destroy` imediatamente após a defesa** para manter custo zero na AWS.

---

## 5. Prompt Sugerido para Iniciar o Próximo Chat

Ao abrir um novo chat, você pode enviar:

> *"Leia `AGENT.md`, `visao_geral_projeto.md`, `docs/estudos-futuros.md`, `docs/etapa-02-passo-a-passo.md` e `docs/guia-estudo-observabilidade.md`. Confirme o estado atual (Fase 1 concluída) e siga as regras de colaboração passo a passo: quero [estudar os detalhes da Fase 1 / montar os slides da Fase 1 / iniciar a Fase 2 (Terraform + S3 + DVC)]."*
