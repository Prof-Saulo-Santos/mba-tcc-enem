"""Instrumentação de observabilidade Prometheus para a API de inferência do ENEM.

Expõe métricas de infraestrutura HTTP (taxa de requisições, latência e rejeições
HTTP 422 contra Data Leakage) e métricas de Machine Learning (tempo puro de
inferência XGBoost, distribuição das notas TARGET_M4 e perfil das features de
entrada para detecção de Prediction Drift e Data Drift).
"""

from typing import Any, Iterable, Sequence

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

from src.api.schemas import CandidatoInput

HTTP_REQUESTS_TOTAL = Counter(
    "enem_api_http_requests_total",
    "Total de requisições HTTP processadas pela API",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "enem_api_http_request_duration_seconds",
    "Latência de ponta a ponta das requisições HTTP (segundos)",
    ["method", "path"],
    buckets=(0.002, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

VALIDATION_ERRORS_TOTAL = Counter(
    "enem_api_validation_errors_total",
    "Total de rejeições HTTP 422 por tipo de violação de contrato Pydantic",
    ["error_type"],
)

MODEL_INFO_GAUGE = Gauge(
    "enem_api_model_info",
    "Indicador de disponibilidade e versão/SHA-256 do artefato carregado (1=pronto, 0=indisponível)",
    ["model_version", "artifact_sha256"],
)

MODEL_INFERENCE_DURATION_SECONDS = Histogram(
    "enem_api_model_inference_duration_seconds",
    "Tempo puro de inferência no estimador XGBRegressor (segundos)",
    ["mode"],
    buckets=(0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

PREDICTIONS_TOTAL = Counter(
    "enem_api_predictions_total",
    "Quantidade acumulada de candidatos escorados",
    ["mode"],
)

PREDICTED_TARGET_M4 = Histogram(
    "enem_api_predicted_target_m4",
    "Distribuição das notas previstas TARGET_M4 na escala TRI (0 a 1000)",
    buckets=(300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 1000),
)

INPUT_RENDA_PER_CAPITA = Histogram(
    "enem_api_input_renda_per_capita",
    "Distribuição da variável RENDA_PER_CAPITA recebida (SM/morador)",
    buckets=(0.0, 0.25, 0.5, 1.0, 1.5, 2.5, 4.0, 6.0, 10.0, 15.0, 25.0),
)

INPUT_CATEGORICAL_TOTAL = Counter(
    "enem_api_input_categorical_total",
    "Contagem das categorias recebidas por feature para monitoramento de Data Drift",
    ["feature", "value"],
)

_CATEGORICAL_FEATURES = ("Q024", "TP_ANO_CONCLUIU", "TP_LINGUA", "TP_SEXO", "Q002")


def set_model_status(model_version: str, artifact_sha256: str, loaded: bool) -> None:
    """Atualiza o Gauge de estado e governança criptográfica do modelo em memória."""
    MODEL_INFO_GAUGE.clear()
    MODEL_INFO_GAUGE.labels(
        model_version=model_version,
        artifact_sha256=artifact_sha256 or "unloaded",
    ).set(1.0 if loaded else 0.0)


def record_http_request(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    """Registra contagem e latência de uma requisição HTTP concluída."""
    HTTP_REQUESTS_TOTAL.labels(
        method=method,
        path=path,
        status_code=str(status_code),
    ).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration_seconds)


def record_validation_error(errors: Sequence[Any]) -> None:
    """Classifica e contabiliza rejeições HTTP 422 (Anti-Leakage vs. domínio/schema)."""
    has_extra_forbidden = any(
        isinstance(err, dict) and err.get("type") == "extra_forbidden" for err in errors
    )
    error_type = "extra_forbidden" if has_extra_forbidden else "domain_or_schema"
    VALIDATION_ERRORS_TOTAL.labels(error_type=error_type).inc()


def record_inference(
    mode: str,
    candidatos: Iterable[CandidatoInput],
    predictions: Iterable[float],
    duration_seconds: float,
) -> None:
    """Registra latência do XGBoost, predições e distribuição das features de entrada."""
    preds_list = list(predictions)
    cands_list = list(candidatos)

    MODEL_INFERENCE_DURATION_SECONDS.labels(mode=mode).observe(duration_seconds)
    PREDICTIONS_TOTAL.labels(mode=mode).inc(len(preds_list))

    for nota in preds_list:
        PREDICTED_TARGET_M4.observe(nota)

    for cand in cands_list:
        INPUT_RENDA_PER_CAPITA.observe(cand.RENDA_PER_CAPITA)
        for feat in _CATEGORICAL_FEATURES:
            INPUT_CATEGORICAL_TOTAL.labels(
                feature=feat,
                value=str(getattr(cand, feat)),
            ).inc()


def render_metrics() -> tuple[bytes, str]:
    """Serializa as métricas no formato de exposição padrão do Prometheus."""
    return generate_latest(), CONTENT_TYPE_LATEST
