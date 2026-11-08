# 📊 Roteiro de Slides: Notebook 06 — Treinamento Escalável, MLflow e XAI (2014–2023)

**Projeto de TCC:** MBA em Ciência de Dados / MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  
**Notebook de Referência:** [`notebooks/06_treinamento_modelo.ipynb`](file:///home/saulo/mba/tcc/enem/notebooks/06_treinamento_modelo.ipynb)  
**Foco da Defesa:** Modelagem Censitária em Big Data (`37,59M` registros), Disputa Concorrente *Bagging vs. Boosting*, Governança **MLflow**, Explicabilidade Sociológica (**TreeSHAP**) e Serialização de Produção (`models/enem.pkl`).

---

## 🧭 Visão Panorâmica da Apresentação (Arco Narrativo para a Banca)

1. **O Desafio Computacional:** Treinar ensembles não lineares sobre **37,59 milhões de estudantes** em hardware local (`7,7 GB` de RAM) com zero vazamento de dados.
2. **A Prova da Não-Linearidade (Estágio 1):** Demonstrar sob **5-Fold CV** que árvores capturam **+19,1% mais variância explicada** que modelos lineares nas mesmas 6 features.
3. **Escalabilidade Científica (Estágios 2 e 3):** Curva de aprendizado assintótica (`50k` $\rightarrow$ `15M`) e coroação do **`XGBRegressor`** em **7,52 milhões** de candidatos cegos.
4. **Resiliência Temporal:** Auditoria anual da Década de Ouro (`2014–2023`), explicação psicométrica da anomalia TRI de `2018` e validação *Out-of-Time* cega em `2023` (`2,68M` alunos).
5. **Sociologia Quantitativa (XAI):** Decomposição exata em pontos da TRI via **TreeSHAP**, traduzindo o capital econômico e cultural de Pierre Bourdieu em métricas auditáveis.
6. **Entrega MLOps (Fechamento da Etapa 1):** Registro oficial no **MLflow Model Registry** e exportação de um artefato ultraleve (`1,73 MB`) pronto para **FastAPI + Docker + AWS**.

---

## 🎯 Slide 1 — Arquitetura de Treinamento Escalável e Governança MLOps
> **Mapeamento no Notebook:** Seções 1 e 2 — Células 01 a 04 (Configuração MLflow, Verificação `SHA-256` e Travas *Anti-Leakage*)

### Mensagem Central
> *"Big Data não exige desperdício computacional: com tipagem enxuta e governança criptográfica, processamos uma década inteira do ENEM em 537,8 MB de RAM com rastreabilidade total no MLflow."*

### Layout Visual Recomendado
* **Topo (Diagrama de Fluxo em 3 Estágios):**
  `Parquet Consolidado (37,59M | SHA-256 OK)` $\longrightarrow$ `[Estágio 1: 5-Fold CV + Tuning (1M)]` $\longrightarrow$ `[Estágio 2: Curva de Aprendizado (50k → 15M)]` $\longrightarrow$ `[Estágio 3: Treino Censitário (27,07M) + Holdout Cego (7,52M)]` $\longrightarrow$ `MLflow Registry + enem.pkl`.
* **Cards de Indicadores Técnicos na Base do Slide:**
  * **Volume Censitário:** `37.593.629` candidatos (`2014–2023`)
  * **Pegada em RAM:** `537,78 MB` (`15,00 bytes/linha`)
  * **Rastreabilidade:** `20/20 runs` auditadas em `sqlite:///mlflow.db`

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Linhagem Criptográfica:** Validação automática do hash `SHA-256` do Parquet consolidado no Notebook 05 antes de iniciar o treino;
* **Blindagem *Anti-Temporal Leakage*:** A coluna `NU_ANO` é usada apenas para estratificação e **bloqueada na matriz preditora `X`**, obrigando o modelo a aprender relações socioeconômicas puras (sem memorizar a edição da prova);
* **Alvo Unificado (`TARGET_M4`):** Média global histórica de **`511,05 ± 70,97` pontos** na escala TRI;
* **Governança Reprodutível:** Semente determinística global (`SEED = 42`) e backend relacional **MLflow 3.17.2**.

### Trecho de Código para o Slide
```python
# Célula 04 — Verificação Criptográfica e Bloqueio de Vazamento Temporal
assert calcular_sha256(CAMINHO_PARQUET) == contrato["sha256_parquet"]
assert "NU_ANO" not in FEATURES_ELITE, "Violação: NU_ANO jamais entra em X!"
# 37.593.629 linhas × 8 colunas carregadas em 537,78 MB de RAM (15,00 B/linha)
```

### Roteiro de Fala do Apresentador
> *"Senhores membros da banca, no Notebook 06 encerramos a Etapa 1 transformando os 37,6 milhões de estudantes harmonizados no Notebook 05 em nosso modelo oficial de produção. Antes de qualquer ajuste matemático, o código verifica o hash SHA-256 da base e aplica uma trava crítica de engenharia: a variável `NU_ANO` é proibida de entrar na matriz `X`. Queremos um modelo atemporal, capaz de operar em 2024 ou 2025 na nuvem sem depender do calendário."*

---

## 🛡️ Slide 2 — Particionamento Censitário Sem Vazamento em Baixa Memória
> **Mapeamento no Notebook:** Seção 3 — Células 05 e 06 (Máscara Estratificada `uint8` e Isolamento de Partições)

### Mensagem Central
> *"Separamos 7,52 milhões de estudantes em um cofre cego intocável e isolamos 3,01 milhões exclusivamente para Early Stopping, mantendo o consumo total das partições em 552 MB de RAM."*

### Layout Visual Recomendado
* **Tabela Oficial das Partições Estratificadas por `NU_ANO`:**

| Partição | Proporção | Volume de Alunos | Média `TARGET_M4` | Desvio ($\sigma$) | Papel Metodológico Estrito |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`df_fit`** | **72,0%** | `27.067.413` | `511,04` | `70,98` | *Pool* censitário de treino e origem de `df_cv` (`1M`) |
| **`df_val_es`** | **8,0%** | `3.007.490` | `511,08` | `70,91` | Exclusivo para *Early Stopping* e Curva de Aprendizado |
| **`df_test`** | **20,0%** | **`7.518.726`** | **`511,07`** | **`70,96`** | **Holdout Cego Final** (aberto uma única vez na Seção 6) |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Engenharia de Memória (`uint8`):** Substituição do `train_test_split` convencional (que gera vetores `int64` pesados e cópias simultâneas) por uma máscara inteira de `1 byte/linha` (`~35,8 MB`), executada em **`8,74 segundos`**;
* **Equilíbrio Estatístico Perfeito:** Diferença de média do alvo entre treino, validação e teste inferior a **`0,04 ponto`** na escala TRI;
* **Isolamento Triplo contra *Data Leakage*:** Nem o *tuning* (feito dentro de `df_fit`) nem a parada antecipada das árvores (`df_val_es`) encostam nos **`7,52 milhões`** de alunos do Holdout.

### Roteiro de Fala do Apresentador
> *"Um erro comum em projetos de Machine Learning é usar o mesmo conjunto de teste para calibrar o Early Stopping do XGBoost, gerando vazamento sutil de informação. Aqui aplicamos separação tripla estrita: 72% para treino, 8% dedicados exclusivamente ao Early Stopping e 20% — mais de 7,5 milhões de candidatos estratificados ano a ano — trancados como Holdout Cego."*

---

## ⚔️ Slide 3 — Estágio 1: Batalha em 5-Fold CV e a Prova da Não-Linearidade
> **Mapeamento no Notebook:** Seção 4 — Células 07 e 08 | **Figura:** [`media/nb06_figuras/01_benchmark_5fold_cv.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/01_benchmark_5fold_cv.png)

### Mensagem Central
> *"Sobre exatamente as mesmas 6 variáveis socioeconômicas, algoritmos de árvore elevam o $R^2$ de 0,2836 (linear) para 0,3359 — provando que o determinismo social opera por sinergias não lineares."*

### Layout Visual Recomendado
* **Lado Esquerdo:** Inserir a figura [`01_benchmark_5fold_cv.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/01_benchmark_5fold_cv.png).
* **Lado Direito — Tabela Comparativa Oficial (`5-Fold CV Estratificado`, `N = 1.000.000`):**

| Família / Modelo | $R^2$ Validação ($\uparrow$) | RMSE ($\downarrow$) | MAE ($\downarrow$) | $\text{RMSE}/\sigma$ ($\downarrow$) | Tempo 5-Fold |
| :--- | :---: | :---: | :---: | :---: | :---: |
| *Baseline Nulo* (`Dummy`) | `0,0000 ± 0,0000` | `71,00 pts` | `56,83 pts` | `1,0000` | `4,7 s` |
| *Linear L2* (`Ridge`) | `0,2836 ± 0,0019` | `60,09 pts` | `47,52 pts` | `0,8464` | `2,5 s` |
| *Bagging* (`RandomForest`) | `0,3337 ± 0,0016` | `57,95 pts` | `45,76 pts` | `0,8162` | `365,5 s` |
| ***Boosting* (`XGBRegressor`)** | **`0,3359 ± 0,0017`** | **`57,86 pts`** | **`45,67 pts`** | **`0,8149`** | **`130,1 s`** |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Salto Não Linear Comprovado:** Ganho direto de **`+5,23 pontos percentuais` em $R^2$** (`+19,1%` de variância explicada relativa no Holdout) frente à regressão linear regularizada;
* **Estabilidade Extrema entre Folds:** Desvio-padrão de apenas **`±0,0017`** nos 5 folds estratificados;
* **Eficiência Algorítmica:** O `XGBRegressor (tree_method="hist")` superou o `RandomForestRegressor` em todas as métricas sendo **2,8 vezes mais rápido**.

### Roteiro de Fala do Apresentador
> *"Por que não usar uma simples regressão linear se temos apenas 6 features? Este experimento responde matematicamente: ao manter exatamente os mesmos 5 folds de 1 milhão de alunos, a regressão Ridge estaciona em 28,4% de $R^2$, enquanto o Random Forest e o XGBoost saltam para quase 33,6%. Esse ganho prova que o capital econômico interage de forma multiplicativa e côncava com a posse de computador e a escolaridade materna."*

---

## 📈 Slide 4 — Tuning (*Nested Runs*) e Estágio 2: Curva de Aprendizado Escalável
> **Mapeamento no Notebook:** Seção 5 — Células 09 e 10 | **Figura:** [`media/nb06_figuras/02_curva_aprendizado_escalavel.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/02_curva_aprendizado_escalavel.png)

### Mensagem Central
> *"Árvores rasas (`max_depth=5`) regularizadas eliminam o overfitting, e a curva de aprendizado de 50 mil a 15 milhões de alunos comprova a convergência assintótica do gradiente."*

### Layout Visual Recomendado
* **Destaque Central/Direito:** Projetar a figura [`02_curva_aprendizado_escalavel.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/02_curva_aprendizado_escalavel.png) (convergência das curvas de Treino e Validação em `3,01M` de alunos).
* **Quadro Lateral — Hiperparâmetros Vencedores Auditados em *Nested Runs* (`3-Fold CV`):**
  * **`XGB-01` (Vencedor Boosting):** `max_depth=5` ($32$ folhas), `learning_rate=0.1`, `min_child_weight=30`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`.
  * **`RF-02` (Vencedor Bagging):** `n_estimators=150`, `max_depth=12`, `min_samples_leaf=20`, `max_features='sqrt'`.

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Por que `max_depth=5` venceu `max_depth=6` e `8`?** Com 6 preditores, profundidade 5 modela interações de até **5ª ordem** sem memorizar ruído residual de células raras;
* **Diagnóstico *Bias-Variance* (`50k` $\rightarrow$ `15M`):**
  * Em `50.000` alunos: Gap Treino-Validação de **`0,97 ponto`** (`57,09` vs. `58,06` pts);
  * A partir de `1.000.000` de alunos: Curvas colam assintoticamente;
  * Em `15.000.000` de alunos: Gap cai para **`0,03 ponto`** (`57,76` vs. `57,73` pts, $R^2 = 0,33716$).
* **Justificativa de Engenharia:** Legitima ajustar o `RandomForest` em `3M` (já no platô assintótico sem estourar vetores `int64`) e escalar o `XGBoost (hist)` aos **`27,07M` integrais** via histogramas `uint8`.

### Roteiro de Fala do Apresentador
> *"Observem no gráfico da Curva de Aprendizado como a engenharia orienta a ciência: em 50 mil amostras ainda existe uma leve distância entre treino e validação; ao cruzarmos 1 milhão e chegarmos a 15 milhões de estudantes, as duas curvas se fundem com diferença de três centésimos de ponto. Isso prova que nosso modelo atingiu a fronteira Bayesiana de informação contida nas 6 variáveis, com zero sobreajuste."*

---

## 🏆 Slide 5 — Estágio 3: Disputa Final no Holdout Cego (`7,52M`) e Coroação
> **Mapeamento no Notebook:** Seção 6 (Blocos 6.1) — Células 11 e 12

### Mensagem Central
> *"Avaliado em 7.518.726 candidatos inéditos, o `XGBRegressor` conquista a coroa oficial combinando maior precisão estatística, treinamento censitário em 27 milhões de linhas e inferência 35% mais veloz."*

### Layout Visual Recomendado
* **Placar Oficial do Confronto Final no Holdout Cego (`N = 7.518.726`):**

| Critério de Homologação | `RandomForestRegressor` (*Bagging*) | `XGBRegressor` (*Boosting Campeão*) | Vantagem do Campeão |
| :--- | :---: | :---: | :---: |
| **Amostra Efetiva de Treino** | `3.000.000` (platô estratificado) | **`27.067.413` + `3,01M` ES (`649` árvores)** | **Escala 100% Censitária** |
| **$R^2$ no Holdout Cego (`7,52M`)** | `0,33606` | **`0,33780`** | **`+0,174 pp` (`+19,1%` vs. Linear)** |
| **RMSE no Holdout Cego** | `57,8198 pts` | **`57,7439 pts`** | **Menor Erro Quadrático** |
| **MAE no Holdout Cego** | `45,6635 pts` | **`45,5904 pts`** | **Menor Erro Absoluto** |
| **Erro Relativo ($\text{RMSE}/\sigma$)** | `0,81483` | **`0,81376`** | **Maior Compressão de Variância** |
| **Latência de Inferência (`10k` linhas)** | `124,42 ms` | **`81,15 ms`** | **35% Mais Rápido para API** |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Inferência em Lotes Controlados:** Predição sobre os `7,52 milhões` de candidatos executada em blocos de `1M` linhas (`prever_em_blocos`), mantendo o kernel inteiro em **`2,26 GB` de RAM** (`4,26 GB` livres no host);
* **Parada Ótima Automática:** O *Early Stopping* sobre `df_val_es` convergiu na iteração **`649`** de `800`, blindando a generalização;
* **Adequação para Nuvem (Etapa 2):** Latência sub-milissegundo por requisição individual (`~0,008 ms`/aluno em lote) e modelo final compacto de **`1,73 MB`**.

### Roteiro de Fala do Apresentador
> *"No confronto definitivo diante de 7,52 milhões de estudantes nunca vistos, ambos os ensembles tiveram performance extraordinária e coerente com a validação cruzada. Contudo, o XGBoost venceu em absolutamente todos os indicadores: maior $R^2$ (0,3378), menor RMSE (57,74 pontos) e, crucialmente para a nossa Etapa 2 na AWS, uma latência de inferência 35% menor e um binário final de apenas 1,73 megabyte."*

---

## ⏳ Slide 6 — Estabilidade na Década (`2014–2023`), o Caso `2018` e a Prova *Out-of-Time*
> **Mapeamento no Notebook:** Seção 6 (Blocos 6.2 e 6.3) — Células 11 e 12 | **Figura:** [`media/nb06_figuras/03_estabilidade_anual_holdout.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/03_estabilidade_anual_holdout.png)

### Mensagem Central
> *"O modelo sustenta $R^2$ entre 0,31 e 0,36 ao longo da década, revela sem vazamento o deslocamento psicométrico da TRI de 2018 e generaliza às cegas para o futuro (`2023` Out-of-Time com $\Delta R^2 = -0,0029$)."*

### Layout Visual Recomendado
* **Topo/Esquerda:** Projetar a figura dupla [`03_estabilidade_anual_holdout.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/03_estabilidade_anual_holdout.png) ($R^2$ e RMSE por ano `2014–2023`).
* **Base/Direita — Card de Destaque da "Viagem no Tempo" (*Out-of-Time* Interno):**
  * **Treino Passado (`2014–2022`):** `34.915.365` alunos $\longrightarrow$ **Teste Futuro Cego (`2023` integral):** **`2.678.264` alunos**
  * **Resultado Cego `2023`:** **$R^2 = 0,31842$** | $\text{RMSE} = 67,62\text{ pts}$ | $\text{RMSE}/\sigma = 0,8256$ (praticamente idêntico ao Holdout *in-sample* de `2023`: $R^2 = 0,32135$).

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Consistência Longitudinal:** Em **9 das 10 edições**, o $R^2$ permanece firme na faixa **`0,312` a `0,363`**;
* **Pico Histórico na Pandemia (`2020`):** Maior $R^2$ da série (**`0,3631`**), refletindo sociologicamente o agravamento da desigualdade digital (posse de computador e renda no ensino remoto);
* **Diagnóstico Científico de `2018` ($R^2 = 0,2260$, viés `-23,81 pts`):** Em 2018, a calibração das provas do INEP elevou atipicamente a média real da TRI nacional para **`533,54 pts`** (`+22,5 pts` acima da década). Como `NU_ANO` **não entra em `X`**, o modelo previu `509,73 pts` — **prova irrefutável de zero vazamento temporal**;
* **Garantia para a Etapa 3 (Airflow 2024):** A perda quase nula no teste *Out-of-Time* ($\Delta R^2 = -0,0029$) comprova que a relação socioeconômica aprendida é estacionária no tempo.

### Roteiro de Fala do Apresentador
> *"Este slide traz duas provas fundamentais para a banca. Primeiro, notem o pico de $R^2$ em 2020 (36,3%): durante a pandemia, ter computador e renda pesou ainda mais na nota do ENEM. Segundo, vejam a queda aparente em 2018: naquele ano, a média nacional da TRI subiu atipicamente 22 pontos para 533,5; como bloqueamos `NU_ANO` no treino, o modelo manteve sua régua pura em 510 pontos, provando que não há vazamento temporal! E quando treinamos apenas até 2022 para prever os 2,68 milhões de alunos de 2023 às cegas, o $R^2$ varia menos de 0,3 ponto percentual."*

---

## 🧠 Slide 7 — XAI com TreeSHAP: A Hierarquia do Determinismo Social na TRI
> **Mapeamento no Notebook:** Seção 7 — Células 13 e 14 | **Figuras:** [`04a_shap_importancia_barras.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/04a_shap_importancia_barras.png) e [`04b_shap_beeswarm.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/04b_shap_beeswarm.png)

### Mensagem Central
> *"Traduzimos a caixa-preta de 649 árvores em pontos exatos da escala TRI: a Renda Per Capita lidera isolada (30,1% do impacto), mas o Capital Cultural e Digital somados respondem por 47,3% da nota."*

### Layout Visual Recomendado
* **Lado Esquerdo:** Figura [`04a_shap_importancia_barras.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/04a_shap_importancia_barras.png) ou [`04b_shap_beeswarm.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/04b_shap_beeswarm.png).
* **Lado Direito — Ranking Oficial TreeSHAP (`N = 10.000` do Holdout, $\mathbb{E}[f(X)] = 511,04\text{ pts}$):**

| Pos. | Variável | Dimensão Sociológica | `|SHAP|` Médio | Peso Relativo | Amplitude Total (Min $\rightarrow$ Max) |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1º** | **`RENDA_PER_CAPITA`** | Capital Econômico Familiar | **`18,48 pts`** | **`30,10%`** | **`127,89 pts`** (`-41,9` a `+86,0`) |
| **2º** | **`TP_LINGUA`** | Capital Cultural / Letramento Global | **`10,90 pts`** | **`17,74%`** | `43,04 pts` (`-24,8` a `+18,2`) |
| **3º** | **`Q024`** | Capital Digital (Computador em Casa) | **`9,49 pts`** | **`15,45%`** | `72,97 pts` (`-19,4` a `+53,6`) |
| **4º** | **`TP_ANO_CONCLUIU`** | Frescor Escolar / Trajetória | **`8,96 pts`** | **`14,59%`** | `44,55 pts` (`-15,3` a `+29,3`) |
| **5º** | **`Q002`** | Capital Cultural Herdado (Mãe) | **`8,64 pts`** | **`14,07%`** | `70,46 pts` (`-42,8` a `+27,6`) |
| **6º** | **`TP_SEXO`** | Clivagem Demográfica Estrutural | **`4,95 pts`** | **`8,05%`** | `25,52 pts` (`-13,1` a `+12,5`) |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Exatidão Matemática Auditada:** Propriedade de aditividade de Shapley verificada com erro numérico máximo de **`1,26 × 10⁻³ ponto`** ($\mathbb{E}[f(X)] + \sum \phi_j = \hat{y}$);
* **Amplitude Dramática da Renda:** Apenas transitar entre os extremos de `RENDA_PER_CAPITA` desloca a expectativa de nota em até **`127,89 pontos` na TRI**;
* **Tríade Cultural-Digital (`47,26%`):** A soma de `TP_LINGUA` (`17,7%`) + `Q024` (`15,5%`) + `Q002` (`14,1%`) supera a própria renda isolada, confirmando a tese multidimensional de Pierre Bourdieu.

### Roteiro de Fala do Apresentador
> *"Com o TreeSHAP exato, abrimos completamente o modelo em unidades reais de pontos do ENEM. Partindo da média nacional de 511,04 pontos, a Renda Per Capita move sozinha 18,5 pontos em média — podendo separar dois estudantes em até 128 pontos da TRI! Mas reparem na riqueza sociológica: quando somamos Língua Estrangeira, Posse de Computador e Escolaridade Materna, o capital cultural e digital responde por 47,3% da explicação do modelo."*

---

## 📚 Slide 8 — Bourdieu em Números: Curva Côncava da Renda e Perfis Contrastantes
> **Mapeamento no Notebook:** Seção 7 — Células 13 e 14 | **Figuras:** [`05_shap_interacoes_bourdieu.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/05_shap_interacoes_bourdieu.png) e [`06_shap_perfis_contrastantes.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/06_shap_perfis_contrastantes.png)

### Mensagem Central
> *"A função aprendida pelo XGBoost captura a lei econômica dos retornos marginais decrescentes da renda e quantifica um fosso estrutural superior a 150 pontos entre extremos sociais."*

### Layout Visual Recomendado
* **Painel Superior / Esquerdo:** Figura [`05_shap_interacoes_bourdieu.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/05_shap_interacoes_bourdieu.png) (curva côncava de `RENDA_PER_CAPITA` colorida por `Q024` + progressão monotônica de `Q002`).
* **Painel Inferior / Direito:** Figura [`06_shap_perfis_contrastantes.png`](file:///home/saulo/mba/tcc/enem/media/nb06_figuras/06_shap_perfis_contrastantes.png) (*Waterfalls* lado a lado: Vulnerabilidade P3 vs. Alto Capital P97).

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Não-Linearidade Côncava da Renda:** O impacto positivo explode na saída da vulnerabilidade extrema (`0,0` $\rightarrow$ `2,0 SM/morador`, subindo de `-40 pts` para `+35 pts`) e desacelera gradualmente nas faixas altas — **exatamente o formato que um modelo linear jamais conseguiria ajustar sem distorção**;
* **Escada Cultural Materna (`Q002`):** Progressão monotônica rigorosa desde *"Nunca estudou"* (`0`) até *"Pós-graduação"* (`5`), com queda abrupta na categoria `7` (*"Não sei"*, indicador clássico de fragilidade de vínculo educacional familiar);
* **Anatomia Individual de Dois Brasis (Amostras Reais do Holdout):**
  * **Perfil P3 (Vulnerabilidade):** Base `511,0` $\rightarrow$ penalizações cumulativas de renda, ausência digital e capital familiar $\rightarrow$ **Predição `456,2 pts`** (Nota Real: `466,2 pts`);
  * **Perfil P97 (Alto Capital):** Base `511,0` $\rightarrow$ impulsos de renda, múltiplos computadores, inglês e mãe pós-graduada $\rightarrow$ **Predição `607,2 pts`** (Nota Real: `627,8 pts`).

### Roteiro de Fala do Apresentador
> *"Aqui vemos visualmente por que o XGBoost venceu a regressão linear: a curva da renda é fortemente côncava! Sair de zero para dois salários mínimos per capita transforma radicalmente a nota do estudante, gerando mais de 75 pontos de salto, especialmente quando combinado aos pontos amarelos de posse de computador. Nos gráficos de cascata individuais, vemos dois estudantes reais do Holdout separados por 151 pontos previstos antes mesmo de abrirem o caderno de questões."*

---

## 🚀 Slide 9 — Governança MLflow, Serialização (`enem.pkl`) e Ponte para a AWS
> **Mapeamento no Notebook:** Seção 8 — Células 15 a 17 (Exportação, Model Registry e *Smoke Test* JSON da FastAPI)

### Mensagem Central
> *"A Etapa 1 entrega não apenas uma análise acadêmica, mas um ativo de engenharia registrado no MLflow, criptograficamente assinado (`1,73 MB`) e validado para deploy imediato na AWS."*

### Layout Visual Recomendado
* **Fluxo de Transição Etapa 1 $\longrightarrow$ Etapa 2:**
  `MLflow Model Registry (enem_target_m4_producao v1 - READY)` $\longrightarrow$ `models/enem.pkl (1,73 MB)` + `models/enem_model_card.json` $\longrightarrow$ **`FastAPI (/predict) + Docker + GitHub Actions + AWS App Runner`**.
* **Mini-Tabela do *Smoke Test* de Inferência REST (Célula 16):**
  * *Payload JSON Vulnerável* (`0,25 SM`, `0 PC`, `Espanhol`, `Mãe Fund. I`): **`476,08 pts`**
  * *Payload JSON Alto Capital* (`3,50 SM`, `3+ PCs`, `Inglês`, `Mãe Pós-Grad`): **`612,26 pts`** (`+136,18 pts`)

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Arquitetura Desacoplada de Artefatos:**
  1. [`models/enem.pkl`](file:///home/saulo/mba/tcc/enem/models/enem.pkl) (`1,727 MB`, `SHA-256: 114f5195...`): Objeto estimador `XGBRegressor` puro, compatível com `pickle.load` e `joblib.load` (paridade numérica bit-a-bit `diff = 0.0`);
  2. [`models/enem_xgboost.ubj`](file:///home/saulo/mba/tcc/enem/models/enem_xgboost.ubj) (`1,712 MB`): Binário universal nativo do XGBoost imune a quebras futuras de versão do Python;
  3. [`models/enem_model_card.json`](file:///home/saulo/mba/tcc/enem/models/enem_model_card.json): Contrato de domínios válidos para validação automática via **Pydantic** na FastAPI;
* **Registro Oficial MLOps:** Modelo versionado no **MLflow Registry** como `enem_target_m4_producao` (**Versão 1 — `READY`**).

### Trecho de Código para o Slide
```python
# Célula 16 — Smoke Test de Produção (Contrato Exato da Futura FastAPI)
modelo_prod = pickle.load(open("models/enem.pkl", "rb"))
X_api = pd.DataFrame([payload_json])[ contrato["features_ordenadas"] ]
nota_prevista = float(modelo_prod.predict(X_api)[0])  # Latência < 1 ms
```

### Roteiro de Fala do Apresentador
> *"Concluímos o Notebook 06 com engenharia de produção real: nosso modelo campeão está versionado no MLflow Registry, possui backup binário universal `.ubj`, contrato JSON para validação Pydantic e um arquivo `enem.pkl` de apenas 1,73 MB validado com hash SHA-256. Com isso, encerramos 100% da Etapa 1 e entregamos o motor pronto para ser encapsulado em FastAPI, Docker e AWS App Runner na Etapa 2."*

---

## ❓ Perguntas Prováveis da Banca sobre o Notebook 06 (e Respostas Blindadas)

**1. "Por que o $R^2$ caiu especificamente no ano de 2018 (`0,226`) enquanto ficou estável entre `0,31` e `0,36` nos outros 9 anos?"**
> *Resposta:* "Essa queda pontual do $R^2$ não centrado em 2018 é, na verdade, a maior prova de integridade metodológica do nosso pipeline. Em 2018, a calibração psicométrica das provas objetivas pelo INEP deslocou a média nacional real do `TARGET_M4` para `533,54` pontos — mais de 22 pontos acima da média histórica da década (`511,05`). Como bloqueamos deliberadamente a coluna `NU_ANO` de entrar na matriz `X` para evitar *Temporal Leakage*, o modelo previu `509,73` pontos com base apenas no perfil socioeconômico dos candidatos, gerando um deslocamento constante de intercepto (`-23,81` pontos), mas preservando perfeitamente a ordenação relativa dos estudantes. Se tivéssemos incluído `NU_ANO`, o $R^2$ de 2018 pareceria artificialmente alto, mas o modelo falharia em produção para anos futuros como 2024 e 2025."

**2. "Por que o XGBoost foi treinado em 27 milhões de registros e o Random Forest em 3 milhões? A comparação no Holdout foi justa?"**
> *Resposta:* "Totalmente justa, e desenhada em duas camadas complementares. Primeiro, no Estágio 1 (`5-Fold CV` em `1.000.000` de alunos idênticos), sob igualdade amostral estrita, o XGBoost já superou o Random Forest (`0,3359` vs. `0,3337`) sendo 2,8 vezes mais rápido. Segundo, no Estágio 2, nossa Curva de Aprendizado provou empiricamente que a partir de `1M–3M` de registros o ganho de generalização já atingiu o platô assintótico (`RMSE` variando centésimos de ponto). Como a implementação clássica de *Bagging* do `scikit-learn` aloca vetores `int64` (`np.bincount`) proporcionais a $N$ por thread, enquanto o `XGBRegressor (hist)` quantiza as features em histogramas `uint8` de 1 byte, escalar o XGBoost aos `27,07M` demonstra na prática por que o *Histogram Gradient Boosting* é o padrão-ouro industrial para Big Data em memória limitada."

**3. "Um erro médio absoluto (MAE) de `45,59` pontos (RMSE de `57,74`) não é elevado para prever a nota individual de um candidato?"**
> *Resposta:* "Para substituir a aplicação do exame individual, sim — e felizmente é elevado, pois significa que o esforço pessoal, a resiliência e a trajetória pedagógica individual do aluno ainda respondem por cerca de dois terços da variância (`~66,2%`) que o questionário socioeconômico não enxerga! Porém, do ponto de vista econométrico e de políticas públicas, prever um terço inteiro da variância cognitiva nacional (`33,8%`) em 7,52 milhões de jovens usando apenas 6 perguntas cadastrais pré-prova é uma comprovação contundente da magnitude do determinismo estrutural no Brasil."

**4. "Como garantir que esse modelo treinado até 2023 não sofrerá degradação severa (*Concept Drift*) quando receber dados de 2024 ou 2025 na nuvem?"**
> *Resposta:* "Antecipamos exatamente esse risco de duas formas: primeiro, deflacionamos a renda convertendo-a em múltiplos de Salários Mínimos per capita da época, tornando a principal variável imune à inflação monetária; segundo, executamos na Seção 6 uma Validação *Out-of-Time* Interna treinando apenas de `2014` a `2022` e avaliando às cegas nos `2.678.264` candidatos de `2023`, obtendo $R^2 = 0,3184$ — uma variação de apenas `-0,0029` em relação ao Holdout *in-sample*. Além disso, na Etapa 3, o Apache Airflow monitorará continuamente o drift das safras futuras registrando as métricas no MLflow."

---

## 📋 Resumo Executivo — Fechamento Oficial da Etapa 1

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ SÍNTESE DE HOMOLOGAÇÃO DO NOTEBOOK 06 (FECHAMENTO DA ETAPA 1 DO TCC)                         │
├──────────────────────────────┬───────────────────────────────────────────────────────────────┤
│ Dimensão Auditada            │ Resultado Oficial Homologado                                  │
├──────────────────────────────┼───────────────────────────────────────────────────────────────┤
│ Universo Censitário          │ 37.593.629 alunos (2014–2023) em 537,78 MB RAM (15 B/linha)   │
│ Holdout Cego Estratificado   │ 7.518.726 alunos intocados durante CV, Tuning e Early Stop    │
│ Modelo Campeão Registrado    │ XGBRegressor (hist, depth=5, 649 árvores) -> MLflow v1 READY  │
│ Métricas Finais (Holdout)    │ R² = 0,33780 | RMSE = 57,74 pts | MAE = 45,59 pts             │
│ Salto Não Linear vs. Ridge   │ +5,23 pp em R² (+19,1% de variância explicada relativa)       │
│ Validação Out-of-Time (2023) │ R² = 0,31842 em 2.678.264 alunos cegos (ΔR² = -0,00293)       │
│ Top #1 Preditor (TreeSHAP)   │ RENDA_PER_CAPITA: 18,48 pts médios (30,1% | swing 127,9 pts)  │
│ Artefato Pronto para Etapa 2 │ models/enem.pkl (1,727 MB | Latência 81,15 ms / 10k amostras) │
└──────────────────────────────┴───────────────────────────────────────────────────────────────┘
```

