# Secret Manager Module Outputs

output "redis_url_secret_id" {
  description = "The ID of the Redis URL secret"
  value       = google_secret_manager_secret.redis_url.secret_id
}

output "redis_url_secret_name" {
  description = "The resource name of the Redis URL secret"
  value       = google_secret_manager_secret.redis_url.name
}

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
