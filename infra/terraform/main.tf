provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "release_risk_scanner" {
  name                 = var.repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_cloudwatch_log_group" "release_risk_scanner" {
  name              = "/ecs/${var.repository_name}"
  retention_in_days = var.log_retention_days
}

