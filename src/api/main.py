"""Serviço REST FastAPI para inferência do modelo preditivo do ENEM.

Este serviço encapsula o estimador campeão XGBoost (enem.pkl) e expõe
endpoints para inferência pontual, inferência em lote, auditoria de saúde,
metadados de governança (Model Card) e métricas Prometheus (/metrics).
"""

from contextlib import asynccontextmanager
import time
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse

from src.api.metrics import (
    record_http_request,
    record_inference,
    record_validation_error,
    render_metrics,
    set_model_status,
)
from src.api.model_loader import ModelManager
from src.api.schemas import (
    BatchCandidatosInput,
    BatchPredictionOutput,
    CandidatoInput,
    HealthResponse,
    ModelInfoResponse,
    PredictionOutput,
)

MODEL_VERSION_TAG = "enem_target_m4_producao:v1"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação carregando o modelo no startup."""
    manager = ModelManager.get_instance()
    try:
        manager.load()
        set_model_status(
            model_version=MODEL_VERSION_TAG,
            artifact_sha256=manager.sha256,
            loaded=manager.is_loaded(),
        )
    except Exception as exc:
        # Permite que o container inicie mesmo se houver erro temporário,
        # mas sinaliza o erro nos logs e nas métricas Prometheus
        set_model_status(
            model_version=MODEL_VERSION_TAG,
            artifact_sha256="",
            loaded=False,
        )
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


@app.middleware("http")
async def prometheus_http_middleware(request: Request, call_next) -> Response:
    """Mede latência e contabiliza requisições HTTP sem explosão de cardinalidade."""
    t_inicio = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duracao = time.perf_counter() - t_inicio
        route = request.scope.get("route")
        route_path = route.path if route is not None else "unmatched"
        if route_path != "/metrics":
            record_http_request(
                method=request.method,
                path=route_path,
                status_code=status_code,
                duration_seconds=duracao,
            )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    """Contabiliza bloqueios HTTP 422 (Anti-Leakage vs. domínio) preservando o payload padrão."""
    record_validation_error(exc.errors())
    return await request_validation_exception_handler(request, exc)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Redireciona para a documentação interativa Swagger."""
    return RedirectResponse(url="/docs")


@app.get(
    "/metrics",
    tags=["Monitoramento"],
    summary="Exposição de métricas no formato Prometheus",
)
def metrics() -> Response:
    """Retorna métricas HTTP e de Machine Learning para coleta pelo Prometheus."""
    payload, content_type = render_metrics()
    return Response(content=payload, media_type=content_type)


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
        model_version=MODEL_VERSION_TAG,
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

    t_inicio = time.perf_counter()
    try:
        nota = manager.predict_single(candidato)
        duracao = time.perf_counter() - t_inicio
        record_inference(
            mode="single",
            candidatos=[candidato],
            predictions=[nota],
            duration_seconds=duracao,
        )
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
        duracao = time.perf_counter() - t_inicio
        tempo_ms = round(duracao * 1000.0, 2)
        record_inference(
            mode="batch",
            candidatos=payload.candidatos,
            predictions=predicoes,
            duration_seconds=duracao,
        )

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
