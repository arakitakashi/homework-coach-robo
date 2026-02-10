# Agent Engine Module
# google_vertex_ai_reasoning_engine を使用してエージェントをデプロイ

resource "google_vertex_ai_reasoning_engine" "homework_coach_agent" {
  provider = google-beta

  display_name = var.display_name
  description  = var.description
  region       = var.region
  project      = var.project_id

  spec {
    agent_framework = "google-adk"

    package_spec {
      pickle_object_gcs_uri    = var.pickle_gcs_uri
      requirements_gcs_uri     = var.requirements_gcs_uri
      dependency_files_gcs_uri = var.dependencies_gcs_uri
      python_version           = var.python_version
    }
  }
}
