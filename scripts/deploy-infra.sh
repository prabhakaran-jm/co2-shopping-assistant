#!/bin/bash

# Full Infrastructure Deployment Script for CO2 Shopping Assistant
# 
# This script creates the complete infrastructure from scratch:
# - GKE Autopilot cluster via Terraform
# - Artifact Registry for Docker images
# - Builds and pushes Docker images
# - Deploys Online Boutique to online-boutique namespace
# - Deploys CO2 Assistant to co2-assistant namespace
# - Creates ingress with custom cloudcarta.com domains

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROJECT_ID=""
GEMINI_API_KEY=""
REGION="us-central1"
CLUSTER_NAME="co2-assistant-cluster"
IMAGE_TAG="latest"
TERRAFORM_BACKEND_BUCKET=""
TERRAFORM_BACKEND_PREFIX=""

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

# Function to show usage
show_usage() {
    echo "Usage: $0 --project-id PROJECT_ID [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  --project-id PROJECT_ID    Google Cloud Project ID"
    echo ""
    echo "Optional:"
    echo "  --gemini-api-key KEY       Google AI API key for Gemini"
    echo "  --region REGION            GCP region (default: us-central1)"
    echo "  --cluster-name NAME        GKE cluster name (default: co2-assistant-cluster)"
    echo "  --image-tag TAG            Docker image tag (default: latest)"
    echo "  --help                     Show this help message"
    echo ""
    echo "This script will:"
    echo "  1. Initialize Terraform with backend.hcl configuration"
    echo "  2. Create GKE Autopilot cluster and Artifact Registry"
    echo "  3. Deploy Online Boutique microservices"
    echo "  4. Deploy CO2-Aware Shopping Assistant"
    echo "  5. Set up monitoring and ingress"
    echo ""
    echo "Examples:"
    echo "  $0 --project-id my-project --gemini-api-key my-api-key"
    echo "  $0 --project-id my-project --region europe-west1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        --gemini-api-key)
            GEMINI_API_KEY="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --cluster-name)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        --image-tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$PROJECT_ID" ]]; then
    print_error "Project ID is required"
    show_usage
    exit 1
fi

# Check if API key is provided, if not prompt for it
if [[ -z "$GEMINI_API_KEY" ]]; then
    echo -n "Enter your Google AI API key: "
    read -s GEMINI_API_KEY
    echo ""
fi

if [[ -z "$GEMINI_API_KEY" ]]; then
    print_error "Google AI API key is required"
    exit 1
fi

# Backend configuration is handled by backend.hcl file
print_status "Using backend configuration from terraform/backend.hcl"

print_status "Starting deployment for CO2-Aware Shopping Assistant"
print_status "Project ID: $PROJECT_ID"
print_status "Region: $REGION"
print_status "Cluster: $CLUSTER_NAME (Autopilot)"
print_status "Image Tag: $IMAGE_TAG"

# Set project
print_status "Setting Google Cloud project..."
gcloud config set project $PROJECT_ID

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install Terraform first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Create terraform.tfvars file
print_status "Creating terraform.tfvars file..."
cat > terraform/terraform.tfvars << EOF
project_id = "$PROJECT_ID"
region = "$REGION"
cluster_name = "$CLUSTER_NAME"
co2_assistant_namespace = "co2-assistant"
online_boutique_namespace = "online-boutique"
artifact_registry_repo_name = "co2-assistant-repo"
deletion_protection = false
enable_network_policy = true
enable_managed_prometheus = true
enable_managed_cni = true
environment = "dev"
labels = {
  project     = "co2-shopping-assistant"
  environment = "dev"
  managed-by  = "terraform"
  hackathon   = "gke-turns-10"
}
EOF

# Initialize Terraform with backend configuration
print_status "Initializing Terraform..."
cd terraform

# Initialize Terraform using backend.hcl
terraform init -backend-config=backend.hcl

# Plan Terraform deployment
print_status "Planning Terraform deployment..."
terraform plan -out=tfplan

# Apply Terraform deployment
print_status "Applying Terraform deployment..."
terraform apply tfplan

# Get outputs
print_status "Getting Terraform outputs..."
CLUSTER_ENDPOINT=$(terraform output -raw cluster_endpoint)
DOCKER_REPO_URL=$(terraform output -raw docker_repository_url)
KUBECTL_CONFIG_CMD=$(terraform output -raw kubectl_config_command)
DOCKER_AUTH_CMD=$(terraform output -raw docker_auth_command)

# Set fallback values if Terraform outputs are empty
if [[ -z "$DOCKER_REPO_URL" ]]; then
    DOCKER_REPO_URL="$REGION-docker.pkg.dev/$PROJECT_ID/co2-assistant-repo"
    print_warning "Using fallback Docker repository URL: $DOCKER_REPO_URL"
fi

if [[ -z "$KUBECTL_CONFIG_CMD" ]]; then
    KUBECTL_CONFIG_CMD="gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION"
    print_warning "Using fallback kubectl config command"
fi

if [[ -z "$DOCKER_AUTH_CMD" ]]; then
    DOCKER_AUTH_CMD="gcloud auth configure-docker $REGION-docker.pkg.dev"
    print_warning "Using fallback Docker auth command"
fi

# Configure kubectl
print_status "Configuring kubectl..."
eval $KUBECTL_CONFIG_CMD

# Configure Docker authentication
print_status "Configuring Docker authentication..."
echo "Y" | eval $DOCKER_AUTH_CMD

# Clone Online Boutique if not exists
if [[ ! -d "../online-boutique" ]]; then
    print_status "Cloning Online Boutique repository..."
    cd ..
    git clone https://github.com/GoogleCloudPlatform/microservices-demo.git online-boutique
    cd terraform
fi

# Build and push CO2 Assistant Docker image
print_status "Building CO2-Aware Shopping Assistant Docker image..."
cd ..
docker build -t $DOCKER_REPO_URL/co2-assistant:$IMAGE_TAG .

print_status "Pushing Docker image to Artifact Registry..."
docker push $DOCKER_REPO_URL/co2-assistant:$IMAGE_TAG

# Deploy Online Boutique to dedicated namespace
print_status "Deploying Online Boutique microservices to 'online-boutique' namespace..."

# Create online-boutique namespace first
kubectl create namespace online-boutique --dry-run=client -o yaml | kubectl apply -f -

if [ -d "online-boutique/helm-chart" ]; then
    helm upgrade --install online-boutique online-boutique/helm-chart \
        --namespace online-boutique \
        --create-namespace \
        --wait --timeout=300s
    print_success "Online Boutique deployed via Helm"
else
    # Fallback to kubectl manifests
    kubectl apply -f online-boutique/release/kubernetes-manifests.yaml -n online-boutique
    print_success "Online Boutique deployed via kubectl manifests"
fi

# Wait for Online Boutique to be ready
print_status "Waiting for Online Boutique services to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/productcatalogservice -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/cartservice -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/checkoutservice -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/emailservice -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/paymentservice -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/recommendationservice -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/redis-cart -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/currencyservice -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/shippingservice -n online-boutique
kubectl wait --for=condition=available --timeout=300s deployment/adservice -n online-boutique

print_success "Online Boutique deployed successfully!"

# Create namespaces first
print_status "Creating namespaces..."
kubectl apply -f k8s/namespaces.yaml

# Deploy CO2-Aware Shopping Assistant with updated image
print_status "Deploying CO2-Aware Shopping Assistant..."

# Create ConfigMap for UI files
print_status "Creating ConfigMap for UI files..."
kubectl create configmap co2-assistant-ui-config \
  --from-file=src/ui/index.html \
  --from-file=src/ui/style.css \
  --from-file=src/ui/script.js \
  -n co2-assistant --dry-run=client -o yaml | kubectl apply -f -

# Create a temporary file with updated image
sed "s|us-central1-docker.pkg.dev/PROJECT_ID/co2-assistant-repo/co2-assistant:latest|$DOCKER_REPO_URL/co2-assistant:$IMAGE_TAG|g" \
    k8s/co2-assistant-deployment.yaml | kubectl apply -f -
kubectl apply -f k8s/ui-deployment.yaml

# Wait for our deployments to be ready
print_status "Waiting for CO2-Aware Shopping Assistant to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/co2-assistant -n co2-assistant
kubectl wait --for=condition=available --timeout=300s deployment/co2-assistant-ui -n co2-assistant

# Create secrets
print_status "Creating secrets..."
kubectl create secret generic co2-assistant-secrets \
    --namespace=co2-assistant \
    --from-literal=google-ai-api-key="$GEMINI_API_KEY" \
    --from-literal=google-project-id="$PROJECT_ID" \
    --dry-run=client -o yaml | kubectl apply -f -

# Deploy ob-proxy for cross-namespace routing
print_status "Deploying ob-proxy for cross-namespace routing..."
kubectl apply -f k8s/ob-proxy.yaml

# Create managed certificate
print_status "Creating managed certificate..."
cat <<EOF | kubectl apply -f -
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: co2-assistant-cert
  namespace: co2-assistant
spec:
  domains:
    - assistant.cloudcarta.com
    - ob.cloudcarta.com
EOF

# Wait for certificate to be ready
print_status "Waiting for certificate to be ready..."
kubectl wait --for=condition=Ready --timeout=300s managedcertificate/co2-assistant-cert -n co2-assistant || print_warning "Certificate may take longer to provision"

# Deploy unified ingress with custom domain
print_status "Deploying unified ingress with custom domain..."
kubectl apply -f k8s/managed-certificate.yaml
kubectl apply -f k8s/https-ingress.yaml

# No cleanup needed - using direct kubectl apply with sed

# Get service URLs
print_status "Getting service information..."
CO2_BACKEND_URL=$(kubectl get service co2-assistant-service -n co2-assistant -o jsonpath='{.status.loadBalancer.ingress[0].ip}' || echo "Pending")
CO2_UI_URL=$(kubectl get service co2-assistant-ui-service -n co2-assistant -o jsonpath='{.status.loadBalancer.ingress[0].ip}' || echo "Pending")
BOUTIQUE_URL=$(kubectl get service frontend -n online-boutique -o jsonpath='{.status.loadBalancer.ingress[0].ip}' || echo "Pending")

print_success "Complete deployment completed successfully!"
echo ""
print_status "Service URLs (HTTPS-only):"
echo "  🌱 CO2-Aware Shopping Assistant: https://assistant.cloudcarta.com"
echo "  🛍️ Online Boutique: https://ob.cloudcarta.com"
echo ""
print_status "🔒 Security Features Enabled:"
echo "  - HTTPS enforcement (HTTP traffic blocked)"
echo "  - TLS 1.2+ with secure ciphers"
echo "  - HSTS headers with preload"
echo "  - Security headers (XSS, CSRF, clickjacking protection)"
echo "  - Content Security Policy"
echo "  - Rate limiting (100 requests/minute)"
echo ""
print_status "Direct Service IPs:"
echo "  CO2 Assistant Backend: http://$CO2_BACKEND_URL"
echo "  CO2 Assistant UI: http://$CO2_UI_URL"
echo "  Online Boutique: http://$BOUTIQUE_URL"
echo ""
print_status "Terraform State:"
echo "  Backend Configuration: terraform/backend.hcl"
echo ""
print_status "To check deployment status:"
echo "  kubectl get pods -n co2-assistant"
echo "  kubectl get pods -n online-boutique"
echo "  kubectl get services -n co2-assistant"
echo "  kubectl get services -n online-boutique"
echo "  kubectl get ingress https-ingress -n co2-assistant"
echo ""
print_status "To view logs:"
echo "  kubectl logs -f deployment/co2-assistant -n co2-assistant"
echo "  kubectl logs -f deployment/frontend -n online-boutique"
echo ""
print_status "To destroy infrastructure:"
echo "  cd terraform && terraform destroy"
echo ""
print_status "Architecture Overview:"
echo "  ┌─────────────────────────────────────────────────────────┐"
echo "  │  GKE Autopilot Cluster (Terraform Managed)             │"
echo "  ├─────────────────────────────────────────────────────────┤"
echo "  │  Online Boutique (online-boutique namespace)           │"
echo "  │  ├─ Frontend, Product Catalog, Cart, Checkout, etc.     │"
echo "  │  └─ Traditional microservices                         │"
echo "  ├─────────────────────────────────────────────────────────┤"
echo "  │  CO2-Aware Shopping Assistant (co2-assistant ns)      │"
echo "  │  ├─ AI Agents (ADK + Gemini)                          │"
echo "  │  ├─ A2A Protocol                                       │"
echo "  │  ├─ MCP Servers                                        │"
echo "  │  └─ Modern Web UI                                     │"
echo "  └─────────────────────────────────────────────────────────┘"
echo ""
print_success "🌱 Complete infrastructure deployed successfully!"
print_success "🛍️ Online Boutique provides the base microservices"
print_success "🤖 CO2-Aware Shopping Assistant enhances it with AI agents"
print_success "🚀 Ready to demonstrate Agentic AI Microservices 2.0!"
print_success "📊 Infrastructure as Code with Terraform!"
