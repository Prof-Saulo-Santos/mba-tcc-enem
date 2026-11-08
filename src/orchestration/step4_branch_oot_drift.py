"""Estágio 4 da DAG Autônoma: Bifurcação Automática (Gatekeeper OOT + Retreino vs. Drift).

Implementa a inteligência decisória de pós-processamento da Etapa 3:
- Ramo A (Com Notas: ex. 2024 ou Backtest OOT):
  1. Avalia o modelo atual `enem.pkl v1` como Gatekeeper Out-of-Time (SLA de R², RMSE e Alinhamento 1:1);
  2. Se reprovado (ex.: base 2024 desidentificada/embaralhada pelo INEP via LGPD), aciona o Circuit Breaker
     bloqueando Data Poisoning da base histórica e redireciona para Inferência em Lote + Data Drift de X;
  3. Se aprovado no SLA, concatena a safra à série histórica, retreina o XGBoost (Challenger) e utiliza o
     MLflow como árbitro Champion (v1) vs. Challenger (v2) para gerar `models/enem_v2.pkl`.
- Ramo B (Sem Notas: ex. 2025):
  1. Executa Inferência Vetorial em Lote (Batch Scoring) prevendo `TARGET_M4`;
  2. Calcula o Data Drift de X via Population Stability Index (PSI) e Kolmogorov-Smirnov (KS) contra a
     referência histórica, registrando o laudo completo no MLflow.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import mlflow
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

FEATURES_ELITE: List[str] = [
    "RENDA_PER_CAPITA",
    "Q024",
    "TP_ANO_CONCLUIU",
    "TP_LINGUA",
    "TP_SEXO",
    "Q002",
]


def decide_branch_task_id(etl_report: Dict[str, Any]) -> str:
    """Função decisora para o BranchPythonOperator do Apache Airflow."""
    if etl_report.get("has_scores", False):
        return "branch_with_scores_oot_gatekeeper"
    return "branch_without_scores_batch_drift"


def compute_psi(
    ref: np.ndarray,
    cur: np.ndarray,
    is_continuous: bool = False,
    n_bins: int = 10,
) -> float:
    """Calcula o Population Stability Index (PSI) entre a distribuição de referência e a atual."""
    eps = 1e-4
    if is_continuous:
        quantiles = np.linspace(0, 100, n_bins + 1)
        bins = np.unique(np.percentile(ref, quantiles))
        if len(bins) < 2:
            bins = np.array([0.0, 25.0])
        bins[0] = -np.inf
        bins[-1] = np.inf
        ref_counts, _ = np.histogram(ref, bins=bins)
        cur_counts, _ = np.histogram(cur, bins=bins)
    else:
        categories = np.union1d(np.unique(ref), np.unique(cur))
        ref_counts = np.array([np.sum(ref == c) for c in categories], dtype=np.float64)
        cur_counts = np.array([np.sum(cur == c) for c in categories], dtype=np.float64)

    p_ref = np.clip(ref_counts / max(len(ref), 1), eps, 1.0)
    p_cur = np.clip(cur_counts / max(len(cur), 1), eps, 1.0)

    psi_value = float(np.sum((p_cur - p_ref) * np.log(p_cur / p_ref)))
    return round(psi_value, 5)


def classify_psi_status(psi: float) -> str:
    """Classifica a severidade do Data Drift segundo os limiares clássicos de MLOps."""
    if psi < 0.10:
        return "ESTAVEL (PSI < 0.10)"
    if psi < 0.25:
        return "ATENCAO_MODERADO (0.10 <= PSI < 0.25)"
    return "DRIFT_SEVERO (PSI >= 0.25)"


def _load_reference_distribution(
    project_root: Path,
    max_rows: int = 200000,
    before_year: Optional[int] = None,
) -> pd.DataFrame:
    """Carrega amostra de referência da Década de Ouro para cálculo de PSI/KS ou Retreino."""
    safras_dir = project_root / "data" / "processed" / "safras_consolidacao"
    if before_year is not None and safras_dir.exists():
        # Carrega uma amostra estratificada das safras anteriores a `before_year` (ex.: 2014 a 2022)
        slim_files = sorted(safras_dir.glob("enem_*_slim.parquet"))
        dfs = []
        rows_per_year = max(max_rows // 9, 10000)
        for sf in slim_files:
            yr_str = sf.name.split("_")[1]
            if yr_str.isdigit() and int(yr_str) < before_year:
                df_y = pd.read_parquet(sf)
                if len(df_y) > rows_per_year:
                    df_y = df_y.sample(n=rows_per_year, random_state=42)
                dfs.append(df_y)
        if dfs:
            return pd.concat(dfs, ignore_index=True)

    slim_2023 = safras_dir / "enem_2023_slim.parquet"
    consolidado = (
        project_root / "data" / "processed" / "enem_2014_2023_consolidado.parquet"
    )
    target_file = slim_2023 if slim_2023.exists() else consolidado
    df_ref = pd.read_parquet(target_file)
    if before_year is not None and "NU_ANO" in df_ref.columns:
        df_ref = df_ref[df_ref["NU_ANO"] < before_year]
    if len(df_ref) > max_rows:
        df_ref = df_ref.sample(n=max_rows, random_state=42).reset_index(drop=True)
    return df_ref


def run_batch_inference_and_drift(
    etl_report: Dict[str, Any],
    log_mlflow: bool = True,
    trigger_reason: str = "EDITION_WITHOUT_SCORES",
) -> Dict[str, Any]:
    """Executa Inferência Vetorial em Lote + Auditoria de Data Drift de X (PSI e KS)."""
    project_root = Path(__file__).resolve().parent.parent.parent
    year = int(etl_report["year"])
    parquet_path = Path(etl_report["parquet_path"])
    model_path = project_root / "models" / "enem.pkl"

    df_cur = pd.read_parquet(parquet_path)
    model_v1 = joblib.load(model_path)

    X_cur = df_cur[FEATURES_ELITE]
    preds = model_v1.predict(X_cur)
    df_cur["PRED_TARGET_M4"] = np.round(preds, 2).astype("float32")

    pred_path = parquet_path.parent / f"enem_{year}_predicoes_batch.parquet"
    df_cur.to_parquet(pred_path, compression="snappy", index=False)

    # Auditoria de Data Drift (PSI + KS) contra a referência histórica
    df_ref = _load_reference_distribution(project_root)
    drift_metrics: Dict[str, Any] = {}
    max_psi = 0.0

    for feat in FEATURES_ELITE:
        is_cont = feat == "RENDA_PER_CAPITA"
        ref_vals = df_ref[feat].to_numpy()
        cur_vals = df_cur[feat].to_numpy()

        psi_val = compute_psi(ref_vals, cur_vals, is_continuous=is_cont)
        ks_stat, ks_pval = ks_2samp(ref_vals, cur_vals)
        max_psi = max(max_psi, psi_val)

        drift_metrics[feat] = {
            "psi": psi_val,
            "status_psi": classify_psi_status(psi_val),
            "ks_statistic": round(float(ks_stat), 4),
            "ks_pvalue": round(float(ks_pval), 6),
            "ref_mean": round(float(np.mean(ref_vals)), 4),
            "cur_mean": round(float(np.mean(cur_vals)), 4),
        }

    pred_summary = {
        "n_scored": len(df_cur),
        "pred_mean": round(float(np.mean(preds)), 2),
        "pred_std": round(float(np.std(preds)), 2),
        "pred_p10": round(float(np.percentile(preds, 10)), 2),
        "pred_p50": round(float(np.percentile(preds, 50)), 2),
        "pred_p90": round(float(np.percentile(preds, 90)), 2),
    }

    report = {
        "year": year,
        "execution_branch": "BATCH_INFERENCE_AND_DATA_DRIFT",
        "trigger_reason": trigger_reason,
        "predictions_parquet": str(pred_path),
        "prediction_summary": pred_summary,
        "max_psi": max_psi,
        "overall_drift_status": classify_psi_status(max_psi),
        "feature_drift": drift_metrics,
    }

    report_path = parquet_path.parent / f"relatorio_etapa3_{year}_drift.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    if log_mlflow:
        mlflow_db = project_root / "mlflow.db"
        mlflow.set_tracking_uri(f"sqlite:///{mlflow_db}")
        mlflow.set_experiment("tcc_enem_etapa3_airflow_autonomo")
        with mlflow.start_run(run_name=f"etapa3_batch_drift_{year}"):
            mlflow.log_param("year", year)
            mlflow.log_param("branch", "BATCH_INFERENCE_AND_DATA_DRIFT")
            mlflow.log_param("trigger_reason", trigger_reason)
            mlflow.log_metric("n_scored", len(df_cur))
            mlflow.log_metric("pred_target_m4_mean", pred_summary["pred_mean"])
            mlflow.log_metric("pred_target_m4_std", pred_summary["pred_std"])
            mlflow.log_metric("max_psi", max_psi)
            for feat, m in drift_metrics.items():
                mlflow.log_metric(f"psi_{feat}", m["psi"])
                mlflow.log_metric(f"ks_{feat}", m["ks_statistic"])
            mlflow.log_artifact(str(report_path))

    return report


def run_oot_gatekeeper_and_retrain(
    etl_report: Dict[str, Any],
    sla_min_r2: float = 0.28,
    sla_max_rmse: float = 72.0,
    retrain_historical_sample: int = 300000,
    log_mlflow: bool = True,
) -> Dict[str, Any]:
    """Executa o Gatekeeper Out-of-Time e, se aprovado no SLA, retreina e julga Champion vs. Challenger."""
    project_root = Path(__file__).resolve().parent.parent.parent
    year = int(etl_report["year"])
    parquet_path = Path(etl_report["parquet_path"])
    model_v1_path = project_root / "models" / "enem.pkl"

    df_new = pd.read_parquet(parquet_path)
    model_v1 = joblib.load(model_v1_path)

    X_oot = df_new[FEATURES_ELITE]
    y_oot = df_new["TARGET_M4"].to_numpy()
    preds_v1_oot = model_v1.predict(X_oot)

    r2_oot = round(float(r2_score(y_oot, preds_v1_oot)), 5)
    rmse_oot = round(float(np.sqrt(mean_squared_error(y_oot, preds_v1_oot))), 4)
    mae_oot = round(float(mean_absolute_error(y_oot, preds_v1_oot)), 4)

    alignment_ok = bool(etl_report.get("positional_alignment_valid", True))
    sla_metrics_ok = (r2_oot >= sla_min_r2) and (rmse_oot <= sla_max_rmse)
    gatekeeper_passed = alignment_ok and sla_metrics_ok

    if not gatekeeper_passed:
        # CIRCUIT BREAKER ACIONADO: Bloqueia contaminação da base histórica e desvia para Batch + Drift
        reason = (
            f"CIRCUIT_BREAKER_OOT_REJECTED (alignment_ok={alignment_ok}, "
            f"positional_match_rate={etl_report.get('positional_match_rate')}, "
            f"r2_oot={r2_oot:.4f} < {sla_min_r2})"
        )
        drift_fallback = run_batch_inference_and_drift(
            etl_report=etl_report,
            log_mlflow=log_mlflow,
            trigger_reason=reason,
        )
        return {
            "year": year,
            "execution_branch": "OOT_GATEKEEPER_CIRCUIT_BREAKER_FALLBACK",
            "gatekeeper_passed": False,
            "positional_alignment_valid": alignment_ok,
            "positional_match_rate": etl_report.get("positional_match_rate"),
            "oot_metrics_v1": {
                "r2": r2_oot,
                "rmse": rmse_oot,
                "mae": mae_oot,
            },
            "circuit_breaker_action": "BLOCKED_RETRAIN_AND_ROUTED_TO_BATCH_DRIFT",
            "fallback_drift_report": drift_fallback,
        }

    # ==========================================================================
    # GATEKEEPER APROVADO NO SLA: Concatenação Histórica + Retreino + Juiz MLflow
    # ==========================================================================
    df_hist = _load_reference_distribution(
        project_root, max_rows=retrain_historical_sample, before_year=year
    )

    cols_treino = ["NU_ANO"] + FEATURES_ELITE + ["TARGET_M4"]
    df_concat = pd.concat(
        [df_hist[cols_treino], df_new[cols_treino]], ignore_index=True
    )

    # Split estratificado em Treino, Early Stopping e Holdout de Julgamento Champion vs Challenger
    df_dev, df_holdout = train_test_split(
        df_concat, test_size=0.20, random_state=42, stratify=df_concat["NU_ANO"]
    )
    df_fit, df_es = train_test_split(
        df_dev, test_size=0.10, random_state=42, stratify=df_dev["NU_ANO"]
    )

    challenger_v2 = XGBRegressor(
        n_estimators=700,
        max_depth=5,
        learning_rate=0.1,
        min_child_weight=30,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        tree_method="hist",
        early_stopping_rounds=30,
        random_state=42,
        n_jobs=-1,
    )

    challenger_v2.fit(
        df_fit[FEATURES_ELITE],
        df_fit["TARGET_M4"],
        eval_set=[(df_es[FEATURES_ELITE], df_es["TARGET_M4"])],
        verbose=False,
    )

    # Avaliação no Holdout Multi-Ano + Safra Nova (Juiz Champion v1 vs Challenger v2)
    X_hold = df_holdout[FEATURES_ELITE]
    y_hold = df_holdout["TARGET_M4"].to_numpy()

    preds_champ = model_v1.predict(X_hold)
    preds_chall = challenger_v2.predict(X_hold)

    r2_champ = round(float(r2_score(y_hold, preds_champ)), 5)
    rmse_champ = round(float(np.sqrt(mean_squared_error(y_hold, preds_champ))), 4)

    r2_chall = round(float(r2_score(y_hold, preds_chall)), 5)
    rmse_chall = round(float(np.sqrt(mean_squared_error(y_hold, preds_chall))), 4)

    # Critério de Promoção: Challenger vence ou empata tecnicamente dentro de 0.25 pts de RMSE
    # incorporando a nova safra temporal
    challenger_promoted = rmse_chall <= (rmse_champ + 0.25)
    model_v2_path = parquet_path.parent / "enem_v2.pkl"
    joblib.dump(challenger_v2, model_v2_path)

    retrain_report = {
        "year": year,
        "execution_branch": "OOT_APPROVED_RETRAIN_CHAMPION_VS_CHALLENGER",
        "gatekeeper_passed": True,
        "oot_metrics_v1": {
            "r2": r2_oot,
            "rmse": rmse_oot,
            "mae": mae_oot,
        },
        "consolidated_rows_used": len(df_concat),
        "holdout_evaluation": {
            "champion_v1": {"r2": r2_champ, "rmse": rmse_champ},
            "challenger_v2": {"r2": r2_chall, "rmse": rmse_chall},
        },
        "challenger_promoted": challenger_promoted,
        "artifact_v2_path": str(model_v2_path),
    }

    report_path = parquet_path.parent / f"relatorio_etapa3_{year}_retrain.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(retrain_report, f, indent=2, ensure_ascii=False)

    if log_mlflow:
        mlflow_db = project_root / "mlflow.db"
        mlflow.set_tracking_uri(f"sqlite:///{mlflow_db}")
        mlflow.set_experiment("tcc_enem_etapa3_airflow_autonomo")
        with mlflow.start_run(run_name=f"etapa3_oot_retrain_challenger_{year}"):
            mlflow.log_param("year", year)
            mlflow.log_param("branch", "OOT_RETRAIN_CHAMPION_VS_CHALLENGER")
            mlflow.log_param("challenger_promoted", challenger_promoted)
            mlflow.log_metric("oot_v1_r2", r2_oot)
            mlflow.log_metric("oot_v1_rmse", rmse_oot)
            mlflow.log_metric("oot_v1_mae", mae_oot)
            mlflow.log_metric("holdout_champion_v1_r2", r2_champ)
            mlflow.log_metric("holdout_champion_v1_rmse", rmse_champ)
            mlflow.log_metric("holdout_challenger_v2_r2", r2_chall)
            mlflow.log_metric("holdout_challenger_v2_rmse", rmse_chall)
            mlflow.log_artifact(str(report_path))
            mlflow.log_artifact(str(model_v2_path))

    return retrain_report

