variable "aws_region" {
  type        = string
  description = "AWS region for the deployment skeleton."
  default     = "us-west-2"
}

variable "repository_name" {
  type        = string
  description = "ECR repository name."
  default     = "ci-cd-release-risk-scanner"
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention period."
  default     = 14
}

