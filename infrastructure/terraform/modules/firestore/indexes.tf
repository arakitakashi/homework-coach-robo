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

# =============================================================================
# Phase 2 Indexes (conditional)
# =============================================================================

# Phase 2a: Curriculum items by subject and grade level
resource "google_firestore_index" "curriculum_by_subject_grade" {
  count      = var.enable_phase2_indexes ? 1 : 0
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "curriculum"

  fields {
    field_path = "subject"
    order      = "ASCENDING"
  }

  fields {
    field_path = "gradeLevel"
    order      = "ASCENDING"
  }

  fields {
    field_path = "unit"
    order      = "ASCENDING"
  }

  depends_on = [google_firestore_database.main]
}

# Phase 2b: Agent configs by name
resource "google_firestore_index" "agent_configs_by_name" {
  count      = var.enable_phase2_indexes ? 1 : 0
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "agent_configs"

  fields {
    field_path = "agentName"
    order      = "ASCENDING"
  }

  fields {
    field_path = "version"
    order      = "DESCENDING"
  }

  depends_on = [google_firestore_database.main]
}

# Phase 2b: Active agent configs
resource "google_firestore_index" "agent_configs_active" {
  count      = var.enable_phase2_indexes ? 1 : 0
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "agent_configs"

  fields {
    field_path = "isActive"
    order      = "ASCENDING"
  }

  fields {
    field_path = "agentName"
    order      = "ASCENDING"
  }

  depends_on = [google_firestore_database.main]
}

# Phase 2d: Emotion analysis by session
resource "google_firestore_index" "emotion_analysis_by_session" {
  count      = var.enable_phase2_indexes ? 1 : 0
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "emotion_analysis"

  fields {
    field_path = "sessionId"
    order      = "ASCENDING"
  }

  fields {
    field_path = "analyzedAt"
    order      = "DESCENDING"
  }

  depends_on = [google_firestore_database.main]
}

# Phase 2d: Emotion analysis by user
resource "google_firestore_index" "emotion_analysis_by_user" {
  count      = var.enable_phase2_indexes ? 1 : 0
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "emotion_analysis"

  fields {
    field_path = "userId"
    order      = "ASCENDING"
  }

  fields {
    field_path = "analyzedAt"
    order      = "DESCENDING"
  }

  depends_on = [google_firestore_database.main]
}
