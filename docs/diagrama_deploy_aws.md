# Arquitetura MLOps: Planos Desacoplados (Workstation Containerizada + Nuvem AWS)

O recorte histórico do projeto foi encerrado em **2023** devido à ruptura estrutural da **LGPD** a partir de `2024` (separação de `PARTICIPANTES` e `RESULTADOS` sem chave identificadora pelo INEP). A capacidade de generalização temporal é comprovada no Notebook 06 via **Validação *Out-of-Time* Interna (`2014–2022 -> 2023`, $R^2 = 0{,}31842$)**.

Com as evoluções das **Fases 1 a 4**, o repositório opera sob uma **Arquitetura Desacoplada por Planos (*Local-to-Cloud MLOps*)**:

1. **Plano Offline / Governança (`profiles: ["mlops"]` + Amazon S3):** `PostgreSQL 16` + `MLflow Tracking Server 3.17.2` + `DVC 3.67.1` armazenam dados pesados (`.parquet` em `dvc-store/`) e artefatos/modelos (`mlflow-artifacts/`) em bucket S3 privado (`AES256`, versionamento habilitado).
2. **Plano Online / *Serving* (`GitHub Actions + Terraform + AWS`):** [`models/enem.pkl`](../models/enem.pkl) embarcado na API **FastAPI** (`Docker multi-stage`, `515 MB` Content Size), validado por CI (`SHA-256` + `ruff` + `mypy` + `26` testes `pytest` + *Docker Smoke Test*), publicado no **Amazon ECR** via **IAM OIDC** e servido pelo **AWS App Runner** sob demanda FinOps (`infra/`).
3. **Plano de Observabilidade (`profiles: ["monitoring"]`):** a API expõe `GET /metrics` (`prometheus-client==0.26.0`), coletado pelo **Prometheus** (`:9090`) e exibido no **Grafana** (`:3000`) com 10 painéis de SLA HTTP, bloqueios Anti-Leakage (`HTTP 422`) e *Data/Prediction Drift*.

```mermaid
flowchart LR
    classDef offline fill:#ede7f6,stroke:#512da8,stroke-width:2px;
    classDef code fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef cicd fill:#fce4ec,stroke:#c2185b,stroke-width:2px;
    classDef aws fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef obs fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;

    subgraph Offline ["Plano Offline / Governanca (Workstation + S3)"]
        NB["Notebooks 01-06 (2014-2023)"]
        DVC["DVC 3.67.1 (.parquet)"]
        PG["PostgreSQL 16 + MLflow Server 3.17.2"]
        NB -->|"Versiona datasets"| DVC
        NB -->|"Registra runs e modelo"| PG
    end
    class NB,DVC,PG offline;

    S3["Amazon S3 (dvc-store/ e mlflow-artifacts/)"]
    DVC -->|"dvc push"| S3
    PG -->|"artifact_root S3"| S3
    class S3 aws;

    subgraph Online ["Plano Online / Serving (GitHub Actions -> AWS)"]
        GIT["GitHub Repo (src/api/, tests/, models/enem.pkl)"]
        CI["GitHub Actions: SHA-256 + Ruff + Mypy + Pytest 26/26 + Docker Smoke"]
        TF["Terraform (infra/: S3, ECR, IAM OIDC, App Runner)"]
        ECR["Amazon ECR (enem-target-m4-api)"]
        AR["AWS App Runner (API HTTPS)"]
        GIT -->|"Push / PR main"| CI
        TF -.->|"Provisiona / Destroi (FinOps)"| ECR
        TF -.->|"Provisiona / Destroi (FinOps)"| AR
        CI -->|"Login OIDC + Push Docker"| ECR
        ECR -->|"Deploy imagem"| AR
    end
    class GIT,CI cicd;
    class TF,ECR,AR aws;

    subgraph Obs ["Plano de Observabilidade"]
        METRICS["Endpoint GET /metrics"]
        PROM["Prometheus (:9090)"]
        GRAF["Grafana (:3000 - 10 Paineis)"]
        AR -.->|"Expoe metricas"| METRICS
        METRICS -->|"Scrape 5s"| PROM -->|"PromQL"| GRAF
    end
    class METRICS code;
    class PROM,GRAF obs;
```
