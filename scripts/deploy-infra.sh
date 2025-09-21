#!/bin/bash

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Default values (can be overridden by .env file or command line)
PROJECT_ID="${GOOGLE_PROJECT_ID:-${PROJECT_ID:-}}"
GEMINI_API_KEY="${GOOGLE_AI_API_KEY:-}"
REGION="${GCP_REGION:-us-central1}"
CLUSTER_NAME="${GKE_CLUSTER_NAME:-co2-assistant-cluster}"
IMAGE_TAG="${DOCKER_IMAGE_TAG:-latest}"
ENVIRONMENT="${ENVIRONMENT:-}"
FORCE_DEPLOYMENT="${FORCE_DEPLOYMENT:-false}"

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
    echo "  --environment ENV          Environment: dev or prod (optional, for app configs only)"
    echo "  --help                     Show this help message"
    echo ""
    echo "This script creates the complete infrastructure:"
    echo "  ✅ GKE Autopilot cluster"
    echo "  ✅ Artifact Registry repository"
    echo "  ✅ Service accounts and IAM bindings"
    echo "  ✅ Basic Kubernetes resources"
    echo ""
    echo "Note: Infrastructure is shared across environments. Environment-specific"
    echo "configurations (security policies, monitoring) are applied during app deployment."
    echo ""
    echo "Backend Configuration:"
    echo "  - Uses backend.hcl by default"
    echo "  - Uses backend-ENV.hcl if environment-specific backend exists"
    echo "  - Example: --environment prod uses backend-prod.hcl (if exists)"
    echo ""
    echo "After infrastructure deployment, use deploy-app.sh to deploy applications:"
    echo "  ./scripts/deploy-app.sh --project-id PROJECT_ID --gemini-api-key KEY"
    echo "  ./scripts/deploy-app.sh --project-id PROJECT_ID --gemini-api-key KEY --environment prod"
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
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --force)
            FORCE_DEPLOYMENT="true"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$PROJECT_ID" ]]; then
    log_error "Project ID is required"
    show_usage
    exit 1
fi

# Show script header
show_script_header "CO2-Aware Shopping Assistant Infrastructure Deployment"

# Check required tools
if ! check_required_tools "terraform" "gcloud" "kubectl"; then
    exit 1
fi

# Confirmation prompt
if [[ "$FORCE_DEPLOYMENT" == "false" ]]; then
    log_info "This will create the complete infrastructure:"
    echo "  ✅ GKE Autopilot cluster"
    echo "  ✅ Artifact Registry repository"
    echo "  ✅ Service accounts and IAM bindings"
    echo "  ✅ Basic Kubernetes resources"
    echo ""
    log_info "After infrastructure deployment, use deploy-app.sh to deploy applications:"
    echo "  ./scripts/deploy-app.sh --project-id $PROJECT_ID --gemini-api-key YOUR_KEY"
    echo ""
    if ! confirm_action "Continue with infrastructure deployment?"; then
        log_info "Deployment cancelled by user"
        exit 0
    fi
fi

# Set project
log_info "Setting Google Cloud project..."
gcloud config set project "$PROJECT_ID"

# Initialize Terraform using appropriate backend configuration
cd terraform

# Determine backend configuration based on environment
local backend_config="backend.hcl"
if [[ -n "$ENVIRONMENT" && -f "envs/${ENVIRONMENT}.tfvars" && -f "backend-${ENVIRONMENT}.hcl" ]]; then
    backend_config="backend-${ENVIRONMENT}.hcl"
    log_info "Using environment-specific backend: $backend_config"
else
    log_info "Using default backend: $backend_config"
fi

log_info "Initializing Terraform with backend: $backend_config..."
terraform init -backend-config="$backend_config"

# Plan Terraform deployment (with optional environment-specific variables)
log_info "Planning Terraform deployment..."
if [[ -n "$ENVIRONMENT" && -f "envs/${ENVIRONMENT}.tfvars" ]]; then
    log_info "Using environment-specific configuration: envs/${ENVIRONMENT}.tfvars"
    terraform plan -var-file="envs/${ENVIRONMENT}.tfvars" -out=tfplan
else
    log_info "Using default Terraform configuration (no environment-specific variables)"
    terraform plan -out=tfplan
fi

# Apply Terraform deployment
log_info "Applying Terraform deployment..."
terraform apply tfplan

# Get cluster endpoint and configure kubectl (after cluster is created)
log_info "Configuring kubectl for cluster..."
gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"

# Configure Docker authentication
log_info "Configuring Docker authentication..."
DOCKER_REPO_URL="$REGION-docker.pkg.dev/$PROJECT_ID/co2-assistant-repo"
DOCKER_AUTH_CMD="gcloud auth configure-docker $REGION-docker.pkg.dev --quiet"
echo "Y" | eval $DOCKER_AUTH_CMD

# Infrastructure deployment completed
print_success "Infrastructure deployment completed successfully!"

# Show infrastructure information
echo ""
print_status "Infrastructure Information:"
echo "  🏗️ GKE Autopilot Cluster: $CLUSTER_NAME"
echo "  📦 Artifact Registry: $DOCKER_REPO_URL"
echo "  🔑 Service Account: co2-assistant-sa@$PROJECT_ID.iam.gserviceaccount.com"
echo "  🌐 Region: $REGION"
echo ""
print_status "Terraform State:"
echo "  Backend Configuration: terraform/backend.hcl"
echo ""
print_status "🎯 NEXT STEPS:"
print_status "   Your infrastructure is ready! Now deploy the applications:"
print_status "   ./scripts/deploy-app.sh --project-id $PROJECT_ID --gemini-api-key YOUR_KEY"
echo ""
print_status "💡 Application deployment provides:"
print_status "   ✅ CO2 Assistant and Online Boutique applications"
print_status "   ✅ Docker image building and pushing"
print_status "   ✅ Ingress and certificate configuration"
print_status "   ✅ Environment-specific configurations (dev/prod)"
echo ""
print_status "To check infrastructure status:"
echo "  gcloud container clusters list"
echo "  gcloud artifacts repositories list"
echo "  kubectl cluster-info"
echo ""
print_status "To destroy infrastructure:"
echo "  ./scripts/teardown-infra.sh --project-id $PROJECT_ID --force"

# Show script footer
show_script_footer "Infrastructure deployment completed successfully!"
