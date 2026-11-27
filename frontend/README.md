---
title: ENEM TARGET_M4 — Cliente Simulador
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 🎓 Front-end Isolado (`frontend/`) — Cliente Streamlit da API ENEM `TARGET_M4`

Aplicação cliente leve em **Streamlit** (empacotada via **Docker SDK** na porta `7860` para **Hugging Face Spaces**) e construída de forma **100% desacoplada** da esteira de MLOps (`src/api/`, `tests/`, `Dockerfile` raiz e `.github/workflows/deploy.yml`).

## Estrutura

* `Dockerfile` — Imagem Docker dedicada para o Hugging Face Spaces (`python:3.13-slim`, usuário não-root UID `1000`, Streamlit na porta `7860`).
* `app.py` — Interface web Streamlit (Botão 1 individual, Botão 2 lote aleatório `1..10.000`, aba de Governança `/health` & `/info` e link fixo para o Space RAG/LLM `Prof-Saulo-Santos/agente-tcc-enem-gemini`).
* `api_client.py` — Cliente HTTP (`httpx`) e gerador sintético compatível com o contrato Pydantic da API.
* `requirements.txt` — Dependências enxutas exclusivas do front-end (`streamlit`, `httpx`, `pandas`, `python-dotenv`).
* `knowledge_base/tcc_enem_completo.md` — Dossiê técnico completo do TCC consolidando todos os notebooks (`01` a `06`), métricas oficiais, decisões metodológicas e arquitetura MLOps (`Fases 1 a 4`), pronto para alimentar seu Space RAG.
* `.env.example` — Variável de configuração local (`API_BASE_URL`).

## Execução Local em Ambiente Virtual Isolado (`frontend/.venv`)

```bash
cd frontend
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env   # ajuste API_BASE_URL se desejar
streamlit run app.py
```

*(Quando rodar localmente contra `http://localhost:8000`, garanta que a API esteja ativa via `uvicorn` ou `docker compose --profile monitoring up -d` para acompanhar as métricas no Prometheus `:9090` e Grafana `:3000`.)*
