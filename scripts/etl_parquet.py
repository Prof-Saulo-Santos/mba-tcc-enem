"""
Script de Big Data ETL: Ingestão em Chunks e Conversão Histórica para Apache Parquet (Snappy)
Projeto TCC MBA - ENEM
Utiliza o contrato canônico 'data/processed/schema_mapping_historico.json' gerado pelo Notebook 04
para resolver dinamicamente o Schema/Semantic Drift em toda a Década de Ouro (2014 a 2023).
"""

import os
import sys
import glob
import json
import time
import argparse
import pandas as pd
import numpy as np

# ── 1. Resolução Robusta de Caminhos ──────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
RAW_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
MAPPING_FILE = os.path.join(PROCESSED_DIR, 'schema_mapping_historico.json')

# Colunas adicionais de controle administrativo (se presentes no CSV)
COLS_CONTROLE_EXTRA = [
    'NU_INSCRICAO', 'NU_ANO', 
    'TP_DEPENDENCIA_ADM_ESC', 'TP_LOCALIZACAO_ESC',
    'NU_NOTA_REDACAO'
]

def carregar_schema_mapping():
    if not os.path.exists(MAPPING_FILE):
        raise FileNotFoundError(
            f"Arquivo de Schema Mapping não encontrado em: {MAPPING_FILE}. "
            "Execute o Notebook 04 para gerá-lo antes do ETL."
        )
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def localizar_csv_ano(ano):
    """Localiza o arquivo CSV principal de microdados do ano especificado."""
    padroes = [
        os.path.join(RAW_DIR, f'enem_{ano}', f'microdados_enem_{ano}', 'DADOS', '*.csv'),
        os.path.join(RAW_DIR, f'enem_{ano}', f'microdados_enem_{ano}', 'dados', '*.csv'),
        os.path.join(RAW_DIR, f'enem_{ano}', '**', '*.csv')
    ]
    for padrao in padroes:
        candidatos = glob.glob(padrao, recursive=True)
        # Filtrar apenas o arquivo de microdados de inscritos (ignorar itens e questionários avulsos)
        candidatos_validos = [
            f for f in candidatos 
            if not any(ign in os.path.basename(f).upper() for ign in ['ITENS', 'HAB_ESTUDO', 'PROVA'])
        ]
        if candidatos_validos:
            return candidatos_validos[0]
    return None

def extrair_e_limpar_ano(ano, mapping_total, chunksize=500000):
    t0 = time.time()
    ano_str = str(ano)
    print(f"\n{'='*70}")
    print(f"🚀 Iniciando Pipeline ETL para o ENEM {ano_str}")
    print(f"{'='*70}")

    if ano_str not in mapping_total:
        print(f"⚠️ Aviso: Ano {ano_str} não possui mapeamento no schema_mapping_historico.json. Ignorando.")
        return False

    map_ano = mapping_total[ano_str]
    reverse_map = {v: k for k, v in map_ano.items()}

    arquivo_csv = localizar_csv_ano(ano_str)
    if not arquivo_csv or not os.path.exists(arquivo_csv):
        print(f"❌ Erro: Arquivo CSV de microdados não encontrado para o ano {ano_str} em {RAW_DIR}")
        return False

    print(f"Arquivo CSV identificado: {arquivo_csv}")
    
    # Inspecionar cabeçalho real do CSV para evitar KeyError com colunas opcionais
    df_header = pd.read_csv(arquivo_csv, sep=';', encoding='latin-1', nrows=1)
    colunas_disponiveis = set(df_header.columns)

    # Identificar quais colunas do mapeamento estão presentes no CSV
    cols_leitura_raw = []
    for can_col, raw_col in map_ano.items():
        if raw_col in colunas_disponiveis:
            cols_leitura_raw.append(raw_col)
        else:
            print(f"⚠️ Atenção: Coluna mapeada '{raw_col}' (Canônica: '{can_col}') não está no CSV {ano_str}!")

    # Adicionar colunas de controle se presentes
    for c in COLS_CONTROLE_EXTRA:
        if c in colunas_disponiveis and c not in cols_leitura_raw:
            cols_leitura_raw.append(c)

    print(f"Colunas brutas selecionadas para leitura: {len(cols_leitura_raw)}")
    print(f"Resolução de Schema para {ano_str}:")
    for can_name, raw_name in map_ano.items():
        if can_name != raw_name:
            print(f" -> Mapeamento Semântico: {raw_name} ➔ {can_name}")

    # Processamento em Chunks para evitar estouro de memória (Out-Of-Memory)
    chunks_purificados = []
    total_linhas_lidas = 0
    total_linhas_presentes = 0

    try:
        reader = pd.read_csv(
            arquivo_csv,
            sep=';',
            encoding='latin-1',
            usecols=cols_leitura_raw,
            chunksize=chunksize,
            low_memory=False
        )

        for i, chunk in enumerate(reader, 1):
            total_linhas_lidas += len(chunk)
            
            # 1. Renomeação Dinâmica para o Schema Canônico de 2023
            chunk = chunk.rename(columns=reverse_map)

            # 2. Filtro Metodológico de Presença Integral (Notebook 02)
            presencas = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']
            presencas_ativas = [p for p in presencas if p in chunk.columns]
            
            if presencas_ativas:
                # Converter para numérico caso venha como string
                for p in presencas_ativas:
                    chunk[p] = pd.to_numeric(chunk[p], errors='coerce').fillna(0)
                mask_presentes = (chunk[presencas_ativas] == 1).all(axis=1)
                chunk = chunk[mask_presentes].copy()
                # Remover colunas de presença após o filtro
                chunk = chunk.drop(columns=presencas_ativas)

            # 3. Cálculo do Alvo Oficial Homologado: TARGET_M4
            provas_objetivas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']
            todas_provas_ok = all(p in chunk.columns for p in provas_objetivas)
            
            if todas_provas_ok:
                for p in provas_objetivas:
                    chunk[p] = pd.to_numeric(chunk[p], errors='coerce')
                # Descartar nulos nas provas de quem estava presente
                chunk = chunk.dropna(subset=provas_objetivas)
                chunk['TARGET_M4'] = chunk[provas_objetivas].mean(axis=1)

            total_linhas_presentes += len(chunk)
            chunks_purificados.append(chunk)
            print(f"Chunk {i:02d}: {len(chunk):,} presentes válidos processados.")

    except Exception as e:
        print(f"❌ Erro durante o processamento de chunks no ano {ano_str}: {e}")
        return False

    if not chunks_purificados:
        print(f"❌ Nenhum registro válido encontrado para {ano_str}!")
        return False

    # 4. Consolidação e Tratamento Final
    df_ano = pd.concat(chunks_purificados, ignore_index=True)
    print(f"\nConsolidação Concluída: {len(df_ano):,} candidatos válidos com presença integral e notas calculadas.")

    # 5. Persistência Colunar Otimizada em Apache Parquet (Snappy)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    arquivo_saida = os.path.join(PROCESSED_DIR, f'enem_{ano_str}_gold.parquet')
    
    df_ano.to_parquet(
        arquivo_saida,
        engine='pyarrow',
        compression='snappy',
        index=False
    )
    
    tamanho_mb = os.path.getsize(arquivo_saida) / (1024 * 1024)
    print(f"✅ Sucesso! Dataset salvo em: {arquivo_saida}")
    print(f"Tamanho do arquivo Parquet: {tamanho_mb:.2f} MB | Tempo decorrido: {time.time()-t0:.1f}s")
    return True

def main():
    parser = argparse.ArgumentParser(description="Pipeline ETL Big Data ENEM - Conversão Histórica para Parquet")
    parser.add_argument(
        '--ano',
        type=int,
        default=None,
        help="Ano específico do ENEM a processar (ex: 2014). Se omitido, processa a década de 2014 a 2023."
    )
    args = parser.parse_args()

    mapping = carregar_schema_mapping()

    if args.ano:
        extrair_e_limpar_ano(args.ano, mapping)
    else:
        # Década de Ouro: 2014 a 2023 (10 anos)
        anos = range(2014, 2024)
        print(f"Iniciando ETL para a Década de Ouro completa: {list(anos)}")
        for a in anos:
            extrair_e_limpar_ano(a, mapping)

if __name__ == "__main__":
    main()
