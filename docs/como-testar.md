# 🧪 Guia Prático — Como Testar a Aplicação (`ENEM TARGET_M4 API`, Front-end & Stack AWS/MLOps)

**Módulos Testados:** [`src/api/`](../src/api/), [`tests/`](../tests/), [`models/enem.pkl`](../models/enem.pkl), [`frontend/`](../frontend/), [`Dockerfile`](../Dockerfile), [`docker-compose.yml`](../docker-compose.yml), [`infra/`](../infra/), [`monitoring/`](../monitoring/), [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)  
**Última Atualização:** 25 de Novembro de 2026 (Alinhado ao **AWS ECS Express Mode** e **Front-end Streamlit**)

---

## ⚠️ Regra de Ouro Antes de Começar: Use 2 Terminais Separados

Este repositório possui **dois ambientes Python isolados** (raiz vs. `frontend/`) e comandos que exigem estar na **pasta raiz** (`docker compose` e `terraform -chdir=infra`). Misturar os diretórios gera erros como `chdir infra: no such file or directory`.

| Terminal | Pasta onde deve ficar | O que você executa nele |
| :--- | :--- | :--- |
| **Terminal 1 (Raiz)** | `/home/saulo/mba/tcc/enem` | `.venv/bin/pytest`, `uvicorn`, `docker compose`, `aws`, `terraform -chdir=infra` |
| **Terminal 2 (Front-end)** | `/home/saulo/mba/tcc/enem/frontend` | `source .venv/bin/activate` e `streamlit run app.py` |

> **Dica rápida:** antes de rodar qualquer comando `docker compose` ou `terraform`, confirme com `pwd` no Terminal 1 que você está em `/home/saulo/mba/tcc/enem`.

---

## 1. Quality Gate Automatizado (Local — sem subir servidor)

**Onde rodar:** **Terminal 1** (raiz `/home/saulo/mba/tcc/enem`).

Executa análise estática (`ruff`, `mypy`) e os **`26` testes automatizados** cobrindo contrato HTTP, blindagem Anti-Leakage (`HTTP 422`), exposição `/metrics`, integridade `SHA-256`, paridade bit-a-bit com [`models/enem.pkl`](../models/enem.pkl), direcionalidade sociológica de Bourdieu e SLA de latência ([`tests/test_api_contract.py`](../tests/test_api_contract.py) e [`tests/test_model_inference.py`](../tests/test_model_inference.py)):

```bash
.venv/bin/ruff check src tests
.venv/bin/mypy --python-executable .venv/bin/python src/api tests
.venv/bin/pytest tests/ -v
```

*(Esse é o mesmo conjunto de validações executado no job `quality-gate-ci` de [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml), usando as regras de [`pyproject.toml`](../pyproject.toml).)*

---

## 2. Teste Rápido Direto no Python (Swagger UI)

**Onde rodar:** **Terminal 1** (raiz `/home/saulo/mba/tcc/enem`).

Sobe apenas a API FastAPI localmente via [`src/api/main.py`](../src/api/main.py):

```bash
.venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

* **Swagger UI (testar pelo navegador):** `http://localhost:8000/docs`
* **Endpoint de métricas Prometheus:** `http://localhost:8000/metrics`
* Pressione `Ctrl + C` no Terminal 1 para encerrar antes de passar ao Nível 3.

---

## 3. Teste Completo Local: API Docker + Prometheus + Grafana + Front-end (Custo Zero)

Siga **exatamente esta ordem** para validar o sistema inteiro na sua máquina sem tocar na AWS:

### Passo 3.1 — Subir API + Prometheus + Grafana (**Terminal 1 — raiz**)

```bash
docker compose --profile monitoring up -d --build
```

*(Sobe os 3 containers: `enem-api` na porta `:8000`, `prometheus` na `:9090` e `grafana` na `:3000`.)*

### Passo 3.2 — (Opcional) Validar endpoints via `curl` (**Terminal 1 — raiz**)

1. **Saúde e hash SHA-256 (`GET /health`):**
   ```bash
   curl -s http://localhost:8000/health | python3 -m json.tool
   ```
   *(Esperado: `"status": "healthy"`, `"model_loaded": true`, `"artifact_sha256": "114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f"`.)*

2. **Governança e linhagem MLflow (`GET /info`):**
   ```bash
   curl -s http://localhost:8000/info | python3 -m json.tool
   ```
   *(Esperado: `"mlflow_run_id_campeao": "6490c396b0e04147b156bedb0c8af9f7"`.)*

3. **Predição individual (`POST /predict`):**
   ```bash
   curl -s -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"RENDA_PER_CAPITA": 1.5, "Q024": 1, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 0, "Q002": 4}' | python3 -m json.tool
   ```

4. **Predição vetorial em lote (`POST /predict/batch`):**
   ```bash
   curl -s -X POST http://localhost:8000/predict/batch \
     -H "Content-Type: application/json" \
     -d '{
       "candidatos": [
         {"RENDA_PER_CAPITA": 1.5, "Q024": 1, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 0, "Q002": 4},
         {"RENDA_PER_CAPITA": 0.0, "Q024": 0, "TP_ANO_CONCLUIU": 2, "TP_LINGUA": 1, "TP_SEXO": 1, "Q002": 1},
         {"RENDA_PER_CAPITA": 5.0, "Q024": 3, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 1, "Q002": 6}
       ]
     }' | python3 -m json.tool
   ```

5. **Bloqueio Anti-Leakage (`HTTP 422 Unprocessable Content`):**
   ```bash
   curl -i -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"RENDA_PER_CAPITA": 1.5, "Q024": 1, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 0, "Q002": 4, "NU_ANO": 2023}'
   ```
   *(Deve rejeitar `"NU_ANO"` com `HTTP/1.1 422` e `"type": "extra_forbidden"`.)*

6. **Popular gráficos `rate()` e *drift* rapidamente via terminal (opcional):**
   ```bash
   for i in $(seq 1 20); do
     curl -s -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
       -d '{"RENDA_PER_CAPITA": 0.5, "Q024": 0, "TP_ANO_CONCLUIU": 1, "TP_LINGUA": 1, "TP_SEXO": 0, "Q002": 2}' > /dev/null
     curl -s -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
       -d '{"RENDA_PER_CAPITA": 4.5, "Q024": 3, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 1, "Q002": 6}' > /dev/null
     curl -s -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
       -d '{"RENDA_PER_CAPITA": 1.5, "Q024": 1, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 0, "Q002": 4, "NU_ANO": 2023}' > /dev/null
     sleep 1
   done
   ```

### Passo 3.3 — Abrir o Front-end Streamlit (**Terminal 2 — pasta `frontend/`**)

* **Apenas na 1ª vez** (caso `frontend/.venv` ainda não exista):
  ```bash
  cd frontend
  uv venv .venv
  source .venv/bin/activate
  uv pip install -r requirements.txt
  cp .env.example .env
  streamlit run app.py
  ```
* **Nos próximos testes (quando `frontend/.venv` já existe):**
  ```bash
  cd frontend
  source .venv/bin/activate
  streamlit run app.py
  ```

No navegador (`http://localhost:8501`):
1. Na barra lateral esquerda, mantenha **`URL base da API FastAPI`** em `http://localhost:8000`.
2. Clique em **`🩺 Verificar saúde da API (/health)`** e depois dispare inferências com **`🔍 Consultar 1 Aluno`** e **`🎲 Gerar e Consultar N Alunos Aleatórios`**.

### Passo 3.4 — Conferir Prometheus e Grafana no navegador

* **Prometheus (`http://localhost:9090`):**
  * **Targets (saúde da coleta):** abra direto **`http://localhost:9090/targets`** (ou clique no menu **`≡`** no canto superior direito $\rightarrow$ `Status` $\rightarrow$ `Target health` / `Targets`) e confirme `enem-api-local` (`http://enem-api:8000/metrics`) como **`UP`**.
  * **Consulta manual (`http://localhost:9090/query`):** a tela abre vazia (*"No data queried yet"*) até você executar uma expressão. No campo **`>_ Enter expression`**, digite uma das métricas abaixo e clique em **`Execute`**:
    * `enem_api_predictions_total` *(total de candidatos escorados)*
    * `enem_api_http_requests_total` *(requisições HTTP por rota e status)*
    * `enem_api_model_info` *(status `1` do modelo carregado e hash SHA-256 ativo)*
    * *Outras métricas disponíveis em [`src/api/metrics.py`](../src/api/metrics.py):* `enem_api_validation_errors_total`, `enem_api_http_request_duration_seconds`, `enem_api_model_inference_duration_seconds`, `enem_api_predicted_target_m4`, `enem_api_input_renda_per_capita` e `enem_api_input_categorical_total`.
  * *(Se continuar zerado no Cenário A, confirme na barra lateral do Streamlit que `URL base da API FastAPI` está em `http://localhost:8000`, e não em uma URL antiga da AWS.)*
* **Grafana (`http://localhost:3000`):** faça login (`admin` / `admin`, definido em [`docker-compose.yml`](../docker-compose.yml#L37-L38)) e abra **`Dashboards` $\rightarrow$ pasta `ENEM TARGET_M4`**.
  * *(Para os gráficos de taxa `rate()` desenharem curvas contínuas, faça 2 a 4 cliques seguidos no Streamlit com alguns segundos de intervalo.)*
  * **Testar o alerta visual `Bloqueios Anti-Leakage` (cartão sobe e fica laranja em ~5s):** execute no **Terminal 1 (raiz)** (trocando `http://localhost:8000` por `https://<SEU_DOMINIO_ECS>` caso esteja testando na AWS):
    ```bash
    curl -i -X POST http://localhost:8000/predict \
      -H "Content-Type: application/json" \
      -d '{"RENDA_PER_CAPITA": 1.5, "Q024": 1, "TP_ANO_CONCLUIU": 0, "TP_LINGUA": 0, "TP_SEXO": 0, "Q002": 4, "NU_ANO": 2023}'
    ```

### Passo 3.5 — Encerrar os ambientes locais

1. No **Terminal 2 (`frontend/`)**: pressione `Ctrl + C` para parar o Streamlit.
2. No **Terminal 1 (raiz)**: derrube os containers:
   ```bash
   docker compose --profile monitoring down
   ```

---

## 4. Teste Completo na Nuvem AWS (ECS Express Mode + Front-end + Prometheus/Grafana)

Siga **rigorosamente a ordem cronológica abaixo** (do Passo `4.1` ao `4.6`):

### Passo 4.1 — (Informativo) CI/CD automático no GitHub Actions
* Qualquer `git push` para a branch `main` (ou Pull Request) nos arquivos da API, testes, modelo, `Dockerfile` ou `pyproject.toml` roda gratuitamente os jobs `quality-gate-ci` e `docker-smoke-test` de [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).
* O Job 3 (`deploy-aws`) só atualiza o serviço na AWS se os Secrets `AWS_ROLE_TO_ASSUME` e `AWS_ECS_SERVICE_ARN` estiverem cadastrados no GitHub.

### Passo 4.2 — Enviar a imagem Docker ao Amazon ECR (**Terminal 1 — raiz**)

*(Necessário na 1ª vez ou sempre que você alterar o código da API em `src/api/`, o `Dockerfile` ou o `models/enem.pkl`. Se a tag `:latest` já está atualizada no ECR, pule direto para o Passo 4.3.)*

```bash
aws sts get-caller-identity
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 703671922740.dkr.ecr.us-east-1.amazonaws.com

docker build -t enem-target-m4-api:latest .
docker tag enem-target-m4-api:latest 703671922740.dkr.ecr.us-east-1.amazonaws.com/enem-target-m4-api:latest
docker push 703671922740.dkr.ecr.us-east-1.amazonaws.com/enem-target-m4-api:latest
```

### Passo 4.3 — Ligar o AWS ECS Express Mode via Terraform (**Terminal 1 — raiz**)

```bash
terraform -chdir=infra apply -var="create_ecs=true"
```
Confirme digitando `yes`. Como `wait_for_steady_state = true` está ativo em [`infra/main.tf`](../infra/main.tf), o Terraform aguardará o container passar no `/health` antes de concluir.

Ao terminar, pegue a URL HTTPS pública gerada:

```bash
terraform -chdir=infra output ecs_service_url
```

*(Opcional) Valide direto no terminal ou abra `https://<SEU_DOMINIO_ECS>/docs` no navegador:*
```bash
curl -s https://<SEU_DOMINIO_ECS>/health | python3 -m json.tool
```

### Passo 4.4 — Conectar Prometheus e Grafana locais na AWS (**Terminal 1 — raiz**)

1. Abra [`monitoring/prometheus/prometheus.yml`](../monitoring/prometheus/prometheus.yml), descomente as linhas do bloco **`enem-api-aws-ecs`** e substitua `SEU-SERVICO.ecs.us-east-1.on.aws` pelo domínio de `ecs_service_url` **SEM `https://`** e sem barra no final (pois `scheme: https` já adiciona o protocolo).
2. Na **raiz `/home/saulo/mba/tcc/enem`**, suba e reinicie o Prometheus para ler a nova configuração:
   ```bash
   docker compose --profile monitoring up -d
   docker compose --profile monitoring restart prometheus
   ```
3. Confirme em **`http://localhost:9090/targets`** (ou `≡` $\rightarrow$ `Status` $\rightarrow$ `Target health` / `Targets`) se **`enem-api-aws-ecs`** aparece como **`UP`**, teste consultas em **`http://localhost:9090/query`** (`enem_api_predictions_total`, `enem_api_http_requests_total`, `enem_api_model_info`), e deixe aberto o Grafana em `http://localhost:3000` (`Dashboards -> ENEM TARGET_M4`).

### Passo 4.5 — Testar os endpoints pelos botões do Front-end (**Terminal 2 — pasta `frontend/`**)

```bash
cd frontend
source .venv/bin/activate
streamlit run app.py
```
*(Se ainda não criou `frontend/.venv`, execute antes o bloco de 1ª vez do Passo 3.3.)*

No navegador (`http://localhost:8501`):
1. Na barra lateral esquerda, em **`URL base da API FastAPI`**, cole o valor completo de `ecs_service_url` (**COM `https://`**, ex.: `https://tc-xxxx.ecs.us-east-1.on.aws`) e aperte `Enter`.
2. Clique em **`🩺 Verificar saúde da API (/health)`** para confirmar conexão saudável (`healthy`).
3. Na aba **`🛡️ Governança & Métricas`**, clique em **`🔄 Atualizar dados de governança da API`** (`GET /info`).
4. Na aba **`🎯 Simulador`**, clique em **`🔍 Consultar 1 Aluno`** (`POST /predict`) e dispare algumas vezes **`🎲 Gerar e Consultar N Alunos Aleatórios`** (`POST /predict/batch`, por exemplo com 100 alunos) com alguns segundos de intervalo para ver as curvas de `rate()`, latência e *drift* atualizando ao vivo no Grafana (`http://localhost:3000`)!

### Passo 4.6 — Desligamento Obrigatório Pós-Teste (**Volte ao Terminal 1 — raiz!**)

1. No **Terminal 2 (`frontend/`)**: pare o Streamlit com `Ctrl + C`.
2. Em [`monitoring/prometheus/prometheus.yml`](../monitoring/prometheus/prometheus.yml): recomente com `#` o bloco `enem-api-aws-ecs` (evita erros de target `DOWN` no próximo teste local).
3. No **Terminal 1 (confira que `pwd` é `/home/saulo/mba/tcc/enem`)**:
   ```bash
   docker compose --profile monitoring down
   terraform -chdir=infra apply -var="create_ecs=false"
   ```
   *(Confirme com `yes`. Isso desliga **apenas** o cluster ECS Express Mode e o Load Balancer ALB, zerando o custo de computação e mantendo intactos seu bucket **S3** com DVC/MLflow e o repositório **ECR** — custo residual `< $0,01/dia`.)*

> **⚠️ CUIDADO COM `terraform destroy`:** Não rode `terraform -chdir=infra destroy` entre testes! Como [`infra/main.tf`](../infra/main.tf) possui `force_destroy = true` no bucket S3 e `force_delete = true` no ECR, `terraform destroy` apaga **tudo** (inclusive `dvc-store/`, `mlflow-artifacts/` e imagens Docker no ECR). Use `terraform -chdir=infra destroy` **somente** para encerramento definitivo após a banca.

---

## 5. Cola Rápida Para Repetir os Testes em Outro Dia

### Cenário A — Testar tudo localmente (Custo Zero)
* **Terminal 1 (`/home/saulo/mba/tcc/enem`):**
  ```bash
  docker compose --profile monitoring up -d
  ```
* **Terminal 2 (`/home/saulo/mba/tcc/enem/frontend`):**
  ```bash
  source .venv/bin/activate
  streamlit run app.py
  ```
* **Acessar:** Front-end `http://localhost:8501` (`http://localhost:8000`) | Prometheus `http://localhost:9090/targets` e `http://localhost:9090/query` (`enem_api_predictions_total`, `enem_api_http_requests_total`, `enem_api_model_info`) | Grafana `http://localhost:3000`
* **Encerrar:** `Ctrl+C` no Terminal 2; `docker compose --profile monitoring down` no Terminal 1.

### Cenário B — Testar tudo na AWS (Ligar $\rightarrow$ Testar $\rightarrow$ Desligar)
* **Terminal 1 (`/home/saulo/mba/tcc/enem`):**
  ```bash
  terraform -chdir=infra apply -var="create_ecs=true"
  terraform -chdir=infra output ecs_service_url
  ```
  *(Colar o domínio sem `https://` em `monitoring/prometheus/prometheus.yml` e rodar:)*
  ```bash
  docker compose --profile monitoring up -d
  docker compose --profile monitoring restart prometheus
  ```
* **Terminal 2 (`/home/saulo/mba/tcc/enem/frontend`):**
  ```bash
  source .venv/bin/activate
  streamlit run app.py
  ```
  *(Colar `ecs_service_url` COM `https://` na barra lateral do Streamlit, clicar nos botões e conferir `http://localhost:9090/targets`, `http://localhost:9090/query` (`enem_api_predictions_total`, `enem_api_http_requests_total`, `enem_api_model_info`) e Grafana `http://localhost:3000`.)*
* **Encerrar (obrigatório!):** `Ctrl+C` no Terminal 2; recomentar bloco AWS em `prometheus.yml`; e no **Terminal 1 (`/home/saulo/mba/tcc/enem`)**:
  ```bash
  docker compose --profile monitoring down
  terraform -chdir=infra apply -var="create_ecs=false"
  ```
