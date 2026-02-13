# Cloud Run Module
# Creates Cloud Run services for backend and frontend.

# Artifact Registry Repository for Docker images
resource "google_artifact_registry_repository" "main" {
  location      = var.region
  repository_id = "${var.name_prefix}-docker"
  project       = var.project_id
  description   = "Docker repository for Homework Coach"
  format        = "DOCKER"

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Backend Cloud Run Service
resource "google_cloud_run_v2_service" "backend" {
  name     = "${var.name_prefix}-backend"
  location = var.region
  project  = var.project_id

  template {
    service_account = var.backend_service_account_email

    scaling {
      min_instance_count = var.backend_min_instances
      max_instance_count = var.backend_max_instances
    }

    vpc_access {
      connector = var.vpc_connector_id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    timeout = "${var.backend_timeout}s"

    containers {
      image = var.backend_image != "" ? var.backend_image : "gcr.io/cloudrun/placeholder"

      resources {
        limits = {
          cpu    = var.backend_cpu
          memory = var.backend_memory
        }
        cpu_idle          = var.environment != "production"
        startup_cpu_boost = true
      }

      # Environment variables
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_REGION"
        value = var.region
      }
      # NOTE: PORT is automatically set by Cloud Run (8080)

      # CORS: フロントエンドCloud Run URLを許可
      env {
        name  = "CORS_ORIGINS"
        value = google_cloud_run_v2_service.frontend.uri
      }

      # Additional environment variables (Phase 2)
      dynamic "env" {
        for_each = var.backend_env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      # Secret environment variables
      dynamic "env" {
        for_each = var.backend_secrets
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value.secret_id
              version = env.value.version
            }
          }
        }
      }

      ports {
        container_port = 8080
      }

      # Health check
      # NOTE: google.cloud.aiplatform のインポートが重く（Python 3.10で15-25秒）、
      # uvicorn起動まで30秒以上かかるため、failure_threshold を余裕を持って設定
      startup_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 10
        period_seconds        = 10
        failure_threshold     = 12
        timeout_seconds       = 5
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        period_seconds    = 30
        failure_threshold = 3
        timeout_seconds   = 5
      }
    }

    max_instance_request_concurrency = var.backend_concurrency
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image, # Image updated by CI/CD
      client,
      client_version,
    ]
  }
}

# Frontend Cloud Run Service
resource "google_cloud_run_v2_service" "frontend" {
  name     = "${var.name_prefix}-frontend"
  location = var.region
  project  = var.project_id

  template {
    service_account = var.frontend_service_account_email

    scaling {
      min_instance_count = var.frontend_min_instances
      max_instance_count = var.frontend_max_instances
    }

    timeout = "${var.frontend_timeout}s"

    containers {
      image = var.frontend_image != "" ? var.frontend_image : "gcr.io/cloudrun/placeholder"

      resources {
        limits = {
          cpu    = var.frontend_cpu
          memory = var.frontend_memory
        }
        cpu_idle          = var.environment != "production"
        startup_cpu_boost = true
      }

      # Environment variables
      env {
        name  = "NODE_ENV"
        value = var.environment == "production" ? "production" : "development"
      }
      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = var.backend_url != "" ? var.backend_url : "https://${var.name_prefix}-backend-${var.project_id}.${var.region}.run.app"
      }
      # NOTE: PORT is automatically set by Cloud Run (8080)

      ports {
        container_port = 8080
      }

      # Health check
      startup_probe {
        http_get {
          path = "/api/health"
          port = 8080
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        failure_threshold     = 3
        timeout_seconds       = 5
      }

      liveness_probe {
        http_get {
          path = "/api/health"
          port = 8080
        }
        period_seconds    = 30
        failure_threshold = 3
        timeout_seconds   = 5
      }
    }

    max_instance_request_concurrency = var.frontend_concurrency
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image, # Image updated by CI/CD
      client,
      client_version,
    ]
  }
}

# Enable Cloud Run API
resource "google_project_service" "cloud_run" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

# Enable Artifact Registry API
resource "google_project_service" "artifact_registry" {
  project            = var.project_id
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}
