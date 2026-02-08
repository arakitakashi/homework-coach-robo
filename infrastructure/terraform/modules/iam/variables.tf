# IAM Module Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "homework-coach"
}

# Phase 2 Feature Flags
variable "enable_phase2_rag" {
  description = "Enable IAM roles for Phase 2c RAG (Discovery Engine)"
  type        = bool
  default     = false
}

variable "enable_phase2_storage_admin" {
  description = "Enable storage.objectAdmin role for RAG data upload"
  type        = bool
  default     = false
}
