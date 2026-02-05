# Cloud Run IAM Configuration
# Controls who can invoke the Cloud Run services.

# Backend: Allow authenticated users (or specific services)
resource "google_cloud_run_v2_service_iam_member" "backend_invoker" {
  count    = var.allow_unauthenticated_backend ? 0 : 1
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.frontend_service_account_email}"
}

# Backend: Allow unauthenticated access (for development/testing)
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  count    = var.allow_unauthenticated_backend ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Frontend: Allow public access (web application)
resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Build can deploy to Cloud Run
resource "google_cloud_run_v2_service_iam_member" "backend_cloud_build" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.developer"
  member   = "serviceAccount:${var.cloud_build_service_account_email}"
}

resource "google_cloud_run_v2_service_iam_member" "frontend_cloud_build" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.developer"
  member   = "serviceAccount:${var.cloud_build_service_account_email}"
}
