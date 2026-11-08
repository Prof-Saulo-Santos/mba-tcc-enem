"""Estágio 1 da DAG Autônoma: Ingestão e Detecção Estrutural da Safra.

Inspeciona os diretórios de microdados brutos de um novo ano do ENEM (ex.: 2024 ou 2025),
localiza a planilha oficial de dicionário (.xlsx), calcula o hash SHA-256 e detecta:
1. O layout físico dos arquivos CSV (Monolítico vs. Bipartido vs. Somente Participantes);
2. A existência física das notas oficiais das 4 provas objetivas (has_scores);
3. O índice de alinhamento posicional (CO_MUNICIPIO_PROVA e SG_UF_PROVA) em safras bipartidas.
"""

import glob
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd


def calcular_sha256(caminho: Path) -> str:
    """Calcula o hash SHA-256 de um arquivo em blocos de 64 KB."""
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def inspect_and_ingest_edition(
    year: int,
    raw_base_dir: Optional[Path] = None,
    sample_check_rows: int = 2000,
) -> Dict[str, Any]:
    """Inspeciona a estrutura bruta de uma edição do ENEM antes do NLP e da seleção."""
    project_root = Path(__file__).resolve().parent.parent.parent
    base_dir = Path(raw_base_dir) if raw_base_dir else project_root / "data" / "raw"
    edition_dir = base_dir / f"enem_{year}"

    if not edition_dir.exists():
        raise FileNotFoundError(f"Diretório da edição {year} não encontrado: {edition_dir}")

    # 1. Localizar Dicionário Oficial (.xlsx)
    dict_matches = sorted(
        glob.glob(str(edition_dir / "**" / "Dicion*.xlsx"), recursive=True)
    )
    if not dict_matches:
        raise FileNotFoundError(
            f"Nenhum arquivo de dicionário (.xlsx) encontrado em {edition_dir}"
        )
    dict_path = Path(dict_matches[0])
    dict_sha256 = calcular_sha256(dict_path)

    # 2. Localizar arquivos CSV na pasta DADOS
    csv_matches = sorted(glob.glob(str(edition_dir / "**" / "*.csv"), recursive=True))
    csv_map = {Path(p).name.upper(): Path(p) for p in csv_matches}

    participantes_csv: Optional[Path] = None
    resultados_csv: Optional[Path] = None
    monolitico_csv: Optional[Path] = None

    for name_upper, path_obj in csv_map.items():
        if f"PARTICIPANTES_{year}" in name_upper:
            participantes_csv = path_obj
        elif f"RESULTADOS_{year}" in name_upper:
            resultados_csv = path_obj
        elif f"MICRODADOS_ENEM_{year}" in name_upper:
            monolitico_csv = path_obj

    colunas_notas = {"NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT"}

    # 3. Classificar layout e verificar presença de notas
    if monolitico_csv is not None:
        layout_type = "MONOLITICO"
        df_head = pd.read_csv(
            monolitico_csv, sep=";", encoding="latin1", nrows=sample_check_rows
        )
        cols_presentes = set(df_head.columns)
        has_scores = colunas_notas.issubset(cols_presentes)
        positional_alignment_valid = True
        positional_match_rate = 1.0
        primary_csv = str(monolitico_csv)
        secondary_csv = None
    elif participantes_csv is not None and resultados_csv is not None:
        layout_type = "BIPARTIDO_PARTICIPANTES_RESULTADOS"
        df_part = pd.read_csv(
            participantes_csv, sep=";", encoding="latin1", nrows=sample_check_rows
        )
        df_res = pd.read_csv(
            resultados_csv, sep=";", encoding="latin1", nrows=sample_check_rows
        )
        cols_presentes = set(df_part.columns).union(set(df_res.columns))
        has_scores = colunas_notas.issubset(set(df_res.columns))

        # Verificação de alinhamento posicional 1:1 (Município e UF de prova)
        if "CO_MUNICIPIO_PROVA" in df_part.columns and "CO_MUNICIPIO_PROVA" in df_res.columns:
            matches = (
                df_part["CO_MUNICIPIO_PROVA"].values == df_res["CO_MUNICIPIO_PROVA"].values
            )
            positional_match_rate = round(float(matches.mean()), 4)
            positional_alignment_valid = positional_match_rate >= 0.99
        else:
            positional_match_rate = 0.0
            positional_alignment_valid = False

        primary_csv = str(participantes_csv)
        secondary_csv = str(resultados_csv)
    elif participantes_csv is not None:
        layout_type = "SOMENTE_PARTICIPANTES_SEM_NOTAS"
        df_part = pd.read_csv(
            participantes_csv, sep=";", encoding="latin1", nrows=sample_check_rows
        )
        cols_presentes = set(df_part.columns)
        has_scores = colunas_notas.issubset(cols_presentes)
        positional_alignment_valid = False
        positional_match_rate = 0.0
        primary_csv = str(participantes_csv)
        secondary_csv = None
    else:
        raise FileNotFoundError(
            f"Nenhum CSV válido de participantes ou microdados localizado em {edition_dir}"
        )

    return {
        "year": year,
        "layout_type": layout_type,
        "dictionary_path": str(dict_path),
        "dictionary_sha256": dict_sha256,
        "primary_csv": primary_csv,
        "secondary_csv": secondary_csv,
        "has_scores": has_scores,
        "positional_alignment_valid": positional_alignment_valid,
        "positional_match_rate": positional_match_rate,
        "detected_columns_count": len(cols_presentes),
    }

