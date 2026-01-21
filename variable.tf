variable "s3_bucket" {
  description = "value"
  default     = "artwork-info-app"
}

variable "region" {
  description = "Region"
  #Update the below to your desired region
  default = "us-east-1"
}

variable "dynamodb_table" {
  description = "Project Location"
  #Update the below to your desired location
  default = "ArtItems"
}
