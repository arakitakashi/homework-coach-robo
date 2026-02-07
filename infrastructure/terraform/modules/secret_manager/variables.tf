# Secret Manager Module Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
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
  description = "Email of the backend service account for IAM bindings"
  type        = string
}

variable "frontend_service_account_email" {
  description = "Email of the frontend service account for IAM bindings"
  type        = string
}

variable "create_api_key_secret" {
  description = "Whether to create the API key secret"
  type        = bool
  default     = false
}

# Phase 2 Feature Flags
variable "create_gemini_api_key_secret" {
  description = "Whether to create the Gemini API key secret (Phase 2)"
  type        = bool
  default     = false
}
