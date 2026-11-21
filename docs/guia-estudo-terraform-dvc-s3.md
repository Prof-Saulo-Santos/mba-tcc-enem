# 📘 Guia de Estudo e Slides — Terraform, Amazon S3, IAM OIDC & DVC (Fase 2)

**Projeto:** TCC MBA — Predição de Desempenho no ENEM (`TARGET_M4`) e Arquitetura MLOps  
**Autor:** Saulo Santos  
**Referência Visual (1920×1080):** [`media/infra_terraform_s3_dvc.png`](../media/infra_terraform_s3_dvc.png)  
**Objetivo deste Documento:** Consolidar os fundamentos de Infraestrutura como Código (IaC), segurança na AWS (OIDC), versionamento de dados em nuvem (DVC + S3) e FinOps implementados na **Fase 2**, servindo como guia de estudo, fonte de slides e preparo para sabatina.

---

## 1. Por Que Implementamos Isso? (Substituindo *ClickOps* e Isolamento Local)

Antes da Fase 2, o projeto já contava com o modelo treinado (`models/enem.pkl`), a API containerizada e observabilidade Prometheus/Grafana, mas apresentava duas lacunas importantes de engenharia em produção:

1. **Provisionamento manual (*ClickOps*):** o deploy em [.github/workflows/deploy.yml](../.github/workflows/deploy.yml) assumia que serviço AWS App Runner, permissões IAM e autenticação OIDC já tivessem sido criados manualmente no console web da AWS — algo difícil de auditar, reproduzir ou destruir com segurança pós-banca.
2. **Dados pesados sem linhagem remota:** os arquivos `.parquet` gerados nos Notebooks `02` e `05` (`26,8 MiB` + `153,2 MiB`) ficavam apenas localmente no disco (ignorados no `.gitignore`), sem histórico versionado em nuvem para reconstruir o ambiente em outra máquina.

Com a **Fase 2**, substituímos esses pontos por:
* **Terraform declarativo (`infra/`):** código versionado no Git que cria, atualiza e destrói toda a infraestrutura AWS de forma idempotente e auditável.
* **Amazon S3 único e estruturado:** bucket privado (`tcc-enem-saulo-mlops-703671922740`) com prefixos separados para **DVC (`dvc-store/`)** e para o futuro **MLflow remoto da Fase 3 (`mlflow-artifacts/`)**.
* **Versionamento DVC (`3.67.1`):** ponteiros leves `.dvc` (com hash MD5 e tamanho em bytes) versionados no Git apontando para os binários armazenados com segurança no Amazon S3.
* **Autenticação OIDC sem chaves estáticas:** role IAM dedicada para o GitHub Actions (`Prof-Saulo-Santos/mba-tcc-enem`, branch `main`), dispensando *Access Keys* fixas de longa duração.

---

## 2. Fundamentos Arquiteturais Para Defender na Banca

### 2.1 Infraestrutura como Código (IaC) Declarativa e Estado (`terraform.tfstate`)
* No Terraform (`Terraform v1.17.2`, provider `hashicorp/aws ~> 5.0`), você descreve **o estado desejado** nos arquivos `.tf` em vez de escrever scripts imperativos de passo a passo.
* Ao executar `terraform plan` e `terraform apply`, o Terraform compara o código `.tf` com o arquivo de estado (`infra/terraform.tfstate`) e com a API real da AWS, aplicando apenas a diferença (*diff*).
* **Por que o estado ficou local no TCC (e protegido no `.gitignore`)?** Em trabalho individual de TCC, manter `infra/terraform.tfstate` fora do Git evita o problema do *ovo e da galinha* (criar manualmente um segundo bucket S3 só para guardar o estado do Terraform). Em equipes corporativas, o padrão evolui para *Remote Backend* em S3 com *locking*.

### 2.2 Estratégia de Provisionamento em 2 Estágios (FinOps + Bootstrap ECR)
* **O problema técnico real (*Bootstrap*):** o **AWS App Runner** exige que já exista uma imagem Docker publicada no **Amazon ECR** no momento da criação do serviço; caso contrário, o `terraform apply` falha.
* **Nossa solução em [infra/variables.tf](../infra/variables.tf) (`create_apprunner`):**
  1. **Estágio 1 (`create_apprunner = false`, aplicado na Fase 2):** cria `S3 + ECR + IAM/OIDC` (`11` recursos), com **custo inferior a `\$0,01/dia`**, enquanto concluímos a Fase 3 (reexecução do Notebook 06) antes de publicar a imagem final.
  2. **Estágio 2 (`create_apprunner = true`, na entrega/banca):** após enviar a imagem Docker da API para o ECR (via GitHub Actions ou `docker push`), alteramos a flag para `true` e rodamos `terraform apply`, subindo o serviço HTTPS do App Runner (`~ \$0,40/dia` ou `~ \$0,12` por janela de apresentação).
  3. **Teardown pós-banca (`terraform destroy`):** como habilitamos `force_destroy = true` no bucket S3 e `force_delete = true` no ECR, um único comando remove 100% dos recursos sem travar por objetos/imagens residuais.

### 2.3 Por Que `models/enem.pkl` Continua no Git e Apenas os `.parquet` Foram ao DVC?
* O modelo final [`models/enem.pkl`](../models/enem.pkl) pesa apenas **`1,727 MB`** e é lido diretamente durante o `quality-gate-ci` e o `docker-smoke-test` em [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).
* Mantê-lo no Git permite que **qualquer Pull Request ou push rode testes e build Docker gratuitos no GitHub Actions sem precisar de credenciais AWS** para fazer `dvc pull`.
* Já os datasets intermediários e consolidados em `data/processed/` somam **`~180 MiB`** (`26,8 MiB` + `153,2 MiB`), ultrapassando boas práticas de armazenamento em Git — por isso são gerenciados exclusivamente pelo **DVC + Amazon S3**.

---

## 3. Inventário Real do Que Foi Provisionado e Versionado

### 3.1 Recursos Criados na AWS (`us-east-1`, Conta `703671922740`) — `11` Recursos

| Camada | Recurso Terraform | Identificador / Configuração Real | Papel FinOps / Segurança |
| :--- | :--- | :--- | :--- |
| **Storage S3** | `aws_s3_bucket` + `versioning` + `encryption` + `public_access_block` | `tcc-enem-saulo-mlops-703671922740` | `AES256`, versionamento ativo, 4 travas contra acesso público, `force_destroy = true`. |
| **Registry ECR** | `aws_ecr_repository` + `aws_ecr_lifecycle_policy` | `enem-target-m4-api` | *Scan on push* contra vulnerabilidades + retenção máxima de **`5` imagens** (FinOps). |
| **OIDC GitHub** | `aws_iam_openid_connect_provider` | `token.actions.githubusercontent.com` | Federação segura sem chaves IAM estáticas. |
| **IAM CI/CD** | `aws_iam_role` + `aws_iam_role_policy` | `tcc-enem-saulo-mlops-github-actions` | *Trust policy* restrita a `repo:Prof-Saulo-Santos/mba-tcc-enem:ref:refs/heads/main`; acesso apenas a ECR e App Runner do projeto. |
| **IAM Serving** | `aws_iam_role` + `aws_iam_role_policy_attachment` | `tcc-enem-saulo-mlops-apprunner-ecr` | Anexa `AWSAppRunnerServicePolicyForECRAccess` para o App Runner puxar imagens do ECR. |

*(Além do recurso condicional `aws_apprunner_service.api` com `count = var.create_apprunner ? 1 : 0`, que permanece desligado no Estágio 1.)*

### 3.2 Datasets Rastreados no DVC e Confirmados no S3

Configuração registrada em [`.dvc/config`](../.dvc/config) (`remote = s3remote`, `url = s3://tcc-enem-saulo-mlops-703671922740/dvc-store`, `region = us-east-1`):

| Dataset | Ponteiro Git (`.dvc`) | Tamanho no S3 | Hash MD5 / Caminho Real no Bucket S3 |
| :--- | :--- | :---: | :--- |
| Silver (EDA 2023 — `212.386 × 53`) | [`enem_2023_eda_purificado.parquet.dvc`](../data/processed/enem_2023_eda_purificado.parquet.dvc) | `26.8 MiB` (`28.136.523` B) | `dvc-store/files/md5/1e/853180cf7167d2bb652a534d43b736` |
| Gold (Década `2014–2023` — `37.593.629 × 8`) | [`enem_2014_2023_consolidado.parquet.dvc`](../data/processed/enem_2014_2023_consolidado.parquet.dvc) | `153.2 MiB` (`160.608.216` B) | `dvc-store/files/md5/84/1dfd3ad2e151882706e3681edae07e` |

### 3.3 Análise de Custos FinOps (`us-east-1`, sem *Free Tier*)
* **Estágio 1 ativo (`S3 + ECR vazio + IAM`):** `~0,18 GB × \$0,023/GB-mês ≈ \$0,004/mês` (**`< \$0,01/dia`**).
* **Após `docker push` (~`0,515 GB` no ECR) + artefatos MLflow:** **~ `\$0,002 / dia`** (`~ \$0,06 / mês`).
* **Estágio 2 (`create_apprunner = true`, `1 vCPU / 2 GB`):** `\$0,336/dia` em espera + `\$0,064/vCPU-hora` ativa (**`~ \$0,40/dia`** ou `~ \$0,12` em janela de apresentação de 4h).

---

## 4. Comandos Operacionais do Dia a Dia

```bash
# 1. Reconstruir os datasets Parquet em outra máquina usando DVC + S3
.venv/bin/dvc pull

# 2. Conferir outputs e estado atual da infraestrutura Terraform
terraform -chdir=infra output
terraform -chdir=infra plan

# 3. Ativar o App Runner no Estágio 2 (após existir imagem publicada no ECR)
terraform -chdir=infra apply -var="create_apprunner=true"

# 4. Configurar o Secret no GitHub Actions para deploy OIDC sem Access Keys:
# GitHub -> Settings -> Secrets and variables -> Actions -> New repository secret:
#   AWS_ROLE_TO_ASSUME = arn:aws:iam::703671922740:role/tcc-enem-saulo-mlops-github-actions
#   AWS_APPRUNNER_SERVICE_ARN = <output apprunner_service_arn após Estágio 2>

# 5. Teardown FinOps pós-banca (custo zero)
terraform -chdir=infra destroy
```

---

## 5. Roteiro Pronto de Slides & Sabatina da Fase 2

### Slide Sugerido — Infraestrutura Declarativa (Terraform), S3 & DVC
* **Visual principal:** [`media/infra_terraform_s3_dvc.png`](../media/infra_terraform_s3_dvc.png) (`1920×1080`).
* **Tópicos na tela:**
  * **Zero *ClickOps* (`infra/`):** `11` recursos AWS provisionados declarativamente com `default_tags`, bucket criptografado (`AES256`) e ECR com retenção FinOps de `5` imagens.
  * **Segurança OIDC:** GitHub Actions autentica com tokens temporários restritos a `Prof-Saulo-Santos/mba-tcc-enem` (`main`).
  * **Separação Git vs. DVC:** ponteiros `.dvc` (MD5) no Git e `180 MiB` de Parquets versionados no Amazon S3.
  * **Bootstrap em 2 Estágios:** `create_apprunner = false` mantém o custo em **`< \$0,01/dia`** até a publicação da imagem final na Fase 3.
* **Nota de fala (~1 min):** *"Para eliminar criação manual de recursos na AWS e garantir linhagem dos nossos 37,59 milhões de registros consolidados, estruturamos toda a nuvem em Terraform e versionamos os Parquets Silver e Gold com DVC sobre Amazon S3. Adotamos uma estratégia FinOps em dois estágios: primeiro provisionamos storage, registry e OIDC sem chaves fixas por menos de um centavo por dia, deixando o App Runner parametrizado para subir apenas após o modelo final da Fase 3."*

### Perguntas Prováveis da Banca
1. **"Por que usar OIDC em vez de criar um usuário IAM com `AWS_ACCESS_KEY_ID`?"**
   * *Resposta:* Chaves fixas podem vazar e não expiram sozinhas. Com OIDC, o GitHub Actions solicita à AWS um token efêmero válido apenas para aquele workflow e restrito à branch `main` do nosso repositório.
2. **"Como você evita versionar gigabytes no Git sem quebrar o pipeline de CI?"**
   * *Resposta:* Os datasets `.parquet` (`~180 MiB`) ficam no S3 rastreados por ponteiros `.dvc`, enquanto `models/enem.pkl` (`1,73 MB`) permanece no Git para que os testes e o *Docker Smoke Test* em Pull Requests rodem com zero dependência de credenciais AWS.
3. **"Por que `create_apprunner` começa como `false`?"**
   * *Resposta:* Por duas razões técnicas e de FinOps: o AWS App Runner exige uma imagem já existente no ECR para concluir a criação sem erro de *bootstrap*, e mantê-lo desligado enquanto finalizamos o MLflow remoto evita cobrança de compute ocioso.
