# 📘 Guia Passo a Passo e Documentação Complementar — Notebook 06

**Arquivo do Notebook:** [`notebooks/06_treinamento_modelo.ipynb`](notebooks/06_treinamento_modelo.ipynb)  
**Projeto de TCC:** MBA em Ciência de Dados & MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  

---

## 1. Visão Geral: O Fechamento da Etapa 1 e a Ponte para Produção (AWS & Airflow)

Na arquitetura em três etapas do projeto, o **Notebook 06** é o elo que transforma **37.593.629 registros históricos harmonizados** em um **modelo preditivo auditado, explicável e serializado para nuvem**:

```text
ETAPA 1 — LABORATÓRIO CIENTÍFICO, NLP E MLFLOW (Concluída neste Notebook)
[01_investigacao] ─> [02_eda] ─> [03_features] ─> [04_nlp_sbert] ─> [05_consolidacao] ─> ⭐ [06_treinamento_modelo]
                                                                                                  │
                       ┌──────────────────────────────────────────────────────────────────────────┴───────────────────┐
                       ▼                                                                                              ▼
ETAPA 2 — PRODUTIZAÇÃO E DEPLOY CONTÍNUO (AWS)                                     ETAPA 3 — ORQUESTRAÇÃO E OOT (2024+)
[models/enem.pkl + enem_model_card.json] ─> FastAPI ─> Docker ─> AWS App Runner    Apache Airflow ─> ENEM 2024 ─> Auditoria Drift MLflow
```

---

## 2. Estratégia de Particionamento: Rigor Estatístico sem Duplicação de Memória RAM

A base consolidada `data/processed/enem_2014_2023_consolidado.parquet` ocupa **537,78 MB em RAM** (`15 bytes/linha`). Para evitar que funções genéricas de particionamento criem cópias simultâneas e vetores `int64` de `300+ MB`, utilizamos na **Seção 3** um vetor único de códigos `uint8` (`1 byte/linha ≈ 35,8 MB`) estratificado exatamente dentro de cada edição (`NU_ANO` de `2014` a `2023`):

| Partição | Proporção Global | Registros Aproximados | Papel Estrito (Zero Vazamento) |
| :--- | :---: | :---: | :--- |
| **`df_fit`** | **72,0%** (90% dos 80% de Dev) | `~27.067.413` | *Pool* censitário principal para ajuste de parâmetros e extração da amostra de CV. |
| **`df_val_es`** | **8,0%** (10% dos 80% de Dev) | `~3.007.490` | Conjunto fixo exclusivo para *Early Stopping* do XGBoost e medição da Curva de Aprendizado. |
| **`df_test`** | **20,0%** (Holdout Cego) | `~7.518.726` | Conjunto **100% lacrado** durante todo o *tuning* — aberto apenas uma vez na Seção 6 para eleger o campeão. |
| **`df_cv`** | Subamostra de `df_fit` | `1.000.000` | Extraída **somente de `df_fit`** para competição rápida em 5-Fold CV e *Tuning* (Estágio 1). |

> **Blindagem Dupla (Estratificada + Temporal):** Além da avaliação estratificada nos `7,52 milhões` de candidatos do Holdout (`2014–2023`), a **Seção 6 (Bloco 6.3)** executa uma rodada independente de **Validação *Out-of-Time* Interna**, treinando exclusivamente de `2014` a `2022` e avaliando nos **`2.678.264` candidatos integrais de `2023`**. Isso comprova à banca que o modelo generaliza para edições futuras inéditas antes mesmo de conectarmos o ENEM 2024 na Etapa 3.

---

## 3. Arquitetura Escalável em 3 Estágios (CPU de 8 Threads / 7,7 GB de RAM)

Por que dividimos a competição entre **Random Forest** (*Bagging*) e **XGBoost** (*Gradient Boosting*) em **3 estágios**?

1. **Estágio 1 — Batalha Concorrente em 5-Fold CV + *Tuning* (`N = 1.000.000`):**
   * Avalia nos **exatos mesmos 5 folds estratificados**: `DummyRegressor`, `Ridge` (benchmark linear), `RandomForestRegressor` e `XGBRegressor`.
   * Mantemos `n_jobs=1` no laço externo do `cross_validate` e paralelismo máximo **dentro** das árvores (`n_jobs` interno). Assim, todos os núcleos da CPU trabalham a 100% sem clonar matrizes em processos paralelos do sistema operacional.
   * Em seguida, refinamos os hiperparâmetros das duas famílias de árvores registrando cada tentativa como *Nested Run* no MLflow.
2. **Estágio 2 — Curva de Aprendizado Escalável (`50k` $\rightarrow$ `200k` $\rightarrow$ `1M` $\rightarrow$ `5M` $\rightarrow$ `15M`):**
   * Como nossas 6 features formam um espaço discreto e bem comportado, o gráfico de convergência prova matematicamente onde a variância amostral zera e o $\text{RMSE}$ estabiliza.
3. **Estágio 3 — Treinamento Final em Escala Censitária (`7,52M` no Holdout):**
   * **Diferença física de algoritmos em Big Data:** O `RandomForestRegressor` clássico (`scikit-learn`) constrói vetores `int64` (`np.bincount`) do tamanho total de $N$ em cada thread; por isso, ajustá-lo em `3.000.000` de alunos estratificados opera no ponto ótimo assintótico da curva consumindo `< 300 MB` de RAM. Já o **`XGBRegressor(tree_method="hist")`** comprime as 6 features em *bins* inteiros de `1 byte` (`max_bin=256`), ajustando-se nos **`27.067.413` registros integrais de `df_fit`** (+ `3.007.490` de *Early Stopping*) com pico total do processo abaixo de `~2,2 GB` de RAM!
   * Ambos são avaliados em lotes de `1.000.000` de linhas (`prever_em_blocos`) sobre os mesmos **`7.518.726` alunos cegos de `df_test`**.

---

## 4. Roteiro Detalhado Célula por Célula

| Seção / Células | O que Executa | Tempo Estimado | O que Conferir na Saída |
| :--- | :--- | :---: | :--- |
| **Seção 1** (Células 01–02) | Imports, `SEED=42`, detecção de núcleos CPU, utilitários de memória/métricas e criação do `sqlite:///mlflow.db`. | `~2 s` | Confirmação de versões (`sklearn`, `xgboost`, `mlflow`, `shap`) e criação do experimento `tcc_enem_decada_ouro_2014_2023`. |
| **Seção 2** (Células 03–04) | Verifica o hash `SHA-256` do Parquet do Notebook 05, carrega os `37,59M` registros e aplica travas *Anti-Leakage*. | `~6 a 10 s` | `Integridade SHA-256: OK`, `537.78 MB (15.00 bytes/linha)` e confirmação de exclusão de `NU_ANO` de `X`. |
| **Seção 3** (Células 05–06) | Particiona em `df_fit` (72%), `df_val_es` (8%) e `df_test` (20%) sem dobrar RAM e extrai `df_cv` (`1M`). | `~8 a 15 s` | Tabela mostrando médias idênticas de `TARGET_M4` (`~511.05`) e soma de RAM controlada (`~552 MB`). |
| **Seção 4** (Células 07–08) | Executa o Benchmark 5-Fold CV (`Dummy`, `Ridge`, `RandomForest`, `XGBoost`) e plota `01_benchmark_5fold_cv.png`. | `~1,5 a 3 min` | Ganho expressivo das árvores não-lineares frente ao modelo linear `Ridge` e desvio-padrão mínimo entre folds. |
| **Seção 5** (Células 09–10) | Executa o *Tuning* concorrente (5 *trials* RF + 6 *trials* XGB via *Nested Runs*) + Curva de Aprendizado (`50k` a `15M`). | `~4 a 7 min` | Melhores hiperparâmetros impressos e gráfico `02_curva_aprendizado_escalavel.png` convergindo suavemente. |
| **Seção 6** (Células 11–12) | Treino final RF (`3M`) vs. XGBoost (`27,07M + ES`), eleição do campeão em `7,52M`, auditoria anual e teste OOT `2023`. | `~3 a 6 min` | Coroação do `modelo_campeao`, tabela anual `2014–2023`, gráfico `03_estabilidade_anual_holdout.png` e $R^2$ cego de `2023`. |
| **Seção 7** (Células 13–14) | Calcula `TreeSHAP` exato em `10.000` alunos do Holdout, valida aditividade e gera 4 painéis sociológicos. | `~10 a 25 s` | `ERRO ADITIVIDADE MÁX < 1e-4`, liderança de `RENDA_PER_CAPITA` / capital cultural e gráficos `04a`, `04b`, `05` e `06`. |
| **Seção 8** (Células 15–16) | Exporta `models/enem.pkl`, `models/enem_model_card.json`, registra no *MLflow Registry* e roda *Smoke Test* da API. | `~5 a 10 s` | Confirmação de `enem.pkl` salvo, `SHA-256`, URI do modelo registrado e tabela final de simulação FastAPI. |

---

## 5. Como Abrir e Explorar o Painel Visual do MLflow UI

Todas as execuções do notebook são gravadas localmente no banco relacional `mlflow.db` e na pasta `mlruns/` na raiz do projeto. Após rodar o notebook, abra um terminal na pasta `/home/saulo/mba/tcc/enem` com o `.venv` ativo e execute:

```bash
source .venv/bin/activate
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

Em seguida, acesse **`http://localhost:5000`** no navegador:
1. Na aba **Experiments** (`tcc_enem_decada_ouro_2014_2023`), você verá todas as rodadas organizadas por estágio (`estagio1_cv_*`, `estagio1_tuning_parent_*` expansível com os 11 *trials* filhos, `estagio2_curva_aprendizado_escalavel` e `estagio3_*`).
2. Selecione os *trials* de *tuning* e clique em **Chart view -> Parallel Coordinates** para capturar um gráfico excelente para os slides da banca mostrando a relação entre hiperparâmetros e `cv_rmse_mean`.
3. Na aba **Models**, clique em **`enem_target_m4_producao` (Version 1)** para visualizar a assinatura oficial de entrada/saída (`Schema`) pronta para produção.

---

## 6. Defesa Sociológica e Estatística com Valores SHAP (Seção 7)

Para responder perguntas da banca sobre *"caixa-preta de algoritmos de Machine Learning"*:
* **Decomposição Exata em Pontos TRI:** Ao contrário da importância por ganho de Gini (que é adimensional e enviesada para variáveis contínuas), os valores SHAP têm **unidade física direta em pontos da prova do ENEM**. Se o valor base $\phi_0 = \mathbb{E}[f(X)] \approx 511,05$ pontos e um aluno recebe $\phi_{\text{RENDA}} = +42,0$ pontos, aquela condição econômica específica elevou sua nota esperada em exatos `42` pontos na escala TRI.
* **Comprovação Empírica de Bourdieu:**
  * O gráfico `05_shap_interacoes_bourdieu.png` (painel esquerdo) revela que o efeito da `RENDA_PER_CAPITA` é **fortemente côncavo**: sair da extrema pobreza (`0,0` a `0,5 SM`) para `2,0 SM` produz um salto dramático de desempenho, enquanto ganhos adicionais acima de `5 SM` apresentam retorno marginal decrescente — confirmando que a privação material severa é o principal freio cognitivo.
  * O painel direito demonstra o efeito cumulativo do **Capital Cultural Institucionalizado**: a cada degrau de escolaridade materna (`Q002`), a nota esperada sobe consistentemente, com vantagem sistemática para os candidatos que optam por Inglês (`TP_LINGUA = 0`), proxy clássico de bagagem escolar prévia.

---

## 7. Checklist de Validação Final do Notebook 06

Após executar todas as células de [`notebooks/06_treinamento_modelo.ipynb`](notebooks/06_treinamento_modelo.ipynb) no kernel **`Python (ENEM .venv)`**, confira:

- [ ] A Seção 2 validou o `SHA-256` do Parquet consolidado sem erros?
- [ ] A Seção 4 confirmou a superioridade dos modelos de árvore (*Random Forest* e *XGBoost*) frente ao modelo linear `Ridge` e ao `Dummy`?
- [ ] A Seção 6 elegeu o `modelo_campeao` no Holdout de `7,52 milhões` de candidatos e validou a generalização *Out-of-Time* na safra `2023` cega?
- [ ] As 6 figuras de alta resolução foram geradas em `media/nb06_figuras/`?
- [ ] Os artefatos finais de produção existem na pasta `models/` e passaram no *Smoke Test* da Seção 8?
  - `models/enem.pkl` (estimador campeão puro compatível com `pickle.load` e `joblib.load`)
  - `models/enem_model_card.json` (contrato completo de inferência para a Etapa 2 — FastAPI + Docker + AWS)

