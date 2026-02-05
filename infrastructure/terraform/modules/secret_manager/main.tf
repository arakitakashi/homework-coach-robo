# Secret Manager Module
# Creates secret placeholders for application secrets.
# Secret values should be set manually or via CI/CD after infrastructure provisioning.

# Redis URL secret
resource "google_secret_manager_secret" "redis_url" {
  secret_id = "${var.name_prefix}-redis-url"
  project   = var.project_id

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  replication {
    auto {}
  }
}

# Firebase/Firestore configuration (if needed)
resource "google_secret_manager_secret" "firebase_config" {
  secret_id = "${var.name_prefix}-firebase-config"
  project   = var.project_id

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  replication {
    auto {}
  }
}

# API key for external services (optional)
resource "google_secret_manager_secret" "api_key" {
  count     = var.create_api_key_secret ? 1 : 0
  secret_id = "${var.name_prefix}-api-key"
  project   = var.project_id

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  replication {
    auto {}
  }
}

# JWT secret for authentication
resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "${var.name_prefix}-jwt-secret"
  project   = var.project_id

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  replication {
    auto {}
  }
}

# IAM binding for backend service account to access secrets
resource "google_secret_manager_secret_iam_member" "backend_redis_url" {
  secret_id = google_secret_manager_secret.redis_url.secret_id
  project   = var.project_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.backend_service_account_email}"
}

resource "google_secret_manager_secret_iam_member" "backend_firebase_config" {
  secret_id = google_secret_manager_secret.firebase_config.secret_id
  project   = var.project_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.backend_service_account_email}"
}

resource "google_secret_manager_secret_iam_member" "backend_jwt_secret" {
  secret_id = google_secret_manager_secret.jwt_secret.secret_id
  project   = var.project_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.backend_service_account_email}"
}

resource "google_secret_manager_secret_iam_member" "backend_api_key" {
  count     = var.create_api_key_secret ? 1 : 0
  secret_id = google_secret_manager_secret.api_key[0].secret_id
  project   = var.project_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.backend_service_account_email}"
}

# IAM binding for frontend service account (limited secrets)
resource "google_secret_manager_secret_iam_member" "frontend_firebase_config" {
  secret_id = google_secret_manager_secret.firebase_config.secret_id
  project   = var.project_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.frontend_service_account_email}"
}
