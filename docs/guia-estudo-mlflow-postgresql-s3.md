# 📘 Guia de Estudo e Slides — MLflow Remoto (`PostgreSQL + Amazon S3`) & Notebook 06 (Fase 3)

**Projeto:** TCC MBA — Predição de Desempenho no ENEM (`TARGET_M4`) e Arquitetura MLOps  
**Autor:** Saulo Santos  
**Referência Visual (1920×1080):** [`media/mlflow_postgresql_s3_fase3.png`](../media/mlflow_postgresql_s3_fase3.png)  
**Objetivo deste Documento:** Consolidar os fundamentos de rastreabilidade distribuída em MLOps (separação *Backend Store* vs. *Artifact Store*), execução containerizada (`PostgreSQL + MLflow Server`), resultados auditados no S3 após a reexecução do Notebook 06 e roteiro pronto de slides/sabatina.

---

## 1. Por Que Substituímos o `SQLite` por `PostgreSQL + S3`?

Na versão inicial da Etapa 1, o Notebook 06 gravava experimentos em `sqlite:///mlflow.db` e os arquivos binários na pasta local `./mlruns`. Embora útil para experimentação solitária, essa abordagem apresenta limitações clássicas criticadas em bancas de produção:

1. **Concorrência e escala de banco:** `SQLite` usa bloqueio de arquivo único, não suporta múltiplos clientes simultâneos com segurança nem representa um banco relacional de servidor.
2. **Artefatos presos ao disco local:** modelos, assinaturas e gráficos em `./mlruns` não possuem replicação, versionamento de objetos nem acesso centralizado em nuvem.

Com a **Fase 3**, migramos para a **Arquitetura Dual do MLflow**:
* **Backend Store (`PostgreSQL 16` em Docker, porta `:5432`):** armazena metadados leves e estruturados (experimentos, `run_id`, hiperparâmetros, métricas e versões do *Model Registry* `enem_target_m4_producao`) com volume persistente `postgres_mlflow_data` e custo de Amazon RDS igual a **`\$0,00/dia`**.
* **Artifact Store (`Amazon S3`, bucket da Fase 2):** armazena todos os arquivos binários (`model.ubj`, `MLmodel`, gráficos PNG, CSV anual e `enem_model_card.json`) em **`s3://tcc-enem-saulo-mlops-703671922740/mlflow-artifacts/`** com criptografia `AES256` e versionamento ativo.
* **Tracking Server (`Dockerfile.mlflow`, porta `:5000`):** container dedicado rodando exatamente **`mlflow==3.17.2` + `psycopg2-binary==2.9.13` + `boto3==1.44.9`**, autenticando na AWS via montagem somente leitura `${HOME}/.aws:/root/.aws:ro`.

---

## 2. Mudanças Realizadas no Repositório (Impacto Cirúrgico)

| Arquivo / Módulo | Papel na Fase 3 | Detalhe Técnico Importante |
| :--- | :--- | :--- |
| [`Dockerfile.mlflow`](../Dockerfile.mlflow) | Container dedicado do Tracking Server | `python:3.13-slim` + `uv` com versões travadas em paridade com o `.venv` e `--allowed-hosts "*"` (necessário para MLflow 3.x aceitar chamadas Docker/localhost). |
| [`docker-compose.yml`](../docker-compose.yml) | Orquestração via `profiles: ["mlops"]` | Sobe `postgres` (`healthcheck` com `start_period: 60s` para suportar *initdb* em WSL2) e `mlflow-server` montando `~/.aws:ro`. |
| [`requirements.txt`](../requirements.txt) | Dependências do ambiente de treino | Fixa `psycopg2-binary==2.9.13` e `boto3==1.44.9` (mantendo [`requirements-api.txt`](../requirements-api.txt) enxuto). |
| [`notebooks/06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb) | Único notebook alterado (`Bloco 1.5`) | Troca `sqlite:///mlflow.db` por `MLFLOW_TRACKING_URI` (`http://127.0.0.1:5000`) e `artifact_location` apontando para o S3; Notebooks `01` a `05` permaneceram intactos. |
| [`tests/test_api_contract.py`](../tests/test_api_contract.py) | Sincronia pós-reexecução | Atualizado `mlflow_run_id_campeao` para o novo run registrado no PostgreSQL (`6490c396b0e04147b156bedb0c8af9f7`). |

---

## 3. Evidências Reais da Reexecução Completa do Notebook 06 (`21/11/2026`)

Após subir a stack `mlops`, todas as células de código do [`06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb) foram reexecutadas de ponta a ponta sem erros:

* **Reprodutibilidade Determinística Bit-a-Bit Comprovada:**
  * `models/enem.pkl` manteve **exatamente o mesmo checksum `SHA-256`**: `114f51959492c89a240f9a64adb5d1365cf7c255b1b95a4cb8510636019bd55f` (`1,727 MB`).
  * Métricas oficiais idênticas em [`models/enem_model_card.json`](../models/enem_model_card.json): Holdout (`7.518.726` alunos) $R^2 = 0{,}3378$, $\text{RMSE} = 57{,}7439\text{ pts}$, $\text{MAE} = 45{,}5904\text{ pts}$; OOT `2023` ($2{,}68\text{M}$) $R^2 = 0{,}31842$.
* **Novo Registro no PostgreSQL & Model Registry:**
  * **Experimento:** `tcc_enem_decada_ouro_2014_2023` (Experimento ID `2`, `http://127.0.0.1:5000/#/experiments/2`).
  * **Run Campeão (`estagio3_final_xgboost_censo_completo`):** `6490c396b0e04147b156bedb0c8af9f7`.
  * **Modelo Registrado:** `enem_target_m4_producao` Versão `1` (`models:/m-ea7931423f5141379ff97886636ae0ea`).
* **Auditoria Direta no Bucket Amazon S3 (`mlflow-artifacts/`):**
  * **`17` objetos** confirmados via `aws s3 ls` (~`2,49 MiB` no total):
    * `mlflow-artifacts/6490c396b0e04147b156bedb0c8af9f7/artifacts/relatorio_auditoria_tcc/`: figuras `01`, `03`, `04a`, `04b`, `05`, `06`, `auditoria_holdout_por_ano_2014_2023.csv` e `enem_model_card.json`;
    * `mlflow-artifacts/64f7e8f525b345188811aa587f74e9ed/artifacts/`: `02_curva_aprendizado_escalavel.png`;
    * `mlflow-artifacts/models/m-ea7931423f5141379ff97886636ae0ea/artifacts/`: `MLmodel`, `model.ubj` (`1,7 MiB`), `conda.yaml`, `requirements.txt`, `python_env.yaml`, `input_example.json` e `serving_input_example.json`.

---

## 4. Comandos Essenciais de Operação

```bash
# Subir PostgreSQL + MLflow Tracking Server
docker compose --profile mlops up -d

# Abrir interface web do MLflow (experimentos, métricas, artefatos no S3 e Model Registry)
# -> http://localhost:5000

# Subir apenas Observabilidade ou tudo ao mesmo tempo usando perfis
docker compose --profile monitoring up -d
docker compose --profile mlops --profile monitoring up -d

# Encerrar containers mantendo o volume postgres_mlflow_data intacto
docker compose --profile mlops down
```

---

## 5. Roteiro Pronto de Slides & Sabatina da Fase 3

### Slide Sugerido — Governança de Experimentos com MLflow (`PostgreSQL + S3`)
* **Visual principal:** [`media/mlflow_postgresql_s3_fase3.png`](../media/mlflow_postgresql_s3_fase3.png) (`1920×1080`).
* **Tópicos na tela:**
  * **Arquitetura Dual:** Metadados estruturados + Model Registry no **PostgreSQL 16** (`:5432`) | Modelos, assinaturas e 7 figuras no **Amazon S3** (`mlflow-artifacts/`).
  * **Impacto mínimo de código:** apenas o `Bloco 1.5` de `06_treinamento_modelo.ipynb` alterado para `http://127.0.0.1:5000`; `01` a `05` intactos.
  * **Reprodutibilidade comprovada:** reexecução completa nos `37,59M` registros produziu o mesmo `SHA-256` bit-a-bit (`114f5195...`) e enviou `17` artefatos ao S3 (`run_id = 6490c396...`).
  * **FinOps:** `PostgreSQL + MLflow Server` em Docker local sob demanda (`\$0,00` de RDS/EC2 na AWS) gravando no mesmo bucket S3 da Fase 2.
* **Nota de fala (~1 min):** *"Para superar as limitações de concorrência e disco local do SQLite, implantamos a arquitetura dual do MLflow: um banco PostgreSQL em Docker armazena parâmetros, métricas e o Model Registry, enquanto todos os modelos e gráficos de auditoria são persistidos diretamente no Amazon S3. Ao reexecutar os 37,59 milhões de registros contra o novo servidor, obtivemos exatamente o mesmo hash SHA-256 do XGBRegressor campeão e sincronizamos automaticamente o novo run ID na suíte de testes da API."*

### Perguntas Prováveis da Banca
1. **"Por que não subir o MLflow e o PostgreSQL em um Amazon RDS na AWS?"**
   * *Resposta:* Pela nossa **Arquitetura Desacoplada por Planos**: o plano de treinamento e governança de experimentos roda sob demanda durante o ciclo de treino, enquanto a persistência dos dados (DVC) e artefatos (MLflow) já fica segura e imutável no Amazon S3. Evitamos pagar um RDS 24/7 sem afetar em nada a autonomia da API de produção no App Runner.
2. **"Qual a diferença prática entre Backend Store e Artifact Store no MLflow?"**
   * *Resposta:* O *Backend Store* (PostgreSQL) guarda dados tabulares leves e consultáveis por SQL (runs, tags, hiperparâmetros, métricas, versões do Registry). O *Artifact Store* (S3) guarda objetos binários pesados (`model.ubj`, imagens PNG, JSONs de contrato), evitando inflar o banco relacional.
3. **"Por que foi necessário atualizar `tests/test_api_contract.py` após a reexecução se o `SHA-256` do modelo não mudou?"**
   * *Resposta:* Porque nossa semente fixa (`SEED=42`) garantiu determinismo matemático idêntico no `models/enem.pkl`, mas o novo registro no PostgreSQL gerou um novo UUID para `mlflow_run_id_campeao` (`6490c396...`) e novo timestamp no `enem_model_card.json`, o que foi imediatamente detectado pelo teste de contrato do `/info`.
