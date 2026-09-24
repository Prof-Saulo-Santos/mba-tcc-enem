import os
import sys
import logging
import pandas as pd

# Garante que a raiz do projeto esteja no PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.harmonizer import load_and_harmonize_auto
from src.processing.validator import validate_harmonized_data, validate_cleaned_data
from src.processing.cleaner import clean_data
from src.processing.features import feature_engineering

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("pipeline")


def run_pipeline(
    year: int,
    data_dir: str = "data/raw",
    output_dir: str = "data/processed",
    nrows: int = None
) -> pd.DataFrame:
    """
    Orquestrador principal do ETL do ENEM.

    Executa as seguintes etapas em sequência (Arquitetura Medalhão):
      T1 - Ingestão e Harmonização (reader + harmonizer)
      Soft Validation - Contrato de dados pós-ingestão (Pandera)
      T2 - Limpeza de dados (cleaner)
      T3/T4 - Engenharia de Atributos (features)
      Hard Validation - Contrato de dados pré-exportação (Pandera)
      Load - Salva o arquivo .parquet na Camada Gold

    Args:
        year: Ano do ENEM a processar (2017 a 2025).
        data_dir: Caminho raiz onde estão os dados brutos (Camada Bronze).
        output_dir: Caminho onde o .parquet final será salvo (Camada Gold).
        nrows: (Opcional) Número de linhas a carregar. Útil para testes rápidos.
               Use None para processar a base completa.

    Returns:
        DataFrame com os dados processados (espelho do que foi salvo em disco).
    """
    logger.info("=" * 60)
    logger.info(f"INICIANDO PIPELINE ENEM — Ano: {year}")
    if nrows:
        logger.info(f"MODO TESTE ATIVO: carregando apenas {nrows} linhas.")
    logger.info("=" * 60)

    # ──────────────────────────────────────────────
    # ETAPA 1: Ingestão + Harmonização (Camada T1)
    # ──────────────────────────────────────────────
    logger.info("[1/5] Ingestão e Harmonização (T1)...")
    kwargs = {"nrows": nrows} if nrows else {}
    df = load_and_harmonize_auto(data_dir, year, **kwargs)

    # Adiciona o ano como coluna para rastreabilidade
    df["NU_ANO"] = year
    linhas_brutas = len(df)
    logger.info(f"      → {linhas_brutas:,} registros brutos carregados.")

    # ──────────────────────────────────────────────
    # ETAPA 2: Soft Validation — Contrato de Dados (pós-ingestão)
    # ──────────────────────────────────────────────
    logger.info("[2/5] Soft Validation — Verificando contrato de dados pós-ingestão...")
    try:
        # Faz o cast das notas para float antes da validação (ainda podem ter nulos)
        score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
        for col in score_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df["NU_ANO"] = df["NU_ANO"].astype(int)

        df = validate_harmonized_data(df)
        logger.info("      → Soft Validation APROVADA.")
    except Exception as e:
        logger.error(f"      ❌ Soft Validation FALHOU: {e}")
        raise

    # ──────────────────────────────────────────────
    # ETAPA 3: Limpeza (T2)
    # ──────────────────────────────────────────────
    logger.info("[3/5] Limpeza de Dados (T2)...")
    df = clean_data(df)
    linhas_limpas = len(df)
    removidos = linhas_brutas - linhas_limpas
    logger.info(f"      → {linhas_limpas:,} registros após limpeza.")
    logger.info(f"      → {removidos:,} registros removidos ({removidos/linhas_brutas*100:.1f}% do total — ausentes/duplicatas).")

    # ──────────────────────────────────────────────
    # ETAPA 4: Engenharia de Atributos (T3/T4)
    # ──────────────────────────────────────────────
    logger.info("[4/5] Engenharia de Atributos (T3/T4)...")
    df = feature_engineering(df)
    logger.info(f"      → Colunas finais: {list(df.columns)}")

    # ──────────────────────────────────────────────
    # ETAPA 5: Hard Validation — Contrato de Dados (pré-exportação)
    # ──────────────────────────────────────────────
    logger.info("[5/5] Hard Validation — Verificando contrato de dados pré-exportação...")
    try:
        df = validate_cleaned_data(df)
        logger.info("      → Hard Validation APROVADA. Dados prontos para exportação.")
    except Exception as e:
        logger.error(f"      ❌ Hard Validation FALHOU: {e}")
        raise

    # ──────────────────────────────────────────────
    # LOAD: Salva o .parquet final (Camada Gold)
    # ──────────────────────────────────────────────
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"enem_{year}_silver.parquet")
    df.to_parquet(output_path, index=False)
    logger.info("=" * 60)
    logger.info(f"✅ PIPELINE CONCLUÍDO — Arquivo salvo em: {output_path}")
    logger.info(f"   Registros finais: {len(df):,} | Colunas: {len(df.columns)}")
    logger.info("=" * 60)

    return df


if __name__ == "__main__":
    # Ponto de entrada direto: processa o ENEM 2023 em modo de teste (10.000 linhas)
    # Para rodar a base completa, remova o argumento nrows=10000
    resultado = run_pipeline(
        year=2023,
        data_dir="data/raw",
        output_dir="data/processed",
        nrows=10000   # ← Mude para None para processar TUDO
    )
    print(f"\nShape final do DataFrame: {resultado.shape}")
    print(resultado[["NU_ANO", "NU_NOTA_MT", "NU_NOTA_MEDIA", "FAIXA_DESEMPENHO"]].head(10))
