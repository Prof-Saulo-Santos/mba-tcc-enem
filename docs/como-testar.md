# 🧪 Guia Prático — Como Testar a Aplicação (`ENEM TARGET_M4 API` & Stack MLOps)

**Módulos Testados:** [`src/api/`](../src/api/), [`tests/`](../tests/), [`models/enem.pkl`](../models/enem.pkl), [`Dockerfile`](../Dockerfile), [`docker-compose.yml`](../docker-compose.yml), [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)  
**Última Atualização:** 22 de Novembro de 2026 (Pós-Fases 1 a 4)

Você pode validar a aplicação em **4 níveis**, indo dos testes automatizados locais até a observabilidade ao vivo em containers e o pipeline na nuvem.

---

## 1. Teste Automatizado Completo (Quality Gate Local — sem subir servidor)

Executa a análise estática de código/tipos e os **`26` testes automatizados** cobrindo contrato HTTP, blindagem Anti-Leakage (`HTTP 422`), exposição `/metrics`, integridade `SHA-256`, paridade bit-a-bit com [`models/enem.pkl`](../models/enem.pkl), direcionalidade sociológica de Bourdieu e SLA de latência ([`tests/test_api_contract.py`](../tests/test_api_contract.py) e [`tests/test_model_inference.py`](../tests/test_model_inference.py)):

```bash
ruff check src tests
mypy --python-executable .venv/bin/python src/api tests
.venv/bin/pytest tests/ -v
```

*(Esse é o mesmo conjunto de validações executado no job `quality-gate-ci` de [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml), usando as regras definidas em [`pyproject.toml`](../pyproject.toml).)*

---

## 2. Teste Interativo Direto no Python (Swagger UI)

Sobe a API FastAPI diretamente pelo ambiente virtual `.venv` executando [`src/api/main.py`](../src/api/main.py):

```bash
.venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

* **Documentação interativa (Swagger UI):** abra `http://localhost:8000/docs` no navegador para enviar payloads manualmente pelo botão *Try it out*.
* **Endpoint de métricas Prometheus:** `http://localhost:8000/metrics`.
* Pressione `Ctrl + C` no terminal para encerrar o servidor.

---

## 3. Teste no Container Docker Oficial + Prometheus & Grafana (Ambiente Completo)

Valida exatamente a imagem OCI de produção definida no [`Dockerfile`](../Dockerfile) e orquestrada pelo [`docker-compose.yml`](../docker-compose.yml):

* **Subir apenas a API (`:8000`):**
  ```bash
  docker compose up -d --build
  ```
* **Subir a API + Stack de Observabilidade (`Prometheus :9090` + `Grafana :3000`):**
  ```bash
  docker compose --profile monitoring up -d --build
  ```

### 3.1 Chamadas `curl` para validar todos os endpoints (`http://localhost:8000`)

1. **Saúde do serviço e integridade SHA-256 (`GET /health`):**
   ```bash
   curl -s http://localhost:8000/health | python3 -m json.tool
   ```
   *(Esperado: `"status": "healthy"`, `"model_loaded": true`, `"artifact_sha256": "114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f"`.)*

2. **Governança e linhagem MLflow (`GET /info`):**
   ```bash
   curl -s http://localhost:8000/info | python3 -m json.tool
   ```
   *(Esperado: `"mlflow_run_id_campeao": "6490c396b0e04147b156bedb0c8af9f7"` e métricas oficiais do Model Card.)*

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

### 3.2 Conferência ao vivo no Prometheus e Grafana

* **Prometheus (`http://localhost:9090`):** acesse `Status -> Targets` e confirme o target `enem-api-local` (`http://enem-api:8000/metrics`) no estado **`UP`**.
* **Grafana (`http://localhost:3000`):** faça login com usuário `admin` e senha `admin` (padrão definido em [`docker-compose.yml`](../docker-compose.yml#L37-L38)) e abra `Dashboards` → pasta **`ENEM TARGET_M4`**.
* **Popular gráficos de taxa (`rate()`) e *drift* em tempo real** (detalhes em [`docs/guia-estudo-observabilidade.md`](guia-estudo-observabilidade.md#L116-L125)):
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
* **Encerrar os containers com segurança:**
  ```bash
  docker compose --profile monitoring down
  ```

---

## 4. Teste em CI/CD (GitHub Actions) e Nuvem (AWS App Runner)

* **GitHub Actions (custo zero):** qualquer `git push` para a branch `main` (ou Pull Request) tocando nos arquivos da API, testes, modelo, `Dockerfile` ou `pyproject.toml` executa automaticamente os jobs `quality-gate-ci` e `docker-smoke-test` definidos em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).
* **AWS App Runner (deploy pontual para demonstração/banca):** caso queira testar via URL HTTPS pública na AWS, habilite o Estágio 2 do Terraform conforme [`docs/etapa-02-passo-a-passo.md`](etapa-02-passo-a-passo.md#L79) e destrua os recursos de computação logo após os testes para evitar custos:
  ```bash
  terraform -chdir=infra apply -var="create_apprunner=true"
  # ... testes HTTP/HTTPS na URL pública ...
  terraform -chdir=infra destroy
  ```
