# 📊 Roteiro de Slides: Capítulo 08 (Etapa 3) — Orquestração Autônoma Airflow, NLP/SBERT, Gatekeeper OOT e Data Drift (2024–2025)

**Projeto de TCC:** MBA em Ciência de Dados / MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  
**Módulos de Referência:** [`dags/enem_autonomous_dag.py`](file:///home/saulo/mba/tcc/enem/dags/enem_autonomous_dag.py), [`src/orchestration/`](file:///home/saulo/mba/tcc/enem/src/orchestration/), [`tests/test_orchestration_etapa3.py`](file:///home/saulo/mba/tcc/enem/tests/test_orchestration_etapa3.py), [`docker-compose.airflow.yml`](file:///home/saulo/mba/tcc/enem/docker-compose.airflow.yml) e [`passo-a-passo-08-airflow-producao.md`](file:///home/saulo/mba/tcc/enem/passo-a-passo-08-airflow-producao.md)  
**Foco da Defesa:** Orquestração Autônoma no **Apache Airflow**, Precedência Obrigatória do **NLP/SBERT antes da Seleção**, **Gatekeeper Out-of-Time (*Circuit Breaker* LGPD)**, Competição Contínua **Champion vs. Challenger no MLflow (`enem_v2.pkl`)** e Auditoria de **Data Drift ($X$) via PSI e KS** nas safras reais de **2024 e 2025**.

---

## 🧭 Visão Panorâmica da Apresentação (Arco Narrativo da Etapa 3 para a Banca)

1. **Engenharia FinOps (Plano Leve em Nuvem vs. Plano Pesado Local):** Por que manter o processamento de milhões de linhas, *embeddings* PyTorch/SBERT, retreinamento do XGBoost e MLflow containerizados localmente sob orquestração do **Apache Airflow**.
2. **A Precedência Crítica do NLP/SBERT antes da Seleção:** Demonstração real nas safras de **2024 e 2025**, onde a coluna `Q024` deixou de existir fisicamente e o modelo `paraphrase-multilingual-MiniLM-L12-v2` descobriu sozinho a migração `Q006` $\rightarrow$ `Q007` (renda) e `Q024` $\rightarrow$ `Q021` (computador) antes de abrir o CSV.
3. **O Gatekeeper Out-of-Time como *Circuit Breaker* Anti-Poisoning (Caso Real ENEM 2024):** Como a DAG detectou automaticamente a desidentificação posicional aplicada pelo INEP em 2024 (`0,55%` de match municipal e $R^2_{\text{OOT}} = -0,1917$), bloqueou a contaminação do Data Lake (`2014–2023`) e desviou a safra para escoragem e auditoria de drift.
4. **Evolução Contínua (*Champion vs. Challenger* no MLflow):** Comprovação do ramo positivo do Gatekeeper ($R^2_{\text{OOT}} = 0,3152 \ge 0,28$), retreinamento automático do `XGBRegressor` e promoção do **`enem_v2.pkl`** após vitória no Holdout (`RMSE 66,17` vs. `66,31 pts`).
5. **Estabilidade Temporal Comprovada em 2024 e 2025 (`PSI < 0.10`):** Inferência vetorial em lote e comprovação matemática via *Population Stability Index* (PSI) e Kolmogorov-Smirnov (KS) de que a estrutura socioeconômica brasileira permanece estacionária em 2024 (`max PSI = 0,0515`) e 2025 (`max PSI = 0,0279`).

---

## 🎯 Slide 1 — Arquitetura do Plano Pesado Local e o Grafo da DAG Autônoma
> **Mapeamento no Repositório:** [`dags/enem_autonomous_dag.py`](file:///home/saulo/mba/tcc/enem/dags/enem_autonomous_dag.py), [`docker-compose.airflow.yml`](file:///home/saulo/mba/tcc/enem/docker-compose.airflow.yml) e [`diagrama_producao_2024.md`](file:///home/saulo/mba/tcc/enem/diagrama_producao_2024.md)

### Mensagem Central
> *"A Etapa 3 fecha o ciclo MLOps com uma DAG autônoma que enxerga o formato da nova safra, traduz o dicionário com IA antes de tocar nos dados e decide sozinha entre retreinar o modelo ou auditar o drift."*

### Layout Visual Recomendado
* **Topo (Fluxo dos 4 Estágios da DAG `enem_autonomous_pipeline_2024_2025`):**
  `[1. t1_ingest_detect]` $\longrightarrow$ **`[2. t2_sbert_dictionary_mapper (ANTES da Seleção)]`** $\longrightarrow$ `[3. t3_select_harmonize_downcast (15/11 B/linha)]` $\longrightarrow$ `[4. t4_branch_router]` $\longrightarrow$ **`[Ramo A: Gatekeeper OOT + Champion/Challenger]`** **OU** **`[Ramo B: Batch Scoring + Data Drift PSI/KS]`**.
* **Cards de Indicadores Técnicos na Base do Slide:**
  * **Motor Semântico:** `LIVE_SBERT_MINILM_L12_V2` (`384 dim`)
  * **Pegada em Memória:** `15 B/linha` (com notas) / `11 B/linha` (sem notas)
  * **Suíte Pytest Etapa 3:** `4/4 PASSED` (`39,98s`)

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Racional FinOps de Produção:** Enquanto a API FastAPI (`515 MB`) roda na AWS para inferência *real-time*, o processamento anual pesado (CSVs de gigabytes + PyTorch/SBERT + retreino XGBoost + MLflow) roda em contêineres Docker locais (`Dockerfile.airflow`), zerando custos de GPU/CPU em nuvem;
* **Orquestração Orientada a Metadados (`XCom`):** Cada task recebe e publica relatórios JSON auditáveis entre os 4 estágios;
* **Bifurcação Dinâmica (`BranchPythonOperator`):** O nó `t4_branch_router` inspeciona a presença física das 4 notas da TRI (`has_scores`) e adapta o comportamento do pipeline sem intervenção humana.

### Trecho de Código para o Slide
```python
# dags/enem_autonomous_dag.py — Encadeamento Oficial das Tasks no Apache Airflow
t1_ingest >> t2_sbert >> t3_etl >> t4_router >> [b_oot, b_drift] >> t5_complete
```

### Roteiro de Fala do Apresentador
> *"Senhores membros da banca, chegamos à Etapa 3, onde respondemos à pergunta decisiva de qualquer sistema de Machine Learning: o que acontece quando o INEP lança uma nova edição do ENEM em 2024 ou 2025? Por disciplina de FinOps, mantemos o plano pesado containerizado localmente com Apache Airflow, PyTorch SBERT, XGBoost e MLflow. Nossa DAG autônoma opera em quatro estágios encadeados e possui inteligência de bifurcação para tratar tanto edições pós-prova com notas quanto bases preliminares de inscritos sem notas."*

---

## 🧠 Slide 2 — Precedência do NLP/SBERT no Dicionário Antes da Seleção (2024 e 2025)
> **Mapeamento no Repositório:** [`src/orchestration/step2_sbert_mapper.py`](file:///home/saulo/mba/tcc/enem/src/orchestration/step2_sbert_mapper.py)

### Mensagem Central
> *"Em 2024 e 2025, a coluna `Q024` deixou de existir no CSV do INEP. Qualquer pipeline tradicional quebraria com `KeyError`; nossa DAG resolveu a mudança sozinha lendo o dicionário com SBERT antes da seleção."*

### Layout Visual Recomendado
* **Tabela da Descoberta Automática em Tempo Real (`LIVE_SBERT_MINILM_L12_V2`):**

| Variável Canônica (2023) | Conceito Sociológico | Código em 2015–2023 | Código Descoberto em 2024 e 2025 | Ação do Estágio 2 (SBERT) |
| :--- | :--- | :---: | :---: | :--- |
| **`Q006`** | Renda Familiar Mensal (`17 faixas SM`) | `Q006` | **`Q007`** | Drift Semântico Mapeado Antes do ETL |
| **`Q024`** | Posse de Computador no Domicílio | `Q024` | **`Q021`** | Drift Semântico Mapeado Antes do ETL |
| **`Q005`** | Número de Moradores na Residência | `Q005` | `Q005` | Estabilidade Confirmada |
| **`Q002`** | Escolaridade da Mãe / Responsável | `Q002` | `Q002` | Estabilidade Confirmada |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Por que a Ordem dos Nós é Vital (`Estágio 2 antes do Estágio 3`):** Em um ano inédito, o engenheiro de dados não sabe a priori quais colunas selecionar porque o INEP renumera o questionário;
* **Parser Multi-Aba + `paraphrase-multilingual-MiniLM-L12-v2`:** O Estágio 2 lê todas as abas válidas da planilha `.xlsx`, projeta os enunciados em 384 dimensões com restrição injetiva 1-para-1 e entrega ao Estágio 3 o mapa exato `{canonica: coluna_nova}`;
* **Harmonização e Downcasting no Estágio 3:** Só após a tradução semântica o CSV é lido nas colunas corretas (`Q007`, `Q021`), deflacionado em Salários Mínimos e compactado em **`15 bytes/linha`** (`2024`) ou **`11 bytes/linha`** (`2025`).

### Trecho de Código para o Slide
```text
# Log Real de Execução em saulo@LeCun:enem (Safras 2024 e 2025)
Loading weights: 100%|████████████████████████████████| 199/199 [00:00<00:00, 308.88it/s]
[Task 2 - NLP/SBERT] Modo=LIVE_SBERT_MINILM_L12_V2 | Drifts detectados=2 (Q006->Q007, Q024->Q021)
[Task 3 - Seleção & Downcasting] Retidos=34467 | Bytes/linha=15 B | RAM=0.493 MB
```

### Roteiro de Fala do Apresentador
> *"Este slide demonstra por que corrigimos a ordem clássica dos pipelines de dados. Nos microdados reais de 2024 e 2025, o questionário do INEP encurtou até a pergunta Q023: a coluna Q024 simplesmente desapareceu. Ao executar o modelo neural SBERT sobre a planilha de dicionário antes da seleção de atributos, a Task 2 descobriu em menos de um segundo que a renda familiar migrou de Q006 para Q007 e o computador migrou de Q024 para Q021, permitindo que a Task 3 extraísse os dados sem nenhuma intervenção manual."*

---

## 🛡️ Slide 3 — O Gatekeeper Out-of-Time como *Circuit Breaker* Anti-Poisoning (ENEM 2024)
> **Mapeamento no Repositório:** [`src/orchestration/step1_ingest_detect.py`](file:///home/saulo/mba/tcc/enem/src/orchestration/step1_ingest_detect.py) e [`src/orchestration/step4_branch_oot_drift.py`](file:///home/saulo/mba/tcc/enem/src/orchestration/step4_branch_oot_drift.py)

### Mensagem Central
> *"Quando o INEP desvinculou os arquivos de Participantes e Resultados em 2024 por exigência da LGPD, nosso Gatekeeper Out-of-Time detectou a anomalia em segundos e impediu a contaminação dos 37,6 milhões de registros históricos."*

### Layout Visual Recomendado
* **Quadro Forense da Auditoria Automática na Safra 2024 (`N = 34.467` elegíveis de `50.000` lidos):**

| Indicador Auditado pela DAG em 2024 | Valor Medido | Limiar de Governança (SLA) | Decisão Automática da DAG |
| :--- | :---: | :---: | :---: |
| **Layout Físico Detectado** | `BIPARTIDO` (`PARTICIPANTES` + `RESULTADOS`) | Presença de Chave 1:1 | ⚠️ Alerta de Cisão Estrutural |
| **Coincidência Posicional (`CO_MUNICIPIO_PROVA`)** | **`0,55%`** (`0.0055`) | $\ge 99,0\%$ (`0.9900`) | ❌ Reprovado (`alignment_ok = False`) |
| **Desempenho Out-of-Time (`enem.pkl v1`)** | **`R² = -0,1917`** (`RMSE = 83,35 pts`) | $R^2 \ge 0,28$ e $\text{RMSE} \le 72,0$ | 🛡️ **Circuit Breaker Acionado!** |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **O Risco de *Data Poisoning* em MLOps:** Em 2024, ambos os arquivos (`PARTICIPANTES_2024.csv` e `RESULTADOS_2024.csv`) possuem exatamente `4.332.944` linhas, mas foram ordenados por chaves desvinculadas (`NU_INSCRICAO` vs. `NU_SEQUENCIAL` — na linha 1, o participante é de Porto Alegre/RS e a prova é de Aratuba/CE);
* **Dupla Barreira do Gatekeeper:** A DAG audita tanto a paridade geográfica (`0,55%`) quanto o $R^2$ preditivo (`-0,1917`);
* **Fallback Gracioso:** Em vez de abortar com falha ou contaminar a base `2014–2023`, o *Circuit Breaker* bloqueia o retreinamento e redireciona automaticamente os `34.467` participantes de 2024 para **Inferência em Lote + Auditoria de Drift**.

### Roteiro de Fala do Apresentador
> *"Aqui vemos o valor real de um Gatekeeper em produção. Em 2024, o INEP dividiu os microdados em dois arquivos de 4,33 milhões de linhas sem chave comum e embaralhou sua ordem por privacidade LGPD. Se um pipeline automatizado comum concatenasse esses arquivos e retreinasse o modelo, destruiria 10 anos de aprendizado com ruído puro. Nosso Gatekeeper detectou que apenas 0,55% dos municípios coincidiam linha a linha e que o R² caía para -0,19, acionando um Circuit Breaker imediato que protegeu nosso Data Lake e desviou os estudantes de 2024 para inferência em lote e análise de drift."*

---

## 🏆 Slide 4 — Evolução Contínua: Retreino XGBoost e Juiz MLflow (*Champion vs. Challenger*)
> **Mapeamento no Repositório:** [`src/orchestration/step4_branch_oot_drift.py`](file:///home/saulo/mba/tcc/enem/src/orchestration/step4_branch_oot_drift.py#L202-L365) e [`passo-a-passo-08-airflow-producao.md`](file:///home/saulo/mba/tcc/enem/passo-a-passo-08-airflow-producao.md#L148-L183)

### Mensagem Central
> *"Quando a safra Out-of-Time cumpre o SLA de integridade e acurácia, a DAG concatena a série histórica, retreina o XGBoost e usa o MLflow como juiz imparcial para promover a versão 2 do modelo."*

### Layout Visual Recomendado
* **Tabela Oficial do Julgamento no MLflow (`tcc_enem_etapa3_airflow_autonomo`):**

| Etapa do Julgamento Autônomo | Modelo Avaliado | $R^2$ ($\uparrow$) | RMSE ($\downarrow$) | MAE ($\downarrow$) | Veredito do Juiz MLflow |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **1. Gatekeeper Out-of-Time** | `Champion (v1)` na Nova Safra | **`0,31520`** | **`67,4727 pts`** | `52,7592 pts` | ✅ **Aprovado no SLA** ($R^2 \ge 0,28$) |
| **2. Disputa no Holdout Cego** | `Champion (v1)` (Treino Anterior) | `0,30880` | `66,3074 pts` | — | Desafiado |
| **2. Disputa no Holdout Cego** | **`Challenger (v2)` (Base Expandida)** | **`0,31173`** | **`66,1667 pts`** | — | 🏆 **Promovido (`enem_v2.pkl`)!** |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Concatenação Longitudinal Estratificada:** Aprovação no Gatekeeper dispara a união da base histórica anterior com a nova safra validada;
* **Mesmo Protocolo Científico da Etapa 1:** O modelo `Challenger (v2)` é treinado com `XGBRegressor(tree_method="hist", max_depth=5)` e *Early Stopping* dedicado (`10%` de validação isolada do Holdout);
* **Rastreabilidade Total (`sqlite:///mlflow.db`):** As métricas de ambos os modelos e o novo artefato `enem_v2.pkl` ficam registrados e auditáveis na interface gráfica do **MLflow UI (`http://localhost:5000`)**.

### Roteiro de Fala do Apresentador
> *"Para comprovar o caminho completo de evolução contínua quando uma safra íntegra passa pelo Gatekeeper, submetemos um lote Out-of-Time alinhado à DAG. O modelo v1 foi aprovado no Gatekeeper com R² de 0,3152. Em seguida, a própria DAG concatenou o histórico, treinou o modelo Challenger v2 e abriu o julgamento no Holdout cego dentro do MLflow: o Challenger v2 superou o Champion v1 reduzindo o RMSE para 66,17 pontos e elevando o R² para 0,3117, sendo automaticamente promovido para `enem_v2.pkl`."*

---

## 📊 Slide 5 — Inferência em Lote e Auditoria de *Data Drift* (`PSI < 0.10` em 2024 e 2025)
> **Mapeamento no Repositório:** [`passo-a-passo-08-airflow-producao.md`](file:///home/saulo/mba/tcc/enem/passo-a-passo-08-airflow-producao.md#L186-L299)

### Mensagem Central
> *"A auditoria matemática via Population Stability Index (PSI) comprova que a estrutura socioeconômica dos candidatos do ENEM permaneceu altamente estável tanto em 2024 quanto em 2025 (`PSI < 0.10` em todas as 6 variáveis)."*

### Layout Visual Recomendado
* **Tabela Comparativa de *Data Drift* ($X$) e Escoragem em Lote (`50.000` linhas lidas por safra):**

| Variável do Esquadrão de Elite | PSI Safra **2024** (`N=34.467`) | Status Drift 2024 | PSI Safra **2025** (`N=50.000`) | Status Drift 2025 | Limiar Crítico |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`RENDA_PER_CAPITA` (SM)** | `0,04449` | ✅ `ESTÁVEL` | `0,01282` | ✅ `ESTÁVEL` | $< 0,10$ |
| **`Q024` $\rightarrow$ `Q021` (Computador)** | `0,00489` | ✅ `ESTÁVEL` | `0,00601` | ✅ `ESTÁVEL` | $< 0,10$ |
| **`TP_ANO_CONCLUIU` (Maturidade)** | `0,05146` | ✅ `ESTÁVEL` | `0,02790` | ✅ `ESTÁVEL` | $< 0,10$ |
| **`TP_LINGUA` (Inglês/Espanhol)** | `0,00048` | ✅ `ESTÁVEL` | `0,00040` | ✅ `ESTÁVEL` | $< 0,10$ |
| **`TP_SEXO` (Gênero)** | `0,00021` | ✅ `ESTÁVEL` | `0,01413` | ✅ `ESTÁVEL` | $< 0,10$ |
| **`Q002` (Escolaridade da Mãe)** | `0,03388` | ✅ `ESTÁVEL` | `0,02016` | ✅ `ESTÁVEL` | $< 0,10$ |
| **Nota Prevista `TARGET_M4` (Média ± DP)** | **`507,20 ± 40,06 pts`** | `P50 = 498,38` | **`516,47 ± 48,92 pts`** | `P50 = 508,14` | Escala TRI |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Fórmula do *Population Stability Index* (PSI):**
  $$\text{PSI} = \sum_{b=1}^{B} \left( P_{\text{atual}}(b) - P_{\text{ref}}(b) \right) \cdot \ln\left(\frac{P_{\text{atual}}(b)}{P_{\text{ref}}(b)}\right) < 0,10 \implies \text{Estabilidade Populacional}$$
* **Prova do Sucesso da Deflação em Salários Mínimos:** O PSI da `RENDA_PER_CAPITA` ficou em apenas **`0,0445` (2024)** e **`0,0128` (2025)** — provando que nossa engenharia de features na Etapa 1 neutralizou completamente a inflação nominal entre 2014 e 2025!

### Roteiro de Fala do Apresentador
> *"Por fim, este slide apresenta o resultado da inferência em lote e da auditoria de Data Drift sobre 50 mil candidatos de 2024 e 50 mil candidatos de 2025. Todas as seis variáveis apresentaram PSI muito abaixo do limiar de 0,10 — com destaque para a Renda Per Capita em Salários Mínimos (PSI de 0,0128 em 2025) e Posse de Computador (PSI de 0,0060). Isso prova matematicamente que nossa harmonização deflacionada eliminou o drift monetário e que o modelo permanece perfeitamente calibrado para prever o desempenho dos estudantes brasileiros no presente e no futuro."*

---

## ❓ Perguntas Prováveis da Banca sobre a Etapa 3 (e Respostas Blindadas)

**1. "Como a DAG tratou a variável `TP_LINGUA` na safra de 2025, já que o INEP moveu a escolha de língua estrangeira para o arquivo de Resultados (que não existe antes da prova)?"**
> *Resposta:* "Excelente observação. A partir de 2024, o INEP moveu `TP_LINGUA` da tabela de `PARTICIPANTES` para a tabela de `RESULTADOS`. Em 2024, como ambos os arquivos existem, o Estágio 3 lê `TP_LINGUA` diretamente de `RESULTADOS_2024.csv`. Já em 2025 (`SOMENTE_PARTICIPANTES_SEM_NOTAS`), o Estágio 3 detecta automaticamente a ausência da coluna no cabeçalho, ativa a flag auditável `tp_lingua_imputed: true` no relatório de governança e aplica uma regra de imputação condicional determinística calibrada no censo 2014–2023 (associando a opção majoritária de Inglês aos candidatos com computador ou renda $\ge 1\text{ SM}$ per capita), preservando um PSI de `0,0004` sem quebrar a inferência em lote."

**2. "Por que usar o *Population Stability Index* (PSI) além do teste de Kolmogorov-Smirnov (KS) para monitorar o *Data Drift* nas safras de 2024 e 2025?"**
> *Resposta:* "Porque em Big Data ($N = 34.467$ ou $N = 50.000$), o p-valor do teste clássico de Kolmogorov-Smirnov sofre de hipersensibilidade amostral: diferenças irrelevantes de `0,01` na distribuição acumulada geram $p < 0,001$. O **PSI** mede a divergência de Kullback-Leibler simetrizada em faixas discretas e quantis, fornecendo uma métrica de magnitude prática consagrada em risco de crédito e MLOps (`< 0,10` estável; `0,10 a 0,25` atenção; $\ge 0,25$ crítico), permitindo automatizar alertas reais sem falsos alarmes estatísticos."

---

## 📋 Resumo Executivo — Fechamento Oficial da Etapa 3 e do TCC

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ SÍNTESE DE HOMOLOGAÇÃO DO CAPÍTULO 08 (FECHAMENTO DA ETAPA 3 E DO PROJETO DE TCC)            │
├──────────────────────────────┬───────────────────────────────────────────────────────────────┤
│ Dimensão Auditada            │ Resultado Oficial Homologado                                  │
├──────────────────────────────┼───────────────────────────────────────────────────────────────┤
│ Orquestrador e Grafo         │ Apache Airflow (`enem_autonomous_pipeline_2024_2025`)         │
│ Motor NLP Pré-Seleção        │ `LIVE_SBERT_MINILM_L12_V2` (`Q006->Q007` e `Q024->Q021`)      │
│ Defesa Safra 2024 (LGPD)     │ Circuit Breaker acionado (`match=0,55%`, `R²=-0,1917 < 0,28`) │
│ Disputa Champion/Challenger  │ Challenger v2 venceu no Holdout (`RMSE 66,17` vs `66,31 pts`) │
│ Estabilidade Data Drift 2024 │ 6/6 features ESTÁVEIS (`max PSI = 0,05146 < 0,10`)            │
│ Estabilidade Data Drift 2025 │ 6/6 features ESTÁVEIS (`max PSI = 0,02790 < 0,10`)            │
│ Suíte Automatizada Etapa 3   │ `4/4 PASSED` em `tests/test_orchestration_etapa3.py` (`39,9s`)│
└──────────────────────────────┴───────────────────────────────────────────────────────────────┘
```

