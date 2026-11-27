# 📘 Guia de Estudo e Slides — Terraform, Amazon S3, IAM OIDC & DVC (Fase 2)

**Projeto:** TCC MBA — Predição de Desempenho no ENEM (`TARGET_M4`) e Arquitetura MLOps  
**Autor:** Saulo Santos  
**Referência Visual (1920×1080):** [`media/infra_terraform_s3_dvc.png`](../media/infra_terraform_s3_dvc.png)  
**Objetivo deste Documento:** Consolidar os fundamentos de Infraestrutura como Código (IaC), segurança na AWS (OIDC), versionamento de dados em nuvem (DVC + S3) e FinOps implementados na **Fase 2** (e atualizados para o **AWS ECS Express Mode**), servindo como guia de estudo, fonte de slides e preparo para sabatina.

---

## 1. Por Que Implementamos Isso? (Substituindo *ClickOps* e Isolamento Local)

Antes da Fase 2, o projeto já contava com o modelo treinado (`models/enem.pkl`), a API containerizada e observabilidade Prometheus/Grafana, mas apresentava duas lacunas importantes de engenharia em produção:

1. **Provisionamento manual (*ClickOps*):** o deploy em [.github/workflows/deploy.yml](../.github/workflows/deploy.yml) assumia que o serviço de *serving* na AWS, permissões IAM e autenticação OIDC já tivessem sido criados manualmente no console web da AWS — algo difícil de auditar, reproduzir ou destruir com segurança pós-banca.
2. **Dados pesados sem linhagem remota:** os arquivos `.parquet` gerados nos Notebooks `02` e `05` (`26,8 MiB` + `153,2 MiB`) ficavam apenas localmente no disco (ignorados no `.gitignore`), sem histórico versionado em nuvem para reconstruir o ambiente em outra máquina.

Com a **Fase 2** (e a migração posterior do plano online para **AWS ECS Express Mode**), substituímos esses pontos por:
* **Terraform declarativo (`infra/`):** código versionado no Git que cria, atualiza e destrói toda a infraestrutura AWS de forma idempotente e auditável.
* **Amazon S3 único e estruturado:** bucket privado (`tcc-enem-saulo-mlops-703671922740`) com prefixos separados para **DVC (`dvc-store/`)** e para o **MLflow remoto da Fase 3 (`mlflow-artifacts/`)**.
* **Versionamento DVC (`3.67.1`):** ponteiros leves `.dvc` (com hash MD5 e tamanho em bytes) versionados no Git apontando para os binários armazenados com segurança no Amazon S3.
* **Autenticação OIDC sem chaves estáticas:** role IAM dedicada para o GitHub Actions (`Prof-Saulo-Santos/mba-tcc-enem`, branch `main`), dispensando *Access Keys* fixas de longa duração.

---

## 2. Fundamentos Arquiteturais Para Defender na Banca

### 2.1 Infraestrutura como Código (IaC) Declarativa e Estado (`terraform.tfstate`)
* No Terraform (`required_version >= 1.6.0`, provider `hashicorp/aws >= 6.41.0, < 7.0.0`, travado em `v6.74.0` em [`infra/.terraform.lock.hcl`](../infra/.terraform.lock.hcl)), você descreve **o estado desejado** nos arquivos `.tf` em vez de escrever scripts imperativos de passo a passo.
* Ao executar `terraform plan` e `terraform apply`, o Terraform compara o código `.tf` com o arquivo de estado (`infra/terraform.tfstate`) e com a API real da AWS, aplicando apenas a diferença (*diff*).
* **Por que o estado ficou local no TCC (e protegido no `.gitignore`)?** Em trabalho individual de TCC, manter `infra/terraform.tfstate` fora do Git evita o problema do *ovo e da galinha* (criar manualmente um segundo bucket S3 só para guardar o estado do Terraform). Em equipes corporativas, o padrão evolui para *Remote Backend* em S3 com *locking*.

### 2.2 Estratégia de Provisionamento em 2 Estágios (ECS Express Mode + FinOps + Bootstrap ECR)
* **Por que AWS ECS Express Mode em vez de App Runner?** O plano inicial previa o AWS App Runner, porém a AWS descontinuou/restringiu a criação de novos serviços App Runner na conta (`InvalidRequestException: Account 703671922740 can't create new App Runner services`) e passou a recomendar o **AWS ECS Express Mode** (`aws_ecs_cluster` + `aws_ecs_express_gateway_service`), que executa a API em **AWS Fargate** com Application Load Balancer (ALB) gerenciado e URL HTTPS nativa.
* **O problema técnico real (*Bootstrap* + custo por hora):** o **ECS Express Mode** precisa de uma imagem Docker já publicada no **Amazon ECR** (`:latest`) para inicializar a task saudável no `/health` (`wait_for_steady_state = true`) e mantém custo contínuo por hora (Fargate + ALB) enquanto estiver ligado.
* **Nossa solução em [infra/variables.tf](../infra/variables.tf) (`create_ecs`):**
  1. **Estágio 1 (`create_ecs = false`, padrão entre testes):** cria apenas `S3 + ECR + IAM/OIDC + roles do ECS` (**`13` recursos**), com custo residual inferior a **`$0,01/dia`**, enquanto mantemos apenas dados, artefatos MLflow e imagens armazenados.
  2. **Estágio 2 (`create_ecs = true`, sob demanda para testes e banca):** após enviar a imagem Docker da API para o ECR (via `docker push` ou GitHub Actions), ativamos `-var="create_ecs=true"`, subindo o cluster `tcc-enem-saulo-mlops-cluster` e o serviço `tcc-enem-saulo-mlops-api` (`1024` CPU / `2048` MiB RAM, auto-scaling `1..2` tasks) com endpoint HTTPS público (`ecs_service_url`).
  3. **Desligamento rápido vs. *Teardown* definitivo pós-banca:** fora das janelas de teste/apresentação, `-var="create_ecs=false"` desliga **apenas** o cluster ECS e o ALB (zerando computação sem apagar S3 nem ECR). Ao final definitivo pós-banca, `terraform -chdir=infra destroy` remove 100% dos recursos (graças a `force_destroy = true` no S3 e `force_delete = true` no ECR).

### 2.3 Por Que `models/enem.pkl` Continua no Git e Apenas os `.parquet` Foram ao DVC?
* O modelo final [`models/enem.pkl`](../models/enem.pkl) pesa apenas **`1,727 MB`** e é lido diretamente durante o `quality-gate-ci` e o `docker-smoke-test` em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).
* Mantê-lo no Git permite que **qualquer Pull Request ou push rode testes e build Docker gratuitos no GitHub Actions sem precisar de credenciais AWS** para fazer `dvc pull`.
* Já os datasets intermediários e consolidados em `data/processed/` somam **`~180 MiB`** (`26,8 MiB` + `153,2 MiB`), ultrapassando boas práticas de armazenamento em Git — por isso são gerenciados exclusivamente pelo **DVC + Amazon S3**.

---

## 3. Inventário Real do Que Foi Provisionado e Versionado

### 3.1 Recursos Criados na AWS (`us-east-1`, Conta `703671922740`) — `13` Base + `2` Sob Demanda

| Camada | Recurso Terraform | Identificador / Configuração Real | Papel FinOps / Segurança |
| :--- | :--- | :--- | :--- |
| **Storage S3** | `aws_s3_bucket` + `versioning` + `encryption` + `public_access_block` | `tcc-enem-saulo-mlops-703671922740` | `AES256`, versionamento ativo, 4 travas contra acesso público, `force_destroy = true`. |
| **Registry ECR** | `aws_ecr_repository` + `aws_ecr_lifecycle_policy` | `enem-target-m4-api` | *Scan on push* contra vulnerabilidades + retenção máxima de **`5` imagens** (FinOps). |
| **OIDC GitHub** | `aws_iam_openid_connect_provider` | `token.actions.githubusercontent.com` | Federação segura sem chaves IAM estáticas (`count = var.create_github_oidc_provider ? 1 : 0`). |
| **IAM CI/CD** | `aws_iam_role` + `aws_iam_role_policy` | `tcc-enem-saulo-mlops-github-actions` | *Trust policy* restrita a `repo:Prof-Saulo-Santos/mba-tcc-enem:ref:refs/heads/main`; acesso restrito a ECR, `ecs:*ExpressGatewayService` e `iam:PassRole` para as roles do ECS. |
| **IAM ECS Tasks** | `aws_iam_role` + `aws_iam_role_policy_attachment` | `tcc-enem-saulo-mlops-ecs-execution` | Assume `ecs-tasks.amazonaws.com` e anexa `AmazonECSTaskExecutionRolePolicy` para baixar imagens do ECR e gravar logs. |
| **IAM ECS Infra** | `aws_iam_role` + `aws_iam_role_policy_attachment` | `tcc-enem-saulo-mlops-ecs-infrastructure` | Assume `ecs.amazonaws.com` e anexa `AmazonECSInfrastructureRoleforExpressGatewayServices` para gerenciar ALB e rede no Express Mode. |

*(Além dos `2` recursos condicionais do plano online controlados por `count = var.create_ecs ? 1 : 0`: `aws_ecs_cluster.api` [`tcc-enem-saulo-mlops-cluster`] e `aws_ecs_express_gateway_service.api` [`tcc-enem-saulo-mlops-api`, `1024` CPU / `2048` MiB, porta `8000`, `/health`, auto-scaling `1..2` tasks por CPU `70%`], que permanecem desligados no Estágio 1.)*

### 3.2 Datasets Rastreados no DVC e Confirmados no S3

Configuração registrada em [`.dvc/config`](../.dvc/config) (`remote = s3remote`, `url = s3://tcc-enem-saulo-mlops-703671922740/dvc-store`, `region = us-east-1`):

| Dataset | Ponteiro Git (`.dvc`) | Tamanho no S3 | Hash MD5 / Caminho Real no Bucket S3 |
| :--- | :--- | :---: | :--- |
| Silver (EDA 2023 — `212.386 × 53`) | [`enem_2023_eda_purificado.parquet.dvc`](../data/processed/enem_2023_eda_purificado.parquet.dvc) | `26.8 MiB` (`28.136.523` B) | `dvc-store/files/md5/1e/853180cf7167d2bb652a534d43b736` |
| Gold (Década `2014–2023` — `37.593.629 × 8`) | [`enem_2014_2023_consolidado.parquet.dvc`](../data/processed/enem_2014_2023_consolidado.parquet.dvc) | `153.2 MiB` (`160.608.216` B) | `dvc-store/files/md5/84/1dfd3ad2e151882706e3681edae07e` |

### 3.3 Análise de Custos FinOps (`us-east-1`)
* **Estágio 1 ativo (`create_ecs = false` — S3 + ECR + IAM):** apenas armazenamento dos `.parquet` no DVC (`~180 MiB`), artefatos MLflow (`~2,49 MiB`) e imagem multi-stage no ECR (`515 MB` Content Size na imagem base, com retenção máxima de `5` imagens) — custo residual **`< $0,01/dia`** (ordem de centavos por mês).
* **Estágio 2 ativo (`create_ecs = true` — AWS ECS Express Mode):** enquanto ligado, há cobrança por hora referente à task **AWS Fargate (`1024` vCPU / `2048` MiB)** e ao **Application Load Balancer (ALB)** gerenciado pelo Express Mode. Por isso desligamos o serviço entre testes com `create_ecs = false`, mantendo apenas S3 e ECR intactos.

---

## 4. Comandos Operacionais do Dia a Dia

```bash
# 1. Reconstruir os datasets Parquet em outra máquina usando DVC + S3
.venv/bin/dvc pull

# 2. Conferir outputs e estado atual da infraestrutura Terraform
terraform -chdir=infra output
terraform -chdir=infra plan

# 3. Ligar o AWS ECS Express Mode no Estágio 2 (após existir imagem :latest no ECR)
terraform -chdir=infra apply -var="create_ecs=true"
terraform -chdir=infra output ecs_service_url

# 4. Desligar apenas o ECS Express Mode + ALB após os testes (mantém S3 e ECR intactos!)
terraform -chdir=infra apply -var="create_ecs=false"

# 5. Configurar os Secrets no GitHub Actions para deploy OIDC sem Access Keys:
# GitHub -> Settings -> Secrets and variables -> Actions -> New repository secret:
#   AWS_ROLE_TO_ASSUME  = arn:aws:iam::703671922740:role/tcc-enem-saulo-mlops-github-actions
#   AWS_ECS_SERVICE_ARN = <output ecs_service_arn obtido com create_ecs = true>

# 6. Teardown FinOps definitivo pós-banca (apaga 100%, inclusive S3 e ECR!)
terraform -chdir=infra destroy
```

---

## 5. Roteiro Pronto de Slides & Sabatina da Fase 2

### Slide Sugerido — Infraestrutura Declarativa (Terraform), S3 & DVC
* **Visual principal:** [`media/infra_terraform_s3_dvc.png`](../media/infra_terraform_s3_dvc.png) (`1920×1080`).
* **Tópicos na tela:**
  * **Zero *ClickOps* (`infra/`):** `13` recursos AWS permanentes (`+2` sob demanda no **ECS Express Mode**) provisionados declarativamente com `default_tags`, bucket criptografado (`AES256`) e ECR com retenção FinOps de `5` imagens.
  * **Segurança OIDC:** GitHub Actions autentica com tokens temporários restritos a `Prof-Saulo-Santos/mba-tcc-enem` (`main`).
  * **Separação Git vs. DVC:** ponteiros `.dvc` (MD5) no Git e `180 MiB` de Parquets versionados no Amazon S3.
  * **Bootstrap em 2 Estágios:** `create_ecs = false` mantém o custo residual em **`< $0,01/dia`**, ativando Fargate + ALB somente durante testes/banca.
* **Nota de fala (~1 min):** *"Para eliminar criação manual de recursos na AWS e garantir linhagem dos nossos 37,59 milhões de registros consolidados, estruturamos toda a nuvem em Terraform e versionamos os Parquets Silver e Gold com DVC sobre Amazon S3. Adotamos uma estratégia FinOps em dois estágios: mantemos storage, registry e OIDC sem chaves fixas por menos de um centavo por dia, deixando o AWS ECS Express Mode parametrizado via `create_ecs` para subir sob demanda apenas durante as demonstrações e desligar logo em seguida."*

### Perguntas Prováveis da Banca
1. **"Por que usar OIDC em vez de criar um usuário IAM com `AWS_ACCESS_KEY_ID`?"**
   * *Resposta:* Chaves fixas podem vazar e não expiram sozinhas. Com OIDC, o GitHub Actions solicita à AWS um token efêmero válido apenas para aquele workflow e restrito à branch `main` do nosso repositório.
2. **"Como você evita versionar gigabytes no Git sem quebrar o pipeline de CI?"**
   * *Resposta:* Os datasets `.parquet` (`~180 MiB`) ficam no S3 rastreados por ponteiros `.dvc`, enquanto `models/enem.pkl` (`1,73 MB`) permanece no Git para que os testes e o *Docker Smoke Test* em Pull Requests rodem com zero dependência de credenciais AWS.
3. **"Por que `create_ecs` começa como `false` (e por que ECS Express Mode em vez de App Runner)?"**
   * *Resposta:* Primeiro, porque a AWS descontinuou/restringiu a criação de novos serviços App Runner na conta (`InvalidRequestException`), motivando a migração para o **AWS ECS Express Mode** (`aws_ecs_cluster` + `aws_ecs_express_gateway_service`, com Fargate e ALB gerenciado). Segundo, manter `create_ecs = false` por padrão resolve o *bootstrap* da imagem no ECR (que precisa existir antes do serviço subir saudável) e zera o custo contínuo por hora de Fargate + ALB fora das sessões de teste e da banca.
