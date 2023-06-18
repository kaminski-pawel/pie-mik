variable "aws_region" {
  default     = "eu-west-1"
  description = "AWS region"
  type        = string
}

variable "aws_access_key" {
  description = "AWS Provider access key"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS Provider secret key"
  type        = string
  sensitive   = true
}

variable "aws_lambda_runtime" {
  default     = "python3.10"
  description = "AWS Lambda runtime"
  type        = string
}
