output "aws_region" {
  description = "Região AWS utilizada"
  value       = var.aws_region
}

output "s3_bucket_name" {
  description = "Bucket S3 criado para armazenar dados DVC e artefatos MLflow"
  value       = aws_s3_bucket.mlops_storage.bucket
}

output "dvc_remote_url" {
  description = "URL S3 configurada como remoto padrão do DVC"
  value       = "s3://${aws_s3_bucket.mlops_storage.bucket}/dvc-store"
}

output "mlflow_artifact_root" {
  description = "URI S3 preparada para --default-artifact-root na Fase 3 (MLflow remoto)"
  value       = "s3://${aws_s3_bucket.mlops_storage.bucket}/mlflow-artifacts"
}

output "ecr_repository_url" {
  description = "URL do repositório Amazon ECR para imagens Docker da API"
  value       = aws_ecr_repository.api.repository_url
}

output "github_actions_role_arn" {
  description = "ARN da IAM Role OIDC para configurar como Secret AWS_ROLE_TO_ASSUME no GitHub"
  value       = aws_iam_role.github_actions.arn
}

output "apprunner_service_arn" {
  description = "ARN do serviço AWS App Runner (disponível quando create_apprunner = true)"
  value       = try(aws_apprunner_service.api[0].arn, null)
}

output "apprunner_service_url" {
  description = "Endpoint HTTPS público do AWS App Runner (disponível quando create_apprunner = true)"
  value       = try("https://${aws_apprunner_service.api[0].service_url}", null)
}

output "apprunner_schedule_timezone" {
  description = "Fuso horário IANA configurado para disponibilidade do AWS App Runner"
  value       = local.scheduler_enabled ? var.schedule_timezone : null
}

output "apprunner_schedules" {
  description = "Expressões cron ativas no EventBridge Scheduler para o AWS App Runner"
  value = {
    for key, cfg in aws_scheduler_schedule.apprunner_window :
    key => cfg.schedule_expression
  }
}
