"""
Script de processamento em chunks para bases massivas do ENEM.
Resolve o problema de OOM (Out of Memory) ao processar ~4 milhões de linhas.

Estratégia: lê o CSV em pedaços de 500k linhas, aplica a limpeza e features
em cada pedaço e salva incrementalmente no .parquet final.
"""
import os
import sys
import logging
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.harmonizer import drop_obsolete_columns
from src.ingestion.reader import find_file
from src.processing.cleaner import clean_data
from src.processing.features import feature_engineering

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("pipeline_chunked")


def run_pipeline_chunked(
    year: int,
    data_dir: str = "data/raw",
    output_dir: str = "data/processed",
    chunksize: int = 300_000
) -> None:
    """
    Versão do pipeline que processa o CSV em chunks para evitar OOM.

    Args:
        year: Ano do ENEM a processar.
        data_dir: Caminho dos dados brutos (Bronze).
        output_dir: Caminho de saída do .parquet (Gold).
        chunksize: Número de linhas por pedaço. Default: 300.000.
    """
    logger.info("=" * 60)
    logger.info(f"PIPELINE CHUNKED — Ano: {year} | Chunk: {chunksize:,} linhas")
    logger.info("=" * 60)

    # Localiza o arquivo CSV
    filepath = find_file(data_dir, year, "MICRODADOS_ENEM")
    logger.info(f"Arquivo: {filepath}")

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"enem_{year}_silver.parquet")

    chunks_processados = []
    total_bruto = 0
    total_limpo = 0
    num_chunk = 0

    # Lê o CSV em pedaços
    reader = pd.read_csv(
        filepath,
        sep=";",
        encoding="latin-1",
        dtype=str,
        chunksize=chunksize
    )

    for chunk in reader:
        num_chunk += 1
        n_bruto = len(chunk)
        total_bruto += n_bruto
        logger.info(f"[Chunk {num_chunk}] Processando {n_bruto:,} linhas...")

        # T1: Harmonização (remover colunas obsoletas)
        chunk = drop_obsolete_columns(chunk, year)
        chunk["NU_ANO"] = year

        # Converter notas para float (necessário para o cleaner e validator)
        score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
        for col in score_cols:
            if col in chunk.columns:
                chunk[col] = pd.to_numeric(chunk[col], errors='coerce')
        chunk["NU_ANO"] = chunk["NU_ANO"].astype(int)

        # T2: Limpeza
        chunk = clean_data(chunk)

        # T3/T4: Feature Engineering
        chunk = feature_engineering(chunk)

        n_limpo = len(chunk)
        total_limpo += n_limpo
        logger.info(f"[Chunk {num_chunk}] → {n_limpo:,} registros após limpeza.")

        chunks_processados.append(chunk)

        # A cada 5 chunks, consolida e libera memória
        if num_chunk % 5 == 0:
            logger.info(f"  Consolidando {len(chunks_processados)} chunks na memória...")
            df_parcial = pd.concat(chunks_processados, ignore_index=True)
            chunks_processados = [df_parcial]

    # Consolidação final
    logger.info("Consolidando todos os chunks no arquivo .parquet final...")
    df_final = pd.concat(chunks_processados, ignore_index=True)

    # Salvar
    df_final.to_parquet(output_path, index=False)

    removidos = total_bruto - total_limpo
    logger.info("=" * 60)
    logger.info(f"✅ CONCLUÍDO — {output_path}")
    logger.info(f"   Registros brutos:  {total_bruto:,}")
    logger.info(f"   Registros finais:  {total_limpo:,}")
    logger.info(f"   Removidos:         {removidos:,} ({removidos/total_bruto*100:.1f}%)")
    logger.info(f"   Colunas:           {len(df_final.columns)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Processar microdados do ENEM em chunks.")
    parser.add_argument("--year", type=int, default=2023, help="Ano do ENEM para processar (ex: 2017)")
    parser.add_argument("--chunksize", type=int, default=300_000, help="Tamanho do chunk (default: 300000)")
    args = parser.parse_args()

    run_pipeline_chunked(
        year=args.year,
        data_dir="data/raw",
        output_dir="data/processed",
        chunksize=args.chunksize
    )
