# Arquitetura MLOps: Diagrama 2 (Pipeline de Produção 2024)

Este diagrama representa o cenário futuro. Aqui, não estamos mais treinando o modelo, estamos **usando** o modelo para prever a nota dos alunos da nova base de 2024.

```mermaid
graph TD
    classDef airflow fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef nlp fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef aws fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef model fill:#fce4ec,stroke:#c2185b,stroke-width:2px;
    classDef data fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;

    %% A ponte do diagrama anterior
    M1("Modelo Final Treinado (Vindo do Diagrama 1)")
    class M1 model;

    subgraph Fase_Airflow ["1. Preparação de Dados (Pipeline Airflow)"]
        A1[("Base de Dados 2024 (Crua)")] --> A2("Nó do AirFlow")
        A2 -->|"1. Retira o lixo"| A3("Seleção de Atributos")
        A3 -->|"2. Padroniza colunas"| A4("Nó de NLP (SBERT)")
        A4 --> A5[("Base 2024 Purificada (S3)")]
    end
    class A1,A5 data;
    class A2,A3 airflow;
    class A4 nlp;

    subgraph Fase_AWS ["2. Inferência e Consumo (AWS)"]
        B1("Servidor AWS (API FastAPI + Docker)")
        M1 -.->|"O Modelo é carregado dentro do Servidor AWS"| B1
    end
    class B1 aws;

    %% A conexão entre o dado limpo e o modelo na nuvem
    A5 -->|"3. Envia alunos de 2024 para o modelo"| B1
    B1 --> C1("Resultado Final: Previsões e Validação")
    class C1 model;
```
