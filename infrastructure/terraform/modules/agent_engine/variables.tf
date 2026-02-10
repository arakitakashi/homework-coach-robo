# Agent Engine Module Variables

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Agent Engine"
  type        = string
  default     = "us-central1"
}

variable "display_name" {
  description = "Display name for the Agent Engine"
  type        = string
  default     = "homework-coach-router-agent"
}

variable "description" {
  description = "Description of the Agent Engine"
  type        = string
  default     = "宿題コーチロボット - Router Agent (Phase 3)"
}

variable "pickle_gcs_uri" {
  description = "GCS URI for the pickle file"
  type        = string
}

variable "requirements_gcs_uri" {
  description = "GCS URI for the requirements.txt file"
  type        = string
}

variable "dependencies_gcs_uri" {
  description = "GCS URI for the dependencies.tar.gz file"
  type        = string
}

variable "python_version" {
  description = "Python version for the Agent Engine"
  type        = string
  default     = "3.10"
}
