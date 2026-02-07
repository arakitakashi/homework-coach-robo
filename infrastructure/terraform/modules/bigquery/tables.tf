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

# =============================================================================
# Phase 2 Tables (conditional)
# =============================================================================

# Agent Metrics Table (Phase 2b: multi-agent performance tracking)
resource "google_bigquery_table" "agent_metrics" {
  count               = var.enable_phase2_tables ? 1 : 0
  dataset_id          = google_bigquery_dataset.main.dataset_id
  table_id            = "agent_metrics"
  project             = var.project_id
  deletion_protection = var.environment == "production"

  description = "Tracks multi-agent routing decisions and performance metrics"

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  clustering = ["agent_name", "session_id"]

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    phase       = "phase2"
  }

  schema = jsonencode([
    {
      name        = "session_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Session identifier"
    },
    {
      name        = "agent_name"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Name of the agent (router, math_coach, japanese_coach, etc.)"
    },
    {
      name        = "timestamp"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Event timestamp"
    },
    {
      name        = "action"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Action performed (route, respond, tool_call, etc.)"
    },
    {
      name        = "latency_ms"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Response latency in milliseconds"
    },
    {
      name        = "tokens_used"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Number of tokens consumed"
    },
    {
      name        = "tool_name"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Name of the tool called (if applicable)"
    },
    {
      name        = "success"
      type        = "BOOLEAN"
      mode        = "NULLABLE"
      description = "Whether the action was successful"
    },
    {
      name        = "error_message"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Error message if action failed"
    },
    {
      name        = "user_id"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "User identifier"
    }
  ])

  depends_on = [google_bigquery_dataset.main]
}

# Emotion Analysis Table (Phase 2d: emotion tracking)
resource "google_bigquery_table" "emotion_analysis" {
  count               = var.enable_phase2_tables ? 1 : 0
  dataset_id          = google_bigquery_dataset.main.dataset_id
  table_id            = "emotion_analysis"
  project             = var.project_id
  deletion_protection = var.environment == "production"

  description = "Stores emotion analysis results from voice tone analysis"

  time_partitioning {
    type  = "DAY"
    field = "analyzed_at"
  }

  clustering = ["user_id", "session_id"]

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    phase       = "phase2"
  }

  schema = jsonencode([
    {
      name        = "session_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Session identifier"
    },
    {
      name        = "user_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "User identifier"
    },
    {
      name        = "analyzed_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Analysis timestamp"
    },
    {
      name        = "emotion"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Detected emotion (frustrated, confident, tired, neutral, etc.)"
    },
    {
      name        = "confidence"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Confidence score of emotion detection (0-1)"
    },
    {
      name        = "frustration_level"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Frustration level (0-10)"
    },
    {
      name        = "support_level_adjustment"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Support level adjustment made (increase, decrease, maintain)"
    },
    {
      name        = "turn_id"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Dialogue turn that triggered the analysis"
    }
  ])

  depends_on = [google_bigquery_dataset.main]
}

# RAG Metrics Table (Phase 2c: RAG performance tracking)
resource "google_bigquery_table" "rag_metrics" {
  count               = var.enable_phase2_tables ? 1 : 0
  dataset_id          = google_bigquery_dataset.main.dataset_id
  table_id            = "rag_metrics"
  project             = var.project_id
  deletion_protection = var.environment == "production"

  description = "Tracks RAG retrieval performance and relevance metrics"

  time_partitioning {
    type  = "DAY"
    field = "queried_at"
  }

  clustering = ["corpus_id"]

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    phase       = "phase2"
  }

  schema = jsonencode([
    {
      name        = "session_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Session identifier"
    },
    {
      name        = "queried_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Query timestamp"
    },
    {
      name        = "corpus_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "RAG corpus identifier"
    },
    {
      name        = "query_text"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "The query sent to RAG"
    },
    {
      name        = "results_count"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Number of results returned"
    },
    {
      name        = "top_relevance_score"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Relevance score of the top result (0-1)"
    },
    {
      name        = "latency_ms"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Query latency in milliseconds"
    },
    {
      name        = "used_in_response"
      type        = "BOOLEAN"
      mode        = "NULLABLE"
      description = "Whether retrieved content was used in the response"
    },
    {
      name        = "user_id"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "User identifier"
    }
  ])

  depends_on = [google_bigquery_dataset.main]
}
