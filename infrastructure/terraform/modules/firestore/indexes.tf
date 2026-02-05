# Firestore Indexes
# Composite indexes for efficient queries based on firestore-design.md

# Sessions by user and creation time
resource "google_firestore_index" "sessions_by_user" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "sessions"

  fields {
    field_path = "userId"
    order      = "ASCENDING"
  }

  fields {
    field_path = "createdAt"
    order      = "DESCENDING"
  }

  depends_on = [google_firestore_database.main]
}

# Active sessions by user
resource "google_firestore_index" "sessions_active_by_user" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "sessions"

  fields {
    field_path = "userId"
    order      = "ASCENDING"
  }

  fields {
    field_path = "isActive"
    order      = "ASCENDING"
  }

  fields {
    field_path = "createdAt"
    order      = "DESCENDING"
  }

  depends_on = [google_firestore_database.main]
}

# Problems by subject and grade
resource "google_firestore_index" "problems_by_subject_grade" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "problems"

  fields {
    field_path = "subject"
    order      = "ASCENDING"
  }

  fields {
    field_path = "gradeLevel"
    order      = "ASCENDING"
  }

  fields {
    field_path = "difficulty"
    order      = "ASCENDING"
  }

  depends_on = [google_firestore_database.main]
}

# Dialogue turns by session and timestamp (subcollection)
resource "google_firestore_index" "dialogue_turns_by_timestamp" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "dialogue_turns"

  # This index is for the subcollection under sessions
  query_scope = "COLLECTION_GROUP"

  fields {
    field_path = "role"
    order      = "ASCENDING"
  }

  fields {
    field_path = "timestamp"
    order      = "ASCENDING"
  }

  depends_on = [google_firestore_database.main]
}

# Notifications by user and read status
resource "google_firestore_index" "notifications_by_user" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "notifications"

  query_scope = "COLLECTION_GROUP"

  fields {
    field_path = "read"
    order      = "ASCENDING"
  }

  fields {
    field_path = "createdAt"
    order      = "DESCENDING"
  }

  depends_on = [google_firestore_database.main]
}

# Users by parent email (for parent-child relationship)
resource "google_firestore_index" "users_by_parent" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "users"

  fields {
    field_path = "settings.parentEmail"
    order      = "ASCENDING"
  }

  fields {
    field_path = "createdAt"
    order      = "DESCENDING"
  }

  depends_on = [google_firestore_database.main]
}
