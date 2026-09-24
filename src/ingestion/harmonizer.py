import pandas as pd
import logging
from .reader import read_microdata, read_microdata_positional_split

logger = logging.getLogger(__name__)

# Constantes do ENEM
TARGET_COLUMNS = [
    "NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"
]

INSTITUTIONAL_COLUMNS = [
    "CO_MUNICIPIO_ESC", "NO_MUNICIPIO_ESC", "CO_UF_ESC", "SG_UF_ESC",
    "TP_DEPENDENCIA_ADM_ESC", "TP_LOCALIZACAO_ESC", "TP_SIT_FUNC_ESC"
]

SOCIOECONOMIC_COLUMNS = [f"Q{str(i).zfill(3)}" for i in range(1, 28)]

def drop_obsolete_columns(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Camada Anticorrupção - Defesa Estrutural: 
    Garante paridade temporal entre edições do ENEM e conformidade com o dicionário de variáveis.
    """
    cols_to_drop = []
    
    # Q026 e Q027 foram removidas a partir de 2019 (Defesa LGPD e mudança de schema)
    for col in ["Q026", "Q027"]:
        if col in df.columns:
            cols_to_drop.append(col)
            
    # TP_VERSAO_DIGITAL existiu apenas em 2020
    if "TP_VERSAO_DIGITAL" in df.columns:
        cols_to_drop.append("TP_VERSAO_DIGITAL")
        
    if cols_to_drop:
        logger.info(f"Removendo colunas anômalas/obsoletas para o ano {year}: {cols_to_drop}")
        df = df.drop(columns=cols_to_drop)
        
    return df

def load_and_harmonize_auto(data_dir: str, year: int, **kwargs) -> pd.DataFrame:
    """
    Orquestrador que roteia a leitura para o módulo correto dependendo do ano 
    e aplica as regras de harmonização (T1).
    """
    logger.info(f"Iniciando orquestração de leitura e harmonização para o ano {year}")
    
    # Decisão de roteamento baseada no ano
    if year <= 2023:
        df = read_microdata(data_dir, year, **kwargs)
    else:
        df = read_microdata_positional_split(data_dir, year, **kwargs)
        
    logger.info("Aplicando regras de harmonização (Defesa estrutural e LGPD)")
    df_harmonized = drop_obsolete_columns(df, year)
    
    return df_harmonized
