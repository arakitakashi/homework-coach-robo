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

# =============================================================================
# Phase 2 Feature Flags
# =============================================================================

variable "enable_phase2_tools" {
  description = "Enable Phase 2a: ADK tools infrastructure"
  type        = bool
  default     = false
}

variable "enable_phase2_multi_agent" {
  description = "Enable Phase 2b: Multi-agent infrastructure"
  type        = bool
  default     = false
}

variable "enable_phase2_rag" {
  description = "Enable Phase 2c: RAG infrastructure (Discovery Engine, indexes, tables)"
  type        = bool
  default     = false
}

variable "enable_phase2_emotion" {
  description = "Enable Phase 2d: Emotion analysis infrastructure"
  type        = bool
  default     = false
}

variable "backend_memory" {
  description = "Memory limit for backend (Phase 2 may need more)"
  type        = string
  default     = "1Gi"
}

# =============================================================================
# Phase 3: Agent Engine Configuration
# =============================================================================

variable "enable_agent_engine" {
  description = "Enable Agent Engine deployment via Terraform"
  type        = bool
  default     = false
}

variable "gcp_location" {
  description = "GCP location for Agent Engine (default: us-central1)"
  type        = string
  default     = "us-central1"
}
