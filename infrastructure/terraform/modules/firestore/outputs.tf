# Firestore Module Outputs

output "database_name" {
  description = "The name of the Firestore database"
  value       = google_firestore_database.main.name
}

output "database_id" {
  description = "The ID of the Firestore database"
  value       = google_firestore_database.main.id
}

output "database_location" {
  description = "The location of the Firestore database"
  value       = google_firestore_database.main.location_id
}
