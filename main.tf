# main
provider "aws" {
  region     = "eu-west-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

# iam
resource "aws_iam_role" "lambda_B" {
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_B" {
  policy_arn = aws_iam_policy.lambda_B.arn
  role       = aws_iam_role.lambda_B.name
}

resource "aws_iam_policy" "lambda_B" {
  policy = data.aws_iam_policy_document.lambda_B.json
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/lambda_B"
  # name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 60
  lifecycle {
    prevent_destroy = false
  }
}

data "aws_iam_policy_document" "lambda_B" {
  statement {
    sid       = "AllowSQSPermissions"
    effect    = "Allow"
    resources = ["arn:aws:sqs:*"]

    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ReceiveMessage",
    ]
  }

  statement {
    sid       = "AllowInvokingLambdas"
    effect    = "Allow"
    resources = ["arn:aws:lambda:eu-west-1:*:function:*"]
    actions   = ["lambda:InvokeFunction"]
  }

  statement {
    sid       = "AllowCreatingLogGroups"
    effect    = "Allow"
    resources = ["arn:aws:logs:eu-west-1:*:*"]
    actions   = ["logs:CreateLogGroup"]
  }
  statement {
    sid       = "AllowWritingLogs"
    effect    = "Allow"
    resources = ["arn:aws:logs:eu-west-1:*:log-group:/aws/lambda/*:*"]

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
  }
}

# sqs
resource "aws_sqs_queue" "some_queue" {
  name = "SomeQueue"
}

# lambda
data "archive_file" "lambda_B" {
  type        = "zip"
  source_file = "${path.module}/lambda_B.py"
  output_path = "${path.module}/lambda_B.py.zip"
}

resource "aws_lambda_function" "lambda_B" {
  function_name = "lambda_B"
  handler       = "lambda_B.handler"
  role          = aws_iam_role.lambda_B.arn
  runtime       = "python3.10"
  depends_on    = [aws_cloudwatch_log_group.lambda_log_group]

  filename         = data.archive_file.lambda_B.output_path
  source_code_hash = data.archive_file.lambda_B.output_base64sha256

  timeout     = 30
  memory_size = 128
}

# event source mapping
resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.some_queue.arn
  enabled          = true
  function_name    = aws_lambda_function.lambda_B.arn
}

# outputs
output "sqs_url" {
  value = aws_sqs_queue.some_queue.id
}
