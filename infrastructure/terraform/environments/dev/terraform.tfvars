# Development Environment Variables
# Update project_id before running terraform apply

project_id  = "homework-coach-robo"
region      = "asia-northeast1"
environment = "dev"
name_prefix = "homework-coach"

# Dev-specific settings (cost optimization)
backend_min_instances  = 0     # Scale to zero when idle
frontend_min_instances = 0     # Scale to zero when idle
enable_cdn             = false # No CDN for dev

# NOTE: Redis removed - session management handled by Vertex AI / ADK
