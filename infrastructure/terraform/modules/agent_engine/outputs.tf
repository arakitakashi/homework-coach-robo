# Agent Engine Module Outputs

output "resource_name" {
  description = "The full resource name of the Agent Engine"
  value       = google_vertex_ai_reasoning_engine.homework_coach_agent.id
}

output "engine_id" {
  description = "The ID of the Agent Engine"
  value       = element(split("/", google_vertex_ai_reasoning_engine.homework_coach_agent.name), length(split("/", google_vertex_ai_reasoning_engine.homework_coach_agent.name)) - 1)
}

output "display_name" {
  description = "The display name of the Agent Engine"
  value       = google_vertex_ai_reasoning_engine.homework_coach_agent.display_name
}

output "region" {
  description = "The region of the Agent Engine"
  value       = google_vertex_ai_reasoning_engine.homework_coach_agent.region
}
