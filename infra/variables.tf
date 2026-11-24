variable "aws_region" {
  description = "Região AWS para provisionamento de S3, ECR, IAM e App Runner"
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

variable "create_apprunner" {
  description = "Habilita a criação do serviço AWS App Runner (manter false até que exista uma imagem publicada no ECR)"
  type        = bool
  default     = false
}

variable "image_tag" {
  description = "Tag da imagem Docker no Amazon ECR consumida pelo AWS App Runner"
  type        = string
  default     = "latest"
}

variable "apprunner_cpu" {
  description = "Capacidade de vCPU do AWS App Runner (1024 = 1 vCPU)"
  type        = string
  default     = "1024"
}

variable "apprunner_memory" {
  description = "Memória RAM do AWS App Runner em MB (2048 = 2 GB)"
  type        = string
  default     = "2048"
}

variable "enable_apprunner_schedule" {
  description = "Ativa janela automática (EventBridge Scheduler) para pausar e retomar o AWS App Runner"
  type        = bool
  default     = true
}

variable "schedule_timezone" {
  description = "Fuso horário IANA utilizado nas expressões cron do EventBridge Scheduler"
  type        = string
  default     = "America/Sao_Paulo"
}
