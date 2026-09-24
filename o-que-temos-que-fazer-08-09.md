# O que temos que fazer a partir de 08/09/2026

Com base no panorama completo da arquitetura MLOps já configurada (Docker, Airflow, MLflow, Pandera, FastAPI, Streamlit, MinIO) e dos módulos Python de ingestão e processamento construídos para o ENADE (Fases 1 e 2), o projeto atual fará um **Refactor Cirúrgico (Fork) da base do ENADE para o ENEM**.

Não começaremos do zero. Vamos adaptar a infraestrutura e o código existentes para o novo domínio.

### O Plano de Ação:

1. **Aproveitar 100% da Infraestrutura:** 
   O `docker-compose.yml`, o MLflow, o banco Postgres, os diretórios (`src`, `dags`, `data`) e as configurações do Airflow servem perfeitamente para o ENEM e serão mantidos.

2. **Jupyter Notebooks para Comprovação (Exploração Acadêmica):**
   Antes de injetar regras diretamente no código (`harmonizer.py`), criaremos Notebooks (`.ipynb`) para ler os dados, exibir as tabelas, gráficos e provar visual e estatisticamente as anomalias encontradas. Isso é vital para a banca examinadora do TCC entender o "porquê" das decisões arquiteturais tomadas na camada anticorrupção.

3. **Atualizar a Ingestão (`reader.py` / `harmonizer.py`):** 
   - Ao invés de lidar com os 32 fragmentos do ENADE 2023, o `reader.py` vai ler os arquivos `.csv` do ENEM.
   - O `harmonizer.py` será atualizado para fazer o **JOIN** entre `PARTICIPANTES` e `RESULTADOS` para as edições de 2024 e 2025, além de aplicar o dicionário de variáveis do ENEM (removendo `Q026`/`Q027` e lidando com `TP_VERSAO_DIGITAL`).

4. **Atualizar Contratos de Dados (`validator.py`):** 
   Trocar os schemas do Pandera do ENADE para o ENEM (adaptando a escala de notas para 0 a 1000 e refletindo os novos nomes de colunas do questionário socioeconômico e demográfico).

5. **Alimentar a `processing_dag`:** 
   Com os dados de 2017 a 2025 disponíveis localmente em `data/raw/`, rodaremos a DAG de processamento diretamente no Airflow para gerar os arquivos analíticos finais (`.parquet` otimizados) no MinIO, destravando a Fase 3 (Treinamento).

---

### Detalhamento: Jupyter Notebook (Comprovação para a Banca)

O notebook de descoberta (`01_analise_anomalias_estruturais.ipynb`) criado na pasta `notebooks/` tem o papel fundamental de atuar como um "Documento de Descoberta" para a banca examinadora, justificando o uso do nosso `harmonizer.py`. A estrutura contemplada e já gerada aborda:

1. **Contextualização:** Explicação acadêmica sobre a quebra do formato histórico em 2024.
2. **Leitura da Base 2023:** Demonstração do schema do formato unificado original.
3. **Leitura da Base 2024:** Carregamento prático das tabelas separadas `PARTICIPANTES` e `RESULTADOS`.
4. **Comprovação Prática (Inner Join):** Junção das bases via `NU_INSCRICAO` comprovando que a informação não se perdeu e justificando o uso do MERGE na engenharia de dados.
5. **Documentação LGPD:** Demonstração da ausência e remoção necessária das variáveis `Q026` e `Q027` no dicionário.
