# Development Environment Main Configuration
# This is the root module that orchestrates all infrastructure components.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }

    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "firestore.googleapis.com",
    "bigquery.googleapis.com",
    "secretmanager.googleapis.com",
    "servicenetworking.googleapis.com",
    "vpcaccess.googleapis.com",
    "cloudbuild.googleapis.com",
    "speech.googleapis.com",
    "texttospeech.googleapis.com",
    "vision.googleapis.com",
    "aiplatform.googleapis.com",
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_id  = var.project_id
  region      = var.region
  name_prefix = var.name_prefix

  depends_on = [google_project_service.required_apis]
}

# IAM Module
module "iam" {
  source = "../../modules/iam"

  project_id  = var.project_id
  name_prefix = var.name_prefix

  depends_on = [google_project_service.required_apis]
}

# Secret Manager Module
module "secret_manager" {
  source = "../../modules/secret_manager"

  project_id                     = var.project_id
  name_prefix                    = var.name_prefix
  environment                    = var.environment
  backend_service_account_email  = module.iam.backend_service_account_email
  frontend_service_account_email = module.iam.frontend_service_account_email

  depends_on = [module.iam]
}

# Firestore Module
module "firestore" {
  source = "../../modules/firestore"

  project_id  = var.project_id
  location    = var.region
  environment = var.environment

  depends_on = [google_project_service.required_apis]
}

# BigQuery Module
module "bigquery" {
  source = "../../modules/bigquery"

  project_id                    = var.project_id
  location                      = var.region
  environment                   = var.environment
  backend_service_account_email = module.iam.backend_service_account_email

  depends_on = [module.iam]
}

# NOTE: Redis module removed - session management handled by Vertex AI / ADK
# Redis can be added later if needed for TTS caching or rate limiting

# Cloud Storage Module
module "cloud_storage" {
  source = "../../modules/cloud_storage"

  project_id                        = var.project_id
  location                          = var.region
  name_prefix                       = var.name_prefix
  environment                       = var.environment
  backend_service_account_email     = module.iam.backend_service_account_email
  frontend_service_account_email    = module.iam.frontend_service_account_email
  cloud_build_service_account_email = module.iam.cloud_build_service_account_email
  enable_cdn                        = var.enable_cdn

  depends_on = [module.iam]
}

# Cloud Run Module
module "cloud_run" {
  source = "../../modules/cloud_run"

  project_id                        = var.project_id
  region                            = var.region
  name_prefix                       = var.name_prefix
  environment                       = var.environment
  backend_service_account_email     = module.iam.backend_service_account_email
  frontend_service_account_email    = module.iam.frontend_service_account_email
  cloud_build_service_account_email = module.iam.cloud_build_service_account_email
  vpc_connector_id                  = module.vpc.connector_id
  backend_min_instances             = var.backend_min_instances
  frontend_min_instances            = var.frontend_min_instances

  # Pass secret references to backend
  backend_secrets = {
    JWT_SECRET = {
      secret_id = module.secret_manager.jwt_secret_id
      version   = "latest"
    }
  }

  # Allow unauthenticated access in dev
  allow_unauthenticated_backend = true

  depends_on = [module.vpc, module.iam, module.secret_manager]
}
