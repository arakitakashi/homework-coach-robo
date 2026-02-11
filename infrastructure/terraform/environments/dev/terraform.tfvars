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
# Agent Engine artifacts are deployed to GCS:
#   - gs://homework-coach-assets-4592ba87/agent-engine/pickle.pkl
#   - gs://homework-coach-assets-4592ba87/agent-engine/requirements.txt
#   - gs://homework-coach-assets-4592ba87/agent-engine/dependencies.tar.gz
# CI/CD pipeline (.github/workflows/cd.yml) automatically updates artifacts on backend changes.
enable_agent_engine = true
gcp_location        = "us-central1" # Agent Engine location
