# 📘 Guia Passo a Passo e Documentação Complementar — Notebook 06

**Arquivo do Notebook:** [`notebooks/06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb)  
**Projeto de TCC:** MBA em Ciência de Dados & MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  
**Última Atualização (Fase 3 — MLflow PostgreSQL + S3):** `21 de Novembro de 2026` (`run_id = 6490c396b0e04147b156bedb0c8af9f7`)

---

## 1. Visão Geral: O Fechamento da Etapa 1 e a Ponte para Produção (API FastAPI, Docker & AWS)

Na arquitetura em duas etapas do projeto, o **Notebook 06** é o elo que transforma **37.593.629 registros históricos harmonizados (`2014–2023`)** em um **modelo preditivo auditado, explicável e serializado para nuvem**:

```text
ETAPA 1 — LABORATÓRIO CIENTÍFICO, NLP E MLFLOW (Concluída neste Notebook)
[01_investigacao] ─> [02_eda] ─> [03_features] ─> [04_nlp_sbert] ─> [05_consolidacao] ─> ⭐ [06_treinamento_modelo]
                                                                                                  │
                                                                                                  ▼
ETAPA 2 — PRODUTIZAÇÃO, TESTES, DOCKER E DEPLOY CONTÍNUO (AWS)
[models/enem.pkl + enem_model_card.json] ─> FastAPI ─> Pytest ─> Docker ─> GitHub Actions ─> AWS App Runner
```

---

## 2. Estratégia de Particionamento: Rigor Estatístico com Controle de Memória RAM

A base consolidada `data/processed/enem_2014_2023_consolidado.parquet` ocupa **537,78 MB em RAM** (`15,00 bytes/linha`). Em vez de chamar `train_test_split` diretamente (o que alocaria vetores de índices `int64` de `~300 MB`), utilizamos na **Seção 3** um vetor único de códigos `uint8` (`1 byte/linha ≈ 35,8 MB`) estratificado exatamente dentro de cada edição (`NU_ANO` de `2014` a `2023`).

Após materializar as três fatias (`df_test`, `df_val_es`, `df_fit`), `df_decada` e `codigo_particao` são imediatamente liberados com `del` + `gc.collect()` (havendo apenas coexistência transitória durante a cópia das fatias, o que eleva o RSS do processo de `1.439,6 MB` pós-carga para `2.114,4 MB` pós-split, enquanto a soma líquida das partições com `df_cv` permanece em **`552,09 MB`**):

| Partição | Proporção Global | Registros Exatos | Papel Estrito (Zero Vazamento no Treino/Tuning) |
| :--- | :---: | :---: | :--- |
| **`df_fit`** | **72,00%** (90% dos 80% de Dev) | `27.067.413` | *Pool* censitário principal para ajuste final do XGBoost, curva de aprendizado e extração de `df_cv` e da subamostra de 3M do RF. |
| **`df_val_es`** | **8,00%** (10% dos 80% de Dev) | `3.007.490` | Conjunto fixo exclusivo para *Early Stopping* do XGBoost e medição da Curva de Aprendizado. |
| **`df_test`** | **20,00%** (Holdout Cego) | `7.518.726` | Conjunto **100% lacrado** durante CV, *tuning* e curva — aberto a partir da Seção 6 para eleição do campeão, auditoria anual, amostra SHAP (`10k`) e *Smoke Test* (`100` linhas). |
| **`df_cv`** | **2,66%** (Subamostra de `df_fit`) | `1.000.000` | Extraída **somente de `df_fit`** para competição rápida em 5-Fold CV e *Tuning* (Estágio 1). |

> **Blindagem Dupla (Estratificada + Temporal):** Além da avaliação estratificada nos `7.518.726` candidatos do Holdout (`2014–2023`), a **Seção 6 (Bloco 6.3)** executa uma rodada independente de **Validação *Out-of-Time* Interna**, treinando um `XGBRegressor` exclusivamente de `2014` a `2022` (`NU_ANO <= 2022`, mantendo os hiperparâmetros selecionados no Estágio 1) e avaliando nos **`2.678.264` candidatos integrais de `2023`**. Isso comprova generalização temporal sem depender das edições `2024` e `2025` (cujo pareamento participante-nota foi impossibilitado pela separação proposital das tabelas do INEP devido à LGPD).

---

## 3. Arquitetura Escalável em 3 Estágios (CPU de 4 Cores Físicos / 8 Threads / 7,70 GB RAM)

Por que dividimos a competição entre **Random Forest** (*Bagging*) e **XGBoost** (*Gradient Boosting*) em **3 estágios**?

1. **Estágio 1 — Batalha Concorrente em 5-Fold CV + *Tuning* (`N = 1.000.000`):**
   * Avalia nos **exatos mesmos 5 folds estratificados**: `DummyRegressor`, `Ridge` (benchmark linear), `RandomForestRegressor` e `XGBRegressor`.
   * Mantemos `n_jobs=1` no laço externo do `cross_validate` para não clonar matrizes em processos Python paralelos, delegando o paralelismo para **dentro** dos estimadores (`n_jobs=N_THREADS_LOGICAS = 8` no XGBoost; `n_jobs=N_THREADS_FISICAS = 4` no Random Forest para conter o uso de RAM).
   * Em seguida, refinamos os hiperparâmetros (5 configurações de RF e 6 de XGBoost em 3-Fold CV) registrando cada tentativa como *Nested Run* no MLflow.
2. **Estágio 2 — Curva de Aprendizado Escalável (`50k` $\rightarrow$ `200k` $\rightarrow$ `1M` $\rightarrow$ `5M` $\rightarrow$ `15M`):**
   * Como as 6 features formam um espaço de baixa dimensionalidade e cardinalidade finita (`5` variáveis `int8` + `RENDA_PER_CAPITA` em `float32` oriunda da razão `Q006 / Q005`), a curva no XGBoost otimizado demonstra onde a variância amostral se dissipa e o $\text{RMSE}$ em `df_val_es` (`3.007.490` alunos) estabiliza assintoticamente entre `1M` e `5M` de registros.
3. **Estágio 3 — Treinamento Final em Escala Censitária (`7,52M` no Holdout):**
   * **Diferença algorítmica em Big Data:** O `RandomForestRegressor` (`scikit-learn`) aloca vetores de índices/contagens `int64` proporcionais a $N$ durante a construção das árvores; por isso, foi ajustado em um teto seguro de **`3.000.000` de alunos estratificados** (aproveitando o platô assintótico sugerido pela curva do Estágio 2) com os hiperparâmetros vencedores (`RF-02`). Já o **`XGBRegressor(tree_method="hist", max_bin=256)`** quantiza as features em histogramas de `1 byte`, ajustando-se nos **`27.067.413` registros integrais de `df_fit`** (+ `3.007.490` de *Early Stopping* com teto elevado para `650` árvores, atingindo `best_iteration = 649`).
   * Ao longo dos checkpoints medidos na execução homologada de `21/11/2026` (com host de `7,70 GB` totais), o RSS do kernel manteve-se entre `1.439,6 MB` (pós-carga) e `2.114,4 MB` (pós-split) / `1.689,0 MB` (ao final da Seção 8).
   * Ambos os modelos são avaliados em lotes de `1.000.000` de linhas (`prever_em_blocos`) sobre os mesmos **`7.518.726` alunos cegos de `df_test`**.

---

## 4. Roteiro Detalhado Célula por Célula (`20` Células: Índices `00` a `19`)

| Seção / Células | O que Executa | Tempo Observado (`21/11/2026`) | O que Conferir na Saída |
| :--- | :--- | :---: | :--- |
| **Cabeçalho** (Célula `00`) | Visão executiva, contrato de dados e resumo dos resultados da execução completa. | — | Alinhamento com os resultados finais registrados em `models/enem_model_card.json`. |
| **Seção 1** (Células `01–03`) | Imports, `SEED=42`, detecção de CPU (`4` físicos / `8` threads), utilitários e conexão ao MLflow Tracking Server remoto (`http://127.0.0.1:5000`, `PostgreSQL + S3`) (+ diagrama Mermaid do Bloco 1.5 na Célula `03`). | `~2 s` | Versões (`sklearn 1.9.0`, `xgboost 3.4.1`, `mlflow 3.17.2`, `shap 0.54.1`) e experimento `tcc_enem_decada_ouro_2014_2023` (`ID=2`). |
| **Seção 2** (Células `04–06`) | Verifica `SHA-256` do Parquet do NB05, carrega os `37,59M` registros e aplica travas *Anti-Leakage* (+ diagrama Mermaid na Célula `05`). | `605,31 s` | `Integridade SHA-256: OK`, `537.78 MB (15.00 bytes/linha)`, RSS `1.439,6 MB` e exclusão formal de `NU_ANO` e `TARGET_M4` de `X`. |
| **Seção 3** (Células `07–08`) | Particiona via vetor `uint8` em `df_fit` (72%), `df_val_es` (8%) e `df_test` (20%), libera `df_decada` e extrai `df_cv` (`1M`). | `338,29 s` | Médias homogêneas de `TARGET_M4`, soma líquida das partições de `552,09 MB` e RSS em `2.114,4 MB`. |
| **Seção 4** (Células `09–10`) | Benchmark 5-Fold CV (`Dummy`, `Ridge`, `RandomForest`, `XGBoost`) no MLflow e plota `01_benchmark_5fold_cv.png`. | `~10,6 min` (`637,6 s`) | Ganho claro das árvores (`R² ~0,334–0,336`) sobre o linear `Ridge` (`0,2836`) e `Dummy` (`0,0000`). |
| **Seção 5** (Células `11–12`) | *Tuning* 3-Fold CV (5 RF + 6 XGB em *Nested Runs*, `~41,5 min`) + Curva de Aprendizado (`50k` a `15M`, `~14,9 min`) e `02_curva_aprendizado_escalavel.png`. | `~56 min` | Melhores configs (`RF-02` e `XGB-01`) e estabilização do $\text{RMSE}$ em `57,73–57,75 pts` a partir de `1M–5M`. |
| **Seção 6** (Células `13–14`) | Treino final RF (`3M`, `467,9 s`) vs. XGBoost (`27,07M + ES`, `1.814,5 s`), Holdout `7,52M`, auditoria anual (`03_estabilidade_anual_holdout.png`) e OOT `2023` (`1.420,0 s`). | `~38 min` (RF+XGB) `+ ~23,7 min` (OOT) | Eleição do `XGBRegressor`, tabela anual `2014–2023` (atenção à anomalia de `2018`) e métricas OOT `2023` completas. |
| **Seção 7** (Células `15–16`) | Calcula `TreeSHAP` exato em `10.000` alunos do Holdout, valida aditividade e gera 4 figuras (`04a`, `04b`, `05` e `06`). | `17,08 s` | `ERRO ADITIVIDADE MÁX = 1.26e-03` (abaixo do limite `assert < 0.05`) e liderança de `RENDA_PER_CAPITA` (`30,10%`). |
| **Seção 8** (Células `17–18`) | Exporta `models/enem.pkl`, `models/enem_xgboost.ubj`, `models/enem_model_card.json`, registra no *MLflow Registry* (S3) e roda *Smoke Test* API. | `~15 s` | `enem.pkl` (`1,727 MB`), `SHA-256`, URI `models:/m-ea7931423f5141379ff97886636ae0ea` (`enem_target_m4_producao` v1) e RSS final `1.689,0 MB`. |
| **Anexo Slides** (Célula `19`) | 6 diagramas Mermaid auxiliares para slides da apresentação de TCC. | — | *Nota:* nos slides desta célula, o *Tuning* é rotulado como "Estágio 2" (convenção visual distinta das Seções 4–5 do código). |

> **Estado salvo do notebook (`21/11/2026` — Fase 3):** Todas as células executáveis (`02`, `06`, `08`, `10`, `12`, `14`, `16` e `18`, com `execution_count` `1` a `8`) foram reexecutadas integralmente sem erros contra o servidor MLflow (`PostgreSQL + S3`), preservando todas as saídas — incluindo o bloco completo do **OOT `2023`**, gráficos SHAP e Model Card sincronizado (`run_id = 6490c396b0e04147b156bedb0c8af9f7`).

---

## 5. Síntese dos Resultados Obtidos na Execução Homologada

| Etapa / Avaliação | Modelo / Escopo | $R^2$ | RMSE (pts TRI) | MAE (pts TRI) | Observações-Chave |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Estágio 1 (5-Fold CV, `1M`)** | `DummyRegressor` | `-0,0000` | `71,00` | `56,83` | Piso nulo ($\text{RMSE}/\sigma = 1,0000$). |
| **Estágio 1 (5-Fold CV, `1M`)** | `Ridge` ($\alpha = 1,0$) | `0,2836` | `60,09` | `47,52` | Benchmark linear ($\text{RMSE}/\sigma = 0,8464$). |
| **Estágio 1 (5-Fold CV, `1M`)** | `RandomForestRegressor` | `0,3337` | `57,95` | `45,76` | Ganho não-linear relevante vs. `Ridge`. |
| **Estágio 1 (5-Fold CV, `1M`)** | `XGBRegressor` (`hist`) | `0,3359` | `57,86` | `45,67` | Melhor já na baseline de CV (`215,5 s` vs. `400,4 s` do RF). |
| **Estágio 1b (Tuning 3-Fold CV)** | Melhor RF (`RF-02`) vs. Melhor XGB (`XGB-01`) | `0,33356` vs. `0,33578` | `57,9589` vs. `57,8619` | — | `XGB-01`: `300 trees, lr=0.10, depth=5, mcw=30, l2=1.0`. |
| **Estágio 2 (Curva XGB, `3,01M` val)** | `50k` $\rightarrow$ `1M` $\rightarrow$ `5M` $\rightarrow$ `15M` | `0,32967` $\rightarrow$ `0,33716` | `58,059` $\rightarrow$ `57,734` | — | Platô de convergência atingido entre `1M` (`57,755`) e `5M` (`57,738`). |
| **Estágio 3 (Holdout `7,52M`)** | `RandomForestRegressor` (`3M`) | `0,33606` | `57,8198` | `45,6635` | Latência: `141,660 ms / 10k` amostras. |
| **Estágio 3 (Holdout `7,52M`)** | **`XGBRegressor` Campeão** (`27,07M + ES`) | **`0,33780`** | **`57,7439`** | **`45,5904`** | **+19,1% relativo em $R^2$ vs. `Ridge`**; latência **`98,561 ms / 10k`**. |
| **Auditoria Anual (Holdout)** | Anos `2014–2023` (destaque `2018`) | `0,312–0,363` (`2018`: `0,22595`) | `53,53–67,45` | `42,06–52,75` | Em `2018`, a média real subiu para `533,54` vs. `509,73` prevista (viés `-23,81 pts`). |
| **Estágio 3C (OOT Interno `2023`)** | `XGBRegressor` (`2014–2022 -> 2023`, `2,68M`) | `0,31842` | `67,6232` | `52,8526` | Viés médio `-5,516 pts` (`-5,52 pts` no log), confirmando generalização temporal. |

---

## 6. Como Abrir e Explorar o Painel Visual do MLflow UI (`PostgreSQL + S3`)

Desde a **Fase 3**, o tracking foi migrado do antigo `SQLite` local para a arquitetura dual em containers (**Backend Store** no `PostgreSQL 16` + **Artifact Store** no `Amazon S3` em `s3://tcc-enem-saulo-mlops-703671922740/mlflow-artifacts`).

Para subir o servidor MLflow e visualizar os experimentos gravados (certifique-se de ter suas credenciais AWS válidas em `~/.aws`), execute na raiz do projeto (`/home/saulo/mba/tcc/enem`):

```bash
docker compose --profile mlops up -d
```

Em seguida, acesse **`http://127.0.0.1:5000`** no navegador (e para encerrar ao final, rode `docker compose --profile mlops down`):
1. Na aba **Experiments** (`tcc_enem_decada_ouro_2014_2023`, Experiment ID `2`), você verá todas as rodadas organizadas por estágio (`estagio1_cv_*`, `estagio1_tuning_parent_*` expansível com os 11 *trials* filhos, `estagio2_curva_aprendizado_escalavel`, `estagio3_*` com o run campeão `6490c396b0e04147b156bedb0c8af9f7` e os artefatos hospedados no S3).
2. Selecione os *trials* de *tuning* e clique em **Chart view -> Parallel Coordinates** para capturar o gráfico da relação entre hiperparâmetros e `cv_rmse_mean`.
3. Na aba **Models**, clique em **`enem_target_m4_producao` (Version 1)** para visualizar o modelo registrado (`models:/m-ea7931423f5141379ff97886636ae0ea`) e sua assinatura oficial de entrada/saída (`Schema`).

*(Consulte também o guia específico [`docs/guia-estudo-mlflow-postgresql-s3.md`](guia-estudo-mlflow-postgresql-s3.md) para detalhes da arquitetura e verificação do bucket S3.)*

---

## 7. Defesa Sociológica e Estatística com Valores SHAP (Seção 7)

Para responder perguntas da banca sobre *"caixa-preta de algoritmos de Machine Learning"*:
* **Decomposição Exata em Pontos TRI:** Ao contrário da importância por ganho de Gini (que é adimensional e enviesada para variáveis contínuas), os valores SHAP têm **unidade física direta em pontos da prova do ENEM**. Com valor base $\phi_0 = \mathbb{E}[f(X)] = 511,04$ pontos (próximo à média global da década de `511,05`), um aluno com $\phi_{\text{RENDA}} = +42,0$ pontos tem sua nota esperada elevada em exatos `42` pontos na escala TRI por aquela condição econômica.
* **Hierarquia Empírica (|SHAP| médio em `10.000` amostras do Holdout):**
  1. `RENDA_PER_CAPITA`: **`18,483 pts` (`30,10%`)** — amplitude de `-41,93` a `+85,96 pts`;
  2. `TP_LINGUA`: **`10,895 pts` (`17,74%`)** — amplitude de `-24,82` a `+18,22 pts`;
  3. `Q024` (Computador): **`9,487 pts` (`15,45%`)** — amplitude de `-19,37` a `+53,60 pts`;
  4. `TP_ANO_CONCLUIU`: **`8,958 pts` (`14,59%`)** — amplitude de `-15,26` a `+29,29 pts`;
  5. `Q002` (Escolaridade Materna): **`8,642 pts` (`14,07%`)** — amplitude de `-42,82` a `+27,64 pts`;
  6. `TP_SEXO`: **`4,946 pts` (`8,05%`)** — amplitude de `-13,06` a `+12,46 pts`.
* **Comprovação Empírica de Bourdieu (`05_shap_interacoes_bourdieu.png`):**
  * **Painel esquerdo (`RENDA_PER_CAPITA × Q024`):** O efeito marginal da renda é **fortemente côncavo** — sair da extrema pobreza (`0,0` a `0,5 SM`) para `~2,0 SM` produz o maior salto de desempenho, enquanto ganhos acima de `~4–5 SM` exibem retorno marginal decrescente (confirmando a privação material severa como principal freio educacional).
  * **Painel direito (`Q002 × TP_LINGUA`):** Demonstra o peso conjunto do **Capital Cultural Institucionalizado**, com vantagem sistemática e expressiva para quem opta por **Inglês (`TP_LINGUA = 0`)** em comparação a Espanhol (`1`) em todos os níveis. A contribuição conjunta cresce monotonicamente de **`Q002 = 0`** (*Nunca estudou*) até **`Q002 = 5`** (*Superior completo*), apresenta uma **leve inflexão negativa em `Q002 = 6`** (*Pós-graduação*) e **despenca em `Q002 = 7`**, pois o código `7` representa a categoria não-ordinal **"Não sei"** (também visível pelos pontos altos em vermelho no lado negativo de `04b_shap_beeswarm.png`).

---

## 8. Checklist de Validação Final do Notebook 06

Após subir o stack `mlops` (`docker compose --profile mlops up -d`) e executar todas as células de [`notebooks/06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb) no kernel **`Python (ENEM .venv)`**, confira:

- [ ] A Seção 1 conectou ao MLflow remoto em `http://127.0.0.1:5000` com `Artifact Store` no Amazon S3?

- [ ] A Seção 2 validou o `SHA-256` do Parquet consolidado sem erros?
- [ ] A Seção 4 confirmou a superioridade dos modelos de árvore (*Random Forest* e *XGBoost*) frente ao modelo linear `Ridge` e ao `Dummy`?
- [ ] A Seção 6 elegeu o `modelo_campeao` no Holdout de `7,52 milhões` de candidatos e concluiu integralmente a rodada *Out-of-Time* na safra `2023` cega (`2.678.264` alunos)?
- [ ] As **7 figuras** de alta resolução foram geradas em `media/nb06_figuras/` (`01`, `02`, `03`, `04a`, `04b`, `05` e `06`)?
- [ ] Os artefatos finais de produção existem na pasta `models/` e passaram no *Smoke Test* da Seção 8?
  - `models/enem.pkl` (`1,727 MB`, estimador campeão puro compatível com `pickle.load` e `joblib.load`)
  - `models/enem_xgboost.ubj` (binário nativo XGBoost)
  - `models/enem_model_card.json` (contrato completo de inferência para a Etapa 2 — FastAPI + Docker + AWS)
  - `models/auditoria_holdout_por_ano_2014_2023.csv` (auditoria anual desagregada no Holdout)
