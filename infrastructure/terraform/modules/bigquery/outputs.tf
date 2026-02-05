# BigQuery Module Outputs

output "dataset_id" {
  description = "The ID of the BigQuery dataset"
  value       = google_bigquery_dataset.main.dataset_id
}

output "dataset_self_link" {
  description = "The self link of the BigQuery dataset"
  value       = google_bigquery_dataset.main.self_link
}

output "dialogue_sessions_table_id" {
  description = "The fully qualified table ID for dialogue_sessions"
  value       = "${var.project_id}.${google_bigquery_dataset.main.dataset_id}.${google_bigquery_table.dialogue_sessions.table_id}"
}

output "learning_history_table_id" {
  description = "The fully qualified table ID for learning_history"
  value       = "${var.project_id}.${google_bigquery_dataset.main.dataset_id}.${google_bigquery_table.learning_history.table_id}"
}

output "learning_profile_snapshots_table_id" {
  description = "The fully qualified table ID for learning_profile_snapshots"
  value       = "${var.project_id}.${google_bigquery_dataset.main.dataset_id}.${google_bigquery_table.learning_profile_snapshots.table_id}"
}
