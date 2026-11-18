# Arquitetura do Projeto: Previsão do ENEM (MLOps)

O diagrama abaixo ilustra o fluxo temporal e tecnológico do projeto, evidenciando a premissa de "viagem no tempo" (estar em 2023 projetando o futuro de 2024/2025) e as etapas de MLOps.

```mermaid
graph TD
    %% Estilos de Cores
    classDef lab fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef nlp fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef airflow fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef cicd fill:#fce4ec,stroke:#c2185b,stroke-width:2px;
    classDef mlflow fill:#ede7f6,stroke:#512da8,stroke-width:2px;
    classDef aws fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;

    %% FASE 1: O Passado/Presente Simulado (2009 a 2023)
    subgraph Fase1 ["Fase 1: Laboratório Manual (Perspectiva: Estamos em 2023)"]
        A1["Bases Históricas 2009-2023 (Download Manual)"] --> A2("Notebooks 01 a 03 (EDA & Engenharia de Features)")
        A2 --> A3{"Treinamento XGBoost"}
        A3 -->|"Loop de Métricas e Hiperparâmetros"| A4[("Registro MLFlow")]
        A4 --> A3
        A3 --> A5["Modelo Baseline Treinado"]
    end
    class A1,A2,A3,A5 lab;
    class A4 mlflow;

    %% FASE 2: A Ponte para o Futuro (A grande sacada)
    subgraph Fase2 ["Fase 2: Antecipação do Futuro (Drift Semântico)"]
        B1["Análise dos Dicionários 2024 e 2025"] -.-> B2("Notebook 04 (Detecção de Mudanças)")
        B2 --> B3[["Módulo NLP - SBERT (Tradutor de Esquemas)"]]
    end
    class B1,B2,B3 nlp;

    %% FASE 3: O Futuro Automatizado
    subgraph Fase3 ["Fase 3: Pipeline Automatizado MLOps (Dados >= 2024)"]
        C1["INEP libera bases novas (2024 e 2025+)"] --> C2("Apache Airflow DAGs")
        C2 -->|"Ingestão"| B3
        B3 -->|"Padroniza Nomes de Colunas"| C3("ETL -> Parquet")
        C3 --> C4[("Data Lake: AWS S3 (Safras Purificadas)")]
        C4 --> C5{"Out-of-Time Validation (Validação nas safras novas)"}
        C5 -->|"Registra e Compara"| A4
        A4 --> C5
        C5 --> C6["Modelo Final Validado"]
    end
    class C1,C2,C3,C4,C5,C6 airflow;

    %% FASE 4: Entrega em Produção
    subgraph Fase4 ["Fase 4: CI/CD & Deploy na Nuvem (AWS)"]
        C6 -.-> D1("Repositório Git")
        D1 -->|"Push / Release Tag"| D2[["GitHub Actions (CI Pipeline)"]]
        D2 -->|"Build, Test & Package"| D3("Docker Compose (Imagem: FastAPI + Modelo)")
        D3 -->|"Push Imagem Docker"| D4[("AWS ECR")]
        D4 -->|"Deploy Contínuo (CD)"| D5(("AWS App Runner / ECS"))
        D5 --> D6["API REST Disponível"]
    end
    class D1,D2,D3 cicd;
    class D4,D5,D6 aws;

    %% Conexões entre Fases
    A5 -.->|"Serve de base para"| C5

```
