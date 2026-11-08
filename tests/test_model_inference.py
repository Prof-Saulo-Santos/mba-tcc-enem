"""Testes de integração, paridade matemática e regressão do modelo XGBoost.

Verifica se o ModelManager produz saídas idênticas ao estimador puro serializado
em models/enem.pkl, respeita a monotonicidade sociológica esperada (Bourdieu)
e cumpre o SLA de latência em lote.
"""

import time
import joblib
import pandas as pd
import pytest

from src.api.model_loader import ModelManager
from src.api.schemas import CandidatoInput


@pytest.fixture(scope="module")
def manager() -> ModelManager:
    """Retorna a instância Singleton do ModelManager carregada."""
    inst = ModelManager.get_instance()
    if not inst.is_loaded():
        inst.load()
    return inst


def test_artifact_sha256_integrity(manager: ModelManager) -> None:
    """Garante que o hash SHA-256 do binário enem.pkl permanece inalterado."""
    expected_sha256 = (
        "114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f"
    )
    assert manager.sha256 == expected_sha256
    assert manager.sha256 == manager.model_card["sha256_enem_pkl"]


def test_parity_with_raw_xgboost_artifact(manager: ModelManager) -> None:
    """Compara a predição do ModelManager com a chamada direta ao estimador joblib."""
    raw_model = joblib.load(manager.model_path)

    candidato = CandidatoInput(
        RENDA_PER_CAPITA=2.25,
        Q024=2,
        TP_ANO_CONCLUIU=1,
        TP_LINGUA=0,
        TP_SEXO=1,
        Q002=5,
    )

    df_raw = pd.DataFrame(
        [
            {
                "RENDA_PER_CAPITA": 2.25,
                "Q024": 2,
                "TP_ANO_CONCLUIU": 1,
                "TP_LINGUA": 0,
                "TP_SEXO": 1,
                "Q002": 5,
            }
        ]
    ).astype(
        {
            "RENDA_PER_CAPITA": "float32",
            "Q024": "int8",
            "TP_ANO_CONCLUIU": "int8",
            "TP_LINGUA": "int8",
            "TP_SEXO": "int8",
            "Q002": "int8",
        }
    )

    pred_raw = round(float(raw_model.predict(df_raw)[0]), 2)
    pred_manager = manager.predict_single(candidato)

    assert pred_manager == pred_raw


def test_single_vs_batch_consistency(manager: ModelManager) -> None:
    """Garante que a inferência individual e em lote produzam resultados idênticos."""
    candidatos = [
        CandidatoInput(
            RENDA_PER_CAPITA=0.5,
            Q024=0,
            TP_ANO_CONCLUIU=0,
            TP_LINGUA=1,
            TP_SEXO=0,
            Q002=2,
        ),
        CandidatoInput(
            RENDA_PER_CAPITA=1.5,
            Q024=1,
            TP_ANO_CONCLUIU=0,
            TP_LINGUA=0,
            TP_SEXO=0,
            Q002=4,
        ),
        CandidatoInput(
            RENDA_PER_CAPITA=8.0,
            Q024=3,
            TP_ANO_CONCLUIU=0,
            TP_LINGUA=0,
            TP_SEXO=1,
            Q002=7,
        ),
    ]

    preds_single = [manager.predict_single(c) for c in candidatos]
    preds_batch = manager.predict_batch(candidatos)

    assert preds_single == preds_batch


def test_sociological_directionality_bourdieu(manager: ModelManager) -> None:
    """Verifica a coerência sociológica (capital econômico e cultural de Bourdieu)."""
    candidato_vulneravel = CandidatoInput(
        RENDA_PER_CAPITA=0.25,
        Q024=0,
        TP_ANO_CONCLUIU=0,
        TP_LINGUA=1,
        TP_SEXO=0,
        Q002=1,
    )
    candidato_alto_capital = CandidatoInput(
        RENDA_PER_CAPITA=6.0,
        Q024=3,
        TP_ANO_CONCLUIU=0,
        TP_LINGUA=0,
        TP_SEXO=0,
        Q002=7,
    )

    nota_vulneravel = manager.predict_single(candidato_vulneravel)
    nota_alto_capital = manager.predict_single(candidato_alto_capital)

    assert nota_alto_capital > nota_vulneravel
    assert (nota_alto_capital - nota_vulneravel) >= 100.0


def test_batch_inference_latency_sla(manager: ModelManager) -> None:
    """Garante que um lote de 1.000 candidatos seja processado em menos de 500 ms."""
    lote_1k = [
        CandidatoInput(
            RENDA_PER_CAPITA=1.5,
            Q024=1,
            TP_ANO_CONCLUIU=0,
            TP_LINGUA=0,
            TP_SEXO=0,
            Q002=4,
        )
        for _ in range(1000)
    ]

    t0 = time.perf_counter()
    preds = manager.predict_batch(lote_1k)
    dt_ms = (time.perf_counter() - t0) * 1000.0

    assert len(preds) == 1000
    assert dt_ms < 500.0

