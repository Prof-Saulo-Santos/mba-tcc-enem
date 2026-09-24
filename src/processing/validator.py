import pandera as pa
from pandera import Column, DataFrameSchema
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Schema de Soft Validation: Aplicado LOGO APÓS a Camada de Ingestão (T1)
# O objetivo é garantir que a estrutura base está correta e coerente.
# Nesta fase, a variável-alvo (notas) AINDA PODE conter nulos, pois a limpeza pesada (T2) não aconteceu.
harmonized_schema = DataFrameSchema(
    {
        # As colunas do ENEM devem respeitar o intervalo definido
        "NU_ANO": Column(int, pa.Check.in_range(2017, 2025), nullable=False),
        
        # As notas ainda podem conter nulos nesta etapa inicial
        "NU_NOTA_MT": Column(float, pa.Check.in_range(0, 1000), nullable=True),
        "NU_NOTA_REDACAO": Column(float, pa.Check.in_range(0, 1000), nullable=True),
        "NU_NOTA_CN": Column(float, pa.Check.in_range(0, 1000), nullable=True),
        "NU_NOTA_CH": Column(float, pa.Check.in_range(0, 1000), nullable=True),
        "NU_NOTA_LC": Column(float, pa.Check.in_range(0, 1000), nullable=True),
    },
    # strict=False permite que existam outras colunas não listadas aqui (o ENEM tem dezenas)
    strict=False, 
    name="HarmonizedSchema"
)

# Schema de Hard Validation: Aplicado APÓS a Camada de Limpeza (T2) / Feature Engineering (T4)
# É o "porteiro final" antes de salvar o arquivo .parquet analítico (Load).
# Aqui, a tolerância a nulos na variável-alvo e a erros críticos é zero.
cleaned_schema = DataFrameSchema(
    {
        "NU_ANO": Column(int, pa.Check.in_range(2017, 2025), nullable=False),
        
        # As notas NÃO PODEM conter nulos. Se contiverem, o Pandera quebra a execução (Fail-fast).
        "NU_NOTA_MT": Column(float, pa.Check.in_range(0, 1000), nullable=False),
        "NU_NOTA_REDACAO": Column(float, pa.Check.in_range(0, 1000), nullable=False),
        "NU_NOTA_CN": Column(float, pa.Check.in_range(0, 1000), nullable=False),
        "NU_NOTA_CH": Column(float, pa.Check.in_range(0, 1000), nullable=False),
        "NU_NOTA_LC": Column(float, pa.Check.in_range(0, 1000), nullable=False),
    },
    checks=[
        # Impede que o pipeline passe adiante um arquivo vazio (ex: erro silencioso num filtro)
        pa.Check(lambda df: len(df) > 0, error="O DataFrame não deve estar vazio")
    ],
    strict=False, 
    name="CleanedSchema"
)

def validate_harmonized_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica o Data Contract 'HarmonizedSchema' (Soft Validation).
    Utilizado na fronteira de saída da fase T1 (Ingestão).
    """
    logger.info("Executando validação de contrato de dados: HarmonizedSchema (Soft Validation)")
    return harmonized_schema.validate(df)

def validate_cleaned_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica o Data Contract 'CleanedSchema' (Hard Validation).
    Utilizado como guardião final antes da Exportação (Load) para o Parquet.
    """
    logger.info("Executando validação de contrato de dados: CleanedSchema (Hard Validation)")
    return cleaned_schema.validate(df)
