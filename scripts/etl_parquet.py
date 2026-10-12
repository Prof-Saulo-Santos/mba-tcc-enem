import pandas as pd
import numpy as np
import os
import glob

# Constantes da Arquitetura
RAW_DIR = '../data/raw'
PROCESSED_DIR = '../data/processed'

# Esquadrão de Elite (Features) + Controle + Targets
COLS_VITAIS = [
    'NU_INSCRICAO', 'NU_ANO', 
    'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
    'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
    'TP_SEXO', 'TP_LINGUA', 'TP_ANO_CONCLUIU', 
    'TP_DEPENDENCIA_ADM_ESC', 'TP_LOCALIZACAO_ESC',
    'Q002', 'Q006', 'Q024'
]

def extrair_e_limpar_ano(ano):
    print(f"\\n--- Iniciando ETL do ENEM {ano} ---")
    
    # Encontrar o CSV correspondente
    pattern = os.path.join(RAW_DIR, f'enem_{ano}', f'microdados_enem_{ano}', 'DADOS', '*.csv')
    arquivos = glob.glob(pattern)
    
    if not arquivos:
        print(f"Erro: Arquivo bruto não encontrado para {ano}")
        return
        
    arquivo_csv = arquivos[0]
    print(f"Lendo: {arquivo_csv} (Extraindo apenas colunas vitais)")
    
    # Parâmetros de leitura do Pandas para evitar OOM
    chunksize = 500000
    chunks = []
    
    try:
        # A detecção de delimitador (; ou ,) pode variar, mas o INEP costuma usar ';'
        for chunk in pd.read_csv(arquivo_csv, sep=';', encoding='latin-1', usecols=COLS_VITAIS, chunksize=chunksize):
            
            # 1. Filtro: Remoção de Candidatos Ausentes (Exigência do Notebook 02)
            presencas = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']
            mask_presentes = (chunk[presencas] == 1).all(axis=1)
            chunk = chunk[mask_presentes].copy()
            
            # Não precisamos das colunas de presença depois de filtrar
            chunk = chunk.drop(columns=presencas)
            
            chunks.append(chunk)
            print(f"Chunk processado: {len(chunk)} candidatos válidos.")
            
    except ValueError as e:
        print(f"Erro ao ler as colunas vitais no ano {ano}: {e}")
        return

    # Consolidar todos os chunks do ano
    df_ano = pd.concat(chunks, ignore_index=True)
    print(f"Volume Final {ano} (Após remover ausentes): {len(df_ano)} registros.")
    
    # 2. Filtro: Eliminar colunas com mais de 30% nulos (Exigência do Notebook 02)
    limitPer = len(df_ano) * 0.70
    colunas_antes = set(df_ano.columns.tolist())
    
    # Proteger as variáveis escolares da exclusão por % (Decisão Arquitetural)
    colunas_protegidas = ['TP_DEPENDENCIA_ADM_ESC', 'TP_LOCALIZACAO_ESC']
    colunas_para_avaliar = [c for c in df_ano.columns if c not in colunas_protegidas]
    
    # Avaliar as outras colunas e fazer o drop
    colunas_mantidas = df_ano[colunas_para_avaliar].dropna(thresh=limitPer, axis=1).columns.tolist()
    df_ano = df_ano[colunas_mantidas + colunas_protegidas]
    
    colunas_removidas = colunas_antes - set(df_ano.columns)
    if colunas_removidas:
        print(f"Atenção: Colunas removidas por excesso de nulos (>30%): {colunas_removidas}")
    
    # 3. Tratamento final e exportação
    # Queremos remover linhas com nulos apenas nas colunas vitais avaliadas (ex: notas).
    # As variáveis escolares PROTEGIDAS continuarão com seus valores NaN para análise futura (MNAR).
    df_ano = df_ano.dropna(subset=colunas_mantidas)
    print(f"Registros finais sem nulos vitais: {len(df_ano)}")
    
    # Salvar em Parquet particionado
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    out_file = os.path.join(PROCESSED_DIR, f'enem_{ano}_gold.parquet')
    
    # Compressão Snappy é excelente para leitura distribuída no Airflow
    df_ano.to_parquet(out_file, engine='pyarrow', compression='snappy')
    print(f"✅ Sucesso! Arquivo salvo em: {out_file} (Tamanho super compacto)")

if __name__ == "__main__":
    # Vamos processar estritamente a "Era Monolítica de Ouro" (2015 a 2023)
    # Os anos de 2024 e 2025 são particionados e testados no Airflow separadamente.
    anos_treino = range(2015, 2024)
    
    for ano in anos_treino:
        extrair_e_limpar_ano(ano)
