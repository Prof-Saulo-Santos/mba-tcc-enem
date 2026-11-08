# 📘 Guia Passo a Passo e Relatório de Homologação — Etapa 2 (API FastAPI, Pytest e Docker)

**Módulos de Produção:** [`src/api/`](src/api/), [`tests/`](tests/), [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml)  
**Projeto de TCC:** MBA em Ciência de Dados & MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  
**Data da Auditoria de Execução:** 08 de Novembro de 2026 (`20:54:58 UTC`)  

---

## 1. Visão Geral: Do Laboratório Científico ao Microserviço Containerizado (Etapa 2)

Após o treinamento e a validação *Out-of-Time* do modelo campeão **`XGBRegressor`** sobre os **37.593.629 candidatos** da Década de Ouro (`2014–2023`) na Etapa 1, a **Etapa 2** encapsula o artefato homologado [`models/enem.pkl`](models/enem.pkl) (`1,727 MB`, SHA-256 `114f51959492...`) e seu contrato canônico [`models/enem_model_card.json`](models/enem_model_card.json) em uma arquitetura de *Serving* pronta para nuvem AWS:

```text
ETAPA 2 — PRODUTIZAÇÃO, TESTES DE CONTRATO E CONTAINERIZAÇÃO HERMÉTICA
[models/enem.pkl + enem_model_card.json]
        │
        ├──> Marco 2.1: Microserviço REST FastAPI + Esquemas Pydantic v2 (src/api/)
        ├──> Marco 2.2: Suíte de Testes de Contrato e Paridade (25/25 PASSED em pytest)
        ├──> Marco 2.3: Imagem Docker Multi-Stage Enxuta (515 MB OCI / appuser não-root)
        └──> Marco 2.4: Esteira CI/CD GitHub Actions ──> Amazon ECR / AWS App Runner
```

---

## 2. Decisões Arquiteturais e Engenharia FinOps para a Banca do TCC

| Decisão de Engenharia | Implementação Técnica | Justificativa Acadêmica e de Produção (FinOps / Segurança) |
| :--- | :--- | :--- |
| **Desacoplamento de Dependências (`requirements-api.txt`)** | Manifesto exclusivo com os 8 pacotes de *serving* (`fastapi`, `uvicorn`, `pydantic`, `joblib`, `numpy`, `pandas`, `scikit-learn`, `xgboost`) nas versões exatas do treino. | Exclui pacotes pesados de laboratório (`torch`, `sentence-transformers`, `jupyter`, `shap`, `mlflow`), reduzindo o tamanho de transferência da imagem (**Content Size**) para **`515 MB`** (uso em disco de `1,47 GB`, contra `>5 GB` caso incluísse PyTorch/CUDA). |
| **Contexto de Build Mínimo (`.dockerignore`)** | Bloqueio estrito de `data/`, `notebooks/`, `mlruns/`, `media/`, `.venv/` e `.git/`. | Reduz o contexto enviado ao Docker Daemon de **>25 GB** de microdados brutos para **~2 MB**, acelerando o build em CI/CD (GitHub Actions). |
| **Build Multi-Stage com `uv` (`Dockerfile`)** | Estágio `builder` compila bytecode (`UV_COMPILE_BYTECODE=1`) em `/opt/venv`; estágio `runtime` copia apenas o ambiente pronto e os artefatos. | Elimina compiladores e caches da imagem final, acelerando o *cold start* no **AWS App Runner**. |
| **Suporte OpenMP Nativo (`libgomp1`)** | Instalação explícita de `libgomp1` no estágio `runtime` (`python:3.13-slim`). | Imagens Debian `-slim` omitem a biblioteca compartilhada `libgomp.so.1` exigida pelo motor C++ do XGBoost. Sua inclusão garante execução multithread sem falhas de carregamento dinâmico. |
| **Segurança Zero-Privilege (`appuser`)** | Criação do grupo e usuário `appuser` (`UID/GID 1000`) sem privilégios de `root`. | Mitiga superfície de ataque em contêineres expostos na nuvem pública (conformidade OWASP Docker Security). |
| **Blindagem Anti-Leakage (`extra="forbid"`)** | Configurada em `CandidatoInput` ([`src/api/schemas.py`](src/api/schemas.py)). | Rejeita imediatamente com **`HTTP 422`** qualquer tentativa de envio de variáveis proibidas (como `NU_ANO` ou notas parciais), protegendo o modelo em produção. |

---

## 3. Resumo da Suíte Automatizada de Testes (Marco 2.2 — `pytest`)

Antes da containerização, a aplicação foi submetida a **25 testes automatizados** ([`tests/test_api_contract.py`](tests/test_api_contract.py) e [`tests/test_model_inference.py`](tests/test_model_inference.py)), alcançando **100% de aprovação (`25 passed in 15.89s`)**:

* **Integridade Criptográfica:** Verificação exata do hash SHA-256 (`114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f`) entre o arquivo físico, o endpoint `/health` e o `enem_model_card.json`.
* **Fronteiras de Domínio (12 Testes Parametrizados):** Rejeição `HTTP 422` para valores abaixo do mínimo ou acima do máximo em todas as 6 variáveis do Esquadrão de Elite (`RENDA_PER_CAPITA` $\notin [0, 25]$, `Q024` $\notin \{0..3\}$, `TP_ANO_CONCLUIU` $\notin \{0..9\}$, `TP_LINGUA` $\notin \{0, 1\}$, `TP_SEXO` $\notin \{0, 1\}$, `Q002` $\notin \{0..7\}$).
* **Paridade Matemática Estrita:** Igualdade exata entre a resposta da API e o estimador puro carregado via `joblib.load`.
* **Direcionalidade Sociológica (Bourdieu):** Comprovação de diferencial superior a $+100\text{ pts}$ na escala TRI entre os extremos de vulnerabilidade e alto capital cultural/econômico.
* **SLA de Latência:** Lote vetorial de $1.000$ candidatos processado abaixo do teto de $500\text{ ms}$.

---

## 4. Registro Oficial de Auditoria: Execução Real do Container Docker (Marco 2.3)

Os comandos abaixo foram executados manualmente no host `saulo@LeCun:enem` em **08/11/2026**, comprovando o funcionamento ponta a ponta da imagem Docker **`enem-target-m4-api:v1`** (`ID: fae92b51099c`).

### 4.1 Inspeção da Imagem Construída e Subida do Serviço (`docker compose`)

```text
saulo@LeCun:enem$ docker images enem-target-m4-api:v1
IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
enem-target-m4-api:v1   fae92b51099c       1.47GB          515MB        

saulo@LeCun:enem$ docker compose up -d
[+] up 2/2
 ✔ Network enem_default         Created                                                            0.5s
 ✔ Container enem-target-m4-api Started                                                            5.8s

saulo@LeCun:enem$ sleep 5
saulo@LeCun:enem$ docker ps --filter "name=enem-target-m4-api"
CONTAINER ID   IMAGE                   COMMAND                  CREATED          STATUS                    PORTS                                         NAMES
3d14c5e44196   enem-target-m4-api:v1   "uvicorn src.api.mai…"   32 seconds ago   Up 27 seconds (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   enem-target-m4-api
```

### 4.2 Auditoria de Liveness e Hash SHA-256 (`GET /health`)

```text
saulo@LeCun:enem$ curl -s http://localhost:8000/health | python3 -m json.tool
{
    "status": "healthy",
    "model_loaded": true,
    "model_version": "enem_target_m4_producao:v1",
    "artifact_sha256": "114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f"
}
```

### 4.3 Auditoria de Governança e Linhagem MLflow (`GET /info`)

```text
saulo@LeCun:enem$ curl -s http://localhost:8000/info | python3 -m json.tool
{
    "nome_artefato": "enem.pkl",
    "modelo_registrado_mlflow": "enem_target_m4_producao",
    "mlflow_run_id_campeao": "8b4ed2c387044363968b6088078bdf2d",
    "classe_modelo_campeao": "XGBRegressor",
    "data_treinamento_utc": "2026-11-03T12:36:10Z",
    "sha256_enem_pkl": "114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f",
    "janela_historica": "2014-2023",
    "n_total_censo": 37593629,
    "n_holdout_cego": 7518726,
    "features_ordenadas": [
        "RENDA_PER_CAPITA",
        "Q024",
        "TP_ANO_CONCLUIU",
        "TP_LINGUA",
        "TP_SEXO",
        "Q002"
    ],
    "metricas_oficiais": {
        "holdout_estratificado_7_52m": {
            "r2": 0.3378,
            "rmse": 57.7439,
            "mae": 45.5904,
            "erro_relativo_sigma": 0.81376
        },
        "out_of_time_interno_2014_2022_para_2023": {
            "r2": 0.31842,
            "rmse": 67.6232,
            "mae": 52.8526,
            "erro_relativo_sigma": 0.82558,
            "vies_medio_pts": -5.516
        }
    }
}
```

### 4.4 Teste de Inferência Individual (`POST /predict`)

```text
saulo@LeCun:enem$ curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "RENDA_PER_CAPITA": 1.5,
    "Q024": 1,
    "TP_ANO_CONCLUIU": 0,
    "TP_LINGUA": 0,
    "TP_SEXO": 0,
    "Q002": 4
  }' | python3 -m json.tool
{
    "target_m4": 547.12,
    "unidade": "pontos_escala_tri_0_a_1000",
    "modelo": "enem_target_m4_producao:v1"
}
```

### 4.5 Teste de Inferência Vetorial em Lote (`POST /predict/batch` — Latência `6,49 ms`)

```text
saulo@LeCun:enem$ curl -s -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "candidatos": [
      {"RENDA_PER_CAPITA": 1.5, "Q024": 1, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 0, "Q002": 4},
      {"RENDA_PER_CAPITA": 0.0, "Q024": 0, "TP_ANO_CONCLUIU": 2, "TP_LINGUA": 1, "TP_SEXO": 1, "Q002": 1},
      {"RENDA_PER_CAPITA": 5.0, "Q024": 3, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 1, "Q002": 6}
    ]
  }' | python3 -m json.tool
{
    "total_candidatos": 3,
    "predicoes": [
        547.12,
        465.83,
        607.9
    ],
    "tempo_inferencia_ms": 6.49,
    "unidade": "pontos_escala_tri_0_a_1000",
    "modelo": "enem_target_m4_producao:v1"
}
```

### 4.6 Teste de Blindagem Anti-Leakage (`HTTP 422 Unprocessable Content`)

```text
saulo@LeCun:enem$ curl -s -i -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "RENDA_PER_CAPITA": 1.5,
    "Q024": 1,
    "TP_ANO_CONCLUIU": 0,
    "TP_LINGUA": 0,
    "TP_SEXO": 0,
    "Q002": 4,
    "NU_ANO": 2023
  }'
HTTP/1.1 422 Unprocessable Content
date: Sun, 08 Nov 2026 20:54:58 GMT
server: uvicorn
content-length: 115
content-type: application/json

{"detail":[{"type":"extra_forbidden","loc":["body","NU_ANO"],"msg":"Extra inputs are not permitted","input":2023}]}
```

### 4.7 Encerramento Limpo do Ambiente

```text
saulo@LeCun:enem$ docker compose down
[+] down 2/2
 ✔ Container enem-target-m4-api Removed                                                           3.1s
 ✔ Network enem_default         Removed                                                           0.7s
```

---

## 5. Esteira Automatizada de CI/CD e FinOps em Nuvem (Marco 2.4 — GitHub Actions & AWS)

Para fechar o ciclo da **Etapa 2**, o arquivolegado `.github/workflows/pipeline.yml` foi removido via `git rm` e substituído pela esteira oficial [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml), desenhada com **3 Jobs encadeados**:

| Job do Workflow | Nome Técnico | O que Executa no Runner (`ubuntu-latest`) | Regra de Governança / FinOps |
| :--- | :--- | :--- | :--- |
| **Job 1** | `quality-gate-ci` | 1. Calcula o `sha256sum` de `models/enem.pkl` e confronta com o hash oficial (`114f51959492...`);<br>2. Instala `requirements-api.txt` via `astral-sh/setup-uv@v5` em ~5s;<br>3. Executa os 25 testes `pytest` e publica relatório no `$GITHUB_STEP_SUMMARY`. | **Fail-Fast:** Qualquer alteração acidental no binário do modelo ou quebra de contrato Pydantic bloqueia o pipeline imediatamente. |
| **Job 2** | `docker-smoke-test` | 1. Depende do Job 1 (`needs: quality-gate-ci`);<br>2. Constrói a imagem Docker multi-stage;<br>3. Sobe o container e executa chamadas HTTP reais em `/health`, `/predict` (`547.12`) e teste de bloqueio `HTTP 422` (`NU_ANO`). | Garante que o `Dockerfile` nunca quebre silenciosamente e que o container responda perfeitamente antes de qualquer envio à nuvem. |
| **Job 3** | `deploy-aws` | 1. Depende do Job 2 (`needs: docker-smoke-test`);<br>2. Autentica na AWS (OIDC `AWS_ROLE_TO_ASSUME` ou Access Keys);<br>3. Faz login no **Amazon ECR**, cria o repositório com *Scan on Push*, envia as tags `$GITHUB_SHA` e `latest`, e aciona `aws apprunner start-deployment`. | **Trava FinOps Inteligente:** Condicionado à presença dos *Secrets* da AWS. Enquanto a nuvem não é ativada para a demonstração final da banca, os Jobs 1 e 2 ficam **100% verdes (✅)** gratuitamente no GitHub e o Job 3 é marcado como *skipped* (custo zero). |


