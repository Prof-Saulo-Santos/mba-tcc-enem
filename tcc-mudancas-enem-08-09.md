# Adaptação do TCC: De ENADE para ENEM (Observações e Mudanças)

> **Data:** 08/09/2026
> **Objetivo:** Registrar os pontos de atenção e as mudanças arquiteturais e de negócio necessárias para migrar o escopo do projeto original (ENADE) para o novo domínio (ENEM), mantendo a proposta de um pipeline escalável e defensivo (MLOps).

---

## 1. Mudança de Domínio e Variável-Alvo

*   **Público-Alvo:** Deixa-se de analisar o desempenho de universitários concluintes (ENADE) para avaliar os candidatos do ensino médio (ENEM). O volume de dados é exponencialmente maior no ENEM (milhões de candidatos vs. centenas de milhares no ENADE).
*   **Variável-Alvo (Target):** No ENADE, a predição era focada na Nota Geral (`NT_GER`). No ENEM, a variável-alvo precisa ser redefinida. Pode-se utilizar a **Nota Média** das 5 provas (Matemática, Linguagens, Ciências da Natureza, Ciências Humanas e Redação) ou focar especificamente na **Nota da Redação** (`NU_NOTA_REDACAO`), que costuma ter forte correlação socioeconômica. As faixas de classificação (Insuficiente, Regular, Bom, Excelente) deverão ser recalibradas para a régua do ENEM (0 a 1000).

## 2. Impactos na Arquitetura de Dados (Camada Anticorrupção)

O principal pilar da metodologia original (uso de *Pipes and Filters* e uma *Anti-Corruption Layer - ACL*) se mostra ainda mais necessário no ENEM, mas por motivos diferentes do ENADE:

*   **O Desafio do ENADE (Original):** Lidar com a fragmentação dos dados de 2023 em 32 arquivos separados.
*   **O Novo Desafio do ENEM (Atual):** A grande anomalia do ENEM ocorreu nas edições de **2024 e 2025**. O arquivo monolítico `MICRODADOS_ENEM_XXXX.csv` (que continha ~76 colunas com dados de perfil e notas) foi **desmembrado pelo INEP em dois arquivos distintos**:
    1.  `PARTICIPANTES_XXXX.csv`: Contém apenas dados de perfil e questionário socioeconômico (38 colunas).
    2.  `RESULTADOS_XXXX.csv`: Contém as notas e gabaritos (42 colunas).

**Ação no Pipeline de Ingestão (`reader.py` / `harmonizer.py`):**
O módulo de abstração de dados (ACL) deverá verificar o ano do dataset durante a carga.
*   Se **Ano <= 2023**: Ler o arquivo único `MICRODADOS_ENEM_XXXX.csv`.
*   Se **Ano >= 2024**: Ler `PARTICIPANTES` e `RESULTADOS` simultaneamente e executar um **JOIN (merge)** utilizando a chave primária (`NU_INSCRICAO`) para reconstruir o formato monolítico antes de injetar os dados no resto do pipeline.

## 3. Qualidade de Dados (Data Contracts) e LGPD

Os esquemas de validação (Pandera) criados para o ENADE (Soft e Hard validation) deverão ser reescritos para o dicionário de variáveis do ENEM, observando as seguintes anomalias já detectadas:

*   **Questões Socioeconômicas:** As questões `Q026` e `Q027` foram removidas pelo INEP a partir de 2019. O Data Contract final deve garantir a exclusão dessas colunas no modelo histórico, ou aceitar alto índice de valores nulos, caso contrário o Pandera interromperá a execução (Fail-fast).
*   **Colunas Transitórias:** O ENEM 2020 possui a coluna extra `TP_VERSAO_DIGITAL` que não existe nos demais anos. O contrato deve prever seu descarte.
*   **Bases Auxiliares (2022):** A base exclusiva `QUEST_HAB_ESTUDO.csv` presente apenas no ano de 2022 não deve integrar o pipeline de machine learning genérico, pois as variáveis de estudo não estarão disponíveis nas demais edições.
*   **LGPD:** O contrato de dados atuará como garantidor de que apenas variáveis pseudonimizadas cheguem à etapa de `Feature Engineering`, bloqueando o vazamento de metadados não autorizados.

## 4. Expansão Analítica (Agregando valor ao TCC)

A infraestrutura original (`Airflow`, `MLflow`, `FastAPI`, `Grafana`) atende perfeitamente ao ENEM sem nenhuma modificação. No entanto, do ponto de vista de *Data Science*, o projeto ganhará muito valor se for além da simples "previsão de nota". 

Recomenda-se adicionar as seguintes etapas na documentação e no código:
1.  **Explainability (XAI - SHAP/Feature Importance):** Demonstrar *por que* o modelo previu uma nota baixa ou alta, explicitando o peso do questionário socioeconômico e da infraestrutura da escola na nota final.
2.  **Monitoramento de Viés (Bias) e Concept Drift:** Usar o `Evidently` (já previsto na arquitetura) para medir como o modelo se degrada ao longo dos 10 anos da série histórica, especialmente avaliando se as previsões são menos acuradas para grupos minoritários ao longo do tempo.

---

### Resumo das Tarefas Práticas Imediatas:
- [ ] Alterar o script de ingestão do Airflow para suportar leitura de arquivos de múltiplos Gigabytes (o volume do ENEM exige processamento em *chunks* ou uso de bibliotecas como `Polars`/`Dask`).
- [ ] Implementar a lógica de *JOIN* condicional no `harmonizer.py` para tratar a cisão de 2024/2025.
- [ ] Atualizar os schemas do Pandera (`validator.py`) com as colunas do dicionário do ENEM.
- [ ] Refatorar os limites da variável-alvo (`NT_GER` 0-100 → `NU_NOTA_*` 0-1000).
