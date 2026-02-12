# Development Environment Main Configuration
# This is the root module that orchestrates all infrastructure components.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 7.13.0"
    }

    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 7.13.0"
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
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "discoveryengine.googleapis.com",
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

  # Phase 2 flags
  enable_phase2_rag           = var.enable_phase2_rag
  enable_phase2_storage_admin = var.enable_phase2_rag

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

  # Phase 2 flags
  create_gemini_api_key_secret = var.enable_phase2_tools || var.enable_phase2_multi_agent

  depends_on = [module.iam]
}

# Firestore Module
module "firestore" {
  source = "../../modules/firestore"

  project_id  = var.project_id
  location    = var.region
  environment = var.environment

  # Phase 2 flags
  enable_phase2_indexes = var.enable_phase2_tools || var.enable_phase2_multi_agent || var.enable_phase2_emotion

  depends_on = [google_project_service.required_apis]
}

# BigQuery Module
module "bigquery" {
  source = "../../modules/bigquery"

  project_id                    = var.project_id
  location                      = var.region
  environment                   = var.environment
  backend_service_account_email = module.iam.backend_service_account_email

  # Phase 2 flags
  enable_phase2_tables = var.enable_phase2_multi_agent || var.enable_phase2_rag || var.enable_phase2_emotion

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
  cloud_build_service_account_email        = module.iam.cloud_build_service_account_email
  github_actions_service_account_email     = module.github_wif.service_account_email
  enable_cdn                               = var.enable_cdn

  depends_on = [module.iam, module.github_wif]
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
  backend_memory                    = var.backend_memory

  # Pass secret references to backend
  backend_secrets = {
    JWT_SECRET = {
      secret_id = module.secret_manager.jwt_secret_id
      version   = "latest"
    }
  }

  # Phase 2 environment variables (conditionally populated)
  backend_env_vars = merge(
    var.enable_phase2_tools ? {
      ENABLE_ADK_TOOLS = "true"
    } : {},
    var.enable_phase2_multi_agent ? {
      ENABLE_MULTI_AGENT = "true"
    } : {},
    var.enable_phase2_rag ? {
      ENABLE_RAG = "true"
    } : {},
    var.enable_phase2_emotion ? {
      ENABLE_EMOTION_ANALYSIS = "true"
    } : {},
    # Phase 3: Agent Engine configuration
    var.enable_agent_engine ? {
      AGENT_ENGINE_RESOURCE_NAME = "projects/${var.project_id}/locations/${var.gcp_location}/reasoningEngines/${module.agent_engine[0].engine_id}"
      AGENT_ENGINE_ID            = module.agent_engine[0].engine_id
      GCP_LOCATION               = var.gcp_location
      PROJECT_ID                 = var.project_id
    } : {},
  )

  # Allow unauthenticated access in dev
  allow_unauthenticated_backend = true

  depends_on = [module.vpc, module.iam, module.secret_manager]
}

# GitHub Actions Workload Identity Federation Module
module "github_wif" {
  source = "../../modules/github_wif"

  project_id   = var.project_id
  github_owner = var.github_owner
  github_repo  = var.github_repo

  depends_on = [google_project_service.required_apis]
}

# Agent Engine Module (Phase 3)
module "agent_engine" {
  source = "../../modules/agent_engine"
  count  = var.enable_agent_engine ? 1 : 0

  project_id           = var.project_id
  region               = var.gcp_location
  pickle_gcs_uri       = "gs://homework-coach-assets-4592ba87/agent-engine/pickle.pkl"
  requirements_gcs_uri = "gs://homework-coach-assets-4592ba87/agent-engine/requirements.txt"
  dependencies_gcs_uri = "gs://homework-coach-assets-4592ba87/agent-engine/dependencies.tar.gz"

  depends_on = [google_project_service.required_apis, module.cloud_storage]
}
