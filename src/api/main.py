"""Serviço REST FastAPI para inferência do modelo preditivo do ENEM.

Este serviço encapsula o estimador campeão XGBoost (enem.pkl) e expõe
endpoints para inferência pontual, inferência em lote, auditoria de saúde
e metadados de governança (Model Card).
"""

from contextlib import asynccontextmanager
import time
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from src.api.model_loader import ModelManager
from src.api.schemas import (
    BatchCandidatosInput,
    BatchPredictionOutput,
    CandidatoInput,
    HealthResponse,
    ModelInfoResponse,
    PredictionOutput,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação carregando o modelo no startup."""
    manager = ModelManager.get_instance()
    try:
        manager.load()
    except Exception as exc:
        # Permite que o container inicie mesmo se houver erro temporário,
        # mas sinaliza o erro nos logs
        print(f"[ERRO LIFESPAN] Falha ao carregar o modelo: {exc}")
    yield


app = FastAPI(
    title="ENEM TARGET_M4 Inference API",
    description=(
        "API de produção para previsão de desempenho cognitivo socioeconômico no ENEM "
        "(TARGET_M4 - Média TRI das 4 Provas Objetivas) baseada em XGBoost treinado "
        "com o censo longitudinal de 2014 a 2023 (37,5 milhões de candidatos)."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Redireciona para a documentação interativa Swagger."""
    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Monitoramento"],
    summary="Verificação de integridade e prontidão do serviço",
)
def health_check() -> HealthResponse:
    """Verifica se o serviço está ativo e se o modelo serializado está carregado."""
    manager = ModelManager.get_instance()
    is_ready = manager.is_loaded()
    return HealthResponse(
        status="healthy" if is_ready else "degraded",
        model_loaded=is_ready,
        model_version="enem_target_m4_producao:v1",
        artifact_sha256=manager.sha256,
    )


@app.get(
    "/info",
    response_model=ModelInfoResponse,
    tags=["Governança"],
    summary="Metadados do modelo e métricas oficiais de validação",
)
def get_model_info() -> ModelInfoResponse:
    """Retorna os metadados oficiais do modelo extraídos do Model Card."""
    manager = ModelManager.get_instance()
    if not manager.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O modelo ainda não está disponível na memória.",
        )
    info = manager.get_info()
    return ModelInfoResponse(**info)


@app.post(
    "/predict",
    response_model=PredictionOutput,
    tags=["Inferência"],
    summary="Predição pontual para um único candidato",
)
def predict(candidato: CandidatoInput) -> PredictionOutput:
    """Recebe os 6 atributos socioeconômicos de um estudante e prevê o TARGET_M4."""
    manager = ModelManager.get_instance()
    if not manager.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O modelo preditivo não está carregado.",
        )

    try:
        nota = manager.predict_single(candidato)
        return PredictionOutput(target_m4=nota)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante a inferência: {str(exc)}",
        ) from exc


@app.post(
    "/predict/batch",
    response_model=BatchPredictionOutput,
    tags=["Inferência"],
    summary="Predição vetorial em lote para múltiplos candidatos",
)
def predict_batch(payload: BatchCandidatosInput) -> BatchPredictionOutput:
    """Recebe até 10.000 candidatos e processa a inferência de forma vetorizada."""
    manager = ModelManager.get_instance()
    if not manager.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O modelo preditivo não está carregado.",
        )

    t_inicio = time.perf_counter()
    try:
        predicoes = manager.predict_batch(payload.candidatos)
        t_fim = time.perf_counter()
        tempo_ms = round((t_fim - t_inicio) * 1000.0, 2)

        return BatchPredictionOutput(
            total_candidatos=len(predicoes),
            predicoes=predicoes,
            tempo_inferencia_ms=tempo_ms,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante a inferência em lote: {str(exc)}",
        ) from exc

