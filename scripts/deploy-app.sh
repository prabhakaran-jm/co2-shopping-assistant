#!/bin/bash

# Application-Only Deployment Script for CO2 Shopping Assistant with Online Boutique
# 
# This script deploys applications to an EXISTING Kubernetes cluster.
# For full infrastructure deployment (cluster creation), use deploy-infra.sh
# 
# Prerequisites:
# - Existing Kubernetes cluster (GKE recommended)
# - kubectl configured and connected to cluster
# - helm installed
# - Online Boutique helm chart at ../online-boutique/helm-chart
#
# This script deploys both services with proper namespace separation

set -e

echo "🚀 Starting unified deployment of CO2 Shopping Assistant with Online Boutique..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    print_error "helm is not installed or not in PATH"
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Not connected to a Kubernetes cluster"
    exit 1
fi

print_status "Connected to cluster: $(kubectl config current-context)"

# Step 1: Create namespaces
print_status "Creating namespaces..."
kubectl apply -f k8s/namespaces.yaml
print_success "Namespaces created"

# Step 2: Deploy Online Boutique to its dedicated namespace
print_status "Deploying Online Boutique to 'online-boutique' namespace..."
if [ -d "online-boutique/helm-chart" ]; then
    helm upgrade --install online-boutique online-boutique/helm-chart \
        --namespace online-boutique \
        --create-namespace \
        --values k8s/online-boutique-namespace-config.yaml \
        --wait --timeout=300s
    print_success "Online Boutique deployed"
else
    print_error "Online Boutique helm chart not found at online-boutique/helm-chart"
    exit 1
fi

# Step 3: Deploy CO2 Assistant
print_status "Deploying CO2 Assistant to 'co2-assistant' namespace..."
kubectl apply -f k8s/co2-assistant-deployment.yaml
kubectl apply -f k8s/ui-deployment.yaml
print_success "CO2 Assistant deployed"

# Step 4: Deploy managed certificate and ingress
print_status "Deploying managed certificate..."
kubectl apply -f k8s/managed-certificate.yaml
print_success "Managed certificate deployed"

print_status "Deploying HTTPS ingress..."
kubectl apply -f k8s/https-ingress.yaml
print_success "HTTPS ingress deployed"

# Step 5: Wait for deployments to be ready
print_status "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/co2-assistant -n co2-assistant
kubectl wait --for=condition=available --timeout=300s deployment/co2-assistant-ui -n co2-assistant
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n online-boutique
print_success "All deployments are ready"

# Step 6: Get ingress information
print_status "Getting ingress information..."
INGRESS_IP=$(kubectl get ingress https-ingress -n co2-assistant -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

if [ "$INGRESS_IP" = "pending" ] || [ -z "$INGRESS_IP" ]; then
    print_warning "Ingress IP is still being assigned. You can check with:"
    print_warning "kubectl get ingress https-ingress -n co2-assistant"
else
    print_success "Ingress IP: $INGRESS_IP"
    echo ""
    print_success "🎉 Deployment completed successfully!"
    echo ""
    echo "Access your services (HTTPS-only):"
    echo "  CO2 Assistant UI: https://assistant.cloudcarta.com"
    echo "  CO2 Assistant API: https://assistant.cloudcarta.com/api"
    echo "  Online Boutique: https://ob.cloudcarta.com"
    echo ""
    echo "🔒 Security: All traffic is HTTPS-only with security headers and HSTS enabled"
    echo "Note: DNS configuration may take a few minutes to propagate."
fi

# Step 7: Show useful commands
echo ""
print_status "Useful commands:"
echo "  Check CO2 Assistant status: kubectl get pods -n co2-assistant"
echo "  Check Online Boutique status: kubectl get pods -n online-boutique"
echo "  Check ingress status: kubectl get ingress -n co2-assistant"
echo "  View logs: kubectl logs -f deployment/co2-assistant -n co2-assistant"
echo "  Delete everything: kubectl delete namespace co2-assistant online-boutique"
