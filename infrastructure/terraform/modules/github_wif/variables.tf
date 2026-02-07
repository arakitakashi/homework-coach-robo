# GitHub WIF Module Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "github_owner" {
  description = "GitHub repository owner (e.g. 'arakitakashi')"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name (e.g. 'homework-coach-robo')"
  type        = string
}
