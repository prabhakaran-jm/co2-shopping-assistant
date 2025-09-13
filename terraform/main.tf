# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Configure the Kubernetes Provider
provider "kubernetes" {
  host                   = "https://${google_container_cluster.autopilot.endpoint}"
  token                  = data.google_client_config.current.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.autopilot.master_auth[0].cluster_ca_certificate)
  
  # Add timeout configuration
  timeout {
    create = "30m"
    update = "30m"
    delete = "30m"
  }
}

# Configure the Helm Provider
provider "helm" {
  kubernetes {
    host                   = google_container_cluster.autopilot.endpoint
    token                  = data.google_client_config.current.access_token
    cluster_ca_certificate = base64decode(google_container_cluster.autopilot.master_auth[0].cluster_ca_certificate)
  }
  
  # Add timeout configuration
  timeout {
    create = "30m"
    update = "30m"
    delete = "30m"
  }
}

# Get current client configuration
data "google_client_config" "current" {}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "container.googleapis.com",
    "artifactregistry.googleapis.com",
    "aiplatform.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "cloudprofiler.googleapis.com",
    "cloudbuild.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# Create Artifact Registry repository
resource "google_artifact_registry_repository" "co2_assistant_repo" {
  depends_on = [google_project_service.required_apis]

  location      = var.region
  repository_id = var.artifact_registry_repo_name
  description   = "Docker repository for CO2-Aware Shopping Assistant"
  format        = "DOCKER"

  labels = var.labels
  # Keep only the 10 most recent versions per image (package)
  cleanup_policies {
    id     = "keep-last-10"
    action = "KEEP"

    most_recent_versions {
      keep_count = 10
      # Optional: limit to certain images in this repo
      # package_name_prefixes = ["co2-assistant"]
    }
  }

  # Optional: set to true to dry-run the policy only
  # cleanup_policy_dry_run = true  
}

# Create GKE Autopilot cluster
resource "google_container_cluster" "autopilot" {
  depends_on = [google_project_service.required_apis]

  name                = var.cluster_name
  location            = var.region
  enable_autopilot    = true
  deletion_protection = var.deletion_protection

  release_channel {
    channel = var.release_channel
  }

  lifecycle {
    ignore_changes = [
      # Ignore changes to node_config as Autopilot manages this
      node_config,
      # Ignore changes to master_auth as it's managed by GKE
      master_auth
    ]
  }
}

# Create Kubernetes namespace for CO2-Aware Shopping Assistant
resource "kubernetes_namespace" "co2_assistant" {
  depends_on = [google_container_cluster.autopilot]

  metadata {
    name = var.co2_assistant_namespace
    labels = merge(var.labels, {
      name = var.co2_assistant_namespace
    })
  }
}

# Create Kubernetes namespace for Online Boutique
resource "kubernetes_namespace" "online_boutique" {
  depends_on = [google_container_cluster.autopilot]

  metadata {
    name = var.online_boutique_namespace
    labels = merge(var.labels, {
      name = var.online_boutique_namespace
    })
  }
}

# Create secrets for CO2-Aware Shopping Assistant
resource "kubernetes_secret" "co2_assistant_secrets" {
  depends_on = [kubernetes_namespace.co2_assistant]

  metadata {
    name      = "co2-assistant-secrets"
    namespace = var.co2_assistant_namespace
    labels    = var.labels
  }

  type = "Opaque"

  data = {
    google-project-id = var.project_id
    # Note: google-ai-api-key should be set manually or via CI/CD
    # kubectl create secret generic co2-assistant-secrets \
    #   --namespace=co2-assistant \
    #   --from-literal=google-ai-api-key="YOUR_API_KEY"
  }
}

# Create ConfigMap for application configuration
resource "kubernetes_config_map" "co2_assistant_config" {
  depends_on = [kubernetes_namespace.co2_assistant]

  metadata {
    name      = "co2-assistant-config"
    namespace = var.co2_assistant_namespace
    labels    = var.labels
  }

  data = {
    PROJECT_ID           = var.project_id
    LOCATION            = var.region
    ONLINE_BOUTIQUE_URL = "http://frontend.${var.online_boutique_namespace}.svc.cluster.local"
    CO2_API_URL         = "https://api.co2data.org"
    ENVIRONMENT         = var.environment
    LOG_LEVEL           = "INFO"
  }
}

# Create Service Account for CO2-Aware Shopping Assistant
resource "google_service_account" "co2_assistant_sa" {
  account_id   = "co2-assistant-sa"
  display_name = "CO2-Aware Shopping Assistant Service Account"
  description  = "Service account for CO2-Aware Shopping Assistant application"
}

# Grant necessary IAM roles to the service account
resource "google_project_iam_member" "co2_assistant_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/cloudtrace.agent",
    "roles/storage.objectViewer"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.co2_assistant_sa.email}"
}

# Create Workload Identity binding
resource "google_service_account_iam_binding" "co2_assistant_workload_identity" {
  service_account_id = google_service_account.co2_assistant_sa.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[${var.co2_assistant_namespace}/co2-assistant-sa]"
  ]
}

# Create Kubernetes Service Account with Workload Identity annotation
resource "kubernetes_service_account" "co2_assistant_sa" {
  depends_on = [kubernetes_namespace.co2_assistant]

  metadata {
    name      = "co2-assistant-sa"
    namespace = var.co2_assistant_namespace
    labels    = var.labels
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.co2_assistant_sa.email
    }
  }
}


