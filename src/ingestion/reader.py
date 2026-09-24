import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def find_file(data_dir: str, year: int, prefix: str) -> str:
    """
    Encontra o caminho correto para o arquivo CSV de um determinado ano,
    lidando com as anomalias de estrutura de diretórios do INEP.
    """
    if year >= 2023:
        base_path = os.path.join(data_dir, f"enem_{year}", f"microdados_enem_{year}", "DADOS")
    else:
        base_path = os.path.join(data_dir, f"enem_{year}", "DADOS")
        
    filename = f"{prefix}_{year}.csv"
    filepath = os.path.join(base_path, filename)
    
    if not os.path.exists(filepath):
        logger.warning(f"Arquivo não encontrado: {filepath}")
        
    return filepath

def read_microdata(data_dir: str, year: int, **kwargs) -> pd.DataFrame:
    """
    Lê o arquivo único MICRODADOS_ENEM_YYYY.csv.
    Válido para as edições até 2023.
    """
    logger.info(f"Iniciando leitura dos microdados para o ano {year}")
    
    filepath = find_file(data_dir, year, "MICRODADOS_ENEM")
    logger.info(f"Lendo base única: {filepath}")
    
    df = pd.read_csv(filepath, sep=";", encoding="latin-1", dtype=str, **kwargs)
    return df

def read_microdata_positional_split(data_dir: str, year: int, **kwargs) -> pd.DataFrame:
    """
    Lê as bases particionadas (PARTICIPANTES e RESULTADOS) de 2024 em diante.
    Realiza concatenação posicional conforme diretiva de design (pd.concat com axis=1),
    assumindo que a ordenação das linhas nos dois arquivos do INEP é simétrica.
    """
    logger.info(f"Iniciando leitura dos microdados particionados para o ano {year}")
    
    part_path = find_file(data_dir, year, "PARTICIPANTES")
    result_path = find_file(data_dir, year, "RESULTADOS")
    
    logger.info(f"Lendo PARTICIPANTES: {part_path}")
    df_part = pd.read_csv(part_path, sep=";", encoding="latin-1", dtype=str, **kwargs)
    
    logger.info(f"Lendo RESULTADOS: {result_path}")
    df_result = pd.read_csv(result_path, sep=";", encoding="latin-1", dtype=str, **kwargs)
    
    if len(df_part) != len(df_result):
        raise ValueError(
            f"Divergência fatal no número de linhas para o ano {year}! "
            f"PARTICIPANTES tem {len(df_part)} linhas e RESULTADOS tem {len(df_result)} linhas."
        )
    
    logger.info("Realizando concatenação posicional (axis=1)")
    df_concat = pd.concat([df_part, df_result], axis=1)
    
    # Remove eventuais colunas duplicadas (ex: NU_INSCRICAO) geradas pela concatenação
    df_concat = df_concat.loc[:, ~df_concat.columns.duplicated()]
    
    return df_concat
