"""Suíte de testes automatizados (Pytest) para os 4 estágios da Etapa 3 (`src/orchestration/`).

Valida:
1. Estágio 1 (Ingestão e Detecção Estrutural) para 2024 (bipartido) e 2025 (sem notas);
2. Estágio 2 (NLP/SBERT no dicionário ANTES da seleção), comprovando a descoberta
   automática do drift semântico (Q006 -> Q007 e Q024 -> Q021 em 2024 e 2025);
3. Estágio 3 (Seleção, Harmonização em SM e Downcasting para 15/11 bytes por linha);
4. Estágio 4 (Bifurcação Automática):
   - Ramo 2024 bruto: Acionamento do Circuit Breaker no Gatekeeper OOT (proteção LGPD) + Fallback Drift;
   - Ramo 2025 sem notas: Inferência Vetorial em Lote + Auditoria de Data Drift (PSI e KS) no MLflow;
   - Ramo OOT Íntegro (2023 vs. 2014-2022): Aprovação no SLA do Gatekeeper OOT + Concatenação +
     Retreino do XGBoost Challenger + Julgamento Champion vs. Challenger no MLflow (`enem_v2.pkl`).
"""

from pathlib import Path
import pandas as pd
import pytest

from dags.enem_autonomous_dag import execute_dag_locally
from src.orchestration import (
    decide_branch_task_id,
    inspect_and_ingest_edition,
    run_batch_inference_and_drift,
    run_oot_gatekeeper_and_retrain,
    run_sbert_schema_mapping,
    select_harmonize_and_downcast,
)


def test_etapa3_full_pipeline_2024_circuit_breaker() -> None:
    """Testa os 4 estágios sobre os dados reais de 2024 (SBERT + Gatekeeper Circuit Breaker)."""
    # 1. Ingestão
    ingest_2024 = inspect_and_ingest_edition(year=2024, sample_check_rows=2000)
    assert ingest_2024["year"] == 2024
    assert ingest_2024["layout_type"] == "BIPARTIDO_PARTICIPANTES_RESULTADOS"
    assert ingest_2024["has_scores"] is True
    assert ingest_2024["positional_alignment_valid"] is False

    # 2. NLP/SBERT no dicionário ANTES da seleção
    schema_2024 = run_sbert_schema_mapping(ingest_2024, use_live_sbert=False)
    col_map = schema_2024["column_mapping"]
    assert col_map["Q006"] == "Q007"
    assert col_map["Q024"] == "Q021"
    assert schema_2024["drift_count"] >= 2

    # 3. Seleção, Harmonização e Downcasting (amostra de 20.000 linhas para rapidez)
    etl_2024 = select_harmonize_and_downcast(
        ingest_2024, schema_2024, max_rows=20000
    )
    assert etl_2024["rows_retained"] > 10000
    assert etl_2024["bytes_per_row_ram"] == 15
    assert etl_2024["has_scores"] is True

    # 4. Bifurcação e Gatekeeper OOT
    branch_id = decide_branch_task_id(etl_2024)
    assert branch_id == "branch_with_scores_oot_gatekeeper"

    oot_res = run_oot_gatekeeper_and_retrain(etl_2024, log_mlflow=True)
    assert oot_res["gatekeeper_passed"] is False
    assert (
        oot_res["execution_branch"] == "OOT_GATEKEEPER_CIRCUIT_BREAKER_FALLBACK"
    )
    assert "fallback_drift_report" in oot_res
    assert oot_res["fallback_drift_report"]["prediction_summary"]["n_scored"] == etl_2024["rows_retained"]


def test_etapa3_full_pipeline_2025_batch_inference_and_drift() -> None:
    """Testa os 4 estágios sobre os dados reais de 2025 (Sem Notas -> Batch Inference + PSI/KS)."""
    # 1. Ingestão
    ingest_2025 = inspect_and_ingest_edition(year=2025, sample_check_rows=2000)
    assert ingest_2025["year"] == 2025
    assert ingest_2025["layout_type"] == "SOMENTE_PARTICIPANTES_SEM_NOTAS"
    assert ingest_2025["has_scores"] is False

    # 2. NLP/SBERT no dicionário ANTES da seleção
    schema_2025 = run_sbert_schema_mapping(ingest_2025, use_live_sbert=False)
    col_map = schema_2025["column_mapping"]
    assert col_map["Q006"] == "Q007"
    assert col_map["Q024"] == "Q021"

    # 3. Seleção, Harmonização e Downcasting
    etl_2025 = select_harmonize_and_downcast(
        ingest_2025, schema_2025, max_rows=20000
    )
    assert etl_2025["rows_retained"] > 15000
    assert etl_2025["bytes_per_row_ram"] == 11
    assert etl_2025["has_scores"] is False
    assert etl_2025["tp_lingua_imputed"] is True

    # 4. Bifurcação para Modo Inferência em Lote + Data Drift
    branch_id = decide_branch_task_id(etl_2025)
    assert branch_id == "branch_without_scores_batch_drift"

    drift_res = run_batch_inference_and_drift(etl_2025, log_mlflow=True)
    assert drift_res["execution_branch"] == "BATCH_INFERENCE_AND_DATA_DRIFT"
    assert 450.0 <= drift_res["prediction_summary"]["pred_mean"] <= 560.0
    assert "RENDA_PER_CAPITA" in drift_res["feature_drift"]
    assert drift_res["max_psi"] >= 0.0


def test_etapa3_oot_approved_retrain_champion_vs_challenger() -> None:
    """Testa o caminho completo de aprovação no Gatekeeper OOT, Retreino e Juiz MLflow (enem_v2.pkl)."""
    project_root = Path(__file__).resolve().parent.parent
    slim_2023 = (
        project_root
        / "data"
        / "processed"
        / "safras_consolidacao"
        / "enem_2023_slim.parquet"
    )
    df_2023_sample = pd.read_parquet(slim_2023).sample(n=30000, random_state=42)
    out_dir = project_root / "data" / "processed" / "safras_etapa3"
    out_dir.mkdir(parents=True, exist_ok=True)
    sample_parquet = out_dir / "enem_2023_oot_aligned_test.parquet"
    df_2023_sample.to_parquet(sample_parquet, compression="snappy", index=False)

    etl_oot_valid = {
        "year": 2023,
        "parquet_path": str(sample_parquet),
        "rows_retained": len(df_2023_sample),
        "bytes_per_row_ram": 15,
        "has_scores": True,
        "positional_alignment_valid": True,
        "positional_match_rate": 1.0,
    }

    retrain_res = run_oot_gatekeeper_and_retrain(
        etl_oot_valid,
        sla_min_r2=0.28,
        sla_max_rmse=72.0,
        retrain_historical_sample=120000,
        log_mlflow=True,
    )

    assert retrain_res["gatekeeper_passed"] is True
    assert (
        retrain_res["execution_branch"]
        == "OOT_APPROVED_RETRAIN_CHAMPION_VS_CHALLENGER"
    )
    assert retrain_res["oot_metrics_v1"]["r2"] >= 0.30
    assert Path(retrain_res["artifact_v2_path"]).exists()


def test_dag_executor_e2e_2024_and_2025() -> None:
    """Testa a execução ponta a ponta da DAG autônoma (`dags/enem_autonomous_dag.py`)."""
    dag_2024 = execute_dag_locally(year=2024, max_rows=10000, use_live_sbert=False)
    assert dag_2024["chosen_branch"] == "branch_with_scores_oot_gatekeeper"
    assert (
        dag_2024["t4_result"]["execution_branch"]
        == "OOT_GATEKEEPER_CIRCUIT_BREAKER_FALLBACK"
    )

    dag_2025 = execute_dag_locally(year=2025, max_rows=10000, use_live_sbert=False)
    assert dag_2025["chosen_branch"] == "branch_without_scores_batch_drift"
    assert (
        dag_2025["t4_result"]["execution_branch"]
        == "BATCH_INFERENCE_AND_DATA_DRIFT"
    )


