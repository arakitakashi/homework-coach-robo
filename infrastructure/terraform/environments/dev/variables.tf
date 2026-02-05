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

variable "enable_cdn" {
  description = "Enable Cloud CDN (dev default: false)"
  type        = bool
  default     = false
}
