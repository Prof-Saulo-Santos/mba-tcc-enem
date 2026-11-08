"""Pacote de orquestração autônoma da Etapa 3 (Apache Airflow + SBERT + XGBoost + MLflow).

Implementa os 4 estágios modulares da DAG autônoma para processamento de novas
safras do ENEM (2024 com notas / Gatekeeper OOT e 2025 sem notas / Data Drift).
"""

from src.orchestration.step1_ingest_detect import inspect_and_ingest_edition
from src.orchestration.step2_sbert_mapper import run_sbert_schema_mapping
from src.orchestration.step3_select_harmonize import select_harmonize_and_downcast
from src.orchestration.step4_branch_oot_drift import (
    decide_branch_task_id,
    run_batch_inference_and_drift,
    run_oot_gatekeeper_and_retrain,
)

__all__ = [
    "inspect_and_ingest_edition",
    "run_sbert_schema_mapping",
    "select_harmonize_and_downcast",
    "decide_branch_task_id",
    "run_batch_inference_and_drift",
    "run_oot_gatekeeper_and_retrain",
]
