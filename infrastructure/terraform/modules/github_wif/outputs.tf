# GitHub WIF Module Outputs

output "workload_identity_provider" {
  description = "The Workload Identity Provider resource name (for GitHub Secret GCP_WORKLOAD_IDENTITY_PROVIDER)"
  value       = google_iam_workload_identity_pool_provider.github_provider.name
}

output "service_account_email" {
  description = "The GitHub Actions service account email (for GitHub Secret GCP_SERVICE_ACCOUNT)"
  value       = google_service_account.github_actions.email
}
