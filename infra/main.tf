data "aws_caller_identity" "current" {}

locals {
  account_id  = data.aws_caller_identity.current.account_id
  bucket_name = "${var.project_name}-${local.account_id}"
  github_oidc_arn = (
    var.create_github_oidc_provider
    ? aws_iam_openid_connect_provider.github[0].arn
    : var.existing_github_oidc_provider_arn
  )
  scheduler_enabled = var.create_apprunner && var.enable_apprunner_schedule
  apprunner_schedules = local.scheduler_enabled ? {
    resume_weekdays = {
      action      = "resumeService"
      cron        = "cron(0 9 ? * MON-FRI *)"
      description = "Disponibiliza o AWS App Runner de segunda a sexta-feira as 09:00"
    }
    pause_weekdays = {
      action      = "pauseService"
      cron        = "cron(0 17 ? * MON-FRI *)"
      description = "Pausa o AWS App Runner de segunda a sexta-feira as 17:00 (custo compute zero)"
    }
    resume_saturday = {
      action      = "resumeService"
      cron        = "cron(0 16 ? * SAT *)"
      description = "Disponibiliza o AWS App Runner aos sabados as 16:00"
    }
    pause_saturday = {
      action      = "pauseService"
      cron        = "cron(0 19 ? * SAT *)"
      description = "Pausa o AWS App Runner aos sabados as 19:00 (custo compute zero ate segunda 09:00)"
    }
  } : {}
}

# ==============================================================================
# 1. AMAZON S3 — Armazenamento unificado para DVC (dvc-store/) e MLflow (mlflow-artifacts/)
# ==============================================================================
resource "aws_s3_bucket" "mlops_storage" {
  bucket        = local.bucket_name
  force_destroy = true # Permite teardown completo via terraform destroy pós-banca
}

resource "aws_s3_bucket_versioning" "mlops_storage" {
  bucket = aws_s3_bucket.mlops_storage.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mlops_storage" {
  bucket = aws_s3_bucket.mlops_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "mlops_storage" {
  bucket = aws_s3_bucket.mlops_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ==============================================================================
# 2. AMAZON ECR — Registro privado de imagens Docker com limpeza automática FinOps
# ==============================================================================
resource "aws_ecr_repository" "api" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "api_finops" {
  repository = aws_ecr_repository.api.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Manter apenas as 5 imagens mais recentes para controle de custo FinOps"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 5
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ==============================================================================
# 3. IAM & OIDC — Autenticação temporária sem chaves estáticas para GitHub Actions
# ==============================================================================
resource "aws_iam_openid_connect_provider" "github" {
  count = var.create_github_oidc_provider ? 1 : 0

  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1", "1c58a3a8518e8759bf075b76b750d4f2df264fcd"]
}

data "aws_iam_policy_document" "github_actions_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [local.github_oidc_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "${var.project_name}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume.json
}

data "aws_iam_policy_document" "github_actions_permissions" {
  statement {
    sid       = "ECRAuthToken"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid    = "ECRPushPullRepository"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:CreateRepository",
      "ecr:DescribeRepositories",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:ListImages",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]
    resources = [aws_ecr_repository.api.arn]
  }

  statement {
    sid    = "AppRunnerDeployTrigger"
    effect = "Allow"
    actions = [
      "apprunner:DescribeService",
      "apprunner:StartDeployment"
    ]
    resources = ["arn:aws:apprunner:${var.aws_region}:${local.account_id}:service/${var.project_name}-api/*"]
  }
}

resource "aws_iam_role_policy" "github_actions" {
  name   = "${var.project_name}-cicd-policy"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_permissions.json
}

# ==============================================================================
# 4. AWS APP RUNNER — Plano Online de Serving (criado somente com imagem no ECR)
# ==============================================================================
data "aws_iam_policy_document" "apprunner_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["build.apprunner.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "apprunner_ecr_access" {
  name               = "${var.project_name}-apprunner-ecr"
  assume_role_policy = data.aws_iam_policy_document.apprunner_assume.json
}

resource "aws_iam_role_policy_attachment" "apprunner_ecr_access" {
  role       = aws_iam_role.apprunner_ecr_access.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

resource "aws_apprunner_service" "api" {
  count = var.create_apprunner ? 1 : 0

  service_name = "${var.project_name}-api"

  source_configuration {
    auto_deployments_enabled = false

    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr_access.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
      image_repository_type = "ECR"

      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          MODEL_PATH      = "/app/models/enem.pkl"
          MODEL_CARD_PATH = "/app/models/enem_model_card.json"
        }
      }
    }
  }

  instance_configuration {
    cpu    = var.apprunner_cpu
    memory = var.apprunner_memory
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }
}

# ==============================================================================
# 5. EVENTBRIDGE SCHEDULER — Janela FinOps do App Runner (Seg-Sex 9h-17h, Sab 16h-19h)
# ==============================================================================
resource "aws_scheduler_schedule_group" "apprunner" {
  count = local.scheduler_enabled ? 1 : 0

  name = "${var.project_name}-apprunner-window"
}

data "aws_iam_policy_document" "scheduler_assume" {
  count = local.scheduler_enabled ? 1 : 0

  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }
  }
}

resource "aws_iam_role" "scheduler_apprunner" {
  count = local.scheduler_enabled ? 1 : 0

  name               = "${var.project_name}-scheduler-apprunner"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume[0].json
}

data "aws_iam_policy_document" "scheduler_apprunner_permissions" {
  count = local.scheduler_enabled ? 1 : 0

  statement {
    sid    = "AppRunnerPauseResume"
    effect = "Allow"
    actions = [
      "apprunner:PauseService",
      "apprunner:ResumeService"
    ]
    resources = [aws_apprunner_service.api[0].arn]
  }
}

resource "aws_iam_role_policy" "scheduler_apprunner" {
  count = local.scheduler_enabled ? 1 : 0

  name   = "${var.project_name}-scheduler-apprunner-policy"
  role   = aws_iam_role.scheduler_apprunner[0].id
  policy = data.aws_iam_policy_document.scheduler_apprunner_permissions[0].json
}

resource "aws_scheduler_schedule" "apprunner_window" {
  for_each = local.apprunner_schedules

  name                         = "${var.project_name}-${replace(each.key, "_", "-")}"
  description                  = each.value.description
  group_name                   = aws_scheduler_schedule_group.apprunner[0].name
  schedule_expression          = each.value.cron
  schedule_expression_timezone = var.schedule_timezone
  state                        = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:apprunner:${each.value.action}"
    role_arn = aws_iam_role.scheduler_apprunner[0].arn
    input = jsonencode({
      ServiceArn = aws_apprunner_service.api[0].arn
    })

    retry_policy {
      maximum_event_age_in_seconds = 300
      maximum_retry_attempts       = 2
    }
  }
}
