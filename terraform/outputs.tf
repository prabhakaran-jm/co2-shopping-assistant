# Cluster Information
output "cluster_name" {
  description = "The name of the GKE cluster"
  value       = google_container_cluster.autopilot.name
}

output "cluster_endpoint" {
  description = "The endpoint of the GKE cluster"
  value       = google_container_cluster.autopilot.endpoint
  sensitive   = true
}

output "cluster_location" {
  description = "The location of the GKE cluster"
  value       = google_container_cluster.autopilot.location
}

output "cluster_ca_certificate" {
  description = "The CA certificate of the GKE cluster"
  value       = google_container_cluster.autopilot.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

# Artifact Registry Information
output "artifact_registry_repository" {
  description = "The Artifact Registry repository"
  value       = google_artifact_registry_repository.co2_assistant_repo.name
}

output "artifact_registry_location" {
  description = "The location of the Artifact Registry repository"
  value       = google_artifact_registry_repository.co2_assistant_repo.location
}

output "docker_repository_url" {
  description = "The Docker repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo_name}"
}

# Service Account Information
output "service_account_email" {
  description = "The email of the CO2 Assistant service account"
  value       = google_service_account.co2_assistant_sa.email
}

# Namespace Information
output "co2_assistant_namespace" {
  description = "The Kubernetes namespace for CO2-Aware Shopping Assistant"
  value       = kubernetes_namespace.co2_assistant.metadata[0].name
}

output "online_boutique_namespace" {
  description = "The Kubernetes namespace for Online Boutique"
  value       = kubernetes_namespace.online_boutique.metadata[0].name
}

# Connection Information
output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.autopilot.name} --region ${google_container_cluster.autopilot.location}"
}

output "docker_auth_command" {
  description = "Command to configure Docker authentication"
  value       = "gcloud auth configure-docker ${var.region}-docker.pkg.dev"
}

# Deployment Information
output "deployment_instructions" {
  description = "Instructions for deploying the application"
  value = <<-EOT
    # 1. Configure kubectl
    gcloud container clusters get-credentials ${google_container_cluster.autopilot.name} --region ${google_container_cluster.autopilot.location}
    
    # 2. Configure Docker authentication
    gcloud auth configure-docker ${var.region}-docker.pkg.dev
    
    # 3. Build and push Docker images
    docker build -t ${google_artifact_registry_repository.co2_assistant_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.co2_assistant_repo.repository_id}/co2-assistant:latest .
    docker push ${google_artifact_registry_repository.co2_assistant_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.co2_assistant_repo.repository_id}/co2-assistant:latest
    
    # 4. Deploy Online Boutique
    kubectl apply -f online-boutique/release/kubernetes-manifests.yaml
    
    # 5. Deploy CO2-Aware Shopping Assistant
    kubectl apply -f k8s/
    
    # 6. Set up secrets
    kubectl create secret generic co2-assistant-secrets \
      --namespace=${kubernetes_namespace.co2_assistant.metadata[0].name} \
      --from-literal=google-ai-api-key="YOUR_API_KEY"
  EOT
}

# Monitoring Information
output "monitoring_dashboard_url" {
  description = "URL to the Google Cloud Monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards?project=${var.project_id}"
}

output "logging_url" {
  description = "URL to the Google Cloud Logging"
  value       = "https://console.cloud.google.com/logs?project=${var.project_id}"
}
