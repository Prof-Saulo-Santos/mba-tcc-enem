import pytest
import pandas as pd
from unittest.mock import patch
from src.ingestion.reader import read_microdata_positional_split

@patch("src.ingestion.reader.find_file")
@patch("src.ingestion.reader.pd.read_csv")
def test_read_microdata_positional_split_success(mock_read_csv, mock_find_file):
    """
    Testa se a concatenação posicional e a remoção de colunas duplicadas
    funcionam corretamente quando ambos os arquivos têm o mesmo tamanho.
    """
    # Mockando caminhos de arquivo
    mock_find_file.side_effect = ["/dummy/PARTICIPANTES_2024.csv", "/dummy/RESULTADOS_2024.csv"]
    
    # Mock de PARTICIPANTES (3 linhas, 2 colunas)
    df_part = pd.DataFrame({
        "NU_INSCRICAO": ["1", "2", "3"],
        "TP_SEXO": ["M", "F", "F"]
    })
    
    # Mock de RESULTADOS (3 linhas, 3 colunas, com NU_INSCRICAO duplicado)
    df_result = pd.DataFrame({
        "NU_INSCRICAO": ["1", "2", "3"],
        "NU_NOTA_MT": ["500", "600", "700"],
        "NU_NOTA_CH": ["450", "650", "750"]
    })
    
    mock_read_csv.side_effect = [df_part, df_result]
    
    # Execução
    df_concat = read_microdata_positional_split("/dummy", 2024)
    
    # Asserções
    assert len(df_concat) == 3, "Número de linhas deve ser preservado após a concatenação"
    assert "TP_SEXO" in df_concat.columns, "Coluna do dataset PARTICIPANTES deve estar presente"
    assert "NU_NOTA_MT" in df_concat.columns, "Coluna do dataset RESULTADOS deve estar presente"
    
    # Como NU_INSCRICAO existe em ambos, pd.concat geraria 5 colunas. 
    # Nossa lógica de remoção de duplicadas deve reduzir para 4 colunas exclusivas.
    assert len(df_concat.columns) == 4, "A coluna duplicada NU_INSCRICAO não foi removida"
    
@patch("src.ingestion.reader.find_file")
@patch("src.ingestion.reader.pd.read_csv")
def test_read_microdata_positional_split_row_divergence(mock_read_csv, mock_find_file):
    """
    Testa a diretiva de falha rápida (fail-fast) da Engenharia de Software Defensiva:
    Se os arquivos PARTICIPANTES e RESULTADOS não tiverem o exato mesmo número de linhas,
    a função deve estourar um ValueError imediatamente antes de tentar concatenar.
    """
    # Mockando caminhos de arquivo
    mock_find_file.side_effect = ["/dummy/PARTICIPANTES_2024.csv", "/dummy/RESULTADOS_2024.csv"]
    
    # Mock de PARTICIPANTES (3 linhas)
    df_part = pd.DataFrame({
        "NU_INSCRICAO": ["1", "2", "3"]
    })
    
    # Mock de RESULTADOS (2 linhas apenas - anomalia simulada)
    df_result = pd.DataFrame({
        "NU_INSCRICAO": ["1", "2"]
    })
    
    mock_read_csv.side_effect = [df_part, df_result]
    
    # Execução & Asserção
    with pytest.raises(ValueError, match="Divergência fatal no número de linhas"):
        read_microdata_positional_split("/dummy", 2024)
