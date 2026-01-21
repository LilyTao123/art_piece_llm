terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}


locals {
  envs = { for tuple in regexall("(.*)=(.*)", file(".env")) : tuple[0] => sensitive(tuple[1]) }
}

provider "aws" {
  region = var.region
  access_key = local.envs["access_key"]
  secret_key = local.envs["secret_key"]
}

resource "aws_s3_bucket" "mybucket" {
  bucket = var.s3_bucket
  force_destroy = true
  tags = {
    Name        = "My bucket"
  }
}

resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket                  = aws_s3_bucket.mybucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "artwork_table" {
  name         = var.dynamodb_table
  billing_mode = "PAY_PER_REQUEST"  # 小项目用按需，不用手动设置 capacity
  hash_key     = "Id"

  attribute {
    name = "Id"
    type = "S"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = true
  }

  tags = {
    Name        = "artwork-table"
    Environment = "production"
  }
}

resource "aws_dynamodb_table_item" "seq_item" {
  table_name = aws_dynamodb_table.artwork_table.name
  hash_key   = "Id"

  item = jsonencode({
    Id      = { S = "__SEQ__" }
    Current = { N = "0" }  # 注意这里是字符串 "0"，表示数字
  })
  depends_on = [aws_dynamodb_table.artwork_table]
}
