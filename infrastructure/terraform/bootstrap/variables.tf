# Bootstrap Variables

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "asia-northeast1"
}

variable "state_bucket_name" {
  description = "Name of the GCS bucket for Terraform state"
  type        = string
  default     = "homework-coach-terraform-state"
}
