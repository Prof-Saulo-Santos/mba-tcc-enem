"""Testes de contrato HTTP e validação de esquemas Pydantic da API FastAPI.

Garante que todos os endpoints respeitem rigorosamente os limites de domínio
estabelecidos em models/enem_model_card.json e bloqueiem payloads inválidos
ou colunas proibidas (ex.: NU_ANO contra Temporal Leakage).
"""

from typing import Any, Dict
from fastapi.testclient import TestClient
import pytest

from src.api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Inicializa o TestClient acionando o lifespan da aplicação FastAPI."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def payload_valido() -> Dict[str, Any]:
    """Retorna um payload canônico válido de candidato do ENEM."""
    return {
        "RENDA_PER_CAPITA": 1.5,
        "Q024": 1,
        "TP_ANO_CONCLUIU": 0,
        "TP_LINGUA": 0,
        "TP_SEXO": 0,
        "Q002": 4,
    }


def test_root_redirects_to_docs(client: TestClient) -> None:
    """Verifica se a rota raiz redireciona para a documentação Swagger (/docs)."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/docs"


def test_health_endpoint(client: TestClient) -> None:
    """Valida o endpoint de liveness/readiness e integridade SHA-256."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["model_version"] == "enem_target_m4_producao:v1"
    assert (
        data["artifact_sha256"]
        == "114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f"
    )


def test_info_endpoint_matches_model_card(client: TestClient) -> None:
    """Valida se os metadados de governança refletem o Model Card oficial."""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["nome_artefato"] == "enem.pkl"
    assert data["modelo_registrado_mlflow"] == "enem_target_m4_producao"
    assert data["mlflow_run_id_campeao"] == "8b4ed2c387044363968b6088078bdf2d"
    assert data["classe_modelo_campeao"] == "XGBRegressor"
    assert data["janela_historica"] == "2014-2023"
    assert data["n_total_censo"] == 37593629
    assert data["n_holdout_cego"] == 7518726
    assert data["features_ordenadas"] == [
        "RENDA_PER_CAPITA",
        "Q024",
        "TP_ANO_CONCLUIU",
        "TP_LINGUA",
        "TP_SEXO",
        "Q002",
    ]
    assert data["metricas_oficiais"]["holdout_estratificado_7_52m"]["r2"] == pytest.approx(
        0.3378, abs=1e-4
    )


def test_predict_single_valid_payload(
    client: TestClient, payload_valido: Dict[str, Any]
) -> None:
    """Testa predição individual com candidato válido."""
    response = client.post("/predict", json=payload_valido)
    assert response.status_code == 200
    data = response.json()
    assert "target_m4" in data
    assert 300.0 <= data["target_m4"] <= 850.0
    assert data["target_m4"] == pytest.approx(547.12, abs=0.05)
    assert data["unidade"] == "pontos_escala_tri_0_a_1000"
    assert data["modelo"] == "enem_target_m4_producao:v1"


def test_predict_single_boundary_values(client: TestClient) -> None:
    """Testa os limites inferiores e superiores exatos permitidos pelo contrato."""
    min_payload = {
        "RENDA_PER_CAPITA": 0.0,
        "Q024": 0,
        "TP_ANO_CONCLUIU": 0,
        "TP_LINGUA": 0,
        "TP_SEXO": 0,
        "Q002": 0,
    }
    max_payload = {
        "RENDA_PER_CAPITA": 25.0,
        "Q024": 3,
        "TP_ANO_CONCLUIU": 9,
        "TP_LINGUA": 1,
        "TP_SEXO": 1,
        "Q002": 7,
    }

    res_min = client.post("/predict", json=min_payload)
    res_max = client.post("/predict", json=max_payload)

    assert res_min.status_code == 200
    assert res_max.status_code == 200
    assert 300.0 <= res_min.json()["target_m4"] <= 850.0
    assert 300.0 <= res_max.json()["target_m4"] <= 850.0


@pytest.mark.parametrize(
    "campo_invalido,valor_invalido",
    [
        ("RENDA_PER_CAPITA", -0.01),
        ("RENDA_PER_CAPITA", 25.01),
        ("Q024", -1),
        ("Q024", 4),
        ("TP_ANO_CONCLUIU", -1),
        ("TP_ANO_CONCLUIU", 10),
        ("TP_LINGUA", -1),
        ("TP_LINGUA", 2),
        ("TP_SEXO", -1),
        ("TP_SEXO", 2),
        ("Q002", -1),
        ("Q002", 8),
    ],
)
def test_predict_rejects_out_of_range_values(
    client: TestClient,
    payload_valido: Dict[str, Any],
    campo_invalido: str,
    valor_invalido: Any,
) -> None:
    """Garante que valores fora do domínio retornem HTTP 422 Unprocessable Entity."""
    payload = dict(payload_valido)
    payload[campo_invalido] = valor_invalido
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_rejects_missing_field(
    client: TestClient, payload_valido: Dict[str, Any]
) -> None:
    """Garante que a omissão de qualquer feature obrigatória retorne HTTP 422."""
    payload = dict(payload_valido)
    del payload["Q002"]
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_rejects_extra_fields_anti_leakage(
    client: TestClient, payload_valido: Dict[str, Any]
) -> None:
    """Garante bloqueio de campos extras não homologados (ex.: NU_ANO ou nota de redação)."""
    payload = dict(payload_valido)
    payload["NU_ANO"] = 2023
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_batch_valid_and_empty(
    client: TestClient, payload_valido: Dict[str, Any]
) -> None:
    """Testa inferência em lote válida e rejeição de lote vazio."""
    batch_payload = {
        "candidatos": [
            payload_valido,
            {
                "RENDA_PER_CAPITA": 0.0,
                "Q024": 0,
                "TP_ANO_CONCLUIU": 2,
                "TP_LINGUA": 1,
                "TP_SEXO": 1,
                "Q002": 1,
            },
            {
                "RENDA_PER_CAPITA": 5.0,
                "Q024": 3,
                "TP_ANO_CONCLUIU": 0,
                "TP_LINGUA": 0,
                "TP_SEXO": 1,
                "Q002": 6,
            },
        ]
    }
    response = client.post("/predict/batch", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_candidatos"] == 3
    assert len(data["predicoes"]) == 3
    assert data["predicoes"] == [547.12, 465.83, 607.9]
    assert data["tempo_inferencia_ms"] >= 0.0

    # Lote vazio deve retornar 422
    empty_response = client.post("/predict/batch", json={"candidatos": []})
    assert empty_response.status_code == 422

