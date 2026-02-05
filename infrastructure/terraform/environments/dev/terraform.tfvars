# Development Environment Variables
# Update project_id before running terraform apply

project_id  = "homework-coach-dev" # TODO: Update with your GCP project ID
region      = "asia-northeast1"
environment = "dev"
name_prefix = "homework-coach"

# Dev-specific settings (cost optimization)
backend_min_instances  = 0       # Scale to zero when idle
frontend_min_instances = 0       # Scale to zero when idle
redis_tier             = "BASIC" # No HA for dev
redis_memory_gb        = 1
enable_cdn             = false # No CDN for dev
