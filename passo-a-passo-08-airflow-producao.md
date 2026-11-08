# 📘 Guia Passo a Passo e Relatório de Homologação — Etapa 3 (Orquestração Autônoma 2024/2025, NLP/SBERT, Gatekeeper OOT e Data Drift)

**Módulos de Produção:** [`src/orchestration/`](src/orchestration/), [`tests/test_orchestration_etapa3.py`](tests/test_orchestration_etapa3.py), [`diagrama_producao_2024.md`](diagrama_producao_2024.md)  
**Projeto de TCC:** MBA em Ciência de Dados & MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  
**Data da Auditoria de Execução:** 08 de Novembro de 2026 (`22:00:06 UTC`)  

---

## 1. Visão Geral: O Plano Pesado Local em Docker e a Governança Autônoma (Etapa 3)

Enquanto a **Etapa 2** isolou o *Plano Leve de Inferência* (`515 MB` OCI) para execução *stateless* na nuvem AWS, a **Etapa 3** implementa o **Plano Pesado Local**, responsável por processar novas safras anuais do INEP (`2024` e `2025`), resolver deriva semântica de questionários via **NLP/SBERT**, proteger o Data Lake contra contaminação (*Circuit Breaker*) e arbitrar o retreinamento contínuo (**Champion vs. Challenger**) ou a auditoria de **Data Drift ($X$)** no **MLflow**.

```text
ETAPA 3 — ESTEIRA AUTÔNOMA EM 4 ESTÁGIOS (2024 COM NOTAS vs. 2025 SEM NOTAS)
(1) Ingestão e Detecção Estrutural (`step1_ingest_detect.py`)
        │
        ▼
(2) NLP/SBERT no Dicionário ANTES da Seleção (`step2_sbert_mapper.py`)
    [Descobre dinamicamente: Q006 -> Q007 (Renda) e Q024 -> Q021 (Computador)]
        │
        ▼
(3) Seleção + Deflação em SM + Downcasting 15/11 B/linha (`step3_select_harmonize.py`)
        │
        ▼
(4) Bifurcação Automática (`step4_branch_oot_drift.py`)
    ├──> [COM NOTAS: 2024 / Backtest OOT] ──> Gatekeeper OOT (`enem.pkl v1`)
    │       ├── Se Reprovado (Ex: Embaralhamento LGPD 2024) ──> Circuit Breaker + Batch Drift
    │       └── Se Aprovado no SLA (R² >= 0.28) ──> Retreino XGBoost + Juiz MLflow (`enem_v2.pkl`)
    └──> [SEM NOTAS: 2025] ──> Inferência Vetorial em Lote + Auditoria Data Drift (PSI & KS)
```

---

## 2. Descrição Técnica dos Módulos de Orquestração (`src/orchestration/`)

| Estágio / Arquivo | Função Principal | Responsabilidade Técnica e Regra de Negócio |
| :--- | :--- | :--- |
| **Estágio 1**<br>[`step1_ingest_detect.py`](src/orchestration/step1_ingest_detect.py) | `inspect_and_ingest_edition()` | Localiza o dicionário `.xlsx` (calculando seu `SHA-256`) e classifica o layout do CSV em `MONOLITICO`, `BIPARTIDO_PARTICIPANTES_RESULTADOS` (2024) ou `SOMENTE_PARTICIPANTES_SEM_NOTAS` (2025). Mede a coincidência posicional de `CO_MUNICIPIO_PROVA` entre arquivos bipartidos. |
| **Estágio 2**<br>[`step2_sbert_mapper.py`](src/orchestration/step2_sbert_mapper.py) | `run_sbert_schema_mapping()` | **Roda obrigatoriamente ANTES da seleção colunar.** Extrai todas as abas válidas do dicionário `.xlsx` e utiliza `paraphrase-multilingual-MiniLM-L12-v2` (com injetividade 1-para-1) para mapear o *Semantic Drift* das perguntas socioeconômicas. |
| **Estágio 3**<br>[`step3_select_harmonize.py`](src/orchestration/step3_select_harmonize.py) | `select_harmonize_and_downcast()` | Seleciona apenas as colunas mapeadas pelo SBERT, converte a renda em múltiplos de Salários Mínimos por morador (`RENDA_PER_CAPITA`), harmoniza categorias e aplica *Downcasting* (`15 bytes/linha` com `TARGET_M4`; `11 bytes/linha` sem notas). |
| **Estágio 4**<br>[`step4_branch_oot_drift.py`](src/orchestration/step4_branch_oot_drift.py) | `decide_branch_task_id()`<br>`run_oot_gatekeeper_and_retrain()`<br>`run_batch_inference_and_drift()` | Roteia automaticamente entre o **Gatekeeper OOT + Retreino Champion/Challenger** (quando há notas) e a **Inferência em Lote + Auditoria de Data Drift (PSI/KS)** (quando não há notas ou quando o *Circuit Breaker* bloqueia bases desidentificadas). |

---

## 3. Registro de Execução da Suíte Pytest da Etapa 3 (`3/3 PASSED`)

Comando executado no ambiente `.venv` (`Python 3.13.9`, `pytest 9.2.0`):

```text
============================= test session starts ==============================
platform linux -- Python 3.13.9, pytest-9.2.0, pluggy-1.7.0 -- /home/saulo/mba/tcc/enem/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/saulo/mba/tcc/enem
plugins: typeguard-4.6.0, anyio-4.15.1
collecting ... collected 3 items

tests/test_orchestration_etapa3.py::test_etapa3_full_pipeline_2024_circuit_breaker PASSED [ 33%]
tests/test_orchestration_etapa3.py::test_etapa3_full_pipeline_2025_batch_inference_and_drift PASSED [ 66%]
tests/test_orchestration_etapa3.py::test_etapa3_oot_approved_retrain_champion_vs_challenger PASSED [100%]

======================== 3 passed, 1 warning in 46.39s =========================
```

---

## 4. Resultados Detalhados dos 3 Cenários Homologados (Evidências para a Banca)

### 4.1 Cenário 1: ENEM 2024 Real — Descoberta SBERT + *Circuit Breaker* Anti-Poisoning + Drift

1. **Descoberta Semântica no Dicionário 2024 (Estágio 2 — SBERT):**
   * No questionário de 2024 (que possui apenas `Q001` a `Q023`), a coluna `Q024` deixou de existir fisicamente.
   * O motor SBERT identificou automaticamente antes da leitura do CSV:
     * `Q006` (Renda Familiar 2023) $\longrightarrow$ **`Q007`** em 2024;
     * `Q024` (Posse de Computador 2023) $\longrightarrow$ **`Q021`** em 2024.
2. **Acionamento do *Circuit Breaker* no Gatekeeper Out-of-Time (Estágio 4):**
   * Ao auditar os arquivos `PARTICIPANTES_2024.csv` e `RESULTADOS_2024.csv`, o Estágio 1 detectou que apenas **`0,55%`** das linhas coincidem no código de município de prova (`positional_match_rate = 0.0055`), pois o INEP desvinculou e reordenou os dois arquivos por exigência de anonimização da LGPD.
   * Quando submetida ao `enem.pkl v1`, a junção posicional bruta resultou em **`R² OOT = -0.1914` (`< SLA 0.28`)**.
   * **Ação Autônoma de Governança:** O **Gatekeeper OOT** reprovou o alinhamento 1:1, **bloqueou a concatenação e o retreinamento** (impedindo a contaminação da base histórica `2014–2023`) e desviou automaticamente os `13.821` participantes elegíveis para **Inferência em Lote + Auditoria de Data Drift de $X$**.

#### Laudo Oficial Gerado (`relatorio_etapa3_2024_drift.json`):
```json
{
  "year": 2024,
  "execution_branch": "BATCH_INFERENCE_AND_DATA_DRIFT",
  "trigger_reason": "CIRCUIT_BREAKER_OOT_REJECTED (alignment_ok=False, positional_match_rate=0.0055, r2_oot=-0.1914 < 0.28)",
  "prediction_summary": {
    "n_scored": 13821,
    "pred_mean": 510.69,
    "pred_std": 40.96,
    "pred_p10": 465.07,
    "pred_p50": 502.72,
    "pred_p90": 568.73
  },
  "max_psi": 0.11927,
  "overall_drift_status": "ATENCAO_MODERADO (0.10 <= PSI < 0.25)",
  "feature_drift": {
    "RENDA_PER_CAPITA": { "psi": 0.01767, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0449, "ref_mean": 0.8223, "cur_mean": 0.7211 },
    "Q024":             { "psi": 0.00440, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0175, "ref_mean": 0.7368, "cur_mean": 0.7340 },
    "TP_ANO_CONCLUIU":  { "psi": 0.11927, "status_psi": "ATENCAO_MODERADO (0.10 <= PSI < 0.25)", "ks_statistic": 0.1381, "ref_mean": 1.5245, "cur_mean": 2.5393 },
    "TP_LINGUA":        { "psi": 0.00077, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0137, "ref_mean": 0.4236, "cur_mean": 0.4099 },
    "TP_SEXO":          { "psi": 0.01628, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0629, "ref_mean": 0.3860, "cur_mean": 0.4489 },
    "Q002":             { "psi": 0.04102, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0641, "ref_mean": 3.7777, "cur_mean": 3.5874 }
  }
}
```

---

### 4.2 Cenário 2: ENEM 2025 Real (Sem Notas) — Inferência Vetorial em Lote + Estabilidade PSI

1. **Detecção e Mapeamento Semântico (Estágios 1 a 3):**
   * Identificado automaticamente como `SOMENTE_PARTICIPANTES_SEM_NOTAS` (`has_scores = False`);
   * Mapeado via SBERT (`Q006 -> Q007` e `Q024 -> Q021`) e compactado em **`11 bytes/linha`** (`20.000` participantes avaliados).
2. **Inferência em Lote e Auditoria de Drift (Estágio 4):**
   * Média prevista `TARGET_M4` para os inscritos de 2025: **`516,27 ± 48,64 pts TRI`**;
   * **100% das 6 features socioeconômicas classificadas como `ESTAVEL (PSI < 0.10)`**, com `max_psi = 0.0318`!

#### Laudo Oficial Gerado (`relatorio_etapa3_2025_drift.json`):
```json
{
  "year": 2025,
  "execution_branch": "BATCH_INFERENCE_AND_DATA_DRIFT",
  "trigger_reason": "EDITION_WITHOUT_SCORES",
  "prediction_summary": {
    "n_scored": 20000,
    "pred_mean": 516.27,
    "pred_std": 48.64,
    "pred_p10": 460.69,
    "pred_p50": 508.46,
    "pred_p90": 586.10
  },
  "max_psi": 0.0318,
  "overall_drift_status": "ESTAVEL (PSI < 0.10)",
  "feature_drift": {
    "RENDA_PER_CAPITA": { "psi": 0.01230, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0238, "ref_mean": 0.8223, "cur_mean": 0.8360 },
    "Q024":             { "psi": 0.00533, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0303, "ref_mean": 0.7368, "cur_mean": 0.8005 },
    "TP_ANO_CONCLUIU":  { "psi": 0.03180, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0595, "ref_mean": 1.5245, "cur_mean": 1.4803 },
    "TP_LINGUA":        { "psi": 0.00029, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0085, "ref_mean": 0.4236, "cur_mean": 0.4320 },
    "TP_SEXO":          { "psi": 0.01576, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0618, "ref_mean": 0.3860, "cur_mean": 0.4479 },
    "Q002":             { "psi": 0.01958, "status_psi": "ESTAVEL (PSI < 0.10)", "ks_statistic": 0.0385, "ref_mean": 3.7777, "cur_mean": 3.9297 }
  }
}
```

---

### 4.3 Cenário 3: Safra OOT Íntegra Aprovada no Gatekeeper — Retreino & Juiz MLflow (`Champion vs. Challenger`)

Para comprovar o funcionamento completo do ramo de retreinamento e evolução do modelo quando o INEP disponibiliza uma safra com integridade referencial 1:1 confirmada (`positional_alignment_valid = True`):

1. **Aprovação no Gatekeeper Out-of-Time (`enem.pkl v1`):**
   * `R² OOT = 0.31520` (`>= SLA 0.28`), `RMSE OOT = 67,4727 pts`, `MAE OOT = 52,7592 pts` $\longrightarrow$ **`gatekeeper_passed = True`**!
2. **Consolidação, Retreino do Challenger (`XGBRegressor hist`) e Disputa no Holdout:**
   * **Champion (`v1`):** `R² = 0.30880` | `RMSE = 66,3074 pts`
   * **Challenger (`v2`):** **`R² = 0.31173`** | **`RMSE = 66,1667 pts`** (**Vencedor: `-0,1407 pts` de RMSE e `+0,29 pp` de $R^2$**)
   * **Promoção no MLflow:** `challenger_promoted = True`, gerando o novo binário `enem_v2.pkl` e registrando todas as métricas e artefatos no experimento `tcc_enem_etapa3_airflow_autonomo` (`sqlite:///mlflow.db`).

#### Laudo Oficial Gerado (`relatorio_etapa3_2023_retrain.json`):
```json
{
  "year": 2023,
  "execution_branch": "OOT_APPROVED_RETRAIN_CHAMPION_VS_CHALLENGER",
  "gatekeeper_passed": true,
  "oot_metrics_v1": {
    "r2": 0.3152,
    "rmse": 67.4727,
    "mae": 52.7592
  },
  "holdout_evaluation": {
    "champion_v1": {
      "r2": 0.3088,
      "rmse": 66.3074
    },
    "challenger_v2": {
      "r2": 0.31173,
      "rmse": 66.1667
    }
  },
  "challenger_promoted": true,
  "artifact_v2_path": "data/processed/safras_etapa3/enem_v2.pkl"
}
```

