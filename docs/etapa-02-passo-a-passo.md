# 🧭 Guia de Continuidade — Evolução Etapa 2 (MLOps de Produção) e Fechamento do TCC

**Projeto:** TCC MBA — Predição de Desempenho no ENEM (`TARGET_M4`) e Arquitetura MLOps  
**Autor:** Saulo Santos  
**Ponto de Partida do Plano:** `main` atualizado + entregas validadas da **Fase 3** (`MLflow PostgreSQL + S3` & `NB06`)  
**Última Atualização:** `21/11/2026`  
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
[✅ Fase 1: Prometheus + Grafana] ──> [✅ Fase 2: Terraform + S3 + DVC] ──> [✅ Fase 3: MLflow PostgreSQL+S3 & NB06] ──> [⏳ Fase 4: CI Hardening + Docs]
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

### ⏸️ Estudo e Slides da Fase 1 — ✅ CONCLUÍDO PELO SAULO (`19/11/2026`)
* Slides da Fase 1 concluídos após validação prática do Docker/Prometheus/Grafana. *(Lembrete opcional: quando quiser visualizar as curvas de `rate()` preenchidas no Grafana ao vivo, use o script da Seção 4 de [`docs/guia-estudo-observabilidade.md`](guia-estudo-observabilidade.md).)*

### Fase 2 — Infraestrutura como Código (`Terraform`) + Versionamento de Dados (`DVC + S3`) — ✅ CONCLUÍDA E VALIDADA (`19–21/11/2026`)
* **O que foi entregue e validado:**
  * [`infra/`](../infra/): `versions.tf`, `variables.tf`, `main.tf`, `outputs.tf`, `terraform.tfvars.example` e `.terraform.lock.hcl` (`Terraform v1.17.2`, provider `hashicorp/aws v5.100.0`).
  * `terraform apply` (Estágio 1 com `create_apprunner = false`, `< $0,01/dia`): **`11` recursos criados na conta `703671922740` (`us-east-1`)** — Bucket S3 `tcc-enem-saulo-mlops-703671922740` (privado, versionado, `AES256`, `force_destroy=true`), ECR `enem-target-m4-api` (retenção `5` imagens, *scan on push*), OIDC Provider + Role `tcc-enem-saulo-mlops-github-actions` (restrita a `Prof-Saulo-Santos/mba-tcc-enem` em `main`) e Role `tcc-enem-saulo-mlops-apprunner-ecr`.
  * [`.gitignore`](../.gitignore) e [`requirements.txt`](../requirements.txt): `dvc[s3]==3.67.1` fixado; `data/raw/`, `*.parquet`, `infra/.terraform/`, `*.tfstate*` e `.env` ignorados; contratos JSON e ponteiros `.dvc` liberados; `models/enem.pkl` mantido no Git para não quebrar o CI de PRs.
  * [`.dvc/config`](../.dvc/config) + [`enem_2023_eda_purificado.parquet.dvc`](../data/processed/enem_2023_eda_purificado.parquet.dvc) (`26.8 MiB`) + [`enem_2014_2023_consolidado.parquet.dvc`](../data/processed/enem_2014_2023_consolidado.parquet.dvc) (`153.2 MiB`): **`2 files pushed`** e confirmados diretamente no bucket via `aws s3 ls` em `dvc-store/files/md5/...`.
  * [`media/infra_terraform_s3_dvc.png`](../media/infra_terraform_s3_dvc.png): infográfico `1920×1080` gerado e validado.
  * [`docs/guia-estudo-terraform-dvc-s3.md`](guia-estudo-terraform-dvc-s3.md): guia didático completo da Fase 2, custos FinOps, comandos de operação e roteiro de slides/sabatina.
* **Observação para a próxima etapa (Fase 3):** O bucket `s3://tcc-enem-saulo-mlops-703671922740/mlflow-artifacts` já está provisionado e pronto para receber o `--default-artifact-root` do MLflow Tracking Server na Fase 3. *(E quando for testar o Estágio 2 do Terraform, após publicar uma imagem no ECR, bastará rodar `terraform -chdir=infra apply -var="create_apprunner=true"` e configurar os secrets `AWS_ROLE_TO_ASSUME` e `AWS_APPRUNNER_SERVICE_ARN` no GitHub.)*

### Fase 3 — MLflow Tracking Remoto (`PostgreSQL + S3`) e Reexecução do Notebook 06 — ✅ CONCLUÍDA E VALIDADA (`21/11/2026`)
* **O que foi entregue e testado:**
  * [`Dockerfile.mlflow`](../Dockerfile.mlflow) + [`docker-compose.yml`](../docker-compose.yml) (`profiles: ["mlops"]`): `postgres:16-alpine` (`:5432`, volume `postgres_mlflow_data`, `healthcheck` com `start_period: 60s`) + `mlflow-server` (`mlflow==3.17.2`, `:5000`, `--default-artifact-root s3://tcc-enem-saulo-mlops-703671922740/mlflow-artifacts`, `~/.aws:ro`).
  * [`requirements.txt`](../requirements.txt): fixado `psycopg2-binary==2.9.13` e `boto3==1.44.9`.
  * [`notebooks/06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb): atualizado `Bloco 1.5`, diagrama Mermaid e textos para tracking remoto (`http://127.0.0.1:5000`) e reexecutado integralmente sem erros (Notebooks `01` a `05` intactos).
  * **Reprodutibilidade e Auditoria S3:** `models/enem.pkl` manteve **exatamente o mesmo `SHA-256`** (`114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f`) e métricas (`R² = 0,33780`, `RMSE = 57,7439`); novo run registrado no PostgreSQL **`6490c396b0e04147b156bedb0c8af9f7`** (`models:/m-ea7931423f5141379ff97886636ae0ea`); **`17` objetos (`~2,49 MiB`)** confirmados no S3 via `aws s3 ls`.
  * [`tests/test_api_contract.py`](../tests/test_api_contract.py): sincronizado com `mlflow_run_id_campeao = "6490c396b0e04147b156bedb0c8af9f7"`, alcançando **`26/26 PASSED`** no `pytest` e `ruff` limpo.
  * [`media/mlflow_postgresql_s3_fase3.png`](../media/mlflow_postgresql_s3_fase3.png), [`media/producao_ecr_apprunner.png`](../media/producao_ecr_apprunner.png) e [`docs/guia-estudo-mlflow-postgresql-s3.md`](guia-estudo-mlflow-postgresql-s3.md): infográficos `1920×1080` e guia de estudo/slides gerados.
* **Lembrete para Fase 4:** Atualizar referências antigas a `8b4ed2c387044363968b6088078bdf2d` e `sqlite:///mlflow.db` em [`AGENT.md`](../AGENT.md) e [`docs/passo-a-passo-07-api-docker.md`](passo-a-passo-07-api-docker.md).

### Fase 4 — Qualidade Estática no CI e Alinhamento Documental — ⏳ PRÓXIMA ETAPA
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

> *"Leia `AGENT.md`, `visao_geral_projeto.md`, `docs/estudos-futuros.md`, `docs/etapa-02-passo-a-passo.md` e `docs/guia-estudo-mlflow-postgresql-s3.md`. Confirme o estado atual (Fases 1, 2 e 3 concluídas) e siga as regras de colaboração passo a passo: quero [estudar os detalhes da Fase 3 / iniciar a Fase 4 (CI Hardening + alinhamento documental) / atualizar a dissertação]."*
