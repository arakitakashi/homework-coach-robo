# Cloud Run Module Outputs

# Artifact Registry
output "artifact_registry_repository" {
  description = "The Artifact Registry repository name"
  value       = google_artifact_registry_repository.main.name
}

output "artifact_registry_url" {
  description = "The Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}"
}

# Backend Service
output "backend_service_name" {
  description = "The name of the backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend.name
}

output "backend_service_id" {
  description = "The ID of the backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend.id
}

output "backend_url" {
  description = "The URL of the backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend.uri
}

output "backend_latest_revision" {
  description = "The latest revision of the backend service"
  value       = google_cloud_run_v2_service.backend.latest_ready_revision
}

# Frontend Service
output "frontend_service_name" {
  description = "The name of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend.name
}

output "frontend_service_id" {
  description = "The ID of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend.id
}

output "frontend_url" {
  description = "The URL of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend.uri
}

output "frontend_latest_revision" {
  description = "The latest revision of the frontend service"
  value       = google_cloud_run_v2_service.frontend.latest_ready_revision
}
