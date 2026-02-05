# Redis Module Outputs

output "instance_id" {
  description = "The ID of the Redis instance"
  value       = google_redis_instance.main.id
}

output "instance_name" {
  description = "The name of the Redis instance"
  value       = google_redis_instance.main.name
}

output "host" {
  description = "The IP address of the Redis instance"
  value       = google_redis_instance.main.host
}

output "port" {
  description = "The port of the Redis instance"
  value       = google_redis_instance.main.port
}

output "connection_string" {
  description = "The Redis connection string (redis://host:port)"
  value       = "redis://${google_redis_instance.main.host}:${google_redis_instance.main.port}"
  sensitive   = true
}

output "auth_string" {
  description = "The auth string for the Redis instance (if auth is enabled)"
  value       = google_redis_instance.main.auth_string
  sensitive   = true
}

output "current_location_id" {
  description = "The current zone where the Redis endpoint is placed"
  value       = google_redis_instance.main.current_location_id
}
