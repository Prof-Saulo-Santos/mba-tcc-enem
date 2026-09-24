import os
import sys
import logging
import pandas as pd
from unittest.mock import patch

# Adiciona a raiz do projeto no PYTHONPATH para encontrar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.harmonizer import load_and_harmonize_auto

logging.basicConfig(level=logging.INFO)

def criar_dados_ficticios(base_dir: str):
    """Cria uma pequena amostra de dados para testes End-to-End da Ingestão."""
    # A partir de 2023, o INEP colocou os DADOS dentro de uma subpasta microdados_enem_XXXX
    dir_2023 = os.path.join(base_dir, "enem_2023", "microdados_enem_2023", "DADOS")
    dir_2024 = os.path.join(base_dir, "enem_2024", "microdados_enem_2024", "DADOS")
    
    os.makedirs(dir_2023, exist_ok=True)
    os.makedirs(dir_2024, exist_ok=True)
    
    # 2023 Monolítico
    df_2023 = pd.DataFrame({
        "NU_INSCRICAO": ["101", "102", "103", "104", "105"],
        "NU_NOTA_MT": ["500", "600", "700", "800", "900"],
        "Q025": ["A", "B", "A", "A", "B"],
        "Q026": ["A", "B", "C", "D", "E"], # Obsoleto
        "Q027": ["F", "G", "H", "I", "J"], # Obsoleto
        "TP_SEXO": ["M", "F", "F", "M", "M"]
    })
    df_2023.to_csv(os.path.join(dir_2023, "MICRODADOS_ENEM_2023.csv"), sep=";", index=False)
    
    # 2024 Particionado
    df_part = pd.DataFrame({
        "NU_INSCRICAO": ["101", "102", "103", "104", "105"],
        "TP_SEXO": ["M", "F", "F", "M", "M"],
        "Q025": ["A", "B", "A", "A", "B"]
    })
    df_part.to_csv(os.path.join(dir_2024, "PARTICIPANTES_2024.csv"), sep=";", index=False)
    
    df_result = pd.DataFrame({
        "NU_INSCRICAO": ["101", "102", "103", "104", "105"],
        "NU_NOTA_MT": ["500", "600", "700", "800", "900"]
    })
    df_result.to_csv(os.path.join(dir_2024, "RESULTADOS_2024.csv"), sep=";", index=False)

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "scratch", "dummy_data")
    criar_dados_ficticios(data_dir)
    
    print("\n" + "="*50)
    print("=== VALIDANDO ENEM 2023 (Base Monolítica) ===")
    print("="*50)
    df_2023 = load_and_harmonize_auto(data_dir, 2023, nrows=5)
    cols_2023 = sorted(df_2023.columns.tolist())
    print(f"\n=> Colunas 2023 ({len(cols_2023)}): {cols_2023}\n")
        
    print("="*50)
    print("=== VALIDANDO ENEM 2024 (Base Particionada) ===")
    print("="*50)
    df_2024 = load_and_harmonize_auto(data_dir, 2024, nrows=5)
    cols_2024 = sorted(df_2024.columns.tolist())
    print(f"\n=> Colunas 2024 ({len(cols_2024)}): {cols_2024}\n")
        
    print("="*50)
    print("=== RESULTADO DA COMPARAÇÃO DA CAMADA ANTICORRUPÇÃO ===")
    print("="*50)
    
    diff_23 = set(cols_2023) - set(cols_2024)
    diff_24 = set(cols_2024) - set(cols_2023)
    
    if not diff_23 and not diff_24:
        print("\n✅ SUCESSO ABSOLUTO: Os schemas de 2023 e 2024 são EXATAMENTE IGUAIS após a harmonização!")
        print("A camada anticorrupção blindou o modelo do desmembramento do INEP e removeu as variáveis obsoletas (Q026, Q027).")
    else:
        print("\n❌ FALHA: Divergência detectada nos schemas.")
        if diff_23: print(f"Colunas exclusivas em 2023: {diff_23}")
        if diff_24: print(f"Colunas exclusivas em 2024: {diff_24}")

if __name__ == "__main__":
    main()
