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
│ [2023] ─> [02_eda] ─> [03_features] ─> [04_nlp] ─> [05_consolidacao] ─> [06_xgboost+mlflow] ─> enem.pkl│
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
* **Big Data ETL Homologado:** O script `scripts/etl_parquet.py` consome dinamicamente o contrato `data/processed/schema_mapping_historico.json`, processa os microdados CSV pesados em chunks de 500.000 linhas, aplica o filtro de presença integral, calcula o alvo oficial `TARGET_M4` e converte os dados em arquivos colunares **Apache Parquet (`snappy`)**. A safra do **ENEM 2014** foi processada e validada com sucesso, gerando `data/processed/enem_2014_gold.parquet` (5.947.909 candidatos purificados $\times$ 17 colunas, 95.91 MB, média TRI $502.98 \pm 67.13$).

### 3.5 `notebooks/05_consolidacao_historica.ipynb` (Consolidação Censitária 2014–2023) - *Homologado*
* **Consolidação Longitudinal da Década de Ouro:** Ingestão em *chunks* de 500.000 linhas dos 10 CSVs brutos (`2014` a `2023`, 25,45 GB, 56.568.785 inscritos brutos varridos) guiada estritamente pelo contrato `data/processed/schema_mapping_historico.json`.
* **Harmonização de *Value Drift* e Deflação Estrutural:**
  * Conversão de `RENDA_PER_CAPITA` diretamente em **múltiplos de Salários Mínimos por morador** (`float32`), neutralizando a inflação nominal da década;
  * Harmonização documental de 2014/2015 nas variáveis `Q024` (`Q010` em 2014), `Q002` e `TP_ANO_CONCLUIU` (escala estacionária `{0..9}`).
* **Compactação de Memória (*Downcasting*):** Redução de 64 bytes/linha para **15,00 bytes/linha** (`5 × int8 + 2 × float32 + 1 × int16`), consolidando **37.593.629 candidatos elegíveis** (zero nulos, zero duplicatas, `TARGET_M4` médio `511,05 ± 70,97`) em **537,78 MB de RAM** e **153,17 MB em disco** (`data/processed/enem_2014_2023_consolidado.parquet` + `data/processed/contrato_consolidacao_2014_2023.json`).

### 3.6 `notebooks/06_treinamento_modelo.ipynb` (Treinamento Oficial com MLflow) - *Homologado*
* **Particionamento Censitário Anti-Leakage em Baixa Memória:** Ingestão de `37.593.629` registros (`537,78 MB` RAM) e divisão estratificada por `NU_ANO` via máscara `uint8` (`8,74s`, pico de partições `552,09 MB` RAM): `df_fit` (`72%`, `27.067.413`), `df_val_es` dedicado a *Early Stopping* e Curva de Aprendizado (`8%`, `3.007.490`) e Holdout Cego intocável `df_test` (`20%`, `7.518.726`). Coluna `NU_ANO` estritamente bloqueada na matriz `X` para impedir *Temporal Leakage*.
* **Treinamento Escalável em 3 Estágios:**
  1. *Estágio 1 — Benchmark 5-Fold CV (`N = 1.000.000`) & Tuning (`3-Fold CV`, 11 Nested Runs):* `DummyRegressor` ($R^2 = 0.0000$, $\text{RMSE} = 71.00$) $\rightarrow$ `Ridge` ($R^2 = 0.2836$, $\text{RMSE} = 60.09$) $\rightarrow$ `RandomForestRegressor` ($R^2 = 0.3337$, $\text{RMSE} = 57.95$) $\rightarrow$ `XGBRegressor` ($R^2 = 0.3359$, $\text{RMSE} = 57.86$), provando ganho não linear de **+5,23 pp de $R^2$ (+19,1% de variância explicada relativa no Holdout)** sobre o baseline linear nas mesmas 6 features. Melhor configuração `XGB-01`: `max_depth=5`, `learning_rate=0.1`, `min_child_weight=30`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`.
  2. *Estágio 2 — Curva de Aprendizado Escalável (`50k` $\rightarrow$ `15M` avaliados em `3,01M`):* Fechamento assintótico do gap treino-validação (`57,76` vs. `57,73` pts em `15M`, $R^2 = 0.33716$), confirmando ausência de *overfitting*.
  3. *Estágio 3 — Disputa Final no Holdout Cego (`7.518.726` alunos) & Validação Out-of-Time Interna:*
     * **Campeão Homologado (`XGBRegressor` `hist`, `27,07M` Fit + `3,01M` ES, `best_iteration = 649`):** **$R^2 = 0.33780$**, **$\text{RMSE} = 57.7439$ pts**, **$\text{MAE} = 45.5904$ pts**, $\text{RMSE}/\sigma = 0.81376$ e latência de **`81,15 ms / 10k` amostras** (superando o `RandomForestRegressor` em `3,0M` com $R^2 = 0.33606$, $\text{RMSE} = 57.8198$ pts e `124,42 ms / 10k`, sendo **35% mais rápido** em inferência).
     * **Estabilidade Longitudinal (`2014–2023`) e Caso TRI `2018`:** $R^2 \in [0.3120, 0.3631]$ em 9 das 10 edições (pico de $R^2 = 0.36314$ na pandemia de `2020`); queda pontual do $R^2$ não centrado em `2018` ($0.22595$, viés `-23,81 pts`) explicada pelo deslocamento histórico da média real da TRI do INEP em 2018 (`533,54 pts`), comprovando que o modelo não memoriza o ano da prova.
     * **Validação *Out-of-Time* Interna (`Treino 2014–2022` $\rightarrow$ `Teste Cego 2023`, `N = 2.678.264`):** **$R^2 = 0.31842$**, **$\text{RMSE} = 67.6232$ pts**, **$\text{MAE} = 52.8526$ pts**, $\text{RMSE}/\sigma = 0.82558$ ($\Delta R^2 = -0.00293$ frente ao Holdout *in-sample* de 2023), atestando estacionariedade temporal para a Etapa 3 (ENEM 2024).
* **Explicabilidade Sociológica Exata (TreeSHAP em `10.000` candidatos do Holdout):** Valor base $\mathbb{E}[f(X)] = 511.04$ pts (erro de aditividade de Shapley `1,26e-03` pts). Liderança isolada de `RENDA_PER_CAPITA` (**`18,483 pts`** de `|SHAP|` médio, **`30,10%`** do impacto total, amplitude de `127,89 pts` entre `-41,93` e `+85,96` pts com curva côncava de retorno marginal), seguida por `TP_LINGUA` (`10,895 pts` / `17,74%`), `Q024` (`9,487 pts` / `15,45%`), `TP_ANO_CONCLUIU` (`8,958 pts` / `14,59%`), `Q002` (`8,642 pts` / `14,07%`) e `TP_SEXO` (`4,946 pts` / `8,05%`).
* **Rastreabilidade MLflow e Artefatos de Produção:** Backend **MLflow 3.17.2** (`sqlite:///mlflow.db` + `./mlruns`, **20/20 runs `FINISHED`**) com modelo registrado **`enem_target_m4_producao` Versão 1 (`READY`, `run_id = 8b4ed2c387044363968b6088078bdf2d`)**. Exportação do estimador puro em **`models/enem.pkl`** (`1,727 MB`, SHA-256 `114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f`), backup nativo `models/enem_xgboost.ubj` (`1,712 MB`), contrato `models/enem_model_card.json`, auditoria `models/auditoria_holdout_por_ano_2014_2023.csv`, 7 figuras em `media/nb06_figuras/`, guia `passo-a-passo-06.md` e roteiro de defesa `slides-06.md`.

---

## 4. Detalhamento da Etapa 2: Produtização, CI/CD e Deploy na AWS - *Homologada*

Baseada no diagrama `media/pipeline-2.jpg`, `diagrama_deploy_aws.md`, `passo-a-passo-07-api-docker.md` e `slides-07.md`:

1. **Encapsulamento com FastAPI (`src/api/`):**
   * Serviço Python modular (`src/api/main.py`, `src/api/model_loader.py` e `src/api/schemas.py`) carregando `models/enem.pkl` e `models/enem_model_card.json` via padrão *Singleton* no `lifespan`.
   * Validação estrita em Pydantic v2 com `extra="forbid"` (bloqueio automático `HTTP 422` contra variáveis proibidas como `NU_ANO`).
   * Endpoints REST homologados: `GET /health` (SHA-256), `GET /info` (linhagem MLflow), `POST /predict` (individual), `POST /predict/batch` (vetorial em lote, `6,49 ms`) e `GET /docs` (Swagger UI).
2. **Suíte Automatizada de Testes (`tests/`):**
   * `25/25 PASSED` no `pytest` (`tests/test_api_contract.py` e `tests/test_model_inference.py`), validando contrato HTTP, fronteiras psicométricas, paridade matemática bit-a-bit com o estimador puro, direcionalidade sociológica de Bourdieu e SLA de latência.
3. **Containerização Multi-Stage FinOps (`Dockerfile` & `docker-compose.yml`):**
   * Manifesto enxuto `requirements-api.txt` (apenas os 8 pacotes de *serving* nas versões exatas do treino) e `.dockerignore` reduzindo o contexto para `~2 MB`.
   * Imagem OCI `enem-target-m4-api:v1` com **`515 MB` Content Size** (`1,47 GB` em disco), biblioteca OpenMP `libgomp1`, usuário não-root (`appuser`, UID 1000) e `HEALTHCHECK` nativo.
4. **Automação CI/CD com GitHub Actions (`.github/workflows/deploy.yml`):**
   * Pipeline em 3 Jobs encadeados: `quality-gate-ci` (SHA-256 + Pytest) $\rightarrow$ `docker-smoke-test` (build e teste HTTP E2E no runner) $\rightarrow$ `deploy-aws` (Amazon ECR + AWS App Runner com trava condicional FinOps).

---

## 5. Detalhamento da Etapa 3: Orquestração Local em Docker e Governança Autônoma (2024/2025)

Baseada no diagrama `media/pipeline-3.jpg` e `diagrama_producao_2024.md`:

1. **Arquitetura FinOps (Plano Pesado Local Containerizado):**
   * Airflow + SBERT + XGBoost + MLflow rodam localmente containerizados, evitando custos ociosos de processamento pesado em nuvem.
2. **Fluxo Ordenado da DAG Autônoma (4 Estágios):**
   * **(1) Ingestão:** Recepção e inspeção estrutural dos microdados e dicionário da nova edição (`2024` ou `2025`).
   * **(2) NLP/SBERT no Dicionário ANTES da Seleção:** Execução do `paraphrase-multilingual-MiniLM-L12-v2` sobre o dicionário para descobrir dinamicamente quais colunas equivalem às 6 variáveis do Esquadrão de Elite antes do corte colunar.
   * **(3) Seleção + Harmonização + Downcasting:** Extração das 6 features mapeadas, deflação da `RENDA_PER_CAPITA` em Salários Mínimos do respectivo ano, harmonização de escalas e compactação para `15 bytes/linha` em Parquet.
   * **(4) Bifurcação Automática (`BranchPythonOperator`):**
     * **Cenário A — Safra com Notas Homologadas (`2024`):** Passa pelo **Gatekeeper Out-of-Time** avaliando `enem.pkl v1`; se aprovado no SLA, concatena a base histórica (`2014–2024`), retreina o `XGBRegressor` e aciona o **MLflow como Juiz Champion vs. Challenger** para promover `enem.pkl v2`.
     * **Cenário B — Safra sem Notas / Pré-Prova (`2025`):** Desvia para **Modo Inferência em Lote (*Batch Scoring*)** + **Auditoria de Data Drift de $X$** (*Population Stability Index* — PSI e teste KS).

---

## 6. Diretrizes Técnicas e Comportamentais para o Agente de IA

1. **Tom de Voz:** Atuar como um orientador sênior de TCC e Arquiteto de MLOps. Suas respostas devem ser tecnicamente densas, metodologicamente defensáveis perante uma banca de pós-graduação e matematicamente rigorosas.
2. **Linguagem e Padrão:** Sempre responda e programe com documentação em **Português do Brasil**. Preserve o padrão PEP8, comentários limpos e código modular.
3. **Pilha Tecnológica do Repositório:**
   * Ambiente: Linux/WSL (`/home/saulo/mba/tcc/enem`).
   * Gerenciador de Pacotes: `uv` com ambiente virtual ativo em `.venv` (Python 3.12 / 3.13).
   * Principais Pacotes: `pandas`, `numpy`, `scikit-learn`, `xgboost`, `shap`, `sentence-transformers`, `torch`, `mlflow`, `fastapi`, `uvicorn`, `docker`, `openpyxl`, `pyarrow`.
4. **Regra de Ouro da Modelagem:**
   * O Random Forest e o XGBoost são modelos concorrentes sob o mesmo protocolo de validação cruzada; o Random Forest não é apenas um seletor descartável, mas o benchmark de *Bagging*.
   * Nunca use a nota de uma prova para prever outra prova (evitar data leakage inter-target).
   * Manter sempre a explicabilidade por meio de valores SHAP.
5. **Estado Atual e Próxima Tarefa:**
   * **Etapa 1 Integralmente Concluída e Homologada:** Todos os notebooks da esteira analítica — `01_investigacao_estrutural.ipynb`, `02_eda.ipynb`, `03_engenharia_features.ipynb`, `04_varredura_semantica.ipynb`, `05_consolidacao_historica.ipynb` e `06_treinamento_modelo.ipynb` — estão 100% executados, auditados e homologados (com guias `passo-a-passo-05.md`, `passo-a-passo-06.md` e roteiros de defesa `slides-03.md`, `slides-04.md`, `slides-05.md` e `slides-06.md`).
   * **Etapa 2 Integralmente Concluída e Homologada:** Microserviço FastAPI (`src/api/`), suíte de 25 testes `pytest` (`tests/`), containerização multi-stage enxuta (`Dockerfile`, `docker-compose.yml`, `requirements-api.txt`, `515 MB` OCI) e esteira CI/CD GitHub Actions (`.github/workflows/deploy.yml`) 100% implementados, testados e documentados em `passo-a-passo-07-api-docker.md` e `slides-07.md`.
   * **Artefatos Canônicos Exportados:**
     * `data/processed/enem_2023_features_modelagem.parquet` (212.386 concluintes $\times$ 8 colunas: `NU_INSCRICAO`, `TARGET_M4` e as 6 features do Esquadrão de Elite);
     * `data/processed/schema_mapping_historico.json` (Contrato canônico de mapeamento semântico 2014–2024 para ETL e Airflow);
     * `data/processed/enem_2014_gold.parquet` (5.947.909 candidatos purificados $\times$ 17 colunas, 95.91 MB, safra histórica inicial da Década de Ouro);
     * `data/processed/enem_2014_2023_consolidado.parquet` + `data/processed/contrato_consolidacao_2014_2023.json` (37.593.629 candidatos $\times$ 8 colunas, 153,17 MB em disco, 537,78 MB em RAM);
     * `models/enem.pkl` (`XGBRegressor` campeão puro, `1,727 MB`, SHA-256 `114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f`, Holdout `7,52M` $R^2 = 0.33780$, $\text{RMSE} = 57.7439$ pts; OOT `2023` $R^2 = 0.31842$) + `models/enem_xgboost.ubj` + `models/enem_model_card.json` + `models/auditoria_holdout_por_ano_2014_2023.csv` + Model Registry MLflow `enem_target_m4_producao` v1 (`sqlite:///mlflow.db`).
   * **Alvo Oficial Definido:** `TARGET_M4` (Média das 4 provas objetivas da TRI: MT, LC, CN, CH), com $R^2 = 0.3467$ (ano-base 2023) / $R^2 = 0.33780$ (censo decenal 2014–2023) e Alfa de Cronbach = 0.865.
   * **Próximo Passo (Avançar com Saulo):**
     * Iniciar a **Etapa 3: Orquestração Local em Docker com Apache Airflow Autônomo (2024/2025)** (`Ingestão -> NLP/SBERT no dicionário ANTES da seleção -> Seleção + Harmonização + Downcasting -> Bifurcação 2024 [Gatekeeper OOT + Retreino XGBoost + MLflow Champion vs. Challenger] vs. 2025 [Inferência em Lote + Data Drift de X]`).
6. **Modo de Colaboração (Regra Mandatória):**
   * O trabalho é feito **em conjunto com o Saulo**, passo a passo. O agente **não** deve agir de forma autônoma.
   * **Toda tomada de decisão** (metodológica, de código, de dados ou de arquitetura) só pode ser aplicada **após o aval explícito do Saulo**.
   * Antes de qualquer alteração, o agente deve explicar o que pretende fazer e por quê, apresentando opções com prós e contras quando houver mais de um caminho.
   * Executar comandos, rodar análises, instalar pacotes ou criar/editar arquivos somente quando solicitado ou autorizado.
   * Fazer exatamente o que foi pedido, sem antecipar etapas futuras. Ao terminar, aguardar a próxima instrução.
