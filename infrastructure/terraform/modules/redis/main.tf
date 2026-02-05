# Redis Module
# Creates Memorystore for Redis instance for caching.

# Memorystore Redis Instance
resource "google_redis_instance" "main" {
  name           = "${var.name_prefix}-redis"
  project        = var.project_id
  region         = var.region
  display_name   = "Homework Coach Redis Cache"
  tier           = var.tier
  memory_size_gb = var.memory_size_gb
  redis_version  = var.redis_version

  # Network configuration
  authorized_network = var.network_id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  # Redis configuration
  redis_configs = {
    maxmemory-policy       = "allkeys-lru"
    notify-keyspace-events = "Ex" # Enable key expiration notifications
  }

  # Maintenance window (Sunday 2:00-6:00 AM JST)
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 17 # 2:00 AM JST = 17:00 UTC previous day
        minutes = 0
        seconds = 0
        nanos   = 0
      }
    }
  }

  # Labels
  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  # Only enable auth for production
  auth_enabled = var.environment == "production"

  # Enable TLS for production
  transit_encryption_mode = var.environment == "production" ? "SERVER_AUTHENTICATION" : "DISABLED"

  depends_on = [var.private_vpc_connection]
}

# Enable Redis API
resource "google_project_service" "redis" {
  project            = var.project_id
  service            = "redis.googleapis.com"
  disable_on_destroy = false
}
