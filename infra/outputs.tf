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

output "ecs_cluster_name" {
  description = "Nome do cluster Amazon ECS (disponível quando create_ecs = true)"
  value       = try(aws_ecs_cluster.api[0].name, null)
}

output "ecs_service_arn" {
  description = "ARN do serviço AWS ECS Express Mode (disponível quando create_ecs = true)"
  value       = try(aws_ecs_express_gateway_service.api[0].service_arn, null)
}

output "ecs_service_url" {
  description = "Endpoint HTTPS público do AWS ECS Express Mode (disponível quando create_ecs = true)"
  value = try(
    startswith(aws_ecs_express_gateway_service.api[0].ingress_paths[0].endpoint, "https://")
    ? aws_ecs_express_gateway_service.api[0].ingress_paths[0].endpoint
    : "https://${aws_ecs_express_gateway_service.api[0].ingress_paths[0].endpoint}",
    null
  )
}
