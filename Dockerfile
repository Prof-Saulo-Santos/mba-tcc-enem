# ==============================================================================
# Stage 1: Builder (Instalação hermética de dependências de inferência via uv)
# ==============================================================================
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /build

COPY requirements-api.txt .

RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache -r requirements-api.txt

# ==============================================================================
# Stage 2: Runtime (Imagem enxuta e segura para AWS App Runner / ECS)
# ==============================================================================
FROM python:3.13-slim AS runtime

# libgomp1 é obrigatório em imagens Debian slim para execução nativa do XGBoost (OpenMP)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH="/app/models/enem.pkl" \
    MODEL_CARD_PATH="/app/models/enem_model_card.json"

WORKDIR /app

# Copia o ambiente virtual pronto do estágio builder
COPY --from=builder /opt/venv /opt/venv

# Copia apenas o código da API e os artefatos homologados do modelo (1,73 MB)
COPY --chown=appuser:appuser src/__init__.py ./src/__init__.py
COPY --chown=appuser:appuser src/api/ ./src/api/
COPY --chown=appuser:appuser models/enem.pkl ./models/enem.pkl
COPY --chown=appuser:appuser models/enem_model_card.json ./models/enem_model_card.json

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

