terraform {
  required_version = ">= 1.5.0, < 2.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.40, < 6.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.20, < 3.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.10, < 3.0"
    }
  }
}
