# 🔭 Estudos Futuros e Arquitetura Comparada (Evoluções de Engenharia e MLOps)

**Projeto de TCC — MBA em Ciência de Dados & MLOps**  
**Autor:** Saulo Santos  
**Objetivo deste Documento:** Consolidar alternativas tecnológicas aplicáveis a cada camada do projeto, analisando *trade-offs*, justificativas arquiteturais para a banca examinadora e possíveis evoluções futuras (com destaque para **Terraform / Infraestrutura como Código**).

---

## 1. O Papel do Terraform (Infraestrutura como Código — IaC) na Etapa 2

### 1.1 Onde o Terraform se encaixa no estado atual do projeto
Ao analisar o workflow de CI/CD em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml), observa-se uma fronteira clara entre automação de entrega (CI/CD) e provisionamento de infraestrutura:

* A esteira atual automatiza o *Quality Gate* (`SHA-256` + `pytest`), o *Docker Smoke Test* E2E, a criação/uso do repositório **Amazon ECR** via AWS CLI (`aws ecr create-repository`), o *push* da imagem e o disparo de atualização no **AWS App Runner** (`aws apprunner start-deployment`).
* Contudo, o pipeline pressupõe que recursos fundacionais já existam previamente na conta AWS — especificamente o serviço do **AWS App Runner (`AWS_APPRUNNER_SERVICE_ARN`)**, as **IAM Roles** de leitura no ECR e a configuração de autenticação **OIDC** entre GitHub Actions e AWS. Caso criados manualmente no console (*ClickOps*), esses recursos não ficam versionados em código.

Com o **Terraform** (por exemplo, em um diretório `infra/` contendo `main.tf`, `variables.tf` e `outputs.tf`), toda essa infraestrutura passaria a ser declarada em **HCL (*HashiCorp Configuration Language*)**:

1. `aws_ecr_repository` + política de ciclo de vida (*lifecycle policy* para expirar imagens antigas e reduzir custo de armazenamento).
2. Provedor OIDC e `aws_iam_role` com privilégios mínimos (*Least Privilege*) para o GitHub Actions e para o App Runner.
3. `aws_apprunner_service` (definição declarativa de vCPU, memória RAM, porta `8000`, endpoint `/health` e limites de *autoscaling*).
4. Alertas básicos de observabilidade e orçamento FinOps (CloudWatch Logs / AWS Budgets).

### 1.2 Análise de Prós e Contras para o TCC

| Prós do uso de Terraform | Contras / Riscos no contexto atual do TCC |
| :--- | :--- |
| **FinOps determinístico (`apply` / `destroy`):** permite provisionar toda a nuvem minutos antes da defesa com `terraform apply` e remover 100% dos recursos imediatamente após a banca com `terraform destroy`, evitando cobranças residuais. | **Sobrecarga de escopo:** as Etapas 1 e 2 já estão 100% implementadas, testadas (`25/25`) e documentadas; adicionar Terraform exige conta AWS ativa, testes reais de provisionamento e gestão segura de estado (`terraform.tfstate`). |
| **Eliminação de *ClickOps*:** garante que a infraestrutura da API em nuvem seja reproduzível do zero por qualquer avaliador ou membro de equipe. | **Foco da avaliação acadêmica:** o núcleo científico e de MLOps do trabalho (consolidação de `37,59M` registros, modelagem/explicabilidade e produtização em container + CI/CD) já está resolvido sem depender de IaC completa. |
| **Diferencial de maturidade DevOps/MLOps:** reforça governança, rastreabilidade de mudanças de infraestrutura em *Pull Requests* e paridade entre ambientes (`staging` vs. `prod`). | **Cuidados de segurança:** exige atenção extra para não versionar arquivos de estado (`.tfstate`) ou credenciais no repositório Git. |

### 1.3 Posicionamento Recomendado
* **Para o fechamento atual do TCC:** manter a arquitetura enxuta existente e posicionar o **Terraform (IaC)** como evolução natural no capítulo de **Trabalhos Futuros** (ou na subseção de limitações operacionais de *ClickOps*).
* **Em caso de evolução futura / demonstração ao vivo recorrente na AWS:** criar um módulo mínimo em `infra/` para automatizar `ECR + IAM OIDC + App Runner` e garantir criação/destruição reprodutível em 1 comando.

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
* **Implementação atual:** API **FastAPI** + **Pydantic v2** (`extra="forbid"`), empacotada em **Docker *multi-stage*** (`515 MB` Content Size) com CI/CD via **GitHub Actions** mirando **Amazon ECR + AWS App Runner**.
* **Alternativas de empacotamento e runtime de inferência:**
  * **ONNX (`ONNX Runtime`):** converte o modelo treinado para formato interoperável independente da biblioteca de treino (`xgboost`/`scikit-learn`), otimizando latência de inferência.
  * **BentoML:** framework especializado em empacotamento de modelos de ML, facilitando *adaptive batching* e padronização de contêineres OCI para múltiplos modelos.
* **Alternativas de hospedagem na AWS:**
  * **AWS Lambda + API Gateway:** modelo *serverless* puro com cobrança estrita por requisição (*scale-to-zero* real), excelente para FinOps em tráfego esporádico, exigindo atenção ao *cold start* e ao limite de tamanho de imagem/camadas.
  * **Amazon ECS (Fargate) ou Amazon EKS (Kubernetes):** recomendados apenas se o sistema evoluir para dezenas de microserviços ou exigir políticas avançadas de rede/malha de serviço, evitando o *overengineering* para uma API única de `1,727 MB`.
  * **Amazon SageMaker Endpoints:** plataforma gerenciada fim-a-fim da AWS para ML, porém com custo fixo por hora consideravelmente superior ao App Runner para cargas acadêmicas ou de baixo tráfego.
* **Alternativas de qualidade de código e monitoramento em produção (pós-deploy):**
  * **Qualidade estática no CI (`quality-gate-ci`):** inclusão de **`ruff`** (*linter*/formatador) e **`mypy`** (checagem estática de tipos) em [`src/api/`](../src/api/) e [`tests/`](../tests/).
  * **Observabilidade e *Drift Monitoring*:** **Evidently AI + Prometheus/Grafana** (ou métricas estruturadas no **AWS CloudWatch**) registrando distribuição das requisições recebidas por `/predict` para detectar **Data Drift** (mudança do perfil socioeconômico de entrada), **Prediction Drift** e latência P95/P99.

---

## 3. Resumo de Prioridades Caso o Projeto Continue Após o TCC

1. **Curto prazo (Baixo esforço / Alto impacto de governança):** adicionar `ruff` e `mypy` ao job `quality-gate-ci` em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) e incluir módulo **Terraform** em `infra/` para automatizar criação e destruição do AWS App Runner + OIDC.
2. **Médio prazo (Performance de dados e reprodutibilidade):** adotar **DVC** (para rastrear `.parquet` e `.pkl` em S3) e avaliar **DuckDB** ou **Polars** na etapa de consolidação histórica.
3. **Longo prazo (Operação contínua em produção):** acoplar **MLflow remoto (PostgreSQL + S3)**, monitoramento de **Data Drift** via **Evidently AI** sobre logs de inferência e comparação controlada de **LightGBM / CatBoost** sob o mesmo protocolo de validação cruzada e Holdout.
