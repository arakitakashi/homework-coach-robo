# BigQuery Tables
# Tables for analytics based on architecture.md

# Dialogue Sessions Table
resource "google_bigquery_table" "dialogue_sessions" {
  dataset_id          = google_bigquery_dataset.main.dataset_id
  table_id            = "dialogue_sessions"
  project             = var.project_id
  deletion_protection = var.environment == "production"

  description = "Stores completed dialogue session data for analysis"

  time_partitioning {
    type  = "DAY"
    field = "start_time"
  }

  clustering = ["user_id"]

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  schema = jsonencode([
    {
      name        = "session_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Unique session identifier"
    },
    {
      name        = "user_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "User identifier"
    },
    {
      name        = "start_time"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Session start timestamp"
    },
    {
      name        = "end_time"
      type        = "TIMESTAMP"
      mode        = "NULLABLE"
      description = "Session end timestamp"
    },
    {
      name        = "problem_ids"
      type        = "STRING"
      mode        = "REPEATED"
      description = "List of problem IDs attempted in the session"
    },
    {
      name        = "total_hints_used"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Total number of hints used"
    },
    {
      name        = "self_solved_count"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Number of problems solved independently"
    },
    {
      name        = "total_points"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Total points earned in the session"
    },
    {
      name = "dialogue_turns"
      type = "RECORD"
      mode = "REPEATED"
      fields = [
        {
          name = "turn_id"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "speaker"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "content"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "timestamp"
          type = "TIMESTAMP"
          mode = "REQUIRED"
        },
        {
          name = "emotion"
          type = "STRING"
          mode = "NULLABLE"
        }
      ]
    },
    {
      name        = "created_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Record creation timestamp"
    }
  ])

  depends_on = [google_bigquery_dataset.main]
}

# Learning History Table
resource "google_bigquery_table" "learning_history" {
  dataset_id          = google_bigquery_dataset.main.dataset_id
  table_id            = "learning_history"
  project             = var.project_id
  deletion_protection = var.environment == "production"

  description = "Stores learning history for long-term analysis"

  time_partitioning {
    type  = "DAY"
    field = "attempted_at"
  }

  clustering = ["user_id", "problem_id"]

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  schema = jsonencode([
    {
      name        = "user_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "User identifier"
    },
    {
      name        = "problem_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Problem identifier"
    },
    {
      name        = "attempted_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Timestamp of the attempt"
    },
    {
      name        = "solved_independently"
      type        = "BOOLEAN"
      mode        = "NULLABLE"
      description = "Whether the problem was solved without hints"
    },
    {
      name        = "hints_used"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Number of hints used"
    },
    {
      name        = "time_spent_seconds"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Time spent on the problem in seconds"
    },
    {
      name        = "points_earned"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Points earned for this attempt"
    },
    {
      name        = "session_id"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Session in which this attempt occurred"
    }
  ])

  depends_on = [google_bigquery_dataset.main]
}

# Learning Profile Snapshots Table (for trend analysis)
resource "google_bigquery_table" "learning_profile_snapshots" {
  dataset_id          = google_bigquery_dataset.main.dataset_id
  table_id            = "learning_profile_snapshots"
  project             = var.project_id
  deletion_protection = var.environment == "production"

  description = "Periodic snapshots of learning profiles for trend analysis"

  time_partitioning {
    type  = "DAY"
    field = "snapshot_at"
  }

  clustering = ["user_id"]

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  schema = jsonencode([
    {
      name        = "user_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "User identifier"
    },
    {
      name        = "snapshot_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Snapshot timestamp"
    },
    {
      name        = "persistence_score"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Persistence score (0-10)"
    },
    {
      name        = "independence_score"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Independence score (0-10)"
    },
    {
      name        = "reflection_quality"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Reflection quality score (0-10)"
    },
    {
      name        = "hint_dependency"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Hint dependency ratio (0-1)"
    },
    {
      name        = "total_sessions"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Total number of sessions"
    },
    {
      name        = "total_problems_solved"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Total problems solved"
    },
    {
      name = "subject_understanding"
      type = "RECORD"
      mode = "REPEATED"
      fields = [
        {
          name = "subject"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "topic"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "level"
          type = "FLOAT64"
          mode = "REQUIRED"
        },
        {
          name = "trend"
          type = "STRING"
          mode = "NULLABLE"
        }
      ]
    }
  ])

  depends_on = [google_bigquery_dataset.main]
}
