---
title: ENEM TARGET_M4 — Cliente Simulador
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: streamlit
app_file: app.py
pinned: false
---

# 🎓 Front-end Isolado (`frontend/`) — Cliente Streamlit da API ENEM `TARGET_M4`

Aplicação cliente leve em **Streamlit** construída de forma **100% desacoplada** da esteira de MLOps (`src/api/`, `tests/`, `Dockerfile`, `.github/workflows/deploy.yml`).

## Funcionalidades

* **Botão 1 — Consultar 1 Aluno (`POST /predict`):** formulário em português mapeando as 6 variáveis do *Esquadrão de Elite* (`RENDA_PER_CAPITA`, `Q024`, `TP_ANO_CONCLUIU`, `TP_LINGUA`, `TP_SEXO`, `Q002`) para os códigos exatos do contrato Pydantic da API.
* **Botão 2 — Gerar e Consultar `N` Alunos Aleatórios (`POST /predict/batch`):** gera de `1` a `10.000` candidatos sintéticos válidos, consulta o endpoint vetorial em lote, mostra estatísticas/distribuição das notas `TARGET_M4` e gera tráfego real para o **Prometheus + Grafana**.
* **Monitor de Saúde & Governança (`GET /health` & `GET /info`):** exibe ao vivo o hash `SHA-256`, `mlflow_run_id_campeao` e métricas oficiais da API conectada.
* **Acesso ao RAG/LLM no Hugging Face (Link Externo):** botão de acesso direto para o seu Space RAG/LLM publicado no Hugging Face + download do dossiê [`knowledge_base/tcc_enem_completo.md`](knowledge_base/tcc_enem_completo.md).

## Execução Local em Ambiente Virtual Isolado (`frontend/.venv`)

```bash
cd frontend
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env   # ajuste API_BASE_URL e HF_RAG_SPACE_URL se desejar
streamlit run app.py
```

*(Quando rodar localmente contra `http://localhost:8000`, garanta que a API esteja ativa via `uvicorn` ou `docker compose --profile monitoring up -d` para acompanhar as métricas no Prometheus `:9090` e Grafana `:3000`.)*
