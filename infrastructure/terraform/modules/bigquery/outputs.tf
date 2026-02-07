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

# Phase 2 outputs
output "agent_metrics_table_id" {
  description = "The fully qualified table ID for agent_metrics (if created)"
  value       = var.enable_phase2_tables ? "${var.project_id}.${google_bigquery_dataset.main.dataset_id}.${google_bigquery_table.agent_metrics[0].table_id}" : null
}

output "emotion_analysis_table_id" {
  description = "The fully qualified table ID for emotion_analysis (if created)"
  value       = var.enable_phase2_tables ? "${var.project_id}.${google_bigquery_dataset.main.dataset_id}.${google_bigquery_table.emotion_analysis[0].table_id}" : null
}

output "rag_metrics_table_id" {
  description = "The fully qualified table ID for rag_metrics (if created)"
  value       = var.enable_phase2_tables ? "${var.project_id}.${google_bigquery_dataset.main.dataset_id}.${google_bigquery_table.rag_metrics[0].table_id}" : null
}
