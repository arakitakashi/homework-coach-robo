# Development Environment Outputs

# VPC
output "vpc_network_name" {
  description = "The name of the VPC network"
  value       = module.vpc.network_name
}

output "vpc_connector_name" {
  description = "The name of the VPC Access Connector"
  value       = module.vpc.connector_name
}

# IAM
output "backend_service_account" {
  description = "The backend service account email"
  value       = module.iam.backend_service_account_email
}

output "frontend_service_account" {
  description = "The frontend service account email"
  value       = module.iam.frontend_service_account_email
}

output "cloud_build_service_account" {
  description = "The Cloud Build service account email"
  value       = module.iam.cloud_build_service_account_email
}

# Firestore
output "firestore_database_name" {
  description = "The Firestore database name"
  value       = module.firestore.database_name
}

# BigQuery
output "bigquery_dataset_id" {
  description = "The BigQuery dataset ID"
  value       = module.bigquery.dataset_id
}

# NOTE: Redis removed - session management handled by Vertex AI / ADK

# Cloud Storage
output "assets_bucket_name" {
  description = "The name of the assets bucket"
  value       = module.cloud_storage.bucket_name
}

output "assets_bucket_url" {
  description = "The public URL for assets"
  value       = module.cloud_storage.public_url
}

# Cloud Run
output "artifact_registry_url" {
  description = "The Artifact Registry URL for Docker images"
  value       = module.cloud_run.artifact_registry_url
}

output "backend_url" {
  description = "The backend Cloud Run service URL"
  value       = module.cloud_run.backend_url
}

output "frontend_url" {
  description = "The frontend Cloud Run service URL"
  value       = module.cloud_run.frontend_url
}

# GitHub Actions WIF
output "github_wif_provider" {
  description = "The Workload Identity Provider (for GitHub Secret GCP_WORKLOAD_IDENTITY_PROVIDER)"
  value       = module.github_wif.workload_identity_provider
}

output "github_wif_service_account" {
  description = "The GitHub Actions service account email (for GitHub Secret GCP_SERVICE_ACCOUNT)"
  value       = module.github_wif.service_account_email
}

# Phase 2 outputs
output "phase2_gemini_api_key_secret_id" {
  description = "The Gemini API key secret ID (if created)"
  value       = module.secret_manager.gemini_api_key_secret_id
}

output "phase2_bigquery_agent_metrics_table" {
  description = "The agent_metrics BigQuery table ID (if created)"
  value       = module.bigquery.agent_metrics_table_id
}

output "phase2_bigquery_emotion_analysis_table" {
  description = "The emotion_analysis BigQuery table ID (if created)"
  value       = module.bigquery.emotion_analysis_table_id
}

output "phase2_bigquery_rag_metrics_table" {
  description = "The rag_metrics BigQuery table ID (if created)"
  value       = module.bigquery.rag_metrics_table_id
}

# Summary for easy reference
output "summary" {
  description = "Summary of important resources"
  value = {
    project_id         = var.project_id
    region             = var.region
    environment        = var.environment
    backend_url        = module.cloud_run.backend_url
    frontend_url       = module.cloud_run.frontend_url
    artifact_registry  = module.cloud_run.artifact_registry_url
    assets_bucket      = module.cloud_storage.bucket_name
    firestore_database = module.firestore.database_name
    bigquery_dataset   = module.bigquery.dataset_id
    # Phase 2 flags
    phase2_tools       = var.enable_phase2_tools
    phase2_multi_agent = var.enable_phase2_multi_agent
    phase2_rag         = var.enable_phase2_rag
    phase2_emotion     = var.enable_phase2_emotion
  }
}
