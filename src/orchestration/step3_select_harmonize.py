"""Estágio 3 da DAG Autônoma: Seleção de Atributos, Harmonização e Downcasting.

Consome o mapeamento semântico gerado pelo SBERT no Estágio 2, extrai apenas as
colunas correspondentes ao Esquadrão de Elite, aplica a deflação estrutural da
renda em múltiplos de Salários Mínimos per capita, harmoniza escalas categóricas
e comprime os tipos de dados (Downcasting: 15 bytes/linha com notas; 11 bytes/linha sem notas).
"""

from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd

MAPA_Q006_SM: Dict[str, float] = {
    "A": 0.0,
    "B": 0.5,
    "C": 1.25,
    "D": 1.75,
    "E": 2.25,
    "F": 2.75,
    "G": 3.5,
    "H": 4.5,
    "I": 5.5,
    "J": 6.5,
    "K": 7.5,
    "L": 8.5,
    "M": 9.5,
    "N": 11.0,
    "O": 13.5,
    "P": 17.5,
    "Q": 22.5,
}

MAPA_Q024_PADRAO: Dict[str, int] = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 3,
}

MAPA_Q024_2014: Dict[str, int] = {
    "D": 0,
    "A": 1,
    "B": 2,
    "C": 3,
}

MAPA_Q002_PADRAO: Dict[str, int] = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
    "F": 5,
    "G": 6,
    "H": 7,
}

MAPA_Q002_2014: Dict[str, int] = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
    "F": 4,
    "G": 5,
    "H": 6,
    "I": 7,
}


def select_harmonize_and_downcast(
    ingest_report: Dict[str, Any],
    schema_report: Dict[str, Any],
    max_rows: Optional[int] = 100000,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Seleciona colunas mapeadas pelo SBERT, harmoniza value drift e aplica downcasting."""
    project_root = Path(__file__).resolve().parent.parent.parent
    out_dir = (
        Path(output_dir)
        if output_dir
        else project_root / "data" / "processed" / "safras_etapa3"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    year = int(ingest_report["year"])
    layout_type = ingest_report["layout_type"]
    col_map = schema_report["column_mapping"]

    col_q006 = col_map["Q006"]
    col_q005 = col_map["Q005"]
    col_q024 = col_map["Q024"]
    col_q002 = col_map["Q002"]
    col_ano_concluiu = col_map["TP_ANO_CONCLUIU"]
    col_sexo = col_map["TP_SEXO"]
    col_lingua = col_map.get("TP_LINGUA", "TP_LINGUA")

    cols_part = [col_q006, col_q005, col_q024, col_q002, col_ano_concluiu, col_sexo]
    cols_notas = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT"]
    cols_pres = ["TP_PRESENCA_CN", "TP_PRESENCA_CH", "TP_PRESENCA_LC", "TP_PRESENCA_MT"]

    tp_lingua_imputed = False

    if layout_type == "MONOLITICO":
        usecols = list(set(cols_part + [col_lingua] + cols_notas + cols_pres))
        df_raw = pd.read_csv(
            ingest_report["primary_csv"],
            sep=";",
            encoding="latin1",
            usecols=usecols,
            nrows=max_rows,
        )
        # Filtrar presença integral nas 4 provas objetivas
        for cp in cols_pres:
            df_raw[cp] = pd.to_numeric(df_raw[cp], errors="coerce").fillna(0)
        mask_pres = (df_raw[cols_pres] == 1).all(axis=1)
        df_raw = df_raw.loc[mask_pres].copy()

        for cn in cols_notas:
            df_raw[cn] = pd.to_numeric(df_raw[cn], errors="coerce")
        df_raw = df_raw.dropna(subset=cols_notas)
        df_raw["TARGET_M4"] = (
            df_raw["NU_NOTA_CN"]
            + df_raw["NU_NOTA_CH"]
            + df_raw["NU_NOTA_LC"]
            + df_raw["NU_NOTA_MT"]
        ) / 4.0

    elif layout_type == "BIPARTIDO_PARTICIPANTES_RESULTADOS":
        df_part = pd.read_csv(
            ingest_report["primary_csv"],
            sep=";",
            encoding="latin1",
            usecols=cols_part,
            nrows=max_rows,
        )
        df_res = pd.read_csv(
            ingest_report["secondary_csv"],
            sep=";",
            encoding="latin1",
            usecols=[col_lingua] + cols_notas + cols_pres,
            nrows=max_rows,
        )
        df_raw = pd.concat(
            [df_part.reset_index(drop=True), df_res.reset_index(drop=True)], axis=1
        )
        for cp in cols_pres:
            df_raw[cp] = pd.to_numeric(df_raw[cp], errors="coerce").fillna(0)
        mask_pres = (df_raw[cols_pres] == 1).all(axis=1)
        df_raw = df_raw.loc[mask_pres].copy()

        for cn in cols_notas:
            df_raw[cn] = pd.to_numeric(df_raw[cn], errors="coerce")
        df_raw = df_raw.dropna(subset=cols_notas)
        df_raw["TARGET_M4"] = (
            df_raw["NU_NOTA_CN"]
            + df_raw["NU_NOTA_CH"]
            + df_raw["NU_NOTA_LC"]
            + df_raw["NU_NOTA_MT"]
        ) / 4.0

    else:
        # SOMENTE_PARTICIPANTES_SEM_NOTAS (Ex.: ENEM 2025)
        df_head = pd.read_csv(
            ingest_report["primary_csv"], sep=";", encoding="latin1", nrows=5
        )
        usecols = list(cols_part)
        if col_lingua in df_head.columns:
            usecols.append(col_lingua)
        df_raw = pd.read_csv(
            ingest_report["primary_csv"],
            sep=";",
            encoding="latin1",
            usecols=usecols,
            nrows=max_rows,
        )

    # Harmonização das 6 features do Esquadrão de Elite
    mapa_q024 = MAPA_Q024_2014 if year == 2014 else MAPA_Q024_PADRAO
    mapa_q002 = MAPA_Q002_2014 if year == 2014 else MAPA_Q002_PADRAO

    renda_sm = df_raw[col_q006].astype(str).str.strip().map(MAPA_Q006_SM)
    moradores = pd.to_numeric(df_raw[col_q005], errors="coerce").clip(lower=1, upper=20)
    renda_per_capita = (renda_sm / moradores).clip(lower=0.0, upper=25.0)

    q024_harm = df_raw[col_q024].astype(str).str.strip().map(mapa_q024)
    q002_harm = df_raw[col_q002].astype(str).str.strip().map(mapa_q002)
    ano_concluiu_harm = (
        pd.to_numeric(df_raw[col_ano_concluiu], errors="coerce").fillna(0).clip(0, 9)
    )
    sexo_harm = (
        df_raw[col_sexo]
        .astype(str)
        .str.strip()
        .str.upper()
        .map({"F": 0, "M": 1, "0": 0, "1": 1})
    )

    if col_lingua in df_raw.columns:
        lingua_harm = pd.to_numeric(df_raw[col_lingua], errors="coerce").clip(0, 1)
    else:
        # Em bases cadastrais sem arquivo RESULTADOS (ex.: PARTICIPANTES_2025.csv),
        # aplica imputação condicional determinística baseada no censo 2014-2023
        tp_lingua_imputed = True
        lingua_harm = pd.Series(
            np.where((q024_harm >= 1) | (renda_per_capita >= 1.0), 0, 1),
            index=df_raw.index,
        )

    df_out = pd.DataFrame(
        {
            "NU_ANO": year,
            "RENDA_PER_CAPITA": renda_per_capita,
            "Q024": q024_harm,
            "TP_ANO_CONCLUIU": ano_concluiu_harm,
            "TP_LINGUA": lingua_harm,
            "TP_SEXO": sexo_harm,
            "Q002": q002_harm,
        }
    )

    if "TARGET_M4" in df_raw.columns:
        df_out["TARGET_M4"] = df_raw["TARGET_M4"]

    df_out = df_out.dropna().reset_index(drop=True)

    # Downcasting Estrito (15 bytes/linha com TARGET_M4; 11 bytes/linha sem TARGET_M4)
    dtype_map = {
        "NU_ANO": "int16",
        "RENDA_PER_CAPITA": "float32",
        "Q024": "int8",
        "TP_ANO_CONCLUIU": "int8",
        "TP_LINGUA": "int8",
        "TP_SEXO": "int8",
        "Q002": "int8",
    }
    if "TARGET_M4" in df_out.columns:
        dtype_map["TARGET_M4"] = "float32"

    df_out = df_out.astype(dtype_map)
    bytes_per_row = int(df_out.memory_usage(index=False).sum() // len(df_out))

    parquet_path = out_dir / f"enem_{year}_purificado.parquet"
    df_out.to_parquet(parquet_path, compression="snappy", index=False)

    return {
        "year": year,
        "parquet_path": str(parquet_path),
        "rows_retained": len(df_out),
        "bytes_per_row_ram": bytes_per_row,
        "ram_usage_mb": round(
            float(df_out.memory_usage(index=False).sum() / (1024**2)), 3
        ),
        "has_scores": bool("TARGET_M4" in df_out.columns),
        "positional_alignment_valid": ingest_report["positional_alignment_valid"],
        "positional_match_rate": ingest_report["positional_match_rate"],
        "tp_lingua_imputed": tp_lingua_imputed,
        "mean_renda_per_capita_sm": round(float(df_out["RENDA_PER_CAPITA"].mean()), 4),
        "mean_target_m4": (
            round(float(df_out["TARGET_M4"].mean()), 2)
            if "TARGET_M4" in df_out.columns
            else None
        ),
    }

