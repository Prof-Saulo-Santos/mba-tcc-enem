# Guia e Memória do Agente de IA (Projeto TCC MBA - Saulo Santos)

Este documento atua como **memória persistente, bússola arquitetural e instrução operacional mandatória** para qualquer novo agente de IA ou sessão de chat que assumir a continuidade deste projeto de TCC. 

---

## 1. Visão Geral e Objetivo do Projeto

### 1.1 Objetivo Acadêmico e Sociológico
O objetivo central deste trabalho de conclusão de curso (MBA em Ciência de Dados / MLOps) é **investigar e prever o determinismo social e o desempenho acadêmico dos estudantes brasileiros no ENEM** (Exame Nacional do Ensino Médio), integrando:
1. **Sociologia Educacional:** Comprovação empírica do impacto do capital cultural e econômico familiar (Bourdieu), tipo de escola, raça e gênero nas notas;
2. **Machine Learning Robusto:** Modelagem preditiva com algoritmos não lineares baseados em árvores (*Random Forest* e *XGBoost*);
3. **Engenharia de Dados & MLOps em Larga Escala:** Consolidação histórica de uma década de microdados (`2014–2023`, Big Data), inteligência semântica via NLP para resolução de deriva de esquema (*Schema/Semantic Drift*), rastreabilidade com **MLflow** e deploy em nuvem (**FastAPI + Docker + GitHub Actions + AWS**).

### 1.2 O Alvo Homologado (`TARGET_M4`)

Após rigoroso benchmark empírico multialvo sob Validação Cruzada (5-Fold CV) no laboratório de features (`03_engenharia_features.ipynb`), a dúvida sobre o alvo ideal foi **definitivamente resolvida**:
* **Alvo Oficial Homologado:** **`TARGET_M4` (Média Aritmética das 4 Provas Objetivas da TRI)**:
  $$\text{TARGET\_M4} = \frac{\text{NU\_NOTA\_CN} + \text{NU\_NOTA\_CH} + \text{NU\_NOTA\_LC} + \text{NU\_NOTA\_MT}}{4}$$
* **Justificativa Defensiva para a Banca do TCC:**
  1. *Campeão de Previsibilidade e Menor Erro Relativo:* Alcançou o maior poder preditivo sociológico entre os 6 alvos avaliados na escala TRI ($R^2 = 0.3743$, $\text{RMSE} = 64.4818$ pontos e menor Erro Relativo $\text{RMSE}/\sigma = 0.7910$ com 19 features; e $R^2 = 0.3397$ com as 6 features do Esquadrão de Elite), superando `TARGET_M2` ($R^2 = 0.3653$, $\text{RMSE}/\sigma = 0.7967$) em 5 de 5 folds;
  2. *Consistência Psicométrica Unidimensional:* As 4 provas da TRI medem um construto cognitivo homogêneo, comprovado por correlações de Pearson robustas ($r = 0.601$ a $0.760$), **Alfa de Cronbach de 0.865**, 1º Componente Principal retendo `74.48%` da variância conjunta e correlação de `0.9967` de `TARGET_M4` com o fator geral (`g`);
  3. *Eliminação do Ruído Subjetivo da Redação:* A nota de Redação (`NU_NOTA_REDACAO`) foi expurgada *a priori* por incompatibilidade psicométrica (avaliada pela Teoria Clássica dos Testes — TCT, em soma discreta de 5 competências em passos de 40 pontos — frente à escala contínua da TRI) e pelo ruído subjetivo de correção humana;
  4. *Blindagem contra Data Leakage:* Isola completamente anomalias administrativas e de anulação de redação (`TP_STATUS_REDACAO`).

---

## 2. A Arquitetura do Projeto em Duas Etapas (e Corte em 2023 por LGPD)

A esteira de desenvolvimento do projeto está estruturada em **duas etapas consolidadas** (`media/pipeline-1.jpg` e `media/pipeline-2.jpg`):

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 1: LABORATÓRIO DE DADOS, SELEÇÃO, NLP E MLFLOW (media/pipeline-1.jpg)            │
│ [2014–2023] ─> [02_eda] ─> [03_features] ─> [04_nlp] ─> [05_consolidacao] ─> [06_xgboost+mlflow] ─> enem.pkl│
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 2: PRODUTIZAÇÃO, CONTAINERIZAÇÃO, CI/CD E NUVEM AWS (media/pipeline-2.jpg)       │
│ [enem.pkl] ──> [API FastAPI] ──> [Docker] ──> [GitHub Actions] ──> [AWS App Runner] ──> Endpoints │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

> **Decisão Arquitetural sobre 2024 e 2025 (Barreira LGPD):** O processamento inicialmente planejado para as safras de 2024 e 2025 (Etapa 3) foi **encerrado do escopo de execução** após a constatação de que, a partir de 2024, o INEP separou os microdados em tabelas distintas sem chave identificadora (`PARTICIPANTES` vs. `RESULTADOS`) propositalmente por adequação à LGPD — impossibilitando o pareamento determinístico entre variáveis socioeconômicas (`X`) e notas (`y`). Assim, o recorte histórico censitário encerra-se em **2023**, com generalização temporal comprovada via **Validação *Out-of-Time* Interna (`2014–2022 -> 2023`)** no Notebook 06.

---

## 3. Detalhamento da Etapa 1: Sequência de Notebooks

A Etapa 1 representa o laboratório analítico e a preparação de dados, tendo o ano de **2023 como ano-base padrão-ouro**.

### 3.1 `notebooks/01_investigacao_estrutural.ipynb`
* **Papel:** Ingestão e diagnóstico estrutural dos microdados brutos do INEP (`2009–2025`), checagem volumétrica de colunas e detecção da ruptura estrutural a partir de 2024 (`PARTICIPANTES` vs. `RESULTADOS`).
* **Resultado:** Mapeamento preliminar de mudanças de layout, identificação de campos do questionário socioeconômico e alerta inicial para a cisão de 2024/2025.

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
  * **Cálculo do Tamanho de Efeito (*Cohen's d* — Notas de Matemática):**
    * Escola Privada vs Pública: $d = 1.079$ (**Efeito Grande/Avassalador** — 86% dos alunos públicos abaixo da média privada).
    * Cor/Raça (Branca vs Preta): $d = 0.625$ (**Efeito Médio/Grande**).
    * Sexo (Masculino vs Feminino em MT): $d = 0.377$ (**Efeito Pequeno**).
  * Justificativa para **não** separar modelos por sexo: algoritmos de árvore já particionam por `TP_SEXO` nativamente, preservando a amostra total ($N = 212.386$) e permitindo explicabilidade marginal via **TreeSHAP no Notebook 06**.
* **Análise Multivariada de Interação (Seção 1.18.2):**
  * Efeitos de não-linearidade cruzando Raça $\times$ Escola e Internet $\times$ Escola, justificando algoritmos não lineares (*Random Forest* e *XGBoost*).

### 3.3 `notebooks/03_engenharia_features.ipynb` (Engenharia e Seleção de Features) - *Homologado*
* **Estrutura Metodológica Oficial (Seções 1 a 7):**
  1. *Introdução e Carregamento:* Ingestão de `enem_2023_eda_purificado.parquet` (212.386 concluintes com presenças integrais e sem anomalias).
  2. *Engenharia Socioeconômica e Redundância de Bens:* Criação de `RENDA_PER_CAPITA` (`Q006` ponto médio / `Q005_NUM`) e análise de correlação de Spearman dos 19 bens materiais (`Q007` a `Q025`) com a renda per capita (liderança de `Q024` com $\rho = 0.575$ e carro `Q010` com $\rho = 0.550$).
  3. *Saneamento Teórico e Criação dos 6 Alvos da TRI:* Expurgo *a priori* de `NU_NOTA_REDACAO` (incompatibilidade psicométrica TCT vs. TRI e ruído subjetivo) e criação das 4 provas isoladas (`TARGET_MT`, `TARGET_LC`, `TARGET_CN`, `TARGET_CH`) e 2 composições (`TARGET_M2`, `TARGET_M4`).
  4. *Estudo de Ablação Progressiva (Navalha de Ockham):* Demonstração de que `Q024` adiciona `+3.18 p.p.` no $R^2$ sobre a renda, enquanto carro `Q010` soma apenas `+0.03 p.p.` e os demais 17 bens juntos `+1.84 p.p.`.
  5. *Preparação para Modelagem:* Codificação blindada para tipos Arrow/Pandas, seleção preliminar de **19 features auditadas** e montagem de `df_ml` (`212.386 × 25`, zero nulos).
  6. *A Batalha dos Alvos (5-Fold CV):* Avaliação cruzada comparativa com `HistGradientBoostingRegressor` que provou a superioridade de **`TARGET_M4`** ($R^2 = 0.3743$, $\text{RMSE} = 64.4818$ pts, $\text{RMSE}/\sigma = 0.7910$), superando `TARGET_M2` ($R^2 = 0.3653$) em 5 de 5 folds.
  7. *Defesa Acadêmica e Validação Estatística (`TARGET_M4`):*
     * **7.1 Validação Psicométrica:** Matriz de Pearson entre provas ($r = 0.601$ a $0.760$), **Alfa de Cronbach de 0.865**, 1º Componente Principal retendo `74.48%` da variância e correlação `0.9967` de `TARGET_M4` com o fator geral (`g`).
     * **7.2 Auditoria de Data Leakage & Permutation:** Nenhuma feature preditora ultrapassou o limiar de 0.80 de correlação linear com o alvo (pico $|r| = 0.4765$ em `Q006`). O *Permutation Importance* confirmou a liderança de `TP_ANO_CONCLUIU`, `RENDA_PER_CAPITA`, `TP_LINGUA` e `Q024` sem viés de Gini.
     * **7.3 A Prova da Parcimônia (Navalha de Ockham):** O modelo completo de **19 features** ($R^2 = 0.3743$, $\text{RMSE} = 64.4818$) versus o "Esquadrão de Elite" titular de **6 features** ($R^2 = 0.3397$, $\text{RMSE} = 66.2362$) reduziu **68,4%** das variáveis e **60,0%** do tempo de treino preservando **90,8%** do $R^2$ (queda absoluta de apenas `3,45 p.p.` e `+1,75` pts no RMSE).
     * **7.4 Contrato Canônico e Exportação:** Validação do subconjunto de 2023 (212.386 concluintes) e persistência do manifesto canônico em **`data/processed/contrato_features_modelagem.json`** (especificação das 6 features de elite e `TARGET_M4` para os Notebooks 04, 05 e 06).
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
  * Pareamento automático e semântico dos dicionários de `2009` a `2025`, com auditoria física amostral em `2014–2024` registrando `integracao_2024_aprovada: false` pela ausência de chave/alinhamento documentado entre `PARTICIPANTES_2024.csv` e `RESULTADOS_2024.csv`.
* **Veredito da Auditoria Histórica:**
  * 2009 a 2013: Descartados por ausência estrutural de perguntas essenciais no questionário.
  * **2014 a 2023 (10 Anos):** "Era de Ouro" aprovada com 100% de consistência semântica e integridade de variáveis.
* **Piloto Histórico de Big Data ETL (Arquivado na tag `archive/pre-faxina-2026-11`):** Como validação preliminar antes da consolidação definitiva no Notebook 05, o antigo script `scripts/etl_parquet.py` consumiu `data/processed/schema_mapping_historico.json` e gerou o piloto `enem_2014_gold.parquet` (5.947.909 candidatos $\times$ 17 colunas, 95,91 MB). O fluxo oficial completo (`2014–2023`) foi integralmente consolidado pelo Notebook 05.

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
     * **Validação *Out-of-Time* Interna (`Treino 2014–2022` $\rightarrow$ `Teste Cego 2023`, `N = 2.678.264`):** **$R^2 = 0.31842$**, **$\text{RMSE} = 67.6232$ pts**, **$\text{MAE} = 52.8526$ pts**, $\text{RMSE}/\sigma = 0.82558$ ($\Delta R^2 = -0.00293$ frente ao Holdout *in-sample* de 2023), atestando estacionariedade temporal e capacidade de generalização em safras inéditas mesmo com o encerramento censitário em 2023 pela barreira LGPD.
* **Explicabilidade Sociológica Exata (TreeSHAP em `10.000` candidatos do Holdout):** Valor base $\mathbb{E}[f(X)] = 511.04$ pts (erro de aditividade de Shapley `1,26e-03` pts). Liderança isolada de `RENDA_PER_CAPITA` (**`18,483 pts`** de `|SHAP|` médio, **`30,10%`** do impacto total, amplitude de `127,89 pts` entre `-41,93` e `+85,96` pts com curva côncava de retorno marginal), seguida por `TP_LINGUA` (`10,895 pts` / `17,74%`), `Q024` (`9,487 pts` / `15,45%`), `TP_ANO_CONCLUIU` (`8,958 pts` / `14,59%`), `Q002` (`8,642 pts` / `14,07%`) e `TP_SEXO` (`4,946 pts` / `8,05%`).
* **Rastreabilidade MLflow e Artefatos de Produção:** Backend remoto **MLflow 3.17.2** (`PostgreSQL 16` em Docker `:5432` + *Artifact Store* no **Amazon S3** `s3://tcc-enem-saulo-mlops-703671922740/mlflow-artifacts`, substituindo o `sqlite:///mlflow.db` inicial) com modelo registrado **`enem_target_m4_producao` Versão 1 (`URI = models:/m-ea7931423f5141379ff97886636ae0ea`, `run_id = 6490c396b0e04147b156bedb0c8af9f7`, reexecutado em `21/11/2026` com `17` objetos / `~2,49 MiB` auditados no S3)**. Exportação do estimador puro em **`models/enem.pkl`** (`1,727 MB`, SHA-256 `114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f`), backup nativo `models/enem_xgboost.ubj` (`1,712 MB`), contrato `models/enem_model_card.json`, auditoria `models/auditoria_holdout_por_ano_2014_2023.csv`, 7 figuras em `media/nb06_figuras/`, guias `docs/passo-a-passo-06.md` e `docs/guia-estudo-mlflow-postgresql-s3.md` e roteiro de defesa `docs/slides-06.md`.

---

## 4. Detalhamento da Etapa 2 e Evolução MLOps (Arquitetura Desacoplada por Planos) - *Homologada*

Baseada em `media/pipeline-2.jpg`, `docs/etapa-02-passo-a-passo.md`, `docs/estudos-futuros.md`, `docs/diagrama_deploy_aws.md`, `docs/passo-a-passo-07-api-docker.md` e nos 3 guias de estudo (`observabilidade`, `terraform-dvc-s3`, `mlflow-postgresql-s3`):

1. **Encapsulamento com FastAPI e Observabilidade (`src/api/`, `monitoring/`):**
   * Serviço Python modular (`src/api/main.py`, `src/api/model_loader.py`, `src/api/schemas.py`, `src/api/metrics.py`) carregando `models/enem.pkl` e `models/enem_model_card.json` via padrão *Singleton* no `lifespan`.
   * Validação estrita em Pydantic v2 com `extra="forbid"` (bloqueio automático `HTTP 422` contra variáveis proibidas como `NU_ANO`) e instrumentação Prometheus (`prometheus-client==0.26.0`) sem explosão de cardinalidade.
   * Endpoints REST homologados: `GET /health` (SHA-256), `GET /info` (linhagem MLflow), `GET /metrics` (Prometheus), `POST /predict` (individual), `POST /predict/batch` (vetorial em lote) e `GET /docs` (Swagger UI).
   * Stack local de observabilidade (`profiles: ["monitoring"]` em `docker-compose.yml`): `Prometheus` (`:9090`, `monitoring/prometheus/prometheus.yml`) + `Grafana` (`:3000`, dashboard provisionado `enem_api_observability.json` com 10 painéis).
2. **Suíte Automatizada de Testes e Qualidade Estática (`tests/`, `pyproject.toml`):**
   * `26/26 PASSED` no `pytest` (`tests/test_api_contract.py` e `tests/test_model_inference.py`), validando contrato HTTP, exposição `/metrics`, fronteiras psicométricas, paridade matemática bit-a-bit com o estimador puro, direcionalidade sociológica de Bourdieu e SLA de latência, além de `ruff` e `mypy` configurados em `pyproject.toml`.
3. **Containerização Multi-Stage, MLflow Remoto & Dados Versionados (`Dockerfile`, `Dockerfile.mlflow`, `.dvc/`):**
   * Manifesto enxuto `requirements-api.txt` (9 pacotes de *serving*, incluindo `prometheus-client==0.26.0`) e `.dockerignore` reduzindo o contexto para `~2 MB`; imagem OCI `enem-target-m4-api:v1` (`515 MB` Content Size na API base, `libgomp1`, `appuser` não-root, `HEALTHCHECK`).
   * Profile `mlops` em `docker-compose.yml`: `postgres:16-alpine` (`:5432`) + `Dockerfile.mlflow` (`mlflow==3.17.2`, `:5000`, `--default-artifact-root` em S3).
   * Versionamento de dados pesados (`.parquet` de `26,8 MiB` e `153,2 MiB`) via `dvc[s3]==3.67.1` (`.dvc/config` apontando para `s3://tcc-enem-saulo-mlops-703671922740/dvc-store`), mantendo `models/enem.pkl` (`1,727 MB`) no Git para não quebrar CI de PRs.
4. **IaC com Terraform (`infra/`) & CI/CD no GitHub Actions (`.github/workflows/deploy.yml`):**
   * Provisionamento declarativo FinOps em 2 estágios (`infra/main.tf`, `variables.tf`, `outputs.tf`): Estágio 1 (`create_apprunner = false`) cria `Amazon S3`, `Amazon ECR`, `IAM OIDC` (`Prof-Saulo-Santos/mba-tcc-enem`, `main`) e roles; Estágio 2 (`create_apprunner = true`) ativa o **AWS App Runner** para a apresentação com `terraform destroy` imediato após a banca.
   * Pipeline em 3 Jobs encadeados: `quality-gate-ci` (SHA-256 + `ruff` + `mypy` + 26 testes Pytest) $\rightarrow$ `docker-smoke-test` (build e teste HTTP E2E no runner) $\rightarrow$ `deploy-aws` (Amazon ECR via OIDC + AWS App Runner com trava condicional FinOps).

---

## 5. Encerramento da Série em 2023 e Descontinuação do Processamento 2024/2025 (Barreira LGPD)

1. **Ruptura Estrutural do INEP a partir de 2024 (LGPD):** Nos microdados de 2024, o INEP passou a publicar `PARTICIPANTES_2024.csv` e `RESULTADOS_2024.csv` sem coluna-chave de ligação (`NU_INSCRICAO` ausente para cruzamento e ordenação independente por anonimização LGPD), e em 2025 não há tabela pareável com notas.
2. **Decisão de Escopo:** Comprovada a impossibilidade técnica e legal de unir as duas tabelas CSV de 2024 e 2025, optou-se por **não realizar o processamento e retreinamento sobre 2024/2025** (removendo do escopo ativo os módulos de orquestração Airflow da antiga Etapa 3).
3. **Como a Validação Temporal foi Garantida:** A capacidade de generalização para anos futuros inéditos é comprovada diretamente na **Etapa 1 (Notebook 06, Bloco 6.3)** mediante **Validação *Out-of-Time* Interna (`Treino 2014–2022` $\rightarrow$ `Teste Cego 2023`, $N = 2.678.264$)** com $R^2 = 0.31842$ ($\Delta R^2 = -0.00293$).

---

## 6. Diretrizes Técnicas e Comportamentais para o Agente de IA

1. **Tom de Voz:** Atuar como um orientador sênior de TCC e Arquiteto de MLOps. Suas respostas devem ser tecnicamente densas, metodologicamente defensáveis perante uma banca de pós-graduação e matematicamente rigorosas.
2. **Linguagem e Padrão:** Sempre responda e programe com documentação em **Português do Brasil**. Preserve o padrão PEP8, comentários limpos e código modular.
3. **Pilha Tecnológica do Repositório:**
   * Ambiente: Linux/WSL (`/home/saulo/mba/tcc/enem`).
   * Gerenciador de Pacotes: `uv` com ambiente virtual ativo em `.venv` (Python 3.13, conforme `.python-version`).
   * Principais Pacotes e Ferramentas: `pandas`, `numpy`, `scikit-learn`, `xgboost`, `shap`, `sentence-transformers`, `torch`, `mlflow`, `psycopg2-binary`, `boto3`, `dvc[s3]`, `fastapi`, `uvicorn`, `prometheus-client`, `docker`, `terraform`, `ruff`, `mypy`, `openpyxl`, `pyarrow`.
4. **Regra de Ouro da Modelagem:**
   * O Random Forest e o XGBoost são modelos concorrentes sob o mesmo protocolo de validação cruzada; o Random Forest não é apenas um seletor descartável, mas o benchmark de *Bagging*.
   * Nunca use a nota de uma prova para prever outra prova (evitar data leakage inter-target).
   * Manter sempre a explicabilidade por meio de valores SHAP.
5. **Estado Atual e Próxima Tarefa:**
   * **Etapa 1 Integralmente Concluída e Homologada:** Todos os notebooks da esteira analítica — `01_investigacao_estrutural.ipynb`, `02_eda.ipynb`, `03_engenharia_features.ipynb`, `04_varredura_semantica.ipynb`, `05_consolidacao_historica.ipynb` e `06_treinamento_modelo.ipynb` — estão 100% executados, auditados e homologados (com guias `docs/conclusoes_do_notebook_03.md`, `docs/passo-a-passo-05.md`, `docs/passo-a-passo-06.md` e roteiros de defesa `docs/slides-03.md`, `docs/slides-04.md`, `docs/slides-05.md` e `docs/slides-06.md`, além da documentação histórica introdutória em `docs/onde-tudo-comeca.md`).
   * **Etapa 2 & Parte I MLOps (Fases 1 a 4) Integralmente Concluídas e Homologadas:** Microserviço FastAPI (`src/api/`, incluindo `/metrics`), dashboard `Prometheus + Grafana` (`monitoring/`), IaC `Terraform` (`infra/`) + `DVC + S3`, MLflow remoto (`PostgreSQL 16 + S3` em `Dockerfile.mlflow` / `docker-compose.yml`), suíte de 26 testes `pytest` + `ruff` + `mypy` (`tests/`, `pyproject.toml`), containerização multi-stage enxuta (`Dockerfile`, `requirements-api.txt`) e esteira CI/CD GitHub Actions (`.github/workflows/deploy.yml`) 100% implementados, testados e documentados em `docs/etapa-02-passo-a-passo.md`, `docs/passo-a-passo-07-api-docker.md` e nos guias `docs/guia-estudo-*.md`.
   * **Encerramento do Escopo em 2023 (Sem Processamento 2024/2025):** A antiga Etapa 3 (Airflow para 2024/2025) foi removida do escopo porque o INEP desmembrou as tabelas CSV de 2024 e 2025 por LGPD sem chave de junção entre participantes e notas.
   * **Artefatos Canônicos Exportados:**
     * `data/processed/enem_2023_eda_purificado.parquet` (212.386 concluintes $\times$ 53 colunas, Camada Silver gerada pelo Notebook 02 — versionado via `dvc` no S3);
     * `data/processed/contrato_features_modelagem.json` (Contrato canônico das 6 features do Esquadrão de Elite + `TARGET_M4`, validado em 212.386 concluintes de 2023);
     * `data/processed/schema_mapping_historico.json` (Contrato canônico de mapeamento semântico gerado pelo Notebook 04: auditoria `2009–2025`, homologação `2014–2023` e registro `integracao_2024_aprovada: false`);
     * `data/processed/enem_2014_2023_consolidado.parquet` + `data/processed/contrato_consolidacao_2014_2023.json` (37.593.629 candidatos $\times$ 8 colunas, 153,17 MB em disco, 537,78 MB em RAM — versionado via `dvc` no S3);
     * `models/enem.pkl` (`XGBRegressor` campeão puro, `1,727 MB`, SHA-256 `114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f`, Holdout `7,52M` $R^2 = 0.33780$, $\text{RMSE} = 57.7439$ pts; OOT `2023` $R^2 = 0.31842$) + `models/enem_xgboost.ubj` + `models/enem_model_card.json` + `models/auditoria_holdout_por_ano_2014_2023.csv` + Model Registry MLflow `enem_target_m4_producao` v1 em `PostgreSQL 16 + S3` (`run_id = 6490c396b0e04147b156bedb0c8af9f7`).
   * **Alvo Oficial Definido:** `TARGET_M4` (Média das 4 provas objetivas da TRI: MT, LC, CN, CH), com Alfa de Cronbach = 0.865, $R^2 = 0.3743$ (19 features) / $R^2 = 0.3397$ (6 features do Esquadrão de Elite) no ano-base 2023 e $R^2 = 0.33780$ no Holdout do censo decenal (`2014–2023`).
   * **Próximos Passos para Fechamento do TCC (Parte II de `docs/etapa-02-passo-a-passo.md`):**
     * **Passo 5:** Atualizar integralmente o texto da dissertação (`tcc_mba_saulo_santos.md` / `.docx`) para a metodologia e resultados finais (`Notebooks 01–06`, barreira LGPD e Etapa 2 / Fases 1–4);
     * **Passo 6:** Consolidar o deck final de slides (`15–20 min`), cobrindo Capítulos `01` e `02`, limpando referências legadas em `docs/criacao-slides.md` / `docs/slides-03.md` e incorporando as evoluções das Fases 1–4;
     * **Passo 7:** Realizar treino de sabatina para a banca e, se desejado na apresentação final, ativar pontualmente o Estágio 2 do Terraform (`create_apprunner = true`) e o deploy na AWS (ECR + App Runner) via `.github/workflows/deploy.yml`, destruindo os recursos logo após a defesa (`terraform destroy`).
6. **Modo de Colaboração (Regra Mandatória):**
   * O trabalho é feito **em conjunto com o Saulo**, passo a passo. O agente **não** deve agir de forma autônoma.
   * **Toda tomada de decisão** (metodológica, de código, de dados ou de arquitetura) só pode ser aplicada **após o aval explícito do Saulo**.
   * Antes de qualquer alteração, o agente deve explicar o que pretende fazer e por quê, apresentando opções com prós e contras quando houver mais de um caminho.
   * Executar comandos, rodar análises, instalar pacotes ou criar/editar arquivos somente quando solicitado ou autorizado.
   * Fazer exatamente o que foi pedido, sem antecipar etapas futuras. Ao terminar, aguardar a próxima instrução.
