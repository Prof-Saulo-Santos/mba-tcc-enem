import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def create_average_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a variável derivada NU_NOTA_MEDIA, que é a média aritmética simples 
    das 5 notas do participante no ENEM (Ciências da Natureza, Ciências Humanas, 
    Linguagens e Códigos, Matemática e Redação).
    """
    score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
    existing_cols = [c for c in score_cols if c in df.columns]
    
    if len(existing_cols) == 5:
        logger.info("Engenharia de Atributos: Calculando variável NU_NOTA_MEDIA")
        # axis=1 calcula a média por linha (por participante)
        df["NU_NOTA_MEDIA"] = df[existing_cols].mean(axis=1)
    else:
        logger.warning(f"Não foi possível calcular NU_NOTA_MEDIA. Faltam colunas de nota: {existing_cols}")
        
    return df

def create_performance_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Discretiza a variável-alvo contínua (NU_NOTA_MEDIA) em faixas categóricas
    para sustentar a trilha experimental de Classificação (Scikit-Learn/XGBoost).
    
    Cortes pedagógicos (escala 0-1000):
    < 450: Insuficiente
    450 - 600: Regular
    600 - 750: Bom
    >= 750: Excelente
    """
    if "NU_NOTA_MEDIA" not in df.columns:
        return df
        
    logger.info("Engenharia de Atributos: Discretizando desempenho em faixas categóricas")
    
    conditions = [
        df["NU_NOTA_MEDIA"] < 450,
        (df["NU_NOTA_MEDIA"] >= 450) & (df["NU_NOTA_MEDIA"] < 600),
        (df["NU_NOTA_MEDIA"] >= 600) & (df["NU_NOTA_MEDIA"] < 750),
        df["NU_NOTA_MEDIA"] >= 750
    ]
    
    choices = ["Insuficiente", "Regular", "Bom", "Excelente"]
    
    df["FAIXA_DESEMPENHO"] = np.select(conditions, choices, default="Não Avaliado")
    
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline completo das camadas T3 (Padronização) e T4 (Feature Engineering).
    Recebe os dados perfeitamente limpos do cleaner.py e enriquece a base para os modelos preditivos.
    """
    logger.info("Iniciando a fase de Engenharia de Atributos (T3/T4).")
    
    df = create_average_score(df)
    df = create_performance_categories(df)
    
    # Espaço reservado para futura padronização (T3) de outras colunas do questionário socioeconômico, 
    # como mapear faixas de renda de A-Q para valores numéricos, ou unificar categorias.
    
    return df
