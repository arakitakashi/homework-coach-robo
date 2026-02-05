# IAM Module Outputs

output "backend_service_account_email" {
  description = "Email of the backend service account"
  value       = google_service_account.backend.email
}

output "backend_service_account_id" {
  description = "ID of the backend service account"
  value       = google_service_account.backend.id
}

output "frontend_service_account_email" {
  description = "Email of the frontend service account"
  value       = google_service_account.frontend.email
}

output "frontend_service_account_id" {
  description = "ID of the frontend service account"
  value       = google_service_account.frontend.id
}

output "cloud_build_service_account_email" {
  description = "Email of the Cloud Build service account"
  value       = google_service_account.cloud_build.email
}

output "cloud_build_service_account_id" {
  description = "ID of the Cloud Build service account"
  value       = google_service_account.cloud_build.id
}
