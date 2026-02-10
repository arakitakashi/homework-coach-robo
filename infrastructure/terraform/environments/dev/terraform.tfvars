# Development Environment Variables
# Update project_id before running terraform apply

project_id  = "homework-coach-robo"
region      = "asia-northeast1"
environment = "dev"
name_prefix = "homework-coach"

# Dev-specific settings (cost optimization)
backend_min_instances  = 0     # Scale to zero when idle
frontend_min_instances = 0     # Scale to zero when idle
enable_cdn             = false # No CDN for dev

# NOTE: Redis removed - session management handled by Vertex AI / ADK

# =============================================================================
# Phase 2 Feature Flags (Issue #104 emergency fix)
# =============================================================================
# Backend requires Phase 2 environment variables for proper initialization.
# These flags enable Cloud Run env vars for tools, multi-agent, and emotion.
enable_phase2_tools       = true
enable_phase2_multi_agent = true
enable_phase2_emotion     = true
# enable_phase2_rag not needed yet (Phase 2c not fully implemented)

# =============================================================================
# Phase 3: Agent Engine (Terraform-managed deployment)
# =============================================================================
# TEMPORARY: Set to false until Agent Engine artifacts are deployed (Issue #104)
# Once CI/CD pipeline is ready and artifacts (pickle.pkl, requirements.txt,
# dependencies.tar.gz) are uploaded to GCS, this can be enabled.
enable_agent_engine = false
gcp_location        = "us-central1" # Agent Engine location
