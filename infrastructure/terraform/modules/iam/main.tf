# IAM Module
# Creates service accounts and IAM bindings with least-privilege access.

# Service Account for Backend (Cloud Run)
resource "google_service_account" "backend" {
  account_id   = "${var.name_prefix}-backend"
  display_name = "Homework Coach Backend Service Account"
  description  = "Service account for the backend Cloud Run service"
  project      = var.project_id
}

# Service Account for Frontend (Cloud Run)
resource "google_service_account" "frontend" {
  account_id   = "${var.name_prefix}-frontend"
  display_name = "Homework Coach Frontend Service Account"
  description  = "Service account for the frontend Cloud Run service"
  project      = var.project_id
}

# Service Account for Cloud Build
resource "google_service_account" "cloud_build" {
  account_id   = "${var.name_prefix}-cloud-build"
  display_name = "Homework Coach Cloud Build Service Account"
  description  = "Service account for Cloud Build CI/CD"
  project      = var.project_id
}

# Backend Service Account Roles
# Firestore access
resource "google_project_iam_member" "backend_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# BigQuery access
resource "google_project_iam_member" "backend_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# BigQuery job user (for running queries)
resource "google_project_iam_member" "backend_bigquery_job" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Secret Manager access
resource "google_project_iam_member" "backend_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Cloud Storage access (for assets)
resource "google_project_iam_member" "backend_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Cloud Speech-to-Text access
# NOTE: Speech-to-Text API doesn't require specific IAM role - API enablement is sufficient

# NOTE: Text-to-Speech API doesn't require specific IAM role - API enablement is sufficient

# Vertex AI access (for Gemini)
resource "google_project_iam_member" "backend_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# NOTE: Vision API doesn't require specific IAM role - API enablement is sufficient

# Cloud Logging access
resource "google_project_iam_member" "backend_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Cloud Trace access
resource "google_project_iam_member" "backend_trace" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Redis (Memorystore) access - via VPC, no IAM needed but adding for network access
resource "google_project_iam_member" "backend_redis" {
  project = var.project_id
  role    = "roles/redis.viewer"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Phase 2c: Discovery Engine (RAG) access
resource "google_project_iam_member" "backend_discovery_engine" {
  count   = var.enable_phase2_rag ? 1 : 0
  project = var.project_id
  role    = "roles/discoveryengine.editor"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Phase 2c: Cloud Storage admin for RAG data upload
resource "google_project_iam_member" "backend_storage_admin" {
  count   = var.enable_phase2_storage_admin ? 1 : 0
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Frontend Service Account Roles
# Secret Manager access (for API keys, etc.)
resource "google_project_iam_member" "frontend_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.frontend.email}"
}

# Cloud Storage access (for static assets)
resource "google_project_iam_member" "frontend_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.frontend.email}"
}

# Cloud Logging access
resource "google_project_iam_member" "frontend_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.frontend.email}"
}

# Cloud Build Service Account Roles
# Cloud Run admin (for deployment)
resource "google_project_iam_member" "cloud_build_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cloud_build.email}"
}

# Service account user (to act as service accounts)
resource "google_project_iam_member" "cloud_build_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cloud_build.email}"
}

# Artifact Registry writer (to push images)
resource "google_project_iam_member" "cloud_build_artifact_registry" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.cloud_build.email}"
}

# Storage admin (for Cloud Build artifacts)
resource "google_project_iam_member" "cloud_build_storage" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.cloud_build.email}"
}

# Cloud Build editor
resource "google_project_iam_member" "cloud_build_editor" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.editor"
  member  = "serviceAccount:${google_service_account.cloud_build.email}"
}

# Logging writer for build logs
resource "google_project_iam_member" "cloud_build_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.cloud_build.email}"
}
