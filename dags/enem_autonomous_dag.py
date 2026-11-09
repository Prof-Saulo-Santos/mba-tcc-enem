"""DAG Autônoma do Apache Airflow — Etapa 3 (ENEM 2024/2025).

Orquestra o Plano Pesado Local em 4 estágios:
1. `t1_ingest_detect`: Ingestão e detecção estrutural da safra (2024 ou 2025);
2. `t2_sbert_dictionary_mapper`: Execução do NLP/SBERT no dicionário (.xlsx) ANTES da seleção;
3. `t3_select_harmonize_downcast`: Seleção das 6 features de elite, deflação em SM e Downcasting;
4. `t4_branch_router` (`BranchPythonOperator`):
   - `branch_with_scores_oot_gatekeeper`: Gatekeeper Out-of-Time (`enem.pkl v1`) -> Se aprovado no SLA,
     concatena `2014-2024`, retreina XGBoost (Challenger) e aciona Juiz MLflow (`enem_v2.pkl`);
     se reprovado (ex.: desidentificação LGPD 2024), aciona Circuit Breaker e redireciona para Drift.
   - `branch_without_scores_batch_drift`: Modo Inferência em Lote + Auditoria de Data Drift (PSI/KS).
"""

import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
from typing import Any, Dict

# Garante que a raiz do projeto esteja no PYTHONPATH dentro do container Airflow
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestration import (
    decide_branch_task_id,
    inspect_and_ingest_edition,
    run_batch_inference_and_drift,
    run_oot_gatekeeper_and_retrain,
    run_sbert_schema_mapping,
    select_harmonize_and_downcast,
)


def _task_ingest_detect(**context: Any) -> Dict[str, Any]:
    """Task 1: Inspeciona os arquivos brutos e o dicionário da edição alvo."""
    dag_run = context.get("dag_run")
    conf = (dag_run.conf if dag_run and dag_run.conf else {}) or {}
    year = int(conf.get("year", 2024))
    return inspect_and_ingest_edition(year=year)


def _task_sbert_mapper(**context: Any) -> Dict[str, Any]:
    """Task 2: Executa o pareamento semântico via NLP/SBERT ANTES da seleção colunar."""
    ti = context["ti"]
    ingest_report = ti.xcom_pull(task_ids="t1_ingest_detect")
    dag_run = context.get("dag_run")
    conf = (dag_run.conf if dag_run and dag_run.conf else {}) or {}
    use_live_sbert = bool(conf.get("use_live_sbert", True))
    return run_sbert_schema_mapping(
        ingest_report=ingest_report, use_live_sbert=use_live_sbert
    )


def _task_select_harmonize_downcast(**context: Any) -> Dict[str, Any]:
    """Task 3: Seleciona colunas mapeadas pelo SBERT, harmoniza em SM e aplica Downcasting."""
    ti = context["ti"]
    ingest_report = ti.xcom_pull(task_ids="t1_ingest_detect")
    schema_report = ti.xcom_pull(task_ids="t2_sbert_dictionary_mapper")
    dag_run = context.get("dag_run")
    conf = (dag_run.conf if dag_run and dag_run.conf else {}) or {}
    max_rows = conf.get("max_rows", 100000)
    return select_harmonize_and_downcast(
        ingest_report=ingest_report,
        schema_report=schema_report,
        max_rows=int(max_rows) if max_rows is not None else None,
    )


def _task_branch_router(**context: Any) -> str:
    """Task 4 (BranchPythonOperator): Decide o ramo de execução conforme presença de notas."""
    ti = context["ti"]
    etl_report = ti.xcom_pull(task_ids="t3_select_harmonize_downcast")
    return decide_branch_task_id(etl_report)


def _task_with_scores_oot_gatekeeper(**context: Any) -> Dict[str, Any]:
    """Ramo A (Com Notas): Gatekeeper OOT -> Retreino XGBoost + Juiz MLflow (ou Circuit Breaker)."""
    ti = context["ti"]
    etl_report = ti.xcom_pull(task_ids="t3_select_harmonize_downcast")
    return run_oot_gatekeeper_and_retrain(etl_report=etl_report, log_mlflow=True)


def _task_without_scores_batch_drift(**context: Any) -> Dict[str, Any]:
    """Ramo B (Sem Notas): Inferência Vetorial em Lote + Auditoria de Data Drift (PSI e KS)."""
    ti = context["ti"]
    etl_report = ti.xcom_pull(task_ids="t3_select_harmonize_downcast")
    return run_batch_inference_and_drift(etl_report=etl_report, log_mlflow=True)


def execute_dag_locally(
    year: int = 2024,
    max_rows: int = 50000,
    use_live_sbert: bool = True,
) -> Dict[str, Any]:
    """Executa o grafo completo da DAG de forma síncrona (para CLI, Docker ou testes E2E)."""
    print(f"\n[DAG START] Iniciando execução autônoma para a safra ENEM {year}...")

    t1_out = inspect_and_ingest_edition(year=year)
    print(
        f"[Task 1 - Ingestão] Layout={t1_out['layout_type']} | "
        f"has_scores={t1_out['has_scores']} | "
        f"positional_match_rate={t1_out['positional_match_rate']}"
    )

    t2_out = run_sbert_schema_mapping(t1_out, use_live_sbert=use_live_sbert)
    print(
        f"[Task 2 - NLP/SBERT] Modo={t2_out['sbert_mode']} | "
        f"Drifts detectados={t2_out['drift_count']} "
        f"(Q006->{t2_out['column_mapping'].get('Q006')}, Q024->{t2_out['column_mapping'].get('Q024')})"
    )

    t3_out = select_harmonize_and_downcast(
        t1_out, t2_out, max_rows=max_rows
    )
    print(
        f"[Task 3 - Seleção & Downcasting] Retidos={t3_out['rows_retained']} | "
        f"Bytes/linha={t3_out['bytes_per_row_ram']} B | "
        f"RAM={t3_out['ram_usage_mb']} MB"
    )

    chosen_branch = decide_branch_task_id(t3_out)
    print(f"[Task 4 - BranchRouter] Rota selecionada: {chosen_branch}")

    if chosen_branch == "branch_with_scores_oot_gatekeeper":
        t4_out = run_oot_gatekeeper_and_retrain(t3_out, log_mlflow=True)
    else:
        t4_out = run_batch_inference_and_drift(t3_out, log_mlflow=True)

    print(f"[DAG COMPLETE] Safra {year} finalizada no ramo: {t4_out['execution_branch']}")
    return {
        "year": year,
        "t1_ingest_detect": t1_out,
        "t2_sbert_dictionary_mapper": t2_out,
        "t3_select_harmonize_downcast": t3_out,
        "chosen_branch": chosen_branch,
        "t4_result": t4_out,
    }


# ==============================================================================
# Definição Nativa do Grafo no Apache Airflow (quando importado pelo Scheduler)
# ==============================================================================
try:
    from airflow import DAG
    from airflow.operators.empty import EmptyOperator
    from airflow.operators.python import BranchPythonOperator, PythonOperator
    from airflow.utils.trigger_rule import TriggerRule

    default_args = {
        "owner": "saulo-santos-mba-mlops",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    }

    with DAG(
        dag_id="enem_autonomous_pipeline_2024_2025",
        description=(
            "DAG Autônoma Etapa 3: (1) Ingestão -> (2) NLP/SBERT no Dicionário ANTES da Seleção -> "
            "(3) Seleção + Harmonização + Downcasting -> (4) Bifurcação OOT/Retreino (2024) vs. Drift (2025)"
        ),
        default_args=default_args,
        start_date=datetime(2026, 1, 1),
        schedule=None,
        catchup=False,
        tags=["enem", "mlops", "sbert", "xgboost", "mlflow", "etapa3"],
    ) as dag:
        t1_ingest = PythonOperator(
            task_id="t1_ingest_detect",
            python_callable=_task_ingest_detect,
        )

        t2_sbert = PythonOperator(
            task_id="t2_sbert_dictionary_mapper",
            python_callable=_task_sbert_mapper,
        )

        t3_etl = PythonOperator(
            task_id="t3_select_harmonize_downcast",
            python_callable=_task_select_harmonize_downcast,
        )

        t4_router = BranchPythonOperator(
            task_id="t4_branch_router",
            python_callable=_task_branch_router,
        )

        b_oot = PythonOperator(
            task_id="branch_with_scores_oot_gatekeeper",
            python_callable=_task_with_scores_oot_gatekeeper,
        )

        b_drift = PythonOperator(
            task_id="branch_without_scores_batch_drift",
            python_callable=_task_without_scores_batch_drift,
        )

        t5_complete = EmptyOperator(
            task_id="t5_pipeline_audit_complete",
            trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        )

        t1_ingest >> t2_sbert >> t3_etl >> t4_router >> [b_oot, b_drift] >> t5_complete

except ImportError:
    # Permite que o módulo seja executado via CLI / Pytest mesmo fora da imagem do Airflow
    dag = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Executor da DAG Autônoma ENEM Etapa 3 (2024 / 2025)"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2024,
        help="Ano da safra a processar (ex.: 2024, 2025, 2023)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=50000,
        help="Limite de linhas a ler do CSV bruto (use 0 para censo completo)",
    )
    parser.add_argument(
        "--no-live-sbert",
        action="store_true",
        help="Usa apenas o cache do contrato sem carregar o modelo PyTorch SBERT em memória",
    )
    args = parser.parse_args()

    res = execute_dag_locally(
        year=args.year,
        max_rows=None if args.max_rows == 0 else args.max_rows,
        use_live_sbert=not args.no_live_sbert,
    )
    print(json.dumps(res["t4_result"], indent=2, ensure_ascii=False))

