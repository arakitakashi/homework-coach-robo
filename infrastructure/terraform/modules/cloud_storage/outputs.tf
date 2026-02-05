# Cloud Storage Module Outputs

output "bucket_name" {
  description = "The name of the assets bucket"
  value       = google_storage_bucket.assets.name
}

output "bucket_url" {
  description = "The URL of the assets bucket"
  value       = google_storage_bucket.assets.url
}

output "bucket_self_link" {
  description = "The self link of the assets bucket"
  value       = google_storage_bucket.assets.self_link
}

output "public_url" {
  description = "The public URL for accessing assets"
  value       = "https://storage.googleapis.com/${google_storage_bucket.assets.name}"
}

output "cdn_backend_bucket_id" {
  description = "The ID of the CDN backend bucket (if enabled)"
  value       = var.enable_cdn ? google_compute_backend_bucket.assets_cdn[0].id : null
}

output "cdn_url_map_id" {
  description = "The ID of the CDN URL map (if enabled)"
  value       = var.enable_cdn ? google_compute_url_map.assets_cdn[0].id : null
}
