# Project Configuration
variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "us-central1-a"
}

# Cluster Configuration
variable "cluster_name" {
  description = "The name of the GKE cluster"
  type        = string
  default     = "co2-assistant-cluster"
}

variable "release_channel" {
  description = "The GKE release channel"
  type        = string
  default     = "REGULAR"
}

# Application Configuration
variable "co2_assistant_namespace" {
  description = "Kubernetes namespace for CO2-Aware Shopping Assistant"
  type        = string
  default     = "co2-assistant"
}

variable "online_boutique_namespace" {
  description = "Kubernetes namespace for Online Boutique"
  type        = string
  default     = "default"
}

# Artifact Registry Configuration
variable "artifact_registry_repo_name" {
  description = "Name of the Artifact Registry repository"
  type        = string
  default     = "co2-assistant-repo"
}

# Security Configuration
variable "deletion_protection" {
  description = "Enable deletion protection for the cluster"
  type        = bool
  default     = false
}


# Monitoring Configuration
variable "enable_managed_prometheus" {
  description = "Enable Google Cloud Managed Service for Prometheus"
  type        = bool
  default     = true
}

variable "enable_managed_cni" {
  description = "Enable Google Cloud CNI"
  type        = bool
  default     = true
}

variable "enable_network_policy" {
  description = "Enable network policy enforcement"
  type        = bool
  default     = true
}

# Environment Configuration
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Labels
variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default = {
    project     = "co2-shopping-assistant"
    environment = "dev"
    managed-by  = "terraform"
    hackathon   = "gke-turns-10"
  }
}
