# 🔭 Estudos Futuros e Arquitetura Comparada (Evoluções de Engenharia e MLOps)

**Projeto de TCC — MBA em Ciência de Dados & MLOps**  
**Autor:** Saulo Santos  
**Objetivo deste Documento:** Consolidar alternativas tecnológicas aplicáveis a cada camada do projeto, analisar *trade-offs* para a banca examinadora e **formalizar a decisão arquitetural aprovada (`Opção A + Cenário 1`)** para evolução de MLOps (eliminação do `SQLite`, adoção de `DVC + S3`, `MLflow` com `PostgreSQL + S3`, `Terraform` e `Prometheus + Grafana`).

---

## 1. O Papel do Terraform (Infraestrutura como Código — IaC) na Etapa 2

### 1.1 Onde o Terraform se encaixa no estado atual do projeto
Ao analisar o workflow de CI/CD em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml), observa-se uma fronteira clara entre automação de entrega (CI/CD) e provisionamento de infraestrutura:

* A esteira atual automatiza o *Quality Gate* (`SHA-256` + `pytest`), o *Docker Smoke Test* E2E, a criação/uso do repositório **Amazon ECR** via AWS CLI (`aws ecr create-repository`), o *push* da imagem e o disparo de atualização no **AWS ECS Express Mode** (`aws ecs update-express-gateway-service`).
* Contudo, antes da criação do módulo `infra/`, o pipeline pressuporia que recursos fundacionais já existissem previamente na conta AWS — especificamente o serviço **AWS ECS Express Mode (`AWS_ECS_SERVICE_ARN`)**, o cluster ECS, as **IAM Roles** (`ecs_execution` e `ecs_infrastructure`) e a configuração de autenticação **OIDC** entre GitHub Actions e AWS. Caso criados manualmente no console (*ClickOps*), esses recursos não ficam versionados em código.

Com o **Terraform** em [`infra/`](../infra/) (`main.tf`, `variables.tf`, `outputs.tf` e `versions.tf`), toda essa infraestrutura é declarada em **HCL (*HashiCorp Configuration Language*)**:

1. `aws_ecr_repository` + política de ciclo de vida (*lifecycle policy* para expirar imagens antigas e reduzir custo de armazenamento).
2. Provedor OIDC e `aws_iam_role` com privilégios mínimos (*Least Privilege*) para o GitHub Actions e para as roles `ecs_execution` e `ecs_infrastructure` do **ECS Express Mode**.
3. `aws_ecs_cluster` + `aws_ecs_express_gateway_service` (definição declarativa de vCPU, memória RAM, porta `8000`, endpoint `/health` e limites de *autoscaling*, com trava FinOps `create_ecs = true/false`).
4. Controle declarativo de custo por hora via flag `create_ecs` (`false` entre testes; `terraform destroy` definitivo pós-banca).

### 1.2 Análise de Prós e Contras para o TCC

| Prós do uso de Terraform | Contras / Riscos no contexto atual do TCC |
| :--- | :--- |
| **FinOps determinístico (`apply` / `destroy`):** permite provisionar toda a nuvem minutos antes da defesa com `terraform apply` e remover 100% dos recursos imediatamente após a banca com `terraform destroy`, evitando cobranças residuais. | **Sobrecarga de escopo:** as Etapas 1 e 2 já estão 100% implementadas, testadas (`25/25`) e documentadas; adicionar Terraform exige conta AWS ativa, testes reais de provisionamento e gestão segura de estado (`terraform.tfstate`). |
| **Eliminação de *ClickOps*:** garante que a infraestrutura da API em nuvem seja reproduzível do zero por qualquer avaliador ou membro de equipe. | **Foco da avaliação acadêmica:** o núcleo científico e de MLOps do trabalho (consolidação de `37,59M` registros, modelagem/explicabilidade e produtização em container + CI/CD) já está resolvido sem depender de IaC completa. |
| **Diferencial de maturidade DevOps/MLOps:** reforça governança, rastreabilidade de mudanças de infraestrutura em *Pull Requests* e paridade entre ambientes (`staging` vs. `prod`). | **Cuidados de segurança:** exige atenção extra para não versionar arquivos de estado (`.tfstate`) ou credenciais no repositório Git. |

### 1.3 Posicionamento Recomendado
* **Para o fechamento atual do TCC:** manter a arquitetura enxuta existente e posicionar o **Terraform (IaC)** como evolução natural no capítulo de **Trabalhos Futuros** (ou na subseção de limitações operacionais de *ClickOps*).
* **Em caso de evolução futura / demonstração ao vivo recorrente na AWS:** o módulo em `infra/` automatiza `S3 + ECR + IAM OIDC + ECS Express Mode` e garante criação/desligamento/destruição reprodutível em 1 comando (`create_ecs = true/false` e `terraform destroy`).

---

## 2. Alternativas Tecnológicas por Camada da Arquitetura

Esta seção mapeia tecnologias equivalentes de mercado para cada etapa do pipeline e consolida os argumentos técnicos que sustentam as escolhas adotadas hoje no repositório.

### 2.1 Camada de Ingestão e Processamento Big Data (`Notebook 05`)
* **Implementação atual:** `Pandas` em fluxo por blocos (*chunked streaming* com `chunksize=500_000` e projeção antecipada `usecols`), `PyArrow` e persistência colunar em **Apache Parquet** (`compressão snappy`) em [`notebooks/05_consolidacao_historica.ipynb`](../notebooks/05_consolidacao_historica.ipynb).
* **Alternativas possíveis:**
  * **Polars:** biblioteca em Rust com *Lazy API* (`pl.scan_csv`), execução paralela em múltiplos núcleos e modo *streaming* nativo, capaz de reduzir significativamente o tempo de leitura dos CSVs.
  * **DuckDB:** motor SQL analítico *in-process* (*out-of-core*) que lê múltiplos CSVs brutos diretamente por consulta SQL e exporta para `.parquet` comprimido com baixíssimo consumo de RAM.
  * **Apache Spark (`PySpark`):** processamento distribuído em cluster, indicado quando o volume ultrapassa a capacidade de um único nó ou exige integração com *Data Lakes* corporativos (Delta Lake / Iceberg).
* **Justificativa da escolha atual:** com `usecols` + *downcasting* extremo (`15 bytes/linha`), `25,45 GB` brutos (`56,57M` inscritos) foram consolidados em `537,78 MB` de RAM (`153,17 MB` em disco). Um processamento *single-node* em *chunks* evitou o custo financeiro, a sobrecarga operacional e a complexidade de cluster JVM do Spark. *(Polars ou DuckDB são candidatos naturais para acelerar a CPU em uma refatoração futura no mesmo hardware.)*

### 2.2 Camada de Harmonização Semântica e Qualidade de Dados (`Notebook 04`)
* **Implementação atual:** embeddings locais via Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensões) + similaridade de cosseno + auditoria *Human-in-the-Loop* gerando [`data/processed/schema_mapping_historico.json`](../data/processed/schema_mapping_historico.json).
* **Alternativas possíveis:**
  * **Modelos de Embeddings maiores / multilíngues recentes** (ex.: `BGE-M3`) ou **LLMs com *Structured Outputs*** para sugerir não apenas correspondência lexical de colunas, mas também mapas de equivalência categórica (*Value Drift* nas faixas `A..Q`).
  * **Frameworks declarativos de Data Quality:** **Great Expectations** ou **Pandera** acoplados em toda a esteira ETL para gerar relatórios automatizados em HTML/JSON a cada execução.
* **Justificativa da escolha atual:** o SBERT executado localmente em CPU evita custos recorrentes de APIs externas, elimina envio de metadados para terceiros e garante reprodutibilidade determinística (`seed=42`).

### 2.3 Camada de Modelagem, Explicabilidade e Experimentação (`Notebook 06`)
* **Implementação atual:** `XGBRegressor` (`tree_method="hist"`), rastreamento local com **MLflow** (`sqlite:///mlflow.db` + `./mlruns`) e explicabilidade exata via **TreeSHAP** em [`notebooks/06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb).
* **Alternativas de algoritmos:**
  * **LightGBM:** frequentemente oferece maior velocidade de treinamento em bases com dezenas de milhões de registros por meio de crescimento *leaf-wise* e *bundling* de features.
  * **CatBoost:** possui tratamento nativo para variáveis categóricas via *ordered target statistics*, reduzindo a dependência da codificação ordinal numérica em atributos como `Q002`, `Q024` e `TP_ANO_CONCLUIU`.
  * **Redes Neurais Tabulares (MLP / TabNet em PyTorch):** alternativa paramétrica profunda, porém tipicamente mais custosa em *tuning* e com explicabilidade mais lenta frente à exatidão do `TreeSHAP` em árvores.
* **Alternativas de governança e versionamento de dados/experimentos:**
  * **DVC (*Data Version Control*):** para versionar os artefatos pesados (`.parquet` de `153,17 MB` e binários de modelo) apontando para um *bucket* **Amazon S3**, mantendo apenas ponteiros leves no Git.
  * **MLflow Tracking Server remoto:** hospedado com backend **PostgreSQL** e *Artifact Store* em **S3**, substituindo o SQLite local em cenários multiusuário.
* **Justificativa da escolha atual:** o `XGBRegressor` (`hist`) escalou sobre `27,07M` linhas de treino em ambiente local, superou o benchmark de *Bagging* (`RandomForestRegressor`: $R^2 = 0{,}33780$ vs. $0{,}33606$) com inferência `~35%` mais rápida (`81,15 ms / 10k` amostras) e possui integração nativa exata com `TreeSHAP`.

### 2.4 Camada de *Serving*, Nuvem e Observabilidade (`Etapa 2`)
* **Implementação atual:** API **FastAPI** + **Pydantic v2** (`extra="forbid"`), empacotada em **Docker *multi-stage*** (`515 MB` Content Size) com CI/CD via **GitHub Actions** mirando **Amazon ECR + AWS ECS Express Mode** (Fargate + ALB gerenciado com URL HTTPS nativa, adotado em substituição ao AWS App Runner após restrição/descontinuação de criação de novos serviços na conta).
* **Alternativas de empacotamento e runtime de inferência:**
  * **ONNX (`ONNX Runtime`):** converte o modelo treinado para formato interoperável independente da biblioteca de treino (`xgboost`/`scikit-learn`), otimizando latência de inferência.
  * **BentoML:** framework especializado em empacotamento de modelos de ML, facilitando *adaptive batching* e padronização de contêineres OCI para múltiplos modelos.
* **Alternativas de hospedagem na AWS:**
  * **AWS App Runner:** originalmente cogitado pela simplicidade PaaS, mas inviabilizado na conta AWS (`InvalidRequestException: Account 703671922740 can't create new App Runner services`), motivando a migração para o **AWS ECS Express Mode**.
  * **AWS Lambda + API Gateway:** modelo *serverless* puro com cobrança estrita por requisição (*scale-to-zero* real), excelente para FinOps em tráfego esporádico, exigindo atenção ao *cold start* e ao limite de tamanho de imagem/camadas.
  * **Amazon ECS clássico (sem Express Mode) ou Amazon EKS (Kubernetes):** exigiriam configuração manual de ALB, *target groups*, rede VPC ou *control plane* completo — complexidade desnecessária que o **ECS Express Mode** elimina em um único recurso (`aws_ecs_express_gateway_service`).
  * **Amazon SageMaker Endpoints:** plataforma gerenciada fim-a-fim da AWS para ML, porém com custo fixo por hora consideravelmente superior ao **ECS Express Mode** sob demanda (`create_ecs = true/false`) para cargas acadêmicas ou de baixo tráfego.
* **Alternativas de qualidade de código e monitoramento em produção (pós-deploy):**
  * **Qualidade estática no CI (`quality-gate-ci`):** inclusão de **`ruff`** (*linter*/formatador) e **`mypy`** (checagem estática de tipos) em [`src/api/`](../src/api/) e [`tests/`](../tests/).
  * **Observabilidade e *Drift Monitoring*:** **Evidently AI + Prometheus/Grafana** (ou métricas estruturadas no **AWS CloudWatch**) registrando distribuição das requisições recebidas por `/predict` para detectar **Data Drift** (mudança do perfil socioeconômico de entrada), **Prediction Drift** e latência P95/P99.

---

## 3. Decisão Arquitetural Definida (`Opção A + Cenário 1` — 18/11/2026)

Para elevar o rigor de produção perante a banca do MBA — eliminando a dependência do `SQLite` local e incorporando versionamento de dados, IaC e observabilidade — foi definida a adoção da **Opção A (Arquitetura Desacoplada por Planos)** combinada ao **Cenário 1 (Observabilidade containerizada com `Prometheus + Grafana`)**.

### 3.1 Enquadramento Conceitual Correto (Por que *não* chamar de *Hybrid Cloud*)
* **Critério rigoroso (NIST):** *Hybrid Cloud* exige a integração orquestrada entre uma **Nuvem Privada corporativa** (*datacenter on-premises*) e uma **Nuvem Pública**. Uma estação de trabalho pessoal (WSL2 + Docker Compose) não configura Nuvem Privada.
* **Classificação técnica adotada — Arquitetura Desacoplada por Planos (*Decoupled Training & Serving Planes* / *Local-to-Cloud MLOps*):**
  1. **Plano Offline / Governança (Workstation Containerizada + Storage em Nuvem):** `PostgreSQL` + `MLflow Tracking Server` + `DVC` executam em containers sob demanda durante os experimentos e treinamentos, persistindo os dados `.parquet` e os artefatos de modelos diretamente no **Amazon S3** (eliminando `sqlite:///mlflow.db` e `./mlruns` locais).
  2. **Plano Online / *Serving* em Produção (Nuvem Pública AWS via Terraform):** **Amazon S3**, **Amazon ECR**, **IAM/OIDC** e **AWS ECS Express Mode** são provisionados via **Terraform (`infra/`)** com chave FinOps `create_ecs = true/false`. A API FastAPI em produção opera de forma **100% independente** da estação local.
  3. **Plano de Observabilidade (Cenário 1 — `Prometheus + Grafana` via `docker-compose`):** a API FastAPI expõe `/metrics` (em ambiente local e em produção no **ECS Express Mode**), sendo monitorada por containers **Prometheus + Grafana** para validação em *staging* local e *scrape* remoto via HTTPS durante demonstração ao vivo.
     * *Limitação transparente para a banca:* como o Prometheus local coleta métricas apenas enquanto a estação está ativa, em produção corporativa contínua (24/7) a coleta migraria para **Amazon Managed Service for Prometheus (AMP) + Amazon Managed Grafana (AMG)** ou instância dedicada na VPC da AWS.

### 3.2 Impacto Exato nos Notebooks e no Repositório

| Componente | Precisa alterar? | Escopo exato da alteração planejada |
| :--- | :---: | :--- |
| [`notebooks/01_investigacao_estrutural.ipynb`](../notebooks/01_investigacao_estrutural.ipynb) | **Não** | Nenhuma alteração. |
| [`notebooks/02_eda.ipynb`](../notebooks/02_eda.ipynb) | **Não (código)** | Código intacto; apenas eventual nota sobre versionamento da saída Silver via CLI do **DVC**. |
| [`notebooks/03_engenharia_features.ipynb`](../notebooks/03_engenharia_features.ipynb) | **Não** | Nenhuma alteração. |
| [`notebooks/04_varredura_semantica.ipynb`](../notebooks/04_varredura_semantica.ipynb) | **Não** | Nenhuma alteração. |
| [`notebooks/05_consolidacao_historica.ipynb`](../notebooks/05_consolidacao_historica.ipynb) | **Não (código)** | Código ETL intacto; `enem_2014_2023_consolidado.parquet` passa a ser rastreado via `dvc add` / `dvc push` para S3 (eventual ajuste apenas textual nas notas finais). |
| [`notebooks/06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb) | **Sim (único)** | Atualizar `Bloco 1.5` (Célula 2) para ler `MLFLOW_TRACKING_URI` remoto (PostgreSQL + S3) via variável de ambiente, atualizar o diagrama da Célula 3 / textos das células `0`, `1`, `18`, `19` e reexecutar o treino para registrar runs e modelo no servidor remoto. |
| **API & Testes (`src/api/`, `tests/`, `requirements-api.txt`)** | **Sim** | Instrumentar `/metrics` no FastAPI (`src/api/main.py`: latência, requisições, bloqueios `HTTP 422` anti-leakage e métricas de distribuição das predições `TARGET_M4`) e cobrir `/metrics` nos testes automatizados. |
| **Containerização & Observabilidade (`docker-compose.yml`, `monitoring/`)** | **Sim** | Orquestrar serviços `postgres`, `mlflow`, `prometheus` e `grafana` (com *scrape config* e dashboard JSON provisionado). |
| **IaC & Dados (`infra/`, `.dvc/`, `.github/workflows/deploy.yml`)** | **Sim** | Criar módulo **Terraform** (`S3`, `ECR`, `IAM/OIDC`, **ECS Express Mode**) com `create_ecs`/`destroy` FinOps, configurar remoto **DVC** no S3 e ajustar o job `deploy-aws` para `ecs:UpdateExpressGatewayService`. |

---

## 4. Roadmap de Execução e Evoluções Adicionais Pós-TCC

1. **Execução do Pacote Definido (`Opção A + Cenário 1`):**
   * **Fase 1 (Observabilidade na API):** instrumentar `/metrics` em [`src/api/main.py`](../src/api/main.py), atualizar testes e configurar `Prometheus + Grafana` no `docker-compose.yml`.
   * **Fase 2 (IaC & Dados em Nuvem):** criar módulo **Terraform** (`infra/`) para `S3 + ECR + IAM/OIDC + ECS Express Mode` e inicializar **DVC** apontando para o bucket S3.
   * **Fase 3 (MLflow Remoto e Reexecução):** subir `PostgreSQL + MLflow Tracking Server` apontando artefatos para o S3, ajustar [`notebooks/06_treinamento_modelo.ipynb`](../notebooks/06_treinamento_modelo.ipynb) e reexecutar o registro oficial dos experimentos e modelo campeão.
   * **Fase 4 (Qualidade CI):** adicionar `ruff` e `mypy` ao job `quality-gate-ci` em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).
2. **Evoluções Futuras Pós-TCC (Fora do Escopo Imediato):**
   * Substituir `Pandas` em chunks por **Polars** ou **DuckDB** na consolidação histórica caso haja reprocessamento de novas safras;
   * Avaliar **LightGBM** / **CatBoost** sob o mesmo protocolo de validação e Holdout;
   * Evoluir a observabilidade para **Evidently AI** + **Amazon Managed Service for Prometheus (AMP) / Amazon Managed Grafana (AMG)** para monitoramento 24/7 de *Data Drift* e *Prediction Drift* na AWS.
