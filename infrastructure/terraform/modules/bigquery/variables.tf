# BigQuery Module Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "location" {
  description = "The location for BigQuery dataset"
  type        = string
  default     = "asia-northeast1"
}

variable "dataset_id" {
  description = "The BigQuery dataset ID"
  type        = string
  default     = "homework_coach"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "backend_service_account_email" {
  description = "Email of the backend service account for dataset access"
  type        = string
}

# Phase 2 Feature Flags
variable "enable_phase2_tables" {
  description = "Enable Phase 2 BigQuery tables (agent_metrics, emotion_analysis, rag_metrics)"
  type        = bool
  default     = false
}
