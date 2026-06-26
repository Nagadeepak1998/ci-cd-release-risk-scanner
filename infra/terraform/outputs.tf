output "repository_url" {
  value = aws_ecr_repository.release_risk_scanner.repository_url
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.release_risk_scanner.name
}

