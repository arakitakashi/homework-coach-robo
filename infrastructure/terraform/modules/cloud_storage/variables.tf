# Cloud Storage Module Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "location" {
  description = "The location for the storage bucket"
  type        = string
  default     = "asia-northeast1"
}

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "homework-coach"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "backend_service_account_email" {
  description = "Email of the backend service account"
  type        = string
}

variable "frontend_service_account_email" {
  description = "Email of the frontend service account"
  type        = string
}

variable "cloud_build_service_account_email" {
  description = "Email of the Cloud Build service account"
  type        = string
}

variable "enable_public_access" {
  description = "Enable public read access to the bucket"
  type        = bool
  default     = true
}

variable "enable_cdn" {
  description = "Enable Cloud CDN for the bucket"
  type        = bool
  default     = false
}

variable "github_actions_service_account_email" {
  description = "Email of the GitHub Actions service account (for Agent Engine artifact uploads)"
  type        = string
  default     = ""
}

variable "cors_origins" {
  description = "List of allowed CORS origins"
  type        = list(string)
  default     = ["*"]
}
