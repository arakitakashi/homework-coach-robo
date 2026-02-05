# Cloud Storage Module
# Creates bucket for static assets with CDN configuration.

# Random suffix for globally unique bucket name
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Assets Bucket
resource "google_storage_bucket" "assets" {
  name          = "${var.name_prefix}-assets-${random_id.bucket_suffix.hex}"
  project       = var.project_id
  location      = var.location
  storage_class = "STANDARD"
  force_destroy = var.environment != "production"

  # Uniform bucket-level access (recommended)
  uniform_bucket_level_access = true

  # Versioning for production
  versioning {
    enabled = var.environment == "production"
  }

  # Lifecycle rules
  lifecycle_rule {
    condition {
      age        = 365
      with_state = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }

  # CORS configuration for web access
  cors {
    origin          = var.cors_origins
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["Content-Type", "Cache-Control", "Content-Length"]
    max_age_seconds = 3600
  }

  # Labels
  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Public access for assets (read-only)
resource "google_storage_bucket_iam_member" "public_read" {
  count  = var.enable_public_access ? 1 : 0
  bucket = google_storage_bucket.assets.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Backend service account access
resource "google_storage_bucket_iam_member" "backend_access" {
  bucket = google_storage_bucket.assets.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.backend_service_account_email}"
}

# Frontend service account access
resource "google_storage_bucket_iam_member" "frontend_access" {
  bucket = google_storage_bucket.assets.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.frontend_service_account_email}"
}

# Cloud Build service account access (for deployment)
resource "google_storage_bucket_iam_member" "cloud_build_access" {
  bucket = google_storage_bucket.assets.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.cloud_build_service_account_email}"
}

# Backend origin for CDN
resource "google_compute_backend_bucket" "assets_cdn" {
  count       = var.enable_cdn ? 1 : 0
  name        = "${var.name_prefix}-assets-cdn"
  project     = var.project_id
  description = "CDN backend for static assets"
  bucket_name = google_storage_bucket.assets.name
  enable_cdn  = true

  cdn_policy {
    cache_mode        = "CACHE_ALL_STATIC"
    default_ttl       = 86400  # 24 hours
    max_ttl           = 604800 # 7 days
    client_ttl        = 86400  # 24 hours
    negative_caching  = true
    serve_while_stale = 86400 # Serve stale content for up to 24 hours if origin is down
  }
}

# URL Map for CDN (simplified - would need more config for production)
resource "google_compute_url_map" "assets_cdn" {
  count           = var.enable_cdn ? 1 : 0
  name            = "${var.name_prefix}-assets-url-map"
  project         = var.project_id
  default_service = google_compute_backend_bucket.assets_cdn[0].id
}
