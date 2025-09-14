#!/bin/bash

# Application Deployment Script for CO2 Shopping Assistant
# This script deploys the CO2 Assistant and Online Boutique applications to an existing cluster

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Load environment variables from .env file if it exists
if [[ -f ".env" ]]; then
    log_info "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Script configuration
SCRIPT_NAME="CO2 Assistant Application Deployment"
SCRIPT_DESCRIPTION="Deploys CO2 Assistant and Online Boutique applications to existing cluster"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --project-id PROJECT_ID    Google Cloud Project ID (required)"
    echo "  --gemini-api-key KEY       Google AI API key for Gemini (required)"
    echo "  --region REGION            GCP region (default: us-central1)"
    echo "  --cluster-name NAME        GKE cluster name (default: co2-assistant-cluster)"
    echo "  --image-tag TAG            Docker image tag (default: latest)"
    echo "  --environment ENV          Environment: dev or prod (default: dev)"
    echo "                             Uses terraform/envs/ENV.tfvars for app-specific configs"
    echo "  --clean                    Clean existing resources before deployment (slower)"
    echo "  --minimal                  Use minimal resources for faster deployment"
    echo "  --no-cert                  Skip certificate creation (HTTP only)"
    echo "  --force                    Skip confirmation prompts"
    echo "  --help                     Show this help message"
    echo ""
    echo "Environment-specific configurations:"
    echo "  dev:  Minimal security, development-optimized settings"
    echo "  prod: Full security, production-grade policies and monitoring"
    echo ""
    echo "Examples:"
    echo "  $0 --project-id my-project --gemini-api-key my-key"
    echo "  $0 --project-id my-project --gemini-api-key my-key --environment prod"
    echo "  $0 --project-id my-project --gemini-api-key my-key --clean  # Force cleanup"
}

# Default values (can be overridden by .env file or command line)
PROJECT_ID="${PROJECT_ID:-}"
GEMINI_API_KEY="${GOOGLE_AI_API_KEY:-}"
REGION="${GCP_REGION:-us-central1}"
CLUSTER_NAME="${CLUSTER_NAME:-co2-assistant-cluster}"
IMAGE_TAG="${DOCKER_IMAGE_TAG:-latest}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
CLEAN_DEPLOYMENT="${CLEAN_DEPLOYMENT:-false}"
MINIMAL_RESOURCES="${MINIMAL_RESOURCES:-false}"
SKIP_CERTIFICATE="${SKIP_CERTIFICATE:-false}"
FORCE_DEPLOYMENT="${FORCE_DEPLOYMENT:-false}"

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
        --clean)
            CLEAN_DEPLOYMENT=true
            shift
            ;;
        --minimal)
            MINIMAL_RESOURCES=true
            shift
            ;;
        --no-cert)
            SKIP_CERTIFICATE=true
            shift
            ;;
        --force)
            FORCE_DEPLOYMENT=true
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

# Main deployment function
deploy_applications() {
    local project_root
    project_root="$(get_project_root)"
    
    # Change to project root
    cd "$project_root"
    
    log_info "Starting application deployment for CO2 Shopping Assistant"
    log_info "Project ID: $PROJECT_ID"
    log_info "Region: $REGION"
    log_info "Cluster: $CLUSTER_NAME"
    log_info "Environment: $ENVIRONMENT"
    log_info "Image Tag: $IMAGE_TAG"
    
    # Load environment-specific configuration if available
    local env_config_file="terraform/envs/${ENVIRONMENT}.tfvars"
    local enable_network_policy="false"
    local enable_managed_prometheus="true"
    local enable_managed_cni="true"
    
    if [[ -f "$env_config_file" ]]; then
        log_info "Loading environment-specific configuration from $env_config_file"
        # Extract key configuration values from tfvars file
        enable_network_policy=$(grep "enable_network_policy" "$env_config_file" | cut -d'=' -f2 | tr -d ' ' || echo "false")
        enable_managed_prometheus=$(grep "enable_managed_prometheus" "$env_config_file" | cut -d'=' -f2 | tr -d ' ' || echo "true")
        enable_managed_cni=$(grep "enable_managed_cni" "$env_config_file" | cut -d'=' -f2 | tr -d ' ' || echo "true")
        
        log_info "Environment configuration loaded:"
        log_info "  Network Policy: $enable_network_policy"
        log_info "  Managed Prometheus: $enable_managed_prometheus"
        log_info "  Managed CNI: $enable_managed_cni"
    else
        log_info "No environment-specific configuration found at $env_config_file"
        log_info "Using default application settings"
    fi
    
    # Validate required parameters
    if ! validate_env_vars "PROJECT_ID" "GEMINI_API_KEY"; then
        exit 1
    fi
    
    # Check required tools
    if ! check_required_tools "kubectl" "docker" "gcloud"; then
        exit 1
    fi
    
    # Check kubectl connectivity
    if ! check_kubectl_connectivity; then
        exit 1
    fi
    
    # Confirmation prompt
    if [[ "$FORCE_DEPLOYMENT" == "false" ]]; then
        log_info "This will deploy applications to your existing cluster:"
        echo "  - CO2 Assistant (co2-assistant namespace)"
        echo "  - Online Boutique (online-boutique namespace)"
        echo "  - Docker images will be built and pushed"
        echo "  - Ingress and certificates will be configured"
        echo ""
        if ! confirm_action "Continue with deployment?"; then
            log_info "Deployment cancelled by user"
            exit 0
        fi
    fi
    
    # Set project
    log_info "Setting Google Cloud project..."
    gcloud config set project "$PROJECT_ID"
    
    # Get cluster endpoint and configure kubectl
    log_info "Configuring kubectl for cluster..."
    gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"
    
    # Configure Docker authentication
    log_info "Configuring Docker authentication..."
    gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
    
    # Build and push Docker images
    log_info "Building and pushing Docker images..."
    local docker_repo_url="$REGION-docker.pkg.dev/$PROJECT_ID/co2-assistant-repo"
    
    # Clone Online Boutique if not exists
    if [[ ! -d "online-boutique" ]]; then
        log_info "Cloning Online Boutique repository..."
        git clone https://github.com/GoogleCloudPlatform/microservices-demo.git online-boutique
    fi
    
    # Build CO2 Assistant image
    log_info "Building CO2 Assistant Docker image..."
    print_warning "This may take 5-15 minutes depending on image size..."
    docker build -t "$docker_repo_url/co2-assistant:$IMAGE_TAG" .
    
    log_info "Pushing CO2 Assistant image..."
    print_warning "This may take 3-10 minutes depending on network speed..."
    docker push "$docker_repo_url/co2-assistant:$IMAGE_TAG"
    
    # Deploy Online Boutique to dedicated namespace
    log_info "Deploying Online Boutique microservices to 'online-boutique' namespace..."
    
    # Create online-boutique namespace first
    kubectl create namespace online-boutique --dry-run=client -o yaml | kubectl apply -f -
    
    # Clean up existing resources only if requested (for faster deployments)
    if [[ "$CLEAN_DEPLOYMENT" == "true" ]]; then
        log_info "Cleaning up existing resources in online-boutique namespace..."
        kubectl delete all --all -n online-boutique --ignore-not-found=true
        kubectl delete serviceaccounts --all -n online-boutique --ignore-not-found=true
        kubectl delete configmaps --all -n online-boutique --ignore-not-found=true
        kubectl delete secrets --all -n online-boutique --ignore-not-found=true
        log_info "Cleanup completed. Proceeding with fresh deployment..."
    else
        log_info "Skipping cleanup for faster deployment. Use --clean to force cleanup if needed."
    fi
    
    if [[ -d "online-boutique/helm-chart" ]]; then
        helm upgrade --install online-boutique online-boutique/helm-chart \
            --namespace online-boutique \
            --create-namespace \
            --set frontend.replicaCount=1 \
            --set frontend.externalService=false \
            --set adservice.replicaCount=1 \
            --set cartservice.replicaCount=1 \
            --set checkoutservice.replicaCount=1 \
            --set currencyservice.replicaCount=1 \
            --set emailservice.replicaCount=1 \
            --set loadgenerator.replicaCount=1 \
            --set paymentservice.replicaCount=1 \
            --set productcatalogservice.replicaCount=1 \
            --set recommendationservice.replicaCount=1 \
            --set shippingservice.replicaCount=1 \
            --wait --timeout=900s
        log_success "Online Boutique deployed via Helm"
    else
        # Fallback to kubectl manifests
        kubectl apply -f online-boutique/release/kubernetes-manifests.yaml -n online-boutique
        log_success "Online Boutique deployed via kubectl manifests"
    fi
    
    # Wait for Online Boutique to be ready (with timeout handling)
    log_info "Waiting for Online Boutique services to be ready..."
    print_warning "This may take 5-10 minutes. Services will be checked in parallel where possible."
    
    # Critical services first
    kubectl wait --for=condition=available --timeout=300s deployment/frontend -n online-boutique &
    kubectl wait --for=condition=available --timeout=300s deployment/productcatalogservice -n online-boutique &
    kubectl wait --for=condition=available --timeout=300s deployment/cartservice -n online-boutique &
    wait
    
    # Secondary services
    kubectl wait --for=condition=available --timeout=300s deployment/checkoutservice -n online-boutique &
    kubectl wait --for=condition=available --timeout=300s deployment/emailservice -n online-boutique &
    kubectl wait --for=condition=available --timeout=300s deployment/paymentservice -n online-boutique &
    wait
    
    # Supporting services
    kubectl wait --for=condition=available --timeout=300s deployment/recommendationservice -n online-boutique &
    kubectl wait --for=condition=available --timeout=300s deployment/redis-cart -n online-boutique &
    kubectl wait --for=condition=available --timeout=300s deployment/currencyservice -n online-boutique &
    wait
    
    # Final services
    kubectl wait --for=condition=available --timeout=300s deployment/shippingservice -n online-boutique &
    kubectl wait --for=condition=available --timeout=300s deployment/adservice -n online-boutique &
    wait
    
    log_success "Online Boutique deployed successfully!"
    
    # Create namespaces first
    log_info "Creating namespaces..."
    kubectl apply -f k8s/namespaces.yaml
    
    # Deploy CO2-Aware Shopping Assistant with updated image
    log_info "Deploying CO2-Aware Shopping Assistant..."
    
    # Create ConfigMap for UI files
    log_info "Creating ConfigMap for UI files..."
    kubectl apply -f k8s/ui-configmap.yaml
    
    # Create a temporary file with updated image and resource optimization
    if [[ "$MINIMAL_RESOURCES" == "true" ]]; then
        log_info "Using minimal resources for faster deployment..."
        sed "s|us-central1-docker.pkg.dev/PROJECT_ID/co2-assistant-repo/co2-assistant:latest|$docker_repo_url/co2-assistant:$IMAGE_TAG|g" \
            k8s/co2-assistant-deployment.yaml | \
        sed 's/replicas: [0-9]*/replicas: 1/g' | \
        kubectl apply -f -
    else
        sed "s|us-central1-docker.pkg.dev/PROJECT_ID/co2-assistant-repo/co2-assistant:latest|$docker_repo_url/co2-assistant:$IMAGE_TAG|g" \
            k8s/co2-assistant-deployment.yaml | kubectl apply -f -
    fi
    kubectl apply -f k8s/ui-deployment.yaml
    
    # Create secrets with validation
    log_info "Creating secrets with validated environment variables..."
    
    # Delete existing secret first to ensure clean creation
    log_info "Removing any existing secret with empty values..."
    kubectl delete secret co2-assistant-secrets -n co2-assistant --ignore-not-found=true
    
    # Create new secret with actual values
    log_info "Creating secret with actual values..."
    kubectl create secret generic co2-assistant-secrets \
        --namespace=co2-assistant \
        --from-literal=google-ai-api-key="$GEMINI_API_KEY" \
        --from-literal=google-project-id="$PROJECT_ID"
    
    # Verify secret was created correctly
    log_info "Verifying secret creation..."
    local secret_api_key
    secret_api_key=$(kubectl get secret co2-assistant-secrets -n co2-assistant -o jsonpath='{.data.google-ai-api-key}' | base64 -d)
    local secret_project_id
    secret_project_id=$(kubectl get secret co2-assistant-secrets -n co2-assistant -o jsonpath='{.data.google-project-id}' | base64 -d)
    
    if [[ -n "$secret_api_key" && -n "$secret_project_id" ]]; then
        log_success "✓ Secret created successfully with actual values"
        log_success "✓ API Key: ${secret_api_key:0:10}..."
        log_success "✓ Project ID: $secret_project_id"
    else
        log_error "✗ Secret creation failed - values are empty"
        log_error "API Key length: ${#secret_api_key}"
        log_error "Project ID length: ${#secret_project_id}"
        exit 1
    fi
    
    # Restart deployment to pick up new secret
    log_info "Restarting deployment to use new secret..."
    kubectl rollout restart deployment/co2-assistant -n co2-assistant
    
    # Wait for rollout to complete
    log_info "Waiting for rollout to complete..."
    kubectl rollout status deployment/co2-assistant -n co2-assistant --timeout=300s
    
    # Wait for our deployments to be ready
    log_info "Waiting for CO2-Aware Shopping Assistant to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/co2-assistant -n co2-assistant
    kubectl wait --for=condition=available --timeout=300s deployment/co2-assistant-ui -n co2-assistant
    
    # Deploy ob-proxy for cross-namespace routing
    log_info "Deploying ob-proxy for cross-namespace routing..."
    kubectl apply -f k8s/ob-proxy.yaml
    
    # Deploy Environment-Specific Security Policies
    log_info "Deploying security policies..."
    if [[ -f "security/pod-security-policy.yaml" ]]; then
        kubectl apply -f security/pod-security-policy.yaml
        log_success "Pod Security Policy deployed"
    else
        log_warning "Pod Security Policy not found, skipping..."
    fi
    
    # Deploy Network Policies based on environment configuration
    if [[ "$enable_network_policy" == "true" ]]; then
        log_info "Deploying network policies (production security mode)..."
        if [[ -f "security/network-policy-${ENVIRONMENT}.yaml" ]]; then
            kubectl apply -f "security/network-policy-${ENVIRONMENT}.yaml"
            log_success "Network policies deployed for $ENVIRONMENT environment"
        elif [[ -f "security/network-policy-prod.yaml" ]]; then
            kubectl apply -f security/network-policy-prod.yaml
            log_success "Production network policies deployed"
        else
            log_warning "Network policy configuration not found for $ENVIRONMENT"
        fi
    else
        log_info "Skipping network policies (development mode - minimal security)"
    fi
    
    # Deploy Environment-Specific Monitoring and Observability
    log_info "Deploying monitoring stack..."
    if [[ "$enable_managed_prometheus" == "true" ]]; then
        log_info "Deploying managed Prometheus monitoring..."
        if [[ -f "monitoring/prometheus-config-${ENVIRONMENT}.yaml" ]]; then
            kubectl apply -f "monitoring/prometheus-config-${ENVIRONMENT}.yaml"
            log_success "Prometheus monitoring deployed ($ENVIRONMENT configuration)"
        elif [[ -f "monitoring/prometheus-config-dev.yaml" ]]; then
            kubectl apply -f monitoring/prometheus-config-dev.yaml
            log_success "Basic Prometheus monitoring deployed (dev configuration)"
        else
            log_warning "Prometheus config not found, skipping..."
        fi
        
        # Deploy observability stack with environment-specific configuration
        if [[ -f "monitoring/observability-stack.yaml" ]]; then
            kubectl apply -f monitoring/observability-stack.yaml -l environment="$ENVIRONMENT"
            log_success "Observability stack deployed for $ENVIRONMENT environment"
        else
            log_warning "Observability stack not found, skipping..."
        fi
    else
        log_info "Skipping managed Prometheus (disabled in environment configuration)"
    fi
    
    if [[ -f "k8s/hpa.yaml" ]]; then
        kubectl apply -f k8s/hpa.yaml
        log_success "Horizontal Pod Autoscaler deployed"
    else
        log_warning "HPA configuration not found, skipping..."
    fi
    
    # Create managed certificate (only if not skipped)
    if [[ "$SKIP_CERTIFICATE" == "true" ]]; then
        log_info "Skipping certificate creation (--no-cert flag used)"
        log_warning "Application will be accessible via HTTP only"
    else
        log_info "Creating managed certificate (if not exists)..."
        if ! kubectl get managedcertificate co2-assistant-cert -n co2-assistant >/dev/null 2>&1; then
            log_info "Certificate doesn't exist, creating new one..."
            kubectl apply -f k8s/managed-certificate.yaml
        else
            log_info "Certificate already exists, preserving existing certificate..."
            kubectl get managedcertificate co2-assistant-cert -n co2-assistant
        fi
    fi
    
    # Check certificate status (non-blocking for faster deployment)
    log_info "Checking certificate status..."
    local cert_status
    cert_status=$(kubectl get managedcertificate co2-assistant-cert -n co2-assistant -o jsonpath='{.status.certificateStatus}' 2>/dev/null || echo "Unknown")
    
    if [[ "$cert_status" == "Active" ]]; then
        log_success "Certificate is already active and ready!"
    elif [[ "$cert_status" == "Provisioning" ]]; then
        log_warning "Certificate is provisioning. This may take 15-30 minutes."
        log_info "You can check status with: kubectl get managedcertificate co2-assistant-cert -n co2-assistant"
    else
        log_warning "Certificate status: $cert_status"
        log_info "Certificate provisioning is in progress. This typically takes 15-30 minutes."
        log_info "Your application will work with HTTP initially, HTTPS will be available once the certificate is ready."
        log_info "Check status with: kubectl get managedcertificate co2-assistant-cert -n co2-assistant"
        
        # Non-blocking check - don't wait for certificate
        if [[ "$MINIMAL_RESOURCES" == "true" ]]; then
            log_info "Skipping certificate wait for faster deployment (minimal mode)"
        else
            log_info "Certificate will be ready in background. Continuing with deployment..."
        fi
    fi
    
    # Generate and deploy unified ingress with custom domain
    log_info "Generating ingress configuration with domains: assistant.cloudcarta.com, ob.cloudcarta.com..."
    if [[ -f "k8s/https-ingress.yaml.template" ]]; then
        envsubst < k8s/https-ingress.yaml.template > k8s/https-ingress.yaml
        log_success "Ingress configuration generated from template"
    else
        log_warning "Ingress template not found, using static configuration"
    fi
    
    log_info "Deploying unified ingress with custom domain..."
    kubectl apply -f k8s/https-ingress.yaml
    
    # Check final status (non-blocking)
    log_info "Checking deployment status..."
    kubectl get ingress https-ingress -n co2-assistant
    kubectl get managedcertificate co2-assistant-cert -n co2-assistant
    
    # Final validation - check that pods are running successfully
    log_info "Final validation - checking pod status..."
    local co2_pods
    co2_pods=$(kubectl get pods -n co2-assistant -l app=co2-assistant --no-headers | wc -l)
    local co2_running_pods
    co2_running_pods=$(kubectl get pods -n co2-assistant -l app=co2-assistant --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [[ "$co2_running_pods" -gt 0 && "$co2_running_pods" -eq "$co2_pods" ]]; then
        log_success "✓ All CO2 Assistant pods are running successfully!"
        kubectl get pods -n co2-assistant -l app=co2-assistant
    else
        log_warning "⚠ Some CO2 Assistant pods may not be running properly"
        kubectl get pods -n co2-assistant -l app=co2-assistant
        log_info "Check pod logs with: kubectl logs -f deployment/co2-assistant -n co2-assistant"
    fi
    
    log_success "Application deployment completed successfully!"
    
    # Show service information
    echo ""
    log_info "Service URLs:"
    echo "  🌱 CO2-Aware Shopping Assistant: https://assistant.cloudcarta.com"
    echo "  🛍️ Online Boutique: https://ob.cloudcarta.com"
    echo ""
    log_info "To check deployment status:"
    echo "  kubectl get pods -n co2-assistant"
    echo "  kubectl get pods -n online-boutique"
    echo "  kubectl get services -n co2-assistant"
    echo "  kubectl get ingress https-ingress -n co2-assistant"
    
    return 0
}

# Show script header
show_script_header "$SCRIPT_NAME" "$SCRIPT_DESCRIPTION"

# Run deployment
if deploy_applications; then
    show_script_footer "$SCRIPT_NAME" "success"
    exit 0
else
    show_script_footer "$SCRIPT_NAME" "failure"
    exit 1
fi
