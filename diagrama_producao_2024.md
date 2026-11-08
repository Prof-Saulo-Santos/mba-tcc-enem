# Arquitetura MLOps: Diagrama da Etapa 3 (Orquestração Autônoma Airflow 2024/2025 — Plano Pesado Local)

Por governança de **FinOps**, toda a carga pesada de Engenharia de Dados e Machine Learning (varredura de milhões de linhas em CSV, *embeddings* neurais com **PyTorch/SBERT**, retreinamento censitário do **XGBoost** e rastreamento no **MLflow**) roda **localmente containerizada em Docker**, evitando custos ociosos na nuvem AWS.

Abaixo está o fluxo arquitetural homologado da DAG autônoma (`enem_autonomous_pipeline_dag`), corrigindo a precedência obrigatória do **NLP/SBERT sobre o dicionário antes da seleção de colunas** e implementando a **bifurcação inteligente entre safras com notas (2024) e safras sem notas (2025)**:

```mermaid
graph TD
    classDef ingest fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef nlp fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef etl fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef branch fill:#ede7f6,stroke:#512da8,stroke-width:2px;
    classDef oot fill:#fce4ec,stroke:#c2185b,stroke-width:2px;
    classDef drift fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;

    subgraph Passo1 ["1. Ingestão e Inspeção Estrutural"]
        I1[("Microdados Brutos CSV<br/>(2024 ou 2025)")] --> I2("Sensor / Detector de Safra<br/>(Verifica Dicionário e Notas)")
        D1[("Dicionário INEP (.xlsx)")] --> I2
    end
    class I1,I2,D1 ingest;

    subgraph Passo2 ["2. Inteligência Semântica ANTES da Seleção"]
        I2 --> N1("Motor NLP / SBERT<br/>(paraphrase-multilingual-MiniLM-L12-v2)")
        N1 -->|"Mapeia Drift Semântico<br/>(Ex: Q007→Renda, Q021→PC)"| N2("Contrato de Schema Atualizado<br/>(schema_mapping_historico.json)")
    end
    class N1,N2 nlp;

    subgraph Passo3 ["3. Seleção, Harmonização e Downcasting"]
        N2 --> E1("Seleção do Esquadrão de Elite<br/>+ Deflação em Salários Mínimos")
        E1 --> E2[("Safra Purificada em Parquet<br/>(Downcasting: 15 bytes/linha)")]
    end
    class E1,E2 etl;

    subgraph Passo4 ["4. Bifurcação Autônoma (BranchPythonOperator)"]
        E2 --> B1{"Possui Notas Oficiais<br/>(NU_NOTA_CN/CH/LC/MT)?"}
    end
    class B1 branch;

    subgraph Ramo2024 ["Ramo A: Safra com Notas (Ex: ENEM 2024)"]
        B1 -->|"SIM (Tem Notas)"| O1("Gatekeeper Out-of-Time (OOT)<br/>Avalia enem.pkl v1 + Alinhamento")
        O1 --> O2{"Aprovado no SLA OOT<br/>e Integridade 1:1?"}
        O2 -->|"SIM (SLA OK)"| O3("Concatena Base 2014–2024<br/>+ Retreina XGBoost (Challenger)")
        O3 --> O4("Juiz MLflow:<br/>Champion (v1) vs. Challenger (v2)")
        O4 --> O5[("Promove enem.pkl v2<br/>no Model Registry")]
    end
    class O1,O2,O3,O4,O5 oot;

    subgraph Ramo2025 ["Ramo B: Modo Inferência em Lote & Data Drift (Ex: ENEM 2025 / Fallback)"]
        B1 -->|"NÃO (Sem Notas: 2025)"| F1("Inferência Vetorial em Lote<br/>(Batch Scoring com enem.pkl)")
        O2 -.->|"NÃO (Circuit Breaker:<br/>Bloqueia Contaminação)"| F1
        F1 --> F2("Auditoria de Data Drift de X<br/>(PSI + Teste KS vs. Censo 2014–2023)")
        F2 --> F3[("Registra Predições e Laudo<br/>de Drift no MLflow")]
    end
    class F1,F2,F3 drift;
```

---

## Detalhamento Técnico dos 4 Estágios da DAG

1. **Estágio 1 — Ingestão e Detecção Estrutural:** Localiza automaticamente os arquivos CSV (`PARTICIPANTES_<ANO>.csv`, `RESULTADOS_<ANO>.csv` ou `MICRODADOS_ENEM_<ANO>.csv`) e a planilha oficial de dicionário `.xlsx` da edição.
2. **Estágio 2 — NLP/SBERT no Dicionário (Antes da Seleção):** Antes de abrir o CSV de milhões de linhas, o modelo neural `paraphrase-multilingual-MiniLM-L12-v2` lê as descrições textuais do dicionário novo e descobre por similaridade de cosseno (com restrição injetiva do Algoritmo Húngaro) quais códigos de colunas correspondem às 6 variáveis canônicas (ex.: detectando automaticamente que em 2024 e 2025 a renda familiar mudou de `Q006` para `Q007` e a posse de computador mudou de `Q024` para `Q021`).
3. **Estágio 3 — Seleção, Harmonização de *Value Drift* e *Downcasting*:** Lê apenas as colunas mapeadas em *chunks*, converte a renda em múltiplos de Salários Mínimos por morador (`RENDA_PER_CAPITA`), harmoniza as categorias e comprime o resultado em Parquet (`snappy`, `15 bytes/linha`).
4. **Estágio 4 — Bifurcação Inteligente e *Circuit Breaker* de Governança:**
   * **Se a safra possui notas e alinhamento íntegro:** Executa a validação *Out-of-Time* com o modelo `Champion (v1)`. Se o erro e o $R^2$ cumprirem o SLA, concatena `2014–2024`, treina o `Challenger` e usa o **MLflow** para decidir a promoção de `enem.pkl v2`.
   * **Se a safra não possui notas (`2025`) ou se o Gatekeeper detectar quebra de integridade referencial entre arquivos bipartidos (`2024` desidentificado pelo INEP):** O *Circuit Breaker* impede a contaminação do Data Lake de treinamento e desvia os participantes para **Inferência em Lote (*Batch Scoring*) + Auditoria de *Data Drift* de $X$ (PSI / KS)**.
