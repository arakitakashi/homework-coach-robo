# Secret Manager Module Outputs

# NOTE: Redis URL outputs removed - session management handled by Vertex AI / ADK

output "firebase_config_secret_id" {
  description = "The ID of the Firebase config secret"
  value       = google_secret_manager_secret.firebase_config.secret_id
}

output "firebase_config_secret_name" {
  description = "The resource name of the Firebase config secret"
  value       = google_secret_manager_secret.firebase_config.name
}

output "jwt_secret_id" {
  description = "The ID of the JWT secret"
  value       = google_secret_manager_secret.jwt_secret.secret_id
}

output "jwt_secret_name" {
  description = "The resource name of the JWT secret"
  value       = google_secret_manager_secret.jwt_secret.name
}

output "api_key_secret_id" {
  description = "The ID of the API key secret (if created)"
  value       = var.create_api_key_secret ? google_secret_manager_secret.api_key[0].secret_id : null
}

output "api_key_secret_name" {
  description = "The resource name of the API key secret (if created)"
  value       = var.create_api_key_secret ? google_secret_manager_secret.api_key[0].name : null
}
