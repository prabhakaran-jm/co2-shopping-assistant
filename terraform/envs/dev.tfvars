# Development Environment Configuration
project_id = "gke10-ai-hackathon"
region = "us-central1"
cluster_name = "co2-assistant-cluster-dev"
co2_assistant_namespace = "co2-assistant"
online_boutique_namespace = "online-boutique"
artifact_registry_repo_name = "co2-assistant-repo-dev"
deletion_protection = false

# Development: Minimal Security
enable_network_policy = false
enable_managed_prometheus = true
enable_managed_cni = true

# Development: Cost Optimization
environment = "dev"
labels = {
  project     = "co2-shopping-assistant"
  environment = "dev"
  managed-by  = "terraform"
  hackathon   = "gke-turns-10"
  cost-center = "development"
}
