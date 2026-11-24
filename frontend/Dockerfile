# Dockerfile isolado para publicação do cliente Streamlit no Hugging Face Spaces (SDK Docker)
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    HOME=/home/user \
    PATH="/home/user/.local/bin:$PATH"

RUN useradd -m -u 1000 user

WORKDIR /app

COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user app.py api_client.py ./
COPY --chown=user:user knowledge_base/ ./knowledge_base/

USER user

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
