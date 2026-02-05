# Bootstrap Configuration
# Creates the Terraform state bucket and enables required GCP APIs.
# This configuration uses local state (no remote backend).
#
# Usage:
#   cd infrastructure/terraform/bootstrap
#   terraform init
#   terraform apply
#
# After successful apply, proceed to environments/dev for main infrastructure.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Local backend - state stored locally
  # This is intentional for bootstrap resources
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# =============================================================================
# Terraform State Bucket
# =============================================================================

resource "google_storage_bucket" "terraform_state" {
  name          = var.state_bucket_name
  project       = var.project_id
  location      = var.region
  storage_class = "STANDARD"
  force_destroy = false

  # Enable versioning for state file protection
  versioning {
    enabled = true
  }

  # Lifecycle rule to clean up old versions
  lifecycle_rule {
    condition {
      num_newer_versions = 5
      with_state         = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }

  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }

  # Uniform bucket-level access
  uniform_bucket_level_access = true

  labels = {
    purpose    = "terraform-state"
    managed_by = "terraform-bootstrap"
  }
}

# =============================================================================
# Enable Required GCP APIs
# =============================================================================

locals {
  required_apis = [
    "compute.googleapis.com",           # VPC, Firewall
    "run.googleapis.com",               # Cloud Run
    "artifactregistry.googleapis.com",  # Container Registry
    "firestore.googleapis.com",         # Firestore Database
    "bigquery.googleapis.com",          # BigQuery
    "redis.googleapis.com",             # Memorystore for Redis
    "secretmanager.googleapis.com",     # Secret Manager
    "cloudbuild.googleapis.com",        # Cloud Build
    "servicenetworking.googleapis.com", # VPC Peering for Redis
    "vpcaccess.googleapis.com",         # VPC Access Connector
    "iam.googleapis.com",               # IAM
    "cloudresourcemanager.googleapis.com", # Resource Manager
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(local.required_apis)

  project = var.project_id
  service = each.value

  # Don't disable APIs on destroy (other resources may depend on them)
  disable_on_destroy = false

  # Wait for API to be fully enabled
  timeouts {
    create = "10m"
    update = "10m"
  }
}

# =============================================================================
# Outputs
# =============================================================================

output "state_bucket_name" {
  description = "Name of the Terraform state bucket"
  value       = google_storage_bucket.terraform_state.name
}

output "state_bucket_url" {
  description = "URL of the Terraform state bucket"
  value       = google_storage_bucket.terraform_state.url
}

output "enabled_apis" {
  description = "List of enabled GCP APIs"
  value       = [for api in google_project_service.apis : api.service]
}

output "next_steps" {
  description = "Instructions for next steps"
  value       = <<-EOT

    Bootstrap complete! Next steps:

    1. cd ../environments/dev
    2. terraform init
    3. terraform plan
    4. terraform apply

  EOT
}
