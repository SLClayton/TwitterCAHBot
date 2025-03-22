variable "PROJECT_NAME" {
  description = "project_name"
  type        = string
  default     = "CAH"
}

//
// LAMBDA
//

resource "aws_iam_role" "lambda_iam_role" {
  name = "${var.PROJECT_NAME}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Effect = "Allow",
        Sid = ""
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.PROJECT_NAME}-lambda-policy"
  description = "Policy for ${var.PROJECT_NAME} lambda"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:GetItem"
        ]
        Effect   = "Allow",
        Resource = "arn:aws:dynamodb:us-east-1:542157534763:table/CAH_combo_history"
      },
      {
        Action   = "secretsmanager:GetSecretValue",
        Effect   = "Allow",
        Resource = "arn:aws:secretsmanager:us-east-1:542157534763:secret:CAH_TWITTER_CREDENTIALS-IRGRfX"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_put_attachment" {
  policy_arn = aws_iam_policy.lambda_policy.arn
  role       = aws_iam_role.lambda_iam_role.name
}

resource "null_resource" "build_lambda" {
  triggers = {
    always_run = "${timestamp()}"
  }

  provisioner "local-exec" {
    command = "sh ../build_lambda.sh"
  }
}

data "archive_file" "lambda_package" {
  source_dir = "../temp_build_dir"
  output_path = "../packages/lambda_package.zip"
  type = "zip"

  depends_on = [null_resource.build_lambda]
}

resource "aws_lambda_function" "main_function" {
  filename          = data.archive_file.lambda_package.output_path
  function_name     = "${var.PROJECT_NAME}-tweeter"
  role              = aws_iam_role.lambda_iam_role.arn
  handler           = "lambda_function.lambda_handler"
  timeout           = 30
  source_code_hash  = data.archive_file.lambda_package.output_base64sha256
  runtime           = "python3.10"

  depends_on = [null_resource.build_lambda]
}

//
// Cloudwatch Event
//

resource "aws_cloudwatch_event_rule" "tweet_trigger" {
  name                = "${var.PROJECT_NAME}-tweet-trigger"
  description         = "Triggers the Lambda function every hour"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "update_lambda_target" {
  rule      = aws_cloudwatch_event_rule.tweet_trigger.name
  arn       = aws_lambda_function.main_function.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.tweet_trigger.arn
}
