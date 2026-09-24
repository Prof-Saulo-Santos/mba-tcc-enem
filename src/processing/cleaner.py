import pandas as pd
import logging

logger = logging.getLogger(__name__)

def filter_present_participants(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove participantes que faltaram ou foram eliminados em qualquer um dos dias de prova.
    No ENEM, TP_PRESENCA_* igual a '1' significa 'Presente na prova'.
    """
    logger.info("Filtrando participantes ausentes ou eliminados.")
    
    presence_cols = ["TP_PRESENCA_CN", "TP_PRESENCA_CH", "TP_PRESENCA_LC", "TP_PRESENCA_MT"]
    
    # Garantir que apenas os participantes que estiveram presentes em TODAS as provas passem.
    # Como a ingestão inicial fez a leitura com dtype=str, a verificação usa string '1'.
    for col in presence_cols:
        if col in df.columns:
            df = df[df[col] == '1']
            
    # Redação não tem presença explícita com o prefixo PRESENCA, mas possui TP_STATUS_REDACAO.
    # TP_STATUS_REDACAO == '1' significa 'Sem problemas' (a redação foi entregue e é válida).
    if "TP_STATUS_REDACAO" in df.columns:
        df = df[df["TP_STATUS_REDACAO"] == '1']
        
    return df

def drop_missing_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Remove registros que ainda possuam valores nulos nas variáveis-alvo (notas)."""
    logger.info("Limpando registros com notas nulas residuais.")
    score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
    existing_cols = [c for c in score_cols if c in df.columns]
    
    return df.dropna(subset=existing_cols)

def cast_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte os tipos das colunas numéricas de volta para os formatos ideais (float/int).
    Como a Ingestão (T1) forçou dtype=str como defesa estrutural (para evitar a perda 
    de zeros à esquerda no Pandas), a conversão explícita ocorre somente agora (T2).
    """
    logger.info("Realizando cast (coerção) de tipos das variáveis contínuas e inteiras.")
    
    # Converter notas para ponto flutuante
    score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
    for col in score_cols:
        if col in df.columns:
            df[col] = df[col].astype(float)
            
    # Converter o ano para inteiro
    if "NU_ANO" in df.columns:
        df["NU_ANO"] = df["NU_ANO"].astype(int)
        
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline completo da camada de Limpeza (T2).
    """
    logger.info("Iniciando a fase de Limpeza (T2).")
    df = filter_present_participants(df)
    df = drop_missing_scores(df)
    
    # Defesa estrutural final contra duplicidades
    df = df.drop_duplicates(subset=["NU_INSCRICAO"]) if "NU_INSCRICAO" in df.columns else df.drop_duplicates()
    
    df = cast_dtypes(df)
    
    return df
