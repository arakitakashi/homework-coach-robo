# Firestore Module Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "location" {
  description = "The location for Firestore (multi-region or single region)"
  type        = string
  default     = "asia-northeast1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"
}

# Phase 2 Feature Flags
variable "enable_phase2_indexes" {
  description = "Enable Phase 2 Firestore composite indexes"
  type        = bool
  default     = false
}
