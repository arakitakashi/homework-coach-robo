# Firestore Module
# Creates Firestore database in Native mode.
# Note: Firestore can only be created once per project. If it already exists,
# this resource will fail. Import existing Firestore using:
# terraform import google_firestore_database.main projects/{project_id}/databases/(default)

resource "google_firestore_database" "main" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.location
  type        = "FIRESTORE_NATIVE"

  # Enable delete protection for production
  delete_protection_state = var.environment == "production" ? "DELETE_PROTECTION_ENABLED" : "DELETE_PROTECTION_DISABLED"

  # Point-in-time recovery for production
  point_in_time_recovery_enablement = var.environment == "production" ? "POINT_IN_TIME_RECOVERY_ENABLED" : "POINT_IN_TIME_RECOVERY_DISABLED"
}

# Enable Firestore API
resource "google_project_service" "firestore" {
  project            = var.project_id
  service            = "firestore.googleapis.com"
  disable_on_destroy = false
}
