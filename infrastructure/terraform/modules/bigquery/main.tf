# BigQuery Module
# Creates dataset for analytics data.

# BigQuery Dataset
resource "google_bigquery_dataset" "main" {
  dataset_id    = var.dataset_id
  project       = var.project_id
  location      = var.location
  friendly_name = "Homework Coach Analytics"
  description   = "Analytics dataset for Homework Coach application"

  # Delete contents when destroying dataset (dev only)
  delete_contents_on_destroy = var.environment != "production"

  # Default table expiration (none for production)
  default_table_expiration_ms = var.environment == "production" ? null : 31536000000 # 1 year

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "WRITER"
    user_by_email = var.backend_service_account_email
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }
}

# Enable BigQuery API
resource "google_project_service" "bigquery" {
  project            = var.project_id
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}
