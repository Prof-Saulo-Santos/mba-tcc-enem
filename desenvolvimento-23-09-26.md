# Diário de Desenvolvimento: 23 de Setembro de 2026

## O Veredito Histórico: A "Era de Ouro" (2014-2023)

Hoje rodamos com sucesso a **Auditoria de Harmonização Histórica (Schema Drift)** em 15 anos de microdados brutos do ENEM. O script varreu os cabeçalhos das dezenas de gigabytes de dados e nos forneceu uma Matriz de Decisão cirúrgica:

1. **2009, 2010 e 2013:** Falharam na auditoria. Houve drásticas mudanças no dicionário de dados (ausência de colunas vitais como Renda, Computador e Ano de Conclusão).
2. **2014 a 2023 (10 Anos):** Passaram com **100% de integridade**. O Dicionário de Dados do INEP se manteve estável para todas as variáveis do nosso "Esquadrão de Elite".

**Decisão Metodológica:** Para blindar o TCC contra questionamentos da banca sobre imputação de dados, excluiremos os anos com anomalias e focaremos o treinamento do modelo em uma janela histórica cravada de **uma década (2014 a 2023)**. O modelo terá robustez sociológica inquestionável, pois será validado ao longo de 10 anos de provas.

## O Desafio de Big Data (A Etapa ETL)

Com 10 anos de dados selecionados, enfrentamos o problema clássico de Big Data: a volumetria.
Tentar ler 10 anos de microdados em CSV usando Pandas no pipeline de treinamento do `MLflow` causaria um estouro de memória (Out-of-Memory / OOM).

**A Solução de Engenharia (Compressão Colunar):**
A próxima etapa do desenvolvimento é criar o pipeline de **ETL (Extract, Transform, Load)**.
O script `scripts/etl_parquet.py` deverá:
1. Ler os pesados arquivos CSVs originais limitando o escopo estritamente para as nossas 8 variáveis (`usecols`).
2. Remover dados nulos dos alvos (candidatos ausentes).
3. Salvar o resultado no formato binário, comprimido e colunar **Apache Parquet**.

## O Ponto de Discussão Arquitetural

Precisamos definir como o Airflow orquestrará a conversão para Parquet.
Temos dois caminhos arquiteturais clássicos de Engenharia de Dados:
- **Caminho A (Monolítico):** Juntar os 10 anos de CSV e gerar apenas 1 arquivo gigante `historico_enem_2014_2023.parquet`.
- **Caminho B (Particionado):** Processar e salvar cada ano individualmente (ex: `enem_2014.parquet`, `enem_2015.parquet`).
