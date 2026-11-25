variable "aws_region" {
  description = "Região AWS para provisionamento de S3, ECR, IAM e ECS Express Mode"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefixo padrão para nomeação dos recursos do projeto"
  type        = string
  default     = "tcc-enem-saulo-mlops"
}

variable "ecr_repository_name" {
  description = "Nome do repositório no Amazon ECR (alinhado ao .github/workflows/deploy.yml)"
  type        = string
  default     = "enem-target-m4-api"
}

variable "github_repo" {
  description = "Repositório GitHub autorizado a assumir a role via OIDC (formato owner/repo)"
  type        = string
  default     = "Prof-Saulo-Santos/mba-tcc-enem"
}

variable "create_github_oidc_provider" {
  description = "Define se o provedor OIDC do GitHub deve ser criado (use false se a conta AWS já possuir um)"
  type        = bool
  default     = true
}

variable "existing_github_oidc_provider_arn" {
  description = "ARN de provedor OIDC do GitHub já existente na conta (usado apenas se create_github_oidc_provider = false)"
  type        = string
  default     = ""
}

variable "create_ecs" {
  description = "Habilita a criação do serviço AWS ECS Express Mode (manter false quando não estiver em teste/banca para custo zero de compute/ALB)"
  type        = bool
  default     = false
}

variable "image_tag" {
  description = "Tag da imagem Docker no Amazon ECR consumida pelo AWS ECS Express Mode"
  type        = string
  default     = "latest"
}

variable "ecs_cpu" {
  description = "Unidades de vCPU da task Fargate no ECS Express Mode (256, 512, 1024 = 1 vCPU)"
  type        = string
  default     = "1024"
}

variable "ecs_memory" {
  description = "Memória RAM da task Fargate em MiB no ECS Express Mode (512, 1024, 2048 = 2 GB)"
  type        = string
  default     = "2048"
}
