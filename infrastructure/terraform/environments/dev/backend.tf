# Terraform Backend Configuration
# Uses Google Cloud Storage for state management.

terraform {
  backend "gcs" {
    bucket = "homework-coach-terraform-state"
    prefix = "dev"
  }
}

# Note: Before running terraform init, create the GCS bucket manually:
# gsutil mb -l asia-northeast1 gs://homework-coach-terraform-state
# gsutil versioning set on gs://homework-coach-terraform-state
