# Cloud Run Module Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
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

# Service Account Variables
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

# VPC Variables
variable "vpc_connector_id" {
  description = "The ID of the VPC Access Connector"
  type        = string
}

# Backend Configuration
variable "backend_image" {
  description = "Docker image for backend (leave empty for placeholder)"
  type        = string
  default     = ""
}

variable "backend_cpu" {
  description = "CPU limit for backend"
  type        = string
  default     = "2"
}

variable "backend_memory" {
  description = "Memory limit for backend"
  type        = string
  default     = "1Gi"
}

variable "backend_min_instances" {
  description = "Minimum instances for backend"
  type        = number
  default     = 0
}

variable "backend_max_instances" {
  description = "Maximum instances for backend"
  type        = number
  default     = 20
}

variable "backend_timeout" {
  description = "Request timeout for backend (in seconds)"
  type        = number
  default     = 300
}

variable "backend_concurrency" {
  description = "Maximum concurrent requests per backend instance"
  type        = number
  default     = 100
}

variable "backend_secrets" {
  description = "Map of secret environment variables for backend"
  type = map(object({
    secret_id = string
    version   = string
  }))
  default = {}
}

variable "backend_url" {
  description = "Override backend URL for frontend (optional)"
  type        = string
  default     = ""
}

# Frontend Configuration
variable "frontend_image" {
  description = "Docker image for frontend (leave empty for placeholder)"
  type        = string
  default     = ""
}

variable "frontend_cpu" {
  description = "CPU limit for frontend"
  type        = string
  default     = "1"
}

variable "frontend_memory" {
  description = "Memory limit for frontend"
  type        = string
  default     = "512Mi"
}

variable "frontend_min_instances" {
  description = "Minimum instances for frontend"
  type        = number
  default     = 0
}

variable "frontend_max_instances" {
  description = "Maximum instances for frontend"
  type        = number
  default     = 10
}

variable "frontend_timeout" {
  description = "Request timeout for frontend (in seconds)"
  type        = number
  default     = 60
}

variable "frontend_concurrency" {
  description = "Maximum concurrent requests per frontend instance"
  type        = number
  default     = 80
}

# IAM Configuration
variable "allow_unauthenticated_backend" {
  description = "Allow unauthenticated access to backend (for development)"
  type        = bool
  default     = true
}
