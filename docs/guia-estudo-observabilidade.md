# 📘 Guia de Estudo e Slides — Observabilidade da API (Docker, Prometheus & Grafana)

**Projeto:** TCC MBA — Predição de Desempenho no ENEM (`TARGET_M4`) e Arquitetura MLOps  
**Autor:** Saulo Santos  
**Referência Visual (1920×1080):** [`media/observabilidade_docker_prometheus_grafana.png`](../media/observabilidade_docker_prometheus_grafana.png)  
**Objetivo deste Documento:** Consolidar todos os conceitos, escolhas técnicas, código e consultas PromQL da **Fase 1** para estudo aprofundado e preparação dos slides da defesa perante a banca.

---

## 1. Por Que Implementamos Isso? (Visão Conceitual)

Antes da Fase 1, o microserviço FastAPI em [`src/api/main.py`](../src/api/main.py) recebia payloads, rodava o `XGBRegressor` e devolvia a nota `target_m4`, mas operava como uma **caixa-preta**: se a latência degradasse, se alguém tentasse enviar variáveis proibidas (`NU_ANO`) repetidamente ou se o perfil socioeconômico dos usuários mudasse (*Data/Prediction Drift*), não havia histórico nem painel visual.

Com a Fase 1, passamos a ter:
1. **Monitoramento contínuo de SLA e erros HTTP** (`/predict` e `/predict/batch`).
2. **Auditoria ativa da blindagem Anti-Leakage (`HTTP 422`)** separada por causa.
3. **Sinalização de *Data Drift* e *Prediction Drift* em produção** usando apenas métricas agregadas de baixa cardinalidade.
4. **Provisionamento declarativo (*Zero ClickOps*)** do Grafana com datasource e dashboard prontos no boot do container.

---

## 2. Fundamentos Arquiteturais Para Defender na Banca

### 2.1 Modelo *Pull (Scrape)* do Prometheus vs. *Push*
* No modelo adotado, a API **não empurra** métricas para um banco externo durante cada predição (o que adicionaria latência de rede à resposta do usuário).
* A API apenas atualiza contadores e histogramas **em memória RAM** (microssegundos) e expõe o resumo atual no endpoint **`GET /metrics`**.
* O **Prometheus (`:9090`)** atua por **Pull (*Scrape*)**: a cada **`5 segundos`** (`scrape_interval: 5s` em [`monitoring/prometheus/prometheus.yml`](../monitoring/prometheus/prometheus.yml)), ele faz uma requisição HTTP `GET http://enem-api:8000/metrics` na rede interna do Docker Compose e grava as amostras no seu **TSDB (*Time Series Database*)** com retenção configurada para `7d`.
* *Evidência observada localmente (19/11/2026):* target `enem-api-local` em `http://enem-api:8000/metrics` com status **`1 / 1 up` (`UP`)** e tempo de coleta de **`4 ms`**.

### 2.2 Por que `prometheus-client` Puro + Middleware Próprio?
* Em vez de adicionar bibliotecas intermediárias de terceiros sobre `fastapi==0.162.0`, usamos apenas a biblioteca oficial **`prometheus-client==0.26.0`** (travada em [`requirements-api.txt`](../requirements-api.txt) e [`requirements.txt`](../requirements.txt)).
* **Vantagens:** menor superfície de incompatibilidade de versões, impacto mínimo no tamanho da imagem Docker e controle explícito das métricas de ML e segurança.

### 2.3 Proteção Contra Explosão de Cardinalidade
* No Prometheus, cada combinação única de *labels* cria uma nova série temporal em memória e disco. Se usássemos `request.url.path` bruto como *label*, um atacante ou *scanner* enviando `/predict/1`, `/predict/2`, `/admin`, `/wp-login` criaria milhares de séries inúteis.
* Em [`src/api/main.py`](../src/api/main.py), o middleware resolve a rota casada pelo FastAPI:
  ```python
  route = request.scope.get("route")
  route_path = route.path if route is not None else "unmatched"
  ```
  Assim, qualquer URL inexistente é agrupada em `"unmatched"`, mantendo a cardinalidade estritamente controlada.
* Da mesma forma, **nunca** colocamos valores contínuos (como `RENDA_PER_CAPITA = 1.537`) em *labels* de `Counter`: variáveis contínuas usam **`Histogram` com *buckets* fixos**, enquanto `Counter` com *label* é usado apenas nas variáveis categóricas discretas e finitas (`Q024`, `TP_ANO_CONCLUIU`, `TP_LINGUA`, `TP_SEXO`, `Q002` — ao todo apenas `4 + 10 + 2 + 2 + 8 = 26` séries).

---

## 3. Anatomia Completa do Código Implementado

### 3.1 Catálogo das `9` Métricas em [`src/api/metrics.py`](../src/api/metrics.py)

| Métrica | Tipo Prometheus | Labels | O que mede e por que existe |
| :--- | :---: | :--- | :--- |
| `enem_api_http_requests_total` | `Counter` | `method`, `path`, `status_code` | Taxa de requisições (`req/s`) por rota e código HTTP (`200`, `422`, `500`, `503`). |
| `enem_api_http_request_duration_seconds` | `Histogram` | `method`, `path` | Latência HTTP ponta a ponta (`11` buckets de `2ms` a `5s`), permitindo calcular `P50` e `P95`. |
| `enem_api_validation_errors_total` | `Counter` | `error_type` | Separa bloqueios `HTTP 422` entre `extra_forbidden` (ex.: tentativa de enviar `NU_ANO`) e `domain_or_schema` (valor fora da faixa). |
| `enem_api_model_info` | `Gauge` | `model_version`, `artifact_sha256` | Vale `1.0` quando `models/enem.pkl` está carregado e `0.0` caso falhe, exibindo a versão e o hash SHA-256 ativo. |
| `enem_api_model_inference_duration_seconds` | `Histogram` | `mode` (`single` \| `batch`) | Tempo **puro** da chamada ao `XGBRegressor` (sem overhead de JSON/HTTP). |
| `enem_api_predictions_total` | `Counter` | `mode` (`single` \| `batch`) | Total acumulado de candidatos escorados (`1` no `/predict`, `N` no `/predict/batch`). |
| `enem_api_predicted_target_m4` | `Histogram` | — | Distribuição das notas `TARGET_M4` preditas (`13` buckets entre `300` e `1000` pts TRI) — monitora **Prediction Drift**. |
| `enem_api_input_renda_per_capita` | `Histogram` | — | Distribuição da feature #1 (`RENDA_PER_CAPITA`, `11` buckets de `0.0` a `25.0` SM) — monitora **Data Drift**. |
| `enem_api_input_categorical_total` | `Counter` | `feature`, `value` | Contagem por categoria de `Q024`, `TP_ANO_CONCLUIU`, `TP_LINGUA`, `TP_SEXO` e `Q002` — monitora mudança de perfil populacional. |

### 3.2 Fluxo de Execução em [`src/api/main.py`](../src/api/main.py)
1. **Startup (`lifespan`):** carrega `models/enem.pkl` via `ModelManager.get_instance().load()` e chama `set_model_status(...)` gravando `1.0` (ou `0.0` em caso de falha) em `enem_api_model_info`.
2. **Middleware HTTP (`prometheus_http_middleware`):** mede a duração de todas as rotas (exceto `/metrics`, para que o próprio *scrape* do Prometheus não polua a estatística de tráfego dos clientes) e chama `record_http_request(...)` no bloco `finally`.
3. **Interceptação transparente de erros 422 (`validation_exception_handler`):** registra `@app.exception_handler(RequestValidationError)`, inspeciona `exc.errors()` via `record_validation_error(...)` procurando `err.get("type") == "extra_forbidden"` e **delega a resposta HTTP para `request_validation_exception_handler(request, exc)`** do próprio FastAPI — preservando 100% do payload JSON original esperado pelos clientes e testes.
4. **Rotas `/predict` e `/predict/batch`:** cronometram a chamada pura ao `ModelManager` e registram em `record_inference(...)`.
5. **Rota `GET /metrics`:** retorna `render_metrics()` (`generate_latest()` com `CONTENT_TYPE_LATEST`).

### 3.3 Como o Teste de Contrato Valida as Métricas ([`tests/test_api_contract.py`](../tests/test_api_contract.py))
* Como contadores (`Counter`) são acumulativos na memória do processo durante a suíte `pytest`, o teste `test_metrics_endpoint_and_observability_counters` lê o valor **antes** (`REGISTRY.get_sample_value(...)`), executa:
  1. `POST /predict` válido (`200`);
  2. `POST /predict` com `"NU_ANO": 2023` (`422` $\rightarrow$ `extra_forbidden`);
  3. `POST /predict` com `"Q024": 99` (`422` $\rightarrow$ `domain_or_schema`);
  4. `GET /metrics` (`200`);
* E comprova que cada contador subiu exatamente `+1.0`.
* Resultado observado da suíte completa após implementação: **`26 passed, 1 warning in 18.76s`** + **`ruff check`** limpo (`All checks passed!`).

### 3.4 Orquestração Docker Compose & Provisionamento do Grafana
* Em [`docker-compose.yml`](../docker-compose.yml):
  * `enem-api` fica sempre disponível no `docker compose up -d` padrão (porta `:8000`).
  * `prometheus` (`:9090`) e `grafana` (`:3000`) usam **`profiles: ["monitoring"]`** — subindo juntos com `docker compose --profile monitoring up -d`.
* Em `monitoring/grafana/provisioning/`:
  * [`datasources/datasource.yml`](../monitoring/grafana/provisioning/datasources/datasource.yml) registra o Data Source padrão (`uid: prometheus`, URL `http://prometheus:9090`).
  * [`dashboards/dashboard.yml`](../monitoring/grafana/provisioning/dashboards/dashboard.yml) + [`dashboards/enem_api_observability.json`](../monitoring/grafana/provisioning/dashboards/enem_api_observability.json) carregam automaticamente os **10 painéis** na pasta **`ENEM TARGET_M4`**.

---

## 4. Entendendo o PromQL no Dashboard (e Por Que Gráficos `rate()` Precisam de Tráfego Contínuo)

Os painéis do dashboard usam três padrões clássicos de **PromQL**:

1. **Contadores e Estado Instantâneo (*Stat* / *Bar Gauge*):**
   * `max(enem_api_model_info)` $\rightarrow$ mostra `CARREGADO (PRONTO)` imediatamente após o 1º scrape.
   * `sum(enem_api_predictions_total) or vector(0)` $\rightarrow$ soma todas as predições (`or vector(0)` evita tela "No data" antes da primeira requisição).
   * `sum by (value) (enem_api_input_categorical_total{feature="Q024"})` $\rightarrow$ exibe barras comparando as categorias recebidas.

2. **Taxas e Percentis (*Time Series* com `rate()` e `histogram_quantile()`):**
   * `sum by (path, status_code) (rate(enem_api_http_requests_total[1m]))` $\rightarrow$ requisições por segundo.
   * `histogram_quantile(0.95, sum by (le) (rate(enem_api_http_request_duration_seconds_bucket{path=~"/predict.*"}[1m])))` $\rightarrow$ estima o **percentil 95 (P95)** da latência HTTP a partir dos *buckets* acumulados.
   * **⚠️ Ponto importante para entender ao abrir o Grafana:** `rate(...[1m])` calcula a taxa média por segundo usando **pelo menos duas amostras em scrapes diferentes dentro da janela**. Se você enviou apenas 1 requisição isolada e não gerou mais tráfego nos últimos 1–5 minutos, os gráficos de média móvel/taxa ficam sem curva contínua até receberem uma pequena sequência de chamadas!

3. **Média Móvel de *Drift* via Razão `_sum / _count` de Histograma:**
   * Todo `Histogram` no Prometheus cria automaticamente três sufixos: `_bucket`, `_sum` e `_count`.
   * Assim, a **nota média predita nos últimos 5 minutos** (*Prediction Drift*) é calculada exatamente por:
     ```promql
     rate(enem_api_predicted_target_m4_sum[5m]) / rate(enem_api_predicted_target_m4_count[5m])
     ```
   * E a **renda per capita média recebida nos últimos 5 minutos** (*Data Drift*) por:
     ```promql
     rate(enem_api_input_renda_per_capita_sum[5m]) / rate(enem_api_input_renda_per_capita_count[5m])
     ```

### Script Rápido Para Popular os 10 Painéis do Grafana Ao Vivo
Para ver todos os gráficos de séries temporais, latência P50/P95 e *Drift* desenhando curvas no Grafana (`http://localhost:3000` $\rightarrow$ `Dashboards` $\rightarrow$ `ENEM TARGET_M4`), rode no terminal com o Docker rodando:

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

---

## 5. Roteiro Pronto de Slides (Para Incorporar ao Deck Final)

### Slide A — Arquitetura de Observabilidade em Tempo Real
* **Visual principal:** [`media/observabilidade_docker_prometheus_grafana.png`](../media/observabilidade_docker_prometheus_grafana.png) (`1920×1080`).
* **Tópicos na tela:**
  * Modelo **Pull (`GET /metrics`)** com *scrape* a cada `5s` (`4 ms` de coleta local).
  * `prometheus-client` em memória: zero impacto perceptível na latência do `XGBRegressor`.
  * Controle estrito de cardinalidade (`route.path` + histogramas + 26 séries categóricas).
  * Provisionamento declarativo do **Grafana** (10 painéis prontos no boot).
* **Nota de fala (~1 min):** *"Para que o modelo em produção não operasse como caixa-preta, instrumentamos a API FastAPI com o padrão Prometheus. Em vez de enviar eventos síncronos que atrasariam a resposta do usuário, a API mantém contadores e histogramas em memória e expõe `/metrics`, coletado a cada 5 segundos pelo Prometheus e exibido em dashboards provisionados automaticamente no Grafana."*

### Slide B — Telemetria de Contrato (`HTTP 422`) e Monitoramento de *Drift*
* **Visual sugerido:** Print ao vivo do dashboard **`ENEM TARGET_M4 — Observabilidade & Drift`** no Grafana (`localhost:3000`).
* **Tópicos na tela:**
  * **Segurança & Contrato:** rastreamento separado de rejeições `422` por `extra_forbidden` (ex.: tentativa de envio de `NU_ANO`) vs. erros de faixa.
  * **SLA de Inferência:** comparação entre latência HTTP P50/P95 e tempo puro de execução do `XGBRegressor`.
  * **Prediction & Data Drift:** acompanhamento em janela móvel da média das notas preditas (`TARGET_M4`), da `RENDA_PER_CAPITA` e do perfil de `Q024` / `TP_LINGUA`.
* **Nota de fala (~1 min):** *"Além da saúde técnica de infraestrutura, o painel monitora a própria governança científica do modelo: contabilizamos tentativas de violação anti-leakage bloqueadas com HTTP 422 e acompanhamos via histogramas PromQL o deslocamento das features de entrada (Data Drift) e das notas preditas (Prediction Drift)."*

---

## 6. Perguntas Prováveis da Banca Sobre Esta Etapa (Sabatina)

1. **"Por que usar Prometheus em vez de gravar cada requisição no PostgreSQL?"**
   * *Resposta:* Banco relacional para séries temporais de alta frequência sofre com crescimento de tabela e *locks* sob carga; o Prometheus foi desenhado para métricas numéricas em TSDB com compactação temporal, consultas de taxa/percentil nativas (`rate`, `histogram_quantile`) e baixíssimo overhead em memória na API.
2. **"Como você evita que a API exploda a memória do Prometheus?"**
   * *Resposta:* Evitamos *labels* de alta cardinalidade: normalizamos rotas não casadas para `"unmatched"`, não colocamos IDs ou renda contínua em *labels* (usamos `Histogram` com buckets fixos) e restringimos os contadores categóricos às 5 variáveis de domínio discreto do contrato.
3. **"O que acontece com o Prometheus/Grafana quando a API estiver no AWS App Runner?"**
   * *Resposta:* O endpoint `/metrics` já vai embarcado na imagem Docker publicada no App Runner. No Cenário 1 aprovado para o TCC, o Prometheus em Docker pode fazer *scrape* remoto via HTTPS nesse endpoint público para demonstração ao vivo (bloco já documentado em `prometheus.yml`); em operação corporativa 24/7, a evolução natural é migrar a coleta para **Amazon Managed Service for Prometheus (AMP) + Amazon Managed Grafana (AMG)**.
