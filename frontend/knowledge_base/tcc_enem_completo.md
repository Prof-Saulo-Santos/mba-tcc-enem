# Dossiê Técnico Completo — TCC MBA em Ciência de Dados & MLOps (Predição de Desempenho no ENEM)

**Autor:** Saulo Santos  
**Alvo Oficial do Modelo:** `TARGET_M4` (Média aritmética das 4 provas objetivas da TRI no ENEM)  
**Recorte Censitário Oficial:** Década de Ouro (`2014–2023`, `37.593.629` candidatos elegíveis)  
**Modelo Campeão de Produção:** `XGBRegressor` (`tree_method="hist"`, `models/enem.pkl`)  
**Arquitetura MLOps:** Arquitetura Desacoplada por Planos (*Local-to-Cloud MLOps* — Workstation Containerizada + AWS)

---

## 1. Visão Geral, Objetivo Acadêmico e Tese Sociológica

Este Trabalho de Conclusão de Curso (MBA em Ciência de Dados & MLOps) investiga e prevê o determinismo socioeconômico sobre o desempenho cognitivo dos estudantes brasileiros no Exame Nacional do Ensino Médio (ENEM), integrando três pilares:

1. **Sociologia Educacional (Pierre Bourdieu):** comprovação empírica de como o **capital econômico** (renda per capita domiciliar) e o **capital cultural e digital** (escolaridade materna, língua estrangeira escolhida e posse de computador) condicionam o desempenho acadêmico antes mesmo de o candidato abrir a prova.
2. **Ciência de Dados e Machine Learning em Larga Escala:** consolidação longitudinal de uma década completa de microdados públicos do INEP (`2014–2023`, `56.568.785` inscritos varridos e `37.593.629` registros elegíveis consolidados), harmonização de deriva semântica via NLP (SBERT) e modelagem não linear com explicabilidade exata via **TreeSHAP**.
3. **Engenharia MLOps Ponta a Ponta:** rastreabilidade remota com **MLflow (`PostgreSQL 16 + Amazon S3`)**, versionamento de datasets com **DVC + S3**, infraestrutura declarativa com **Terraform** (`S3`, `ECR`, `IAM OIDC`, **AWS ECS Express Mode**), microserviço REST **FastAPI** containerizado (`Docker multi-stage`), qualidade estática/funcional no CI/CD (**GitHub Actions**: `SHA-256 + Ruff + Mypy + 26 Pytest + Docker Smoke Test`) e observabilidade em tempo real (**Prometheus + Grafana**).

---

## 2. Investigação Estrutural e Análise Exploratória (`Notebooks 01 e 02`, Ano-Base `2023`)

### 2.1 Metodologia de Saneamento da Amostra de Referência (`2023`)
* **Ano-base padrão-ouro:** `2023` (Notebook `02_eda.ipynb`), resultando em **`212.386` estudantes concluintes elegíveis** (`enem_2023_eda_purificado.parquet`, Camada Silver, `53` colunas).
* **Filtros aplicados:**
  * Mantidos exclusivamente candidatos com presença integral nas provas (`TP_PRESENCA == 1`).
  * Saneamento de Redação: exclusão de anomalias com `TP_STATUS_REDACAO != 1` (removendo zeros espúrios por fuga ao tema, folha em branco ou cópia, cerca de `3,5%` da base).
  * Imputação lógica controlada em concluintes (`TP_ST_CONCLUSAO == 2`) preservando nulos estruturais de egressos (`TP_ST_CONCLUSAO == 1`).

### 2.2 Momentos Estatísticos e Tamanhos de Efeito (*Cohen's d* em Matemática — `2023`)
* **Distribuições de notas:** Matemática apresentou assimetria `Sk = +0,100`; Ciências Humanas `Sk = -0,414`; Ciências da Natureza apresentou curtose leptocúrtica extrema (`K = 4,341`), explicada pela alta concentração de notas em torno de `499` pontos associada às caudas da TRI.
* **Desigualdades medidas por *Cohen's d* na nota de Matemática (`N = 212.386`):**
  * **Tipo de Escola (Privada vs. Pública):** `d = 1,079` (**Efeito Grande / Avassalador** — `86%` dos alunos de escola pública ficam abaixo da média das escolas privadas).
  * **Cor/Raça (Branca vs. Preta):** `d = 0,625` (**Efeito Médio/Grande**).
  * **Sexo (Masculino vs. Feminino em Matemática):** `d = 0,377` (**Efeito Pequeno**, seguindo o padrão PISA: homens à frente em Matemática e Ciências da Natureza; mulheres com liderança expressiva de `+30` a `+40` pontos em Redação e leve vantagem em Linguagens).
* **Decisão sobre segmentação por sexo:** optou-se por **não** dividir modelos por sexo, mantendo a amostra total e permitindo que árvores particionem nativamente por `TP_SEXO` com explicação marginal auditada via TreeSHAP.

---

## 3. Engenharia de Features e Homologação do Alvo `TARGET_M4` (`Notebook 03`)

### 3.1 Definição do Alvo Oficial (`TARGET_M4`)
Após avaliação comparativa de 6 alvos potenciais (`TARGET_MT`, `TARGET_LC`, `TARGET_CN`, `TARGET_CH`, `TARGET_M2` e `TARGET_M4`) sob Validação Cruzada Estratificada (`5-Fold CV` com `HistGradientBoostingRegressor` em `N = 212.386`), foi homologado como alvo oficial:

$$\text{TARGET\_M4} = \frac{\text{NU\_NOTA\_CN} + \text{NU\_NOTA\_CH} + \text{NU\_NOTA\_LC} + \text{NU\_NOTA\_MT}}{4}$$

**Justificativas científicas e psicométricas para a escolha de `TARGET_M4`:**
1. **Maior previsibilidade sociológica e menor erro relativo:** alcançou $R^2 = 0{,}3743$, $\text{RMSE} = 64{,}4818\text{ pts}$ e $\text{RMSE}/\sigma = 0{,}7910$ (com 19 features), superando `TARGET_M2` ($R^2 = 0{,}3653$, $\text{RMSE}/\sigma = 0{,}7967$) em 5 de 5 folds.
2. **Consistência psicométrica unidimensional:** as 4 provas objetivas calibradas pela **Teoria de Resposta ao Item (TRI)** medem um construto cognitivo homogêneo, comprovado por correlações de Pearson robustas ($r = 0{,}601$ a $0{,}760$), **Alfa de Cronbach = `0,865`**, 1º componente principal retendo `74,48%` da variância conjunta e correlação de `0,9967` com o fator geral (`g`).
3. **Expurgo *a priori* da Redação (`NU_NOTA_REDACAO`):** a Redação usa **Teoria Clássica dos Testes (TCT)** em soma discreta de 5 competências (passos de `40` pontos, de `0` a `1000`) com maior ruído subjetivo de correção humana e anomalias de `TP_STATUS_REDACAO`, sendo psicometricamente incompatível com a escala contínua da TRI.

### 3.2 O "Esquadrão de Elite" (6 Features) e a Prova da Parcimônia
* **Estudo de ablação (Navalha de Ockham):** entre os 19 bens do questionário (`Q007` a `Q025`), a posse de computador (`Q024`) tem correlação de Spearman $\rho = 0{,}575$ com a renda e adiciona `+3,18 p.p.` de $R^2$ sobre a renda per capita, enquanto posse de carro (`Q010`) adiciona apenas `+0,03 p.p.` e outros 17 bens juntos somam apenas `+1,84 p.p.`.
* **Comparação `19` vs. `6` features no ano-base `2023`:**
  * Modelo completo (`19` features): $R^2 = 0{,}3743$, $\text{RMSE} = 64{,}4818\text{ pts}$.
  * Modelo parcimonioso (**Esquadrão de Elite — `6` features**): $R^2 = 0{,}3397$, $\text{RMSE} = 66{,}2362\text{ pts}$.
  * **Resultado:** redução de **`68,4%` nas variáveis** (`19 -> 6`) e **`60,0%` no tempo de treino**, preservando **`90,8%` do poder explicativo ($R^2$)** (diferença absoluta de apenas `3,45 p.p.` em $R^2$ e `+1,75` pt no RMSE).
* **Auditoria anti-leakage:** pico de correlação linear absoluta entre preditor e alvo foi `|r| = 0,4765` (abaixo do limiar `0,80`); *Permutation Importance* confirmou a relevância sem viés de Gini.

### 3.3 Contrato Oficial das 6 Features de Entrada (Produção / API)
Especificadas em `data/processed/contrato_features_modelagem.json`, `data/processed/contrato_consolidacao_2014_2023.json` e `models/enem_model_card.json`:

| Ordem | Variável | Tipo na API | Domínio Válido | Significado Sociológico / Codificação Oficial |
| :---: | :--- | :---: | :---: | :--- |
| `1` | `RENDA_PER_CAPITA` | `float` (`float32`) | `[0.0, 25.0]` | Renda familiar estimada por morador em múltiplos do **Salário Mínimo (SM)** vigente (`MAPA_Q006 / Q005`). Feature engenhada de maior impacto. |
| `2` | `Q024` | `int` (`int8`) | `{0, 1, 2, 3}` | Posse de computador no domicílio: `0` = Nenhum, `1` = 1 computador, `2` = 2 computadores, `3` = 3 ou mais. |
| `3` | `TP_ANO_CONCLUIU` | `int` (`int8`) | `{0..9}` | Anos decorridos desde a conclusão do Ensino Médio: `0` = Não informado/concluinte no ano, `1..8` = anos exatos, `9` = 9 ou mais anos. |
| `4` | `TP_LINGUA` | `int` (`int8`) | `{0, 1}` | Língua estrangeira escolhida na prova: `0` = Inglês, `1` = Espanhol (proxy forte de letramento e capital cultural). |
| `5` | `TP_SEXO` | `int` (`int8`) | `{0, 1}` | Sexo informado pelo candidato: `0` = Feminino (`F`), `1` = Masculino (`M`). |
| `6` | `Q002` | `int` (`int8`) | `{0..7}` | Escolaridade da mãe / mulher responsável: `0` = Nunca estudou, `1` = EF I incompleto, `2` = EF I completo / EF II incompleto, `3` = EF completo / EM incompleto, `4` = EM completo / Sup. incompleto, `5` = Superior completo, `6` = Pós-graduação, `7` = Não sei. |

---

## 4. Harmonização Semântica via NLP e a Barreira LGPD 2024–2025 (`Notebook 04`)

### 4.1 Resolução de *Schema/Semantic Drift* com SBERT
* Como o INEP altera códigos e enunciados de perguntas entre edições (ex.: em `2014`, computador era `Q010` e renda era `Q003`; de `2015–2023`, passaram para `Q024` e `Q006`), o Notebook `04_varredura_semantica.ipynb` aplicou o modelo local de *Sentence Transformers* **`paraphrase-multilingual-MiniLM-L12-v2`** (384 dimensões) com **Similaridade de Cosseno** e auditoria humana (*Human-in-the-Loop*), gerando o contrato `data/processed/schema_mapping_historico.json`.
* O uso de embeddings locais evitou custo recorrente de APIs externas de LLM, impediu envio de dados para terceiros e garantiu determinismo (`seed=42`).
* **Veredito histórico:** as edições `2009–2013` foram descartadas por ausência estrutural de perguntas essenciais; a janela **`2014–2023` (10 edições)** foi 100% homologada como **Década de Ouro**.

### 4.2 Por Que `2024` e `2025` Não Entram no Treinamento (Barreira LGPD)
* A partir da edição de **2024**, por adequação à **Lei Geral de Proteção de Dados (LGPD)**, o INEP deixou de publicar os microdados em tabela única por inscrito e passou a dividir os dados em tabelas independentes (`PARTICIPANTES_2024.csv` e `RESULTADOS_2024.csv`) **sem chave identificadora de junção (`NU_INSCRICAO` ausente para pareamento e ordenação independente para anonimização)** — e em `2025` tampouco há tabela pareável com notas.
* Como ficou técnica e legalmente impossível unir as variáveis socioeconômicas (`X`) às notas (`y`) de um mesmo candidato nessas edições (`integracao_2024_aprovada: false`), a antiga Etapa 3 (orquestração Airflow para `2024/2025`) foi **removida do escopo**, encerrando a série censitária em `2023` e comprovando a capacidade de generalização temporal mediante **Validação *Out-of-Time* Interna (`2014–2022 -> 2023`)**.

---

## 5. Consolidação Censitária Big Data e Regras *Anti-Value Drift* (`Notebook 05`)

### 5.1 Engenharia de Memória (*Single-Node Chunked Streaming* e *Downcasting*)
* O Notebook `05_consolidacao_historica.ipynb` leu os 10 CSVs brutos (`2014–2023`, `25,45 GB`, **`56.568.785` inscritos brutos varridos**) em blocos (*chunks*) de `500.000` linhas com projeção antecipada de colunas (`usecols`).
* Aplicando *downcasting* explícito (`5 × int8 + 2 × float32 + 1 × int16`), o custo caiu de `64+ bytes/linha` para **`15,00 bytes/linha`** (economia de `76,6%`).
* **Artefato Gold consolidado (`data/processed/enem_2014_2023_consolidado.parquet`):**
  * **`37.593.629` candidatos elegíveis** $\times$ `8` colunas (`NU_ANO`, as `6` features e `TARGET_M4`), zero nulos e zero duplicatas (`NU_INSCRICAO` auditado em cada ano e descartado na persistência final para economizar `~304 MB` e evitar memorização).
  * Tamanho em disco: **`153,17 MB`** (Apache Parquet, compressão Snappy); consumo em RAM: **`537,78 MB`**.
  * Checksum `SHA-256`: `a7fbce7cd5f6e89244351c8712be588f53dbbdf4ff46e9d3b397157647438d3a`.
  * Estatística global de `TARGET_M4` na década: **média `511,05` pontos** e **desvio padrão `70,97` pontos** (`511.0497 ± 70.9684`).
* **Por que `Pandas` em chunks em vez de Spark?** Porque com `15 bytes/linha` a base coube em apenas `537,78 MB` de RAM (`< 10%` da RAM livre em workstation de `7,70 GB`), evitando custo de cluster JVM e sobrecarga operacional do Apache Spark (*Polars* ou *DuckDB* ficam registrados como alternativas futuras em CPU).

### 5.2 As 4 Regras de Harmonização Longitudinal (*Anti-Value Drift*)
1. **Deflação estrutural da renda (`RENDA_PER_CAPITA`):** entre 2014 (`R$ 724,00`) e 2023 (`R$ 1.320,00`), o salário mínimo subiu `+82,3%` nominalmente. Mapeando as letras `A..Q` diretamente aos **múltiplos do Salário Mínimo vigente** (`0.0` até `22.5` SM) divididos por `Q005`, a renda ficou deflacionada na origem sem depender de tabelas externas de IPCA.
2. **Correção da inversão de `Q024` em `2014` (`Q010`):** em 2014, `'D'` significava *"Não possui computador"* (`0`) e `'A'`, `'B'`, `'C'` significavam `1, 2, 3+` (ordem oposta a 2015–2023, onde `'A' = 0`). Sem a regra, um codificador alfabético teria invertido extremos de inclusão digital em quase 6 milhões de alunos de 2014.
3. **Alinhamento de escolaridade materna (`Q002`) em `2014`:** em 2014 havia 9 letras (`A..I`), enquanto 2015–2023 usam 8 (`A..H`). A regra unificou `E` e `F` de 2014 para `4` (EM completo / Sup. incompleto), alinhando `G -> 5` (Superior), `H -> 6` (Pós-graduação) e `I -> 7` (Não sei), evitando misturar mães pós-graduadas com "Não sei".
4. **Estacionariedade anti-leakage de `TP_ANO_CONCLUIU` (`[0, 9]`):** converteu anos literais (`2013..2004` em 2014) e caudas crescentes (`10` até `17` em 2023) para anos decorridos estacionários no teto `0..9`, impedindo o modelo de inferir o calendário da prova pelo código de conclusão.

---

## 6. Modelagem em 3 Estágios, Auditorias e TreeSHAP (`Notebook 06`)

### 6.1 Particionamento Censitário com Blindagem Tripla Anti-Leakage
* `NU_ANO` é usado **exclusivamente** para estratificação ano a ano via máscara `uint8` e é estritamente excluído de `X`:
  * **`df_fit` (`72%`):** `27.067.413` candidatos (pool censitário de treino + origem da subamostra `df_cv` de `1.000.000` e da amostra de `3.000.000` do Random Forest).
  * **`df_val_es` (`8%`):** `3.007.490` candidatos dedicados exclusivamente ao *Early Stopping* do XGBoost e à medição da Curva de Aprendizado.
  * **`df_test` (`20%`):** `7.518.726` candidatos lacrados como **Holdout Cego Final** (abertos apenas na Seção 6).

### 6.2 Modelos Avaliados e Benchmark `5-Fold CV` (Estágio 1, `N = 1.000.000`) & *Tuning* (`3-Fold CV`, `11` Nested Runs)
* **Lista exata dos 4 modelos concorrentes avaliados oficialmente no Notebook `06_treinamento_modelo.ipynb`:**
  1. `DummyRegressor` (Baseline nulo): $R^2 = 0{,}0000$, $\text{RMSE} = 71{,}00\text{ pts}$, $\text{MAE} = 56{,}83\text{ pts}$.
  2. `Ridge` (Regressão Linear L2): $R^2 = 0{,}2836$, $\text{RMSE} = 60{,}09\text{ pts}$, $\text{MAE} = 47{,}52\text{ pts}$.
  3. `RandomForestRegressor` (*Bagging*): $R^2 = 0{,}3337$, $\text{RMSE} = 57{,}95\text{ pts}$, $\text{MAE} = 45{,}76\text{ pts}$.
  4. `XGBRegressor` (`hist` — *Boosting* campeão de produção): $R^2 = 0{,}3359$, $\text{RMSE} = 57{,}86\text{ pts}$, $\text{MAE} = 45{,}67\text{ pts}$.
* **Modelo auxiliar na engenharia de atributos (`Notebook 03`):** apenas `HistGradientBoostingRegressor` (`5-Fold CV` em `2023`) foi utilizado como avaliador fixo para selecionar o alvo `TARGET_M4` e validar a ablação de `19 -> 6` features.
* **Algoritmos NÃO avaliados neste TCC:** modelos como `LightGBM` e `CatBoost` constam exclusivamente como **trabalhos futuros** (Seção 8); nenhum outro algoritmo (`ExtraTrees`, `Lasso`, `ElasticNet`, `SGDRegressor`, `Huber`, `LinearSVR` ou redes neurais) foi avaliado no estudo.
* **Conclusão:** algoritmos de árvore superam a regressão linear nas mesmas 6 features em **`+5,23 p.p.` no $R^2$ de CV** (**`+19,1%` relativo em variância explicada no Holdout final** vs. `Ridge`), provando não-linearidade sociológica.
* **Melhores configurações no *Tuning*:**
  * `XGB-01` (vencedor Boosting): `max_depth=5`, `learning_rate=0.10`, `min_child_weight=30`, `subsample=0.80`, `colsample_bytree=0.80`, `reg_lambda=1.0`, elevado no treino final do censo para `n_estimators=650` com `early_stopping_rounds=25`.
  * `RF-02` (vencedor Bagging): `n_estimators=150`, `max_depth=12`, `min_samples_leaf=20`, `max_features="sqrt"`.

### 6.3 Estágio 2 — Curva de Aprendizado Escalável (`50k` $\rightarrow$ `15M` avaliados em `3,01M`)
* `50.000`: $\text{RMSE}_{\text{treino}} = 57{,}086$ vs. $\text{RMSE}_{\text{val}} = 58{,}059$ ($R^2 = 0{,}32967$).
* `200.000`: $57{,}397$ vs. $57{,}825$ ($R^2 = 0{,}33507$).
* `1.000.000`: $57{,}700$ vs. $57{,}755$ ($R^2 = 0{,}33669$).
* `5.000.000`: $57{,}754$ vs. $57{,}738$ ($R^2 = 0{,}33708$).
* `15.000.000`: $57{,}762$ vs. $57{,}734$ ($R^2 = 0{,}33716$).
* **Diagnóstico Bias–Variance:** entre `5M` e `15M`, as curvas se colam com gap residual de `0,03` pt, provando ausência de *overfitting* e proximidade do platô bayesiano das 6 variáveis — legitimando treinar o `RandomForest` em `3M` (sem estourar RAM com vetores `int64`) e escalar o `XGBRegressor (hist)` em histogramas `1 byte` para os `27,07M` integrais do censo em uma execução única.

### 6.4 Estágio 3 — Disputa Final no Holdout Cego (`7.518.726`), Caso `2018` e *Out-of-Time* `2023`
* **Confronto no Holdout (`7.518.726` alunos):**
  * **`XGBRegressor` Campeão** (`27.067.413` Fit + `3.007.490` ES, `best_iteration = 649`): **$R^2 = 0{,}33780$**, **$\text{RMSE} = 57{,}7439\text{ pts}$**, **$\text{MAE} = 45{,}5904\text{ pts}$**, $\text{RMSE}/\sigma = 0{,}81376$ (latência de `98,561 ms / 10k` amostras na rodada final de `21/11/2026`, `30,4%` mais rápido que o RF na mesma rodada).
  * `RandomForestRegressor` (`3.000.000` estratificados): $R^2 = 0{,}33606$, $\text{RMSE} = 57{,}8198\text{ pts}$, $\text{MAE} = 45{,}6635\text{ pts}$, $\text{RMSE}/\sigma = 0{,}81483$ (`141,660 ms / 10k`).
* **Estabilidade anual (`2014–2023`) e Anomalia TRI de `2018`:** em 9 das 10 edições, $R^2 \in [0{,}31197, 0{,}36314]$, atingindo o pico na pandemia de **`2020`** (`0,36314`, ampliando o peso da desigualdade digital). Em **`2018`**, o $R^2$ cai pontualmente para `0,22595` (viés `-23,81 pts`) porque a média real da TRI do INEP subiu atipicamente para `533,54 pts`, enquanto o modelo manteve sua previsão em `509,73 pts` — provando que não memorizou o ano (`NU_ANO`).
* **Validação *Out-of-Time* Interna (`Treino 2014–2022 -> Teste Cego 2023`, `N = 2.678.264`):**
  * **$R^2 = 0{,}31842$**, **$\text{RMSE} = 67{,}6232\text{ pts}$**, **$\text{MAE} = 52{,}8526\text{ pts}$**, $\text{RMSE}/\sigma = 0{,}82558$, viés médio `-5,516 pts` ($\Delta R^2 = -0{,}00293$ em relação ao Holdout *in-sample* de 2023 `0,32135`), comprovando estacionariedade e generalização em safras inéditas.

### 6.5 Explicabilidade Exata via TreeSHAP (`10.000` alunos do Holdout)
* Valor base esperado $\mathbb{E}[f(X)] = 511{,}04\text{ pts}$ (erro máximo de aditividade de Shapley `1,26e-03` pts).
* **Ranking Global de Impacto Marginal (`|SHAP|` médio em pontos TRI e participação relativa):**
  1. **`RENDA_PER_CAPITA`:** `18,483 pts` (**`30,10%`**) | amplitude `-41,93` a `+85,96` (`127,89 pts`), curva fortemente côncava com retornos marginais decrescentes após `~2–4 SM`.
  2. **`TP_LINGUA`:** `10,895 pts` (**`17,74%`**) | `-24,82` a `+18,22` (vantagem sistemática para Inglês `0` vs. Espanhol `1`).
  3. **`Q024` (Computador):** `9,487 pts` (**`15,45%`**) | `-19,37` a `+53,60`.
  4. **`TP_ANO_CONCLUIU`:** `8,958 pts` (**`14,59%`**) | `-15,26` a `+29,29`.
  5. **`Q002` (Escolaridade Materna):** `8,642 pts` (**`14,07%`**) | `-42,82` a `+27,64` (progressão crescente até Pós-graduação `6` e queda acentuada no código `7` = *"Não sei"*).
  6. **`TP_SEXO`:** `4,946 pts` (**`8,05%`**) | `-13,06` a `+12,46`.
* **Síntese sociológica:** embora a renda lidere isolada (`30,10%`), a tríade **Cultural-Digital** (`TP_LINGUA + Q024 + Q002`) soma **`47,26%`** do impacto total, corroborando quantitativamente Pierre Bourdieu.

### 6.6 Artefatos Gerados e Rastreabilidade MLflow (`21/11/2026`)
* **Modelo de produção:** `models/enem.pkl` (`1,727 MB`, `SHA-256: 114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f`), acompanhado de `models/enem_xgboost.ubj`, `models/enem_model_card.json` e `models/auditoria_holdout_por_ano_2014_2023.csv`.
* **Registro oficial no MLflow Remoto (`PostgreSQL 16 + S3`):** experimento `tcc_enem_decada_ouro_2014_2023` (`ID=2`), `mlflow_run_id_campeao = 6490c396b0e04147b156bedb0c8af9f7`, modelo registrado `enem_target_m4_producao` Versão `1` (`URI=models:/m-ea7931423f5141379ff97886636ae0ea`), com `17` objetos (`~2,49 MiB`) auditados em `s3://tcc-enem-saulo-mlops-703671922740/mlflow-artifacts/`.

---

## 7. Arquitetura MLOps Desacoplada por Planos (`Etapa 2` e `Fases 1 a 4`)

### 7.1 Enquadramento Conceitual (Por que *não* chamar de *Hybrid Cloud*)
Segundo o padrão NIST, *Hybrid Cloud* exige integração orquestrada entre uma Nuvem Privada corporativa (*datacenter on-premises*) e uma Nuvem Pública. Como uma estação de trabalho local (WSL2 + Docker Compose) não configura datacenter corporativo, a arquitetura aprovada classifica-se rigorosamente como **Arquitetura Desacoplada por Planos (*Decoupled Training & Serving Planes* / *Local-to-Cloud MLOps*)**:
1. **Plano Offline / Governança (Workstation Containerizada + Amazon S3):** `PostgreSQL 16` + `MLflow Server 3.17.2` + `DVC 3.67.1`, persistindo dados `.parquet` (`dvc-store/`) e artefatos (`mlflow-artifacts/`) no S3 com custo RDS `$0,00`.
2. **Plano Online / *Serving* (AWS via Terraform + CI/CD):** API **FastAPI** empacotada em Docker servindo de modo 100% autônomo na nuvem via **Amazon ECR + IAM OIDC + AWS ECS Express Mode** (`Fargate + ALB` com endpoint HTTPS nativo, em substituição ao AWS App Runner).
3. **Plano de Observabilidade (`Prometheus + Grafana`):** endpoint `GET /metrics` na API, monitorado localmente em desenvolvimento/apresentação com evolução documentada para **Amazon Managed Service for Prometheus (AMP) + Amazon Managed Grafana (AMG)** em operação 24/7.

### 7.2 Microserviço FastAPI e Containerização (`src/api/`, `Dockerfile`)
* **Endpoints:**
  * `GET /health`: status de prontidão (`healthy`/`degraded`), versão do modelo e `artifact_sha256`.
  * `GET /info`: metadados, features e métricas oficiais lidas de `enem_model_card.json`.
  * `POST /predict`: predição pontual para 1 candidato (`target_m4` arredondado a 2 casas na escala TRI `0–1000`).
  * `POST /predict/batch`: predição vetorial em lote (`1` a `10.000` candidatos por requisição), retornando predições e `tempo_inferencia_ms`.
  * `GET /metrics`: métricas no formato Prometheus (`CONTENT_TYPE_LATEST`).
  * `GET /docs`: documentação interativa Swagger UI.
* **Blindagem Anti-Leakage:** `CandidatoInput` usa `ConfigDict(extra="forbid")` em Pydantic v2, rejeitando qualquer campo extra (como `NU_ANO`) ou fora dos limites com **`HTTP 422`**.
* **Engenharia Docker FinOps:** build *multi-stage* com `python:3.13-slim` e `uv`, `requirements-api.txt` enxuto (9 pacotes: `fastapi`, `uvicorn`, `pydantic`, `joblib`, `numpy`, `pandas`, `scikit-learn`, `xgboost`, `prometheus-client`), inclusão de `libgomp1` (OpenMP para XGBoost em Debian slim) e execução não-root como `appuser` (`UID 1000`), resultando em **`515 MB` Content Size** na imagem base da API.

### 7.3 Fase 1 — Observabilidade (`Prometheus + Grafana`)
* **9 métricas em `src/api/metrics.py`:** `enem_api_http_requests_total`, `enem_api_http_request_duration_seconds`, `enem_api_validation_errors_total` (separando `extra_forbidden` vs. `domain_or_schema`), `enem_api_model_info`, `enem_api_model_inference_duration_seconds`, `enem_api_predictions_total`, `enem_api_predicted_target_m4` (*Prediction Drift*), `enem_api_input_renda_per_capita` (*Data Drift*) e `enem_api_input_categorical_total` (perfil de `Q024`, `TP_ANO_CONCLUIU`, `TP_LINGUA`, `TP_SEXO`, `Q002`).
* **Proteção contra explosão de cardinalidade:** middleware HTTP usa a rota casada (`route.path` ou `"unmatched"`, ignorando `/metrics`), histogramas usam buckets fixos para contínuas e contadores categóricos somam apenas `26` séries discretas.
* **Stack (`docker compose --profile monitoring up -d`):** Prometheus (`:9090`, `scrape_interval: 5s`, TSDB `7d`) + Grafana (`:3000`) com datasource e dashboard **`ENEM TARGET_M4`** (`10` painéis) provisionados via código (*Zero ClickOps*).

### 7.4 Fase 2 — Infraestrutura como Código (`Terraform`) & `DVC + S3` (com Migração para ECS Express Mode)
* **Terraform (`infra/` — `hashicorp/aws v6.74.0`):** provisiona **`13` recursos base permanentes na conta AWS (`us-east-1`)** + **`2` condicionais sob demanda**: bucket S3 `tcc-enem-saulo-mlops-703671922740` (privado, versionado, criptografia `AES256`, `force_destroy=true`), repositório ECR `enem-target-m4-api` (*scan on push* + política de retenção FinOps de `5` imagens), provedor **IAM OIDC** + role `tcc-enem-saulo-mlops-github-actions` (restrita a `Prof-Saulo-Santos/mba-tcc-enem` em `main`, sem Access Keys estáticas) e as roles do ECS Express Mode (`tcc-enem-saulo-mlops-ecs-execution` e `tcc-enem-saulo-mlops-ecs-infrastructure`).
* **Estratégia FinOps em 2 Estágios (`create_ecs`):**
  * **Estágio 1 (`create_ecs = false`, padrão entre testes):** mantém S3 + ECR + OIDC + roles por `< US$ 0,01/dia`, evitando erro de bootstrap antes da imagem existir no ECR e mantendo custo zero de computação/ALB ociosa.
  * **Estágio 2 (`create_ecs = true`, sob demanda):** sobe `aws_ecs_cluster` (`tcc-enem-saulo-mlops-cluster`) e `aws_ecs_express_gateway_service` (`tcc-enem-saulo-mlops-api`, `1024` CPU / `2048` MiB, auto-scaling `1..2` tasks) com URL HTTPS pública; após os testes, volta a `create_ecs = false` (ou `terraform destroy` definitivo após a banca).
* **DVC + S3:** `.dvc/config` aponta para `s3://tcc-enem-saulo-mlops-703671922740/dvc-store`, versionando os Parquets Silver (`26,8 MiB`) e Gold (`153,2 MiB`), enquanto `models/enem.pkl` (`1,727 MB`) permanece no Git para que testes e Docker Smoke Tests em PRs rodem sem credenciais AWS.

### 7.5 Fase 3 & Fase 4 — MLflow Remoto & CI Quality Gate
* **Fase 3:** `Dockerfile.mlflow` + `docker compose --profile mlops up -d` sobe `postgres:16-alpine` (`:5432`) e `mlflow-server` (`3.17.2`, `:5000`, `--default-artifact-root s3://.../mlflow-artifacts`), eliminando o `sqlite:///mlflow.db` local e comprovando reprodutibilidade bit-a-bit no `SHA-256` de `enem.pkl`.
* **Fase 4:** criação de `pyproject.toml` (`Ruff 0.14.8` + `Mypy 2.4.1`), limpeza de tipagem em `src/api/` e `tests/`, e endurecimento do workflow `.github/workflows/deploy.yml` em 3 jobs:
  1. `quality-gate-ci`: checksum `SHA-256` + `ruff check src tests` + `mypy src/api tests` + **`26/26` testes `pytest`** (contrato HTTP, `/metrics`, paridade numérica, Bourdieu e SLA `< 500 ms` para 1.000 linhas).
  2. `docker-smoke-test`: build Docker real + teste HTTP E2E em `/health`, `/predict` (`547.12`) e bloqueio `422` (`NU_ANO`).
  3. `deploy-aws`: push para Amazon ECR via OIDC e atualização no **AWS ECS Express Mode** (`aws ecs update-express-gateway-service`, com trava FinOps condicional aos secrets `AWS_ROLE_TO_ASSUME` e `AWS_ECS_SERVICE_ARN`).

---

## 8. Perguntas Frequentes de Sabatina & Trabalhos Futuros

* **Por que o $R^2$ fica em torno de `0,34` (`33,78%`) e isso é bom?** Em fenômenos educacionais e sociológicos humanos, a nota depende fortemente de fatores individuais não observados nos microdados públicos (esforço individual, qualidade docente específica de cada sala, saúde emocional no dia da prova). Explicar cerca de **um terço de toda a variância cognitiva nacional** usando apenas **6 variáveis socioeconômicas** sem qualquer dado escolar prévio comprova o peso estrutural da desigualdade de origem (Bourdieu).
* **Por que `AWS ECS Express Mode` em vez de App Runner, Lambda, EKS ou SageMaker?** O plano inicial previa o AWS App Runner, mas a AWS descontinuou/restringiu a criação de novos serviços App Runner na conta (`InvalidRequestException: Account 703671922740 can't create new App Runner services`) e passou a recomendar o **AWS ECS Express Mode**. Para uma única API leve de `1,727 MB` embarcada em `515 MB` OCI, **EKS** traria *overengineering* de Kubernetes, **Lambda** exigiria gestão de *cold start* com camada científica XGBoost/Pandas, e **SageMaker Endpoints** teria custo fixo por hora muito maior; já o **ECS Express Mode** entrega Fargate + ALB gerenciado + HTTPS nativo + escala automática em um único recurso Terraform (`create_ecs = true/false`).
* **Trabalhos futuros mapeados (`docs/estudos-futuros.md`):** avaliar `Polars`/`DuckDB` no ETL por blocos, comparar `LightGBM` e `CatBoost` sob o mesmo protocolo de validação, exportar inferência interoperável para `ONNX Runtime` e migrar observabilidade 24/7 para `Evidently AI + AMP + AMG`.
