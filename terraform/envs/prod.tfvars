# Production Environment Configuration
project_id = "gke10-ai-hackathon"
region = "us-central1"
cluster_name = "co2-assistant-cluster-prod"
co2_assistant_namespace = "co2-assistant"
online_boutique_namespace = "online-boutique"
artifact_registry_repo_name = "co2-assistant-repo-prod"
deletion_protection = true

# Production: Full Security
enable_network_policy = true
enable_managed_prometheus = true
enable_managed_cni = true

# Production: High Availability
environment = "prod"
labels = {
  project     = "co2-shopping-assistant"
  environment = "prod"
  managed-by  = "terraform"
  hackathon   = "gke-turns-10"
  cost-center = "production"
  compliance  = "required"
}
