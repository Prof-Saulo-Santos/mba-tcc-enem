# Guia e Memória do Agente de IA (Projeto TCC MBA - Saulo Santos)

Este documento atua como **memória persistente, bússola arquitetural e instrução operacional mandatória** para qualquer novo agente de IA ou sessão de chat que assumir a continuidade deste projeto de TCC. 

---

## 1. Visão Geral e Objetivo do Projeto

### 1.1 Objetivo Acadêmico e Sociológico
O objetivo central deste trabalho de conclusão de curso (MBA em Ciência de Dados / MLOps) é **investigar e prever o determinismo social e o desempenho acadêmico dos estudantes brasileiros no ENEM** (Exame Nacional do Ensino Médio), integrando:
1. **Sociologia Educacional:** Comprovação empírica do impacto do capital cultural e econômico familiar (Bourdieu), tipo de escola, raça e gênero nas notas;
2. **Machine Learning Robusto:** Modelagem preditiva com algoritmos não lineares baseados em árvores (*Random Forest* e *XGBoost*);
3. **Engenharia de Dados & MLOps em Larga Escala:** Consolidação histórica de uma década de microdados (Big Data), inteligência semântica via NLP para resolução de deriva de esquema (*Schema/Semantic Drift*), rastreabilidade com **MLFlow**, deploy em nuvem (**FastAPI + Docker + GitHub Actions + AWS**) e orquestração contínua com **Apache Airflow**.

### 1.2 O Alvo Homologado (`TARGET_M4`)

Após rigoroso benchmark empírico multialvo sob Validação Cruzada (5-Fold CV) no laboratório de features (`03_engenharia_features.ipynb` e `scripts/analise_alvos_compara_note03.py`), a dúvida sobre o alvo ideal foi **definitivamente resolvida**:
* **Alvo Oficial Homologado:** **`TARGET_M4` (Média Aritmética das 4 Provas Objetivas da TRI)**:
  $$\text{TARGET\_M4} = \frac{\text{NU\_NOTA\_CN} + \text{NU\_NOTA\_CH} + \text{NU\_NOTA\_LC} + \text{NU\_NOTA\_MT}}{4}$$
* **Justificativa Defensiva para a Banca do TCC:**
  1. *Campeão de Previsibilidade e Menor Erro:* Alcançou o maior poder preditivo sociológico entre todos os 10 cenários avaliados ($R^2 = 0.3467$, $\text{RMSE} = 66.12$ pontos e menor Erro Relativo $\text{RMSE}/\sigma = 0.8083$), superando o `TARGET_M2` ($R^2 = 0.3362$);
  2. *Consistência Psicométrica Unidimensional:* As 4 provas da TRI medem um construto cognitivo homogêneo, comprovado por correlações de Pearson robustas ($r = 0.60$ a $0.76$) e **Alfa de Cronbach de 0.865** (alta consistência interna);
  3. *Eliminação do Ruído Subjetivo da Redação:* A prova de Redação apresentou a menor previsibilidade socioeconômica ($R^2 = 0.1942$) e menor correlação com as demais ($r \approx 0.45$ a $0.53$). A sua inclusão degrada qualquer média composta (ex.: $M4 \rightarrow M5$ derruba o $R^2$ de 0.3467 para 0.3286; $M2 \rightarrow M3$ derruba de 0.3362 para 0.3050) devido ao ruído de correção humana e critérios subjetivos.
  4. *Blindagem contra Data Leakage:* Isola completamente anomalias administrativas e de anulação de redação (`TP_STATUS_REDACAO`).

---

## 2. A Arquitetura do Projeto em Três Etapas

A esteira de desenvolvimento do projeto está estruturada rigorosamente em **três etapas evolutivas**, ilustradas nos diagramas de arquitetura do projeto (`media/pipeline-1.jpg`, `media/pipeline-2.jpg` e `media/pipeline-3.jpg`):

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 1: LABORATÓRIO DE DADOS, SELEÇÃO, NLP E MLFLOW (media/pipeline-1.jpg)            │
│ [2023] ──> [02_eda] ──> [03_features] ──> [04_nlp] ──> [2014-2023] ──> [XGBoost+MLFlow] ──> enem.pkl│
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 2: PRODUTIZAÇÃO, CONTAINERIZAÇÃO, CI/CD E NUVEM AWS (media/pipeline-2.jpg)       │
│ [enem.pkl] ──> [API FastAPI] ──> [Docker] ──> [GitHub Actions] ──> [AWS App Runner] ──> Endpoints │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 3: ORQUESTRAÇÃO BIG DATA E PRODUÇÃO EM TEMPO REAL (media/pipeline-3.jpg)         │
│ [ENEM 2024] ──> [Airflow DAG] ──> [Seleção/NLP] ──> [2014-2024] ──> [OOT Validation MLFlow]   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detalhamento da Etapa 1: Sequência de Notebooks

A Etapa 1 representa o laboratório analítico e a preparação de dados, tendo o ano de **2023 como ano-base padrão-ouro**.

### 3.1 `notebooks/01_iniciando_dados.ipynb` (ou `01_investigacao_estrutural.ipynb`)
* **Papel:** Ingestão primária dos microdados brutos do INEP, checagem volumétrica de colunas e inspeção inicial dos tipos de dados.
* **Resultado:** Mapeamento preliminar de ausentes e identificação de campos estruturais do questionário socioeconômico.

### 3.2 `notebooks/02_eda.ipynb` (Análise Exploratória de Dados)
* **Tratamento de Anomalias e Filtros Metodológicos:**
  * Filtro de presença: Mantidos apenas candidatos presentes em todas as provas (`TP_PRESENCA == 1`).
  * Saneamento de Redação: Remoção de anomalias com `TP_STATUS_REDACAO == 1` (elimina zeros espúrios de cópia, fuga ao tema ou folha em branco, ~3.5% da base).
  * Imputação Lógica de Concluintes 2023 (`TP_ST_CONCLUSAO == 2`): Local de escola preenchido a partir do local de prova; variáveis administrativas com nulos estruturais imputadas com categoria `0` ("Não informado"). Egressos (`TP_ST_CONCLUSAO == 1`) preservam 100% de nulos estruturais por regra de questionário do INEP.
* **Forma e Momentos das Distribuições de Notas:**
  * Assimetria calculada matematicamente (Matemática com $Sk = +0.100$, Ciências Humanas $Sk = -0.414$).
  * Curtose leptocúrtica extrema em Ciências da Natureza ($K = 4.341$), justificada pela alta concentração de notas em torno de 499 (50% dos alunos no intervalo de 110 pontos) associada a caudas longas de TRI.
  * Diferença entre Média e Mediana da Redação explicada pela soma discreta de 5 competências (0 a 200, passos de 40).
* **Decisão Metodológica sobre o Gráfico Pairplot (Seção 1.9):**
  * O `pairplot` de notas contra notas ($y \times y$) foi eliminado por sofrer de *overplotting* severo (mancha azul sólida em 212 mil pontos) e não ter função preditiva.
* **Análise Bivariada Demográfica $\times$ Notas (Seção 1.11):**
  * Avaliação das **5 notas oficiais** (`NU_NOTA_CN`, `NU_NOTA_CH`, `NU_NOTA_LC`, `NU_NOTA_MT` e `NU_NOTA_REDACAO`) cruzadas com Sexo, Cor/Raça e Tipo de Escola.
  * Gráficos de violinos e boxplots com notas zero excluídas (densidade pura de quem fez a prova).
  * Constatação do padrão PISA: Homens superiores em MT e CN; Mulheres com liderança expressiva em Redação (+30 a +40 pontos) e leve vantagem em LC.
  * **Cálculo do Tamanho de Efeito (*Cohen's d*):**
    * Escola Privada vs Pública: $d = 1.079$ (**Efeito Grande/Avassalador** — 86% dos alunos públicos abaixo da média privada).
    * Cor/Raça (Branca vs Preta): $d = 0.625$ (**Efeito Médio/Grande**).
    * Sexo (Masculino vs Feminino em MT): $d = 0.377$ (**Efeito Pequeno**).
  * Justificativa para **não** separar modelos por sexo: algoritmos de árvore já particionam por `TP_SEXO` nativamente, preservando a amostra total ($N \approx 212.000$) e permitindo explicabilidade marginal via SHAP no Notebook 04/05.
* **Análise Multivariada de Interação (Seção 1.18.2):**
  * Efeitos de não-linearidade cruzando Raça $\times$ Escola e Internet $\times$ Escola, justificando algoritmos não lineares (*Random Forest* e *XGBoost*).

### 3.3 `notebooks/03_engenharia_features.ipynb` (Engenharia e Seleção de Features) - *Homologado*
* **Estrutura Metodológica Oficial (Seções 1 a 7):**
  1. *Introdução e Carregamento:* Ingestão de `enem_2023_eda_purificado.parquet` (212.386 concluintes com presenças integrais e sem anomalias).
  2. *Engenharia Socioeconômica:* Criação de `RENDA_PER_CAPITA` (`Q006` ponto médio / `Q005_NUM`), que se consolidou como o preditor #1 de desempenho educacional no Brasil.
  3. *Ablação e Parcimônia Inicial:* Demonstração da redundância dos 19 bens materiais (`Q007` a `Q025`) com a renda familiar (`Q006`, Spearman $\rho$ até 0.616).
  4. *Criação dos 10 Alvos Candidatos:* Cálculo de notas individuais (`TARGET_CN`, `TARGET_CH`, `TARGET_LC`, `TARGET_MT`, `TARGET_RD`) e composições (`TARGET_M2`, `TARGET_LR`, `TARGET_M3`, `TARGET_M4`, `TARGET_M5`).
  5. *Preparação para Modelagem:* Codificação com `OrdinalEncoder` blindado para tipos Arrow/Pandas, seleção preliminar de 21 features e montagem do `df_ml`.
  6. *A Batalha dos Alvos (5-Fold CV):* Avaliação cruzada comparativa com `HistGradientBoostingRegressor` que provou a superioridade de **`TARGET_M4` ($R^2 = 0.3467$, $\text{RMSE} = 66.12$)**.
  7. *Defesa Acadêmica e Validação Estatística (`TARGET_M4`):*
     * **7.1 Validação Psicométrica:** Matriz de Pearson entre provas e **Alfa de Cronbach de 0.865**, provando alta consistência interna unidimensional na escala TRI.
     * **7.2 Auditoria de Data Leakage & Permutation:** Nenhuma feature preditora ultrapassou o limiar de 0.80 de correlação com o alvo. O *Permutation Importance* confirmou a liderança de `RENDA_PER_CAPITA`, `TP_ANO_CONCLUIU`, `TP_LINGUA` e `Q024` sem viés de Gini.
     * **7.3 A Prova da Parcimônia (Navalha de Ockham):** O modelo completo de 21 features ($R^2 = 0.3546$) versus o "Esquadrão de Elite" de 6 features ($R^2 = 0.3294$) registrou perda desprezível de apenas **7.11% de $R^2$**, justificando a economia de 71% das perguntas do questionário.
     * **7.4 Contrato Canônico e Exportação:** Persistência do dataset final homologado em **`data/processed/enem_2023_features_modelagem.parquet`** (212.386 linhas $\times$ 8 colunas: `NU_INSCRICAO`, `TARGET_M4` e as 6 features de elite).
* **O "Esquadrão de Elite" Oficial (6 Features Homologadas):**
  1. `RENDA_PER_CAPITA`: Renda familiar estimada por morador do domicílio (Feature engenhada suprema);
  2. `Q024`: Posse de computador no domicílio (Inclusão digital e ferramenta de estudo);
  3. `TP_ANO_CONCLUIU`: Frescor acadêmico / tempo decorrido desde a conclusão do Ensino Médio;
  4. `TP_LINGUA`: Língua estrangeira (Inglês vs Espanhol — forte proxy de capital cultural e letramento);
  5. `TP_SEXO`: Gênero do candidato;
  6. `Q002`: Escolaridade da mãe / mulher responsável (Capital cultural primário de Bourdieu).

### 3.4 `notebooks/04_varredura_semantica.ipynb` (Harmonização Histórica via NLP)
* **O Problema do *Semantic Drift*:** O INEP altera periodicamente os códigos das perguntas (ex.: `Q024` vira `Q021`) e sua redação textual ("Na sua residência tem computador?" vs "Em sua casa, existe computador/notebook?").
* **Solução Inteligente com NLP:**
  * Uso do modelo de Sentence Transformers **`paraphrase-multilingual-MiniLM-L12-v2`** (SBERT, 12 camadas, embeddings densos de 384 dimensões).
  * Cálculo da **Similaridade de Cosseno** entre as descrições de 2023 e as de cada edição histórica.
  * Pareamento automático e semântico dos dicionários de 2009 a 2025.
* **Veredito da Auditoria Histórica:**
  * 2009 a 2013: Descartados por ausência estrutural de perguntas essenciais no questionário.
  * **2014 a 2023 (10 Anos):** "Era de Ouro" aprovada com 100% de consistência semântica e integridade de variáveis.
* **Big Data ETL:** Script `scripts/etl_parquet.py` lê os microdados CSV pesados em chunks e converte a década de ouro em arquivos colunares comprimidos **Apache Parquet (`snappy`)**, resolvendo restrições de memória RAM (evita OOM).

### 3.5 `notebooks/05_treinamento_modelo.ipynb` (Treinamento Oficial com MLflow) - *Próximo a Construir*
* **Treinamento Escalável:** Treino do modelo campeão (**XGBoost**) alimentado pelo dataset histórico unificado de 10 anos (2014 a 2023).
* **Rastreabilidade e MLOps com MLflow:**
  * Servidor local do MLFlow para rastrear parâmetros (`learning_rate`, `max_depth`, `n_estimators`), métricas ($R^2$, RMSE, MAE) e curvas de aprendizado.
  * Geração do artefato de produção serializado: **`enem.pkl`**.
  * Interpretabilidade com **SHAP Values** para demonstrar a contribuição marginal de cada variável à banca.

---

## 4. Detalhamento da Etapa 2: Produtização, CI/CD e Deploy na AWS

Baseada no diagrama `media/pipeline-2.jpg` e `diagrama_deploy_aws.md`:

1. **Encapsulamento com FastAPI:**
   * Criação do serviço Python `src/api/` que carrega o modelo serializado `enem.pkl`.
   * Endpoints REST:
     * `POST /predict`: Recebe os 6 atributos do candidato via JSON e retorna a nota prevista (`TARGET_M2`).
     * `GET /health`: Checagem de integridade e liveness do serviço.
     * `GET /docs`: Documentação interativa Swagger/OpenAPI.
2. **Containerização com Docker:**
   * Criação de `Dockerfile` otimizado (multi-stage build) e `docker-compose.yml`.
   * Empacotamento hermético de dependências, modelo e runtime.
3. **Automação CI/CD com GitHub Actions:**
   * Workflow `.github/workflows/deploy.yml` disparado por push ou tag na branch principal.
   * Execução de testes de contrato e integração (`pytest`).
   * Build automatizado da imagem Docker e envio (*push*) para o **Amazon ECR** (*Elastic Container Registry*).
4. **Deploy e Consumo na AWS:**
   * Orquestração e subida do contêiner no **AWS App Runner** ou **AWS ECS (Fargate)**.
   * Exposição de endpoint HTTPS público para consumo live de predições.

---

## 5. Detalhamento da Etapa 3: Orquestração Big Data e Validação Out-of-Time (2024)

Baseada no diagrama `media/pipeline-3.jpg` e `diagrama_producao_2024.md`:

1. **Premissa de "Viagem no Tempo" (Out-of-Time Validation):**
   * O modelo foi treinado com o passado consolidado (2014–2023).
   * A edição do **ENEM de 2024** atua como o "futuro cego" para testar o comportamento do pipeline em ambiente de produção real.
2. **Orquestração com Apache Airflow:**
   * Criação de DAGs para:
     1. Ingestão/Download automático dos microdados brutos do ENEM 2024;
     2. Filtragem de dados brutos e seleção do escopo de features;
     3. Acionamento do nó de **NLP/SBERT** para harmonização dinâmica do dicionário de 2024;
     4. Limpeza e persistência da safra 2024 purificada em Parquet no **Amazon S3**;
     5. Integração dos dados de 2024 à base consolidada (**2014 a 2023 $\longrightarrow$ 2014 a 2024**).
3. **Auditoria de Drift no MLflow:**
   * Envio da base de 2024 purificada para o modelo `enem.pkl` em produção.
   * Registro e comparação das métricas de inferência no MLflow para auditar estabilidade e resiliência temporal (*Data Drift* e *Concept Drift*).

---

## 6. Diretrizes Técnicas e Comportamentais para o Agente de IA

1. **Tom de Voz:** Atuar como um orientador sênior de TCC e Arquiteto de MLOps. Suas respostas devem ser tecnicamente densas, metodologicamente defensáveis perante uma banca de pós-graduação e matematicamente rigorosas.
2. **Linguagem e Padrão:** Sempre responda e programe com documentação em **Português do Brasil**. Preserve o padrão PEP8, comentários limpos e código modular.
3. **Pilha Tecnológica do Repositório:**
   * Ambiente: Linux/WSL (`/home/saulo/mba/tcc/enem`).
   * Gerenciador de Pacotes: `uv` com ambiente virtual ativo em `.venv` (Python 3.12 / 3.13).
   * Principais Pacotes: `pandas`, `numpy`, `scikit-learn`, `xgboost`, `sentence-transformers`, `torch`, `mlflow`, `fastapi`, `uvicorn`, `docker`, `openpyxl`, `pyarrow`.
4. **Regra de Ouro da Modelagem:**
   * O Random Forest e o XGBoost são modelos concorrentes sob o mesmo protocolo de validação cruzada; o Random Forest não é apenas um seletor descartável, mas o benchmark de *Bagging*.
   * Nunca use a nota de uma prova para prever outra prova (evitar data leakage inter-target).
   * Manter sempre a explicabilidade por meio de valores SHAP.
5. **Estado Atual e Próxima Tarefa:**
   * **Notebook 02 (`02_eda.ipynb`) e Notebook 03 (`03_engenharia_features.ipynb`):** 100% concluídos, auditados e homologados.
   * **Artefato Canônico Exportado:** `data/processed/enem_2023_features_modelagem.parquet` (212.386 concluintes $\times$ 8 colunas: `NU_INSCRICAO`, `TARGET_M4` e as 6 features do Esquadrão de Elite).
   * **Alvo Oficial Definido:** `TARGET_M4` (Média das 4 provas objetivas da TRI: MT, LC, CN, CH), com $R^2 = 0.3467$ e Alfa de Cronbach = 0.865.
   * **Próximos Passos (Avançar com Saulo):**
     1. Revisar o Notebook `04_varredura_semantica.ipynb` para garantir o mapeamento do Esquadrão de Elite e do `TARGET_M4` ao longo dos 10 anos históricos (2014 a 2023);
     2. Construir o Notebook `05_treinamento_modelo.ipynb` (Modelagem preditiva XGBoost / LightGBM, rastreabilidade completa no MLflow, análise de SHAP values e exportação do artefato `enem.pkl`).
6. **Modo de Colaboração (Regra Mandatória):**
   * O trabalho é feito **em conjunto com o Saulo**, passo a passo. O agente **não** deve agir de forma autônoma.
   * **Toda tomada de decisão** (metodológica, de código, de dados ou de arquitetura) só pode ser aplicada **após o aval explícito do Saulo**.
   * Antes de qualquer alteração, o agente deve explicar o que pretende fazer e por quê, apresentando opções com prós e contras quando houver mais de um caminho.
   * Executar comandos, rodar análises, instalar pacotes ou criar/editar arquivos somente quando solicitado ou autorizado.
   * Fazer exatamente o que foi pedido, sem antecipar etapas futuras. Ao terminar, aguardar a próxima instrução.
