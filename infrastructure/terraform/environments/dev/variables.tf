# Development Environment Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The default GCP region"
  type        = string
  default     = "asia-northeast1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "homework-coach"
}

# Optional overrides
variable "backend_min_instances" {
  description = "Minimum instances for backend (dev default: 0)"
  type        = number
  default     = 0
}

variable "frontend_min_instances" {
  description = "Minimum instances for frontend (dev default: 0)"
  type        = number
  default     = 0
}

# NOTE: Redis variables removed - session management handled by Vertex AI / ADK

variable "github_owner" {
  description = "GitHub repository owner for Workload Identity Federation"
  type        = string
  default     = "arakitakashi"
}

variable "github_repo" {
  description = "GitHub repository name for Workload Identity Federation"
  type        = string
  default     = "homework-coach-robo"
}

variable "enable_cdn" {
  description = "Enable Cloud CDN (dev default: false)"
  type        = bool
  default     = false
}
