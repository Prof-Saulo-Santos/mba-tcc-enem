# Diagramas Mermaid — TCC ENEM MLOps
**Data:** 19/09/2026 | Estilo visual adaptado do padrão do TCC

---

## Diagrama 1 — Arquitetura Geral do Pipeline MLOps

```mermaid
flowchart LR
    classDef base fill:#f0f4c3,stroke:#827717,stroke-width:2px,color:#33691e;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef govern fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef gold fill:#fff8e1,stroke:#f9a825,stroke-width:2px,color:#795548;

    L1["🗄️ Infraestrutura<br/>WSL + .venv + Docker"]:::base

    subgraph L_Core ["Fluxo de Dados — ETL Defensivo"]
        direction LR
        L2["📥 Ingestão<br/>reader.py + harmonizer.py"]:::core
        L3["🛡️ Soft Validation<br/>Pandera"]:::core
        L4["🧹 Limpeza<br/>cleaner.py"]:::core
        L5["⚙️ Feature Eng.<br/>features.py"]:::core
        L6["✅ Hard Validation<br/>Pandera"]:::core
        L7["💾 Data Lake<br/>.parquet — Camada Gold"]:::gold
        L2 ==> L3 ==> L4 ==> L5 ==> L6 ==> L7
    end

    L8["🔬 Laboratório ML<br/>EDA + Modelagem"]:::govern
    L9["🏆 Produção<br/>train.py + MLflow"]:::govern

    L1 -. "Sustenta" .-> L_Core
    L7 -. "Alimenta" .-> L8
    L8 -. "Promove" .-> L9
```

---

## Diagrama 2 — Arquitetura Medalhão (Bronze / Silver / Gold)

```mermaid
flowchart LR
    classDef base fill:#f0f4c3,stroke:#827717,stroke-width:2px,color:#33691e;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef govern fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef gold fill:#fff8e1,stroke:#f9a825,stroke-width:2px,color:#795548;

    subgraph B ["🥉 Bronze"]
        direction LR
        B1["2017 a 2023<br/>MICRODADOS_ENEM_XXXX.csv<br/>Formato Monolítico"]:::base
        B2["2024 e 2025<br/>PARTICIPANTES_XXXX.csv<br/>+ RESULTADOS_XXXX.csv<br/>Formato Particionado"]:::base
    end

    subgraph S ["🥈 Silver"]
        direction LR

        ORCH["⚙️ Orquestrador<br/>(Airflow DAG / CI-CD)<br/>Gatilho automático por ano"]:::govern

        subgraph PROD ["Execução de Scripts Python"]
            direction TB
            P1["reader.py + harmonizer.py<br/>Camada Anticorrupção"]:::core
            P2["validator.py<br/>Pandera Soft + Hard"]:::core
            P3["cleaner.py + features.py<br/>Limpeza e Features"]:::core
            P1 --> P2 --> P3
        end

        ORCH --> PROD
    end

    subgraph G ["🥇 Gold — Pronto para ML"]
        direction LR
        G1["✅ enem_2023_silver.parquet<br/>2.585.115 candidatos · 78 colunas<br/>Concluído"]:::gold
        G2["⏳ 2017–2022 e 2024–2025<br/>8 anos restantes<br/>Pendente"]:::base
    end

    B --> S --> G
```

---

## Diagrama 3 — Camada Anticorrupção: reader.py + harmonizer.py

```mermaid
flowchart LR
    classDef base fill:#f0f4c3,stroke:#827717,stroke-width:2px,color:#33691e;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef govern fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;

    START(["📂 Solicitar<br/>Ano X"]):::govern

    DEC{"Ano X<br/>≤ 2023?"}:::govern

    PATH_A["Lê arquivo único<br/>MICRODADOS_ENEM_X.csv"]:::core
    PATH_B["Lê PARTICIPANTES_X.csv<br/>+ RESULTADOS_X.csv"]:::core
    CHECK{"linhas P<br/>== linhas R?"}:::govern
    JOIN["pd.concat axis=1<br/>Unificação posicional"]:::core
    ERR["❌ ValueError<br/>Pipeline interrompido"]:::govern
    HARMONIZE["harmonizer.py<br/>Remove Q026, Q027<br/>Remove TP_VERSAO_DIGITAL"]:::core
    RESULT(["✅ DataFrame Unificado<br/>Schema idêntico — todos os anos"]):::core

    START --> DEC
    DEC -- "Sim" --> PATH_A
    DEC -- "Não 2024+" --> PATH_B
    PATH_B --> CHECK
    CHECK -- "OK" --> JOIN
    CHECK -- "Divergência!" --> ERR
    PATH_A --> HARMONIZE
    JOIN --> HARMONIZE
    HARMONIZE --> RESULT
```

---

## Diagrama 4 — Pipeline Chunked: Processando 4 Milhões de Linhas

```mermaid
flowchart LR
    classDef base fill:#f0f4c3,stroke:#827717,stroke-width:2px,color:#33691e;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef govern fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef gold fill:#fff8e1,stroke:#f9a825,stroke-width:2px,color:#795548;

    CSV["📄 CSV Bruto<br/>~4 milhões de linhas"]:::base

    subgraph CHUNK ["Loop de Chunks — 300k linhas por vez"]
        direction LR
        C1["📦 Lê 300k linhas<br/>dtype=str"]:::core
        C2["🔧 Harmonização T1<br/>Remove obsoletas<br/>Cast numérico"]:::core
        C3["🧹 Limpeza T2<br/>Filtra ausentes<br/>Remove nulos"]:::core
        C4["⚙️ Feature Eng.<br/>NU_NOTA_MEDIA<br/>FAIXA_DESEMPENHO"]:::core
        LOOP{"Mais<br/>chunks?"}:::govern
        C1 --> C2 --> C3 --> C4 --> LOOP
        LOOP -- "Sim" --> C1
    end

    CONCAT["🔗 pd.concat<br/>Consolida chunks"]:::core
    SAVE["💾 .parquet<br/>2.585.115 linhas<br/>78 colunas"]:::gold
    LOG["📊 Remoção: 34,3%<br/>1.348.840 ausentes"]:::govern

    CSV --> CHUNK
    LOOP -- "Não" --> CONCAT
    CONCAT --> SAVE
    SAVE --> LOG
```

---

## Diagrama 5 — Arena de Algoritmos: Regressão e Classificação

```mermaid
flowchart LR
    classDef base fill:#f0f4c3,stroke:#827717,stroke-width:2px,color:#33691e;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef govern fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef gold fill:#fff8e1,stroke:#f9a825,stroke-width:2px,color:#795548;

    PARQUET["💾 Gold .parquet<br/>2.585.115 candidatos"]:::gold

    subgraph FT ["Features — X"]
        direction LR
        F1["TP_SEXO"]:::base
        F2["TP_ESCOLA"]:::base
        F3["Q001 — Escol. Pai"]:::base
        F4["Q002 — Escol. Mãe"]:::base
        F5["Q006 — Renda"]:::base
    end

    SPLIT["✂️ 80% Treino<br/>20% Teste<br/>OrdinalEncoder"]:::core

    subgraph REG ["Regressão:NU_NOTA_MT"]
        direction TB
        R1["🐢 Dummy<br/>RMSE=130 R²=0.00"]:::base
        R2["📐 Linear<br/>RMSE=114 R²=0.23"]:::core
        R3["🌲 Random Forest<br/>RMSE=112 R²=0.26"]:::core
        R4["⚡ HistGB — VENCEDOR<br/>RMSE=111 R²=0.26"]:::govern
    end

    subgraph CLS ["Clas.: FAIXA_DESEMPENHO"]
        direction TB
        CL1["🐢 Dummy"]:::base
        CL2["🌲 Random Forest"]:::core
        CL3["⚡ HistGB — Classificador"]:::govern
        CL4["📋 Acurácia<br/>Precisão | Recall | F1"]:::gold
        CL3 --> CL4
    end

    PARQUET --> FT --> SPLIT
    SPLIT --> REG
    SPLIT --> CLS
```

---

## Diagrama 6 — Roadmap do Projeto

```mermaid
flowchart TB
    classDef base fill:#f0f4c3,stroke:#827717,stroke-width:2px,color:#33691e;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef govern fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef gold fill:#fff8e1,stroke:#f9a825,stroke-width:2px,color:#795548;

    subgraph DONE ["✅ Concluído"]
        direction LR
        D1["Pipeline ETL<br/>Bronze → Gold<br/>2023 completo"]:::core
        D2["EDA + Gráficos<br/>Renda · Escola · Notas"]:::core
        D3["Arena de Algoritmos<br/>Regressão + Classificação"]:::core
    end

    subgraph SHORT ["📅 Curto Prazo"]
        direction LR
        S1["Processar 8 anos<br/>2017–2022<br/>2024–2025"]:::base
        S2["Feature Importance<br/>Quais features mais importam?"]:::base
        S3["Script train.py<br/>Fora do Notebook"]:::base
    end

    subgraph MLOPS ["🐳 MLOps — Docker"]
        direction LR
        M1["MLflow Server<br/>Rastrear experimentos"]:::govern
        M2["Model Registry<br/>Versionar o vencedor"]:::govern
        M3["FastAPI<br/>API de predição"]:::govern
    end

    subgraph CICD ["⚙️ CI/CD — GitHub Actions"]
        direction LR
        CI1["Job 1 — pytest<br/>Testes unitários automáticos"]:::govern
        CI2["Job 2 — Pandera<br/>Validação de contratos"]:::govern
        CI3["Job 3 — train.py<br/>Retreino + registro MLflow"]:::govern
        CI4["Job 4 — Docker<br/>Deploy automático da API"]:::govern
        CI1 --> CI2 --> CI3 --> CI4
    end

    subgraph FUTURE ["🚀 Pós-TCC"]
        direction LR
        F1["ELT + dbt<br/>+ BigQuery"]:::gold
        F2["9 anos históricos<br/>Tendências temporais"]:::gold
    end

    DONE ==> SHORT ==> MLOPS ==> CICD ==> FUTURE
```

---

## Diagrama 7 — Visão Macro: O Pipeline ETL vs Arquitetura Medalhão

Este diagrama ilustra como os scripts Python (o motor) executam os verbos do **ETL** para movimentar e transformar os dados através dos estados da **Arquitetura Medalhão**.

```mermaid
flowchart LR
    classDef base fill:#f0f4c3,stroke:#827717,stroke-width:2px,color:#33691e;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef govern fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef gold fill:#fff8e1,stroke:#f9a825,stroke-width:2px,color:#795548;

    subgraph EXTRACT ["📤 EXTRACT"]
        direction TB
        E1["🥉 Camada Bronze<br/>(CSVs imutáveis do INEP)"]:::base
        E2["reader.py<br/>Extrai os dados da origem"]:::govern
        E1 --> E2
    end

    subgraph TRANSFORM ["⚙️ TRANSFORM"]
        direction TB
        T1["harmonizer.py<br/>(Camada Anticorrupção)"]:::core
        T2["validator.py<br/>(Contratos de Dados Pandera)"]:::core
        T3["cleaner.py + features.py<br/>(Limpeza e Novas Variáveis)"]:::core
        
        T1 --> T2 --> T3
    end

    subgraph LOAD ["💾 LOAD"]
        direction TB
        L1["pipeline_chunked.py<br/>Consolida e escreve"]:::govern
        L2["🥇 Camada Gold<br/>Salva em .parquet para ML"]:::gold
        L1 --> L2
    end

    EXTRACT ==>|Alimenta| TRANSFORM
    TRANSFORM ==>|Carrega| LOAD
```

---

## Diagrama 8 — Visão de Orquestração: O Ciclo de Vida com Apache Airflow

Este diagrama mapeia o fluxo completo de "causa e efeito": desde o momento em que um arquivo cai na Camada Bronze até o acionamento do Airflow, que por sua vez dispara a esteira de processamento em chunks do nosso código Python.

```mermaid
flowchart LR
    classDef base fill:#f0f4c3,stroke:#827717,stroke-width:2px,color:#33691e;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef govern fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef gold fill:#fff8e1,stroke:#f9a825,stroke-width:2px,color:#795548;
    classDef airflow fill:#e1bee7,stroke:#8e24aa,stroke-width:2px,color:#4a148c;

    BRONZE["📥 1. Evento Exterrno<br/>INEP faz upload do CSV na pasta Bronze"]:::base

    subgraph AF ["Gerente: Apache Airflow (Orquestrador)"]
        direction LR
        SENS["🔍 FileSensor<br/>Fica em loop 'escutando' a pasta Bronze"]:::airflow
        BASH["💻 BashOperator<br/>Comando: python pipeline_chunked.py"]:::airflow
        SENS -->|Detecta arquivo novo| BASH
    end

    subgraph CHUNK ["pipeline_chunked.py"]
        direction LR
        START["⏱️ Inicia Leitura em Chunks<br/>pd.read_csv(chunksize=300k)"]:::govern
        
        subgraph MODULOS ["Repete a cada Chunk"]
            direction TB
            M1["1. reader.py (Localiza o arquivo)"]:::core
            M2["2. harmonizer.py (Drop de colunas)"]:::core
            M3["3. validator.py (Contrato Pandera)"]:::core
            M4["4. cleaner.py (Filtra Faltantes)"]:::core
            M5["5. features.py (Calcula Média)"]:::core
            
            M1 --> M2 --> M3 --> M4 --> M5
        end
        
        END["🧵 Consolidação Final<br/>pd.concat() une todas as fatias limpas"]:::govern
        
        START --> MODULOS
        MODULOS --> END
    end
    
    GOLD["💾 2. Evento Final<br/>Salva enem_silver.parquet na Gold"]:::gold

    BRONZE -. "Acorda o Sensor" .-> SENS
    BASH ==>|Dispara o script principal| START
    END ==>|Grava no disco| GOLD
```

---

## Diagrama 9 — Visão MLOps: Integração com MLflow (O Coração do Treinamento)

Este diagrama isola a etapa de treinamento do Machine Learning. Ele mostra como o script futuro (`src/train.py`) se comunicará com o Servidor MLflow para registrar absolutamente tudo o que acontece durante o treino, garantindo rastreabilidade e controle de versão.

```mermaid
flowchart TD
    classDef base fill:#f0f4c3,stroke:#827717,stroke-width:2px,color:#33691e;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef govern fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef gold fill:#fff8e1,stroke:#f9a825,stroke-width:2px,color:#795548;
    classDef mlflow fill:#bbdefb,stroke:#0d47a1,stroke-width:4px,color:#0d47a1,font-size:16px;

    DATA["🥇 enem_silver.parquet<br/>(Tabela Gold)"]:::gold
    TRAIN["💻 src/train.py<br/>Código de Treinamento (Futuro)"]:::core
    
    MLF{{"🎯 SERVIDOR MLflow<br/>(Tracking & Model Registry)"}}:::mlflow

    subgraph TRACKING ["O que o código envia para o servidor? (Tracking)"]
        direction LR
        P["🎛️ Parâmetros<br/>(Ex: max_iter=100)"]:::govern
        M["📊 Métricas<br/>(Ex: RMSE=111, R²=0.26)"]:::govern
        A["📦 Artefato<br/>(Ex: modelo.joblib)"]:::govern
    end

    PROD["🚀 Deploy API<br/>Baixa o modelo direto do MLflow"]:::base

    DATA -->|Alimenta| TRAIN
    
    TRAIN ==>|mlflow.log_params| P
    TRAIN ==>|mlflow.log_metrics| M
    TRAIN ==>|mlflow.sklearn.log_model| A
    
    P -.-> MLF
    M -.-> MLF
    A -.-> MLF
    
    MLF ==>|Fornece a versão Oficial - Production| PROD
```
