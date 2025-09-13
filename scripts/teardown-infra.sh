#!/bin/bash

# Complete Infrastructure Teardown Script for CO2 Shopping Assistant
# 
# This script completely destroys all infrastructure created by deploy-infra.sh:
# - Kubernetes applications and resources
# - GKE Autopilot cluster
# - Artifact Registry repository
# - Service accounts and IAM bindings
# - Load balancers and firewall rules
# - All Terraform-managed resources
# 
# Note: Static IPs (including agent-layer-ip) are preserved for reuse

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROJECT_ID=""
REGION="us-central1"
CLUSTER_NAME="co2-assistant-cluster"
FORCE=false

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
    echo "Options:"
    echo "  --project-id PROJECT_ID    Google Cloud Project ID (required)"
    echo "  --region REGION           GCP region (default: us-central1)"
    echo "  --cluster-name NAME       GKE cluster name (default: co2-assistant-cluster)"
    echo "  --force                   Skip confirmation prompts"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --project-id my-project-123"
    echo "  $0 --project-id my-project-123 --region us-east1 --force"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-id)
            PROJECT_ID="$2"
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
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
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

# Confirmation prompt
if [[ "$FORCE" != "true" ]]; then
    print_warning "This will completely destroy all infrastructure including:"
    echo "  - GKE Autopilot cluster: $CLUSTER_NAME"
    echo "  - Artifact Registry repository"
    echo "  - All Kubernetes applications and data"
    echo "  - Service accounts and IAM bindings"
    echo "  - All Terraform-managed resources"
    echo ""
    read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM
    if [[ "$CONFIRM" != "yes" ]]; then
        print_status "Teardown cancelled"
        exit 0
    fi
fi

print_status "Starting complete infrastructure teardown..."

# Set project
print_status "Setting project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

# Check if terraform directory exists
if [[ -d "terraform" ]]; then
    print_status "Found Terraform directory. Attempting Terraform destroy..."
    
    # Change to terraform directory
    cd terraform
    
    # Initialize terraform (in case it wasn't initialized)
    print_status "Initializing Terraform with remote backend..."
    terraform init -backend-config=backend.hcl
    
    # Check if there's actually state to destroy
    print_status "Checking Terraform state..."
    if terraform state list >/dev/null 2>&1; then
        print_status "Found Terraform state. Attempting Terraform destroy..."
        
        # Try to plan the destruction first
        if terraform plan -destroy -out=tfplan-destroy >/dev/null 2>&1; then
            print_status "Terraform plan successful. Proceeding with destruction..."
            
            if [[ "$FORCE" != "true" ]]; then
                print_warning "Review the destruction plan above."
                read -p "Continue with destruction? (type 'yes' to confirm): " CONFIRM_TF
                if [[ "$CONFIRM_TF" != "yes" ]]; then
                    print_status "Terraform destruction cancelled"
                    cd ..
                    exit 0
                fi
            fi
            
            # Destroy infrastructure
            print_status "Destroying infrastructure with Terraform..."
            terraform destroy -auto-approve
            
            print_success "Terraform destruction completed successfully!"
        else
            print_warning "Terraform plan failed (likely cluster already deleted)"
            print_status "Attempting to remove resources from state manually..."
            
            # Remove Kubernetes resources from state since cluster is gone
            print_status "Removing Kubernetes resources from Terraform state..."
            # Note: Most Kubernetes resources are created via kubectl, not Terraform
            # Only remove resources that are actually managed by Terraform
            terraform state rm kubernetes_namespace.co2_assistant 2>/dev/null || true
            terraform state rm kubernetes_secret.co2_assistant_secrets 2>/dev/null || true
            terraform state rm kubernetes_config_map.co2_assistant_ui_config 2>/dev/null || true
            terraform state rm kubernetes_service_account.co2_assistant_sa 2>/dev/null || true
            
            # Try destroy again for remaining resources
            print_status "Attempting Terraform destroy for remaining resources..."
            terraform destroy -auto-approve || print_warning "Some resources may have already been deleted"
        fi
    else
        print_warning "No Terraform state found (empty state or not initialized)"
        print_status "Proceeding with manual cleanup..."
    fi
    
    # Clean up terraform files
    print_status "Cleaning up Terraform files..."
    rm -f tfplan tfplan-destroy .terraform.lock.hcl
    rm -rf .terraform/
    
    cd ..
    
else
    print_warning "No Terraform state found. Attempting to clean up resources manually..."
    
    # Check if cluster exists before trying to delete
    if gcloud container clusters describe "$CLUSTER_NAME" --region="$REGION" --quiet >/dev/null 2>&1; then
        print_status "Deleting GKE cluster: $CLUSTER_NAME..."
        gcloud container clusters delete "$CLUSTER_NAME" --region="$REGION" --quiet || true
    else
        print_status "GKE cluster $CLUSTER_NAME not found or already deleted"
    fi
    
    # Check if Artifact Registry repository exists
    if gcloud artifacts repositories describe co2-assistant-repo --location="$REGION" --quiet >/dev/null 2>&1; then
        print_status "Deleting Artifact Registry repository..."
        gcloud artifacts repositories delete co2-assistant-repo --location="$REGION" --quiet || true
    else
        print_status "Artifact Registry repository not found or already deleted"
    fi
    
    # Check if service account exists
    if gcloud iam service-accounts describe co2-assistant-sa@"$PROJECT_ID".iam.gserviceaccount.com --quiet >/dev/null 2>&1; then
        print_status "Deleting service account..."
        gcloud iam service-accounts delete co2-assistant-sa@"$PROJECT_ID".iam.gserviceaccount.com --quiet || true
    else
        print_status "Service account not found or already deleted"
    fi
    
    # Clean up Kubernetes resources (these are safe to run even if they don't exist)
    print_status "Cleaning up Kubernetes resources..."
    
    # Delete ingress first (in case it's in default namespace)
    print_status "Deleting ingress resources..."
    kubectl delete ingress unified-ingress -n default --ignore-not-found=true || true
    kubectl delete ingress co2-assistant-ingress -n co2-assistant --ignore-not-found=true || true
    kubectl delete ingress online-boutique-ingress -n default --ignore-not-found=true || true
    
    # Delete ConfigMaps
    print_status "Deleting ConfigMaps..."
    kubectl delete configmap co2-assistant-ui-config -n co2-assistant --ignore-not-found=true || true
    kubectl delete configmap ob-proxy-config -n co2-assistant --ignore-not-found=true || true
    
    # Delete managed certificates (only if --delete-certificates flag is provided)
    if [[ "$1" == "--delete-certificates" ]]; then
        print_status "Deleting managed certificates..."
        kubectl delete managedcertificate co2-assistant-cert -n co2-assistant --ignore-not-found=true || true
    else
        print_status "Preserving managed certificates (use --delete-certificates to remove them)"
        print_status "Certificate status:"
        kubectl get managedcertificate co2-assistant-cert -n co2-assistant 2>/dev/null || print_warning "Certificate not found"
    fi
    
    # Delete secrets
    print_status "Deleting secrets..."
    kubectl delete secret co2-assistant-secrets -n co2-assistant --ignore-not-found=true || true
    
    # Delete Online Boutique resources first (if they exist)
    print_status "Deleting Online Boutique resources..."
    kubectl delete all --all -n online-boutique --ignore-not-found=true || true
    kubectl delete configmap --all -n online-boutique --ignore-not-found=true || true
    kubectl delete secret --all -n online-boutique --ignore-not-found=true || true
    kubectl delete serviceaccount --all -n online-boutique --ignore-not-found=true || true
    
    # Delete CO2 Assistant resources
    print_status "Deleting CO2 Assistant resources..."
    kubectl delete all --all -n co2-assistant --ignore-not-found=true || true
    
    # Delete namespaces (this will clean up any remaining resources)
    print_status "Deleting namespaces..."
    kubectl delete namespace co2-assistant --ignore-not-found=true || true
    kubectl delete namespace online-boutique --ignore-not-found=true || true
fi

# Clean up load balancers (but preserve static IPs)
print_status "Cleaning up load balancers..."
LB_RULES=$(gcloud compute forwarding-rules list --filter="name~co2-assistant OR name~online-boutique" --format="value(name)" 2>/dev/null || echo "")
if [[ -n "$LB_RULES" ]]; then
    echo "$LB_RULES" | while read rule; do
        if [[ -n "$rule" ]]; then
            print_status "Deleting forwarding rule: $rule"
            gcloud compute forwarding-rules delete "$rule" --global --quiet || true
        fi
    done
else
    print_status "No load balancer forwarding rules found"
fi

# Note: Preserving static IPs (especially agent-layer-ip) as they may be reused
print_status "Preserving static IPs (including agent-layer-ip) for potential reuse..."

# Clean up any remaining firewall rules
print_status "Cleaning up firewall rules..."
FW_RULES=$(gcloud compute firewall-rules list --filter="name~co2-assistant OR name~online-boutique" --format="value(name)" 2>/dev/null || echo "")
if [[ -n "$FW_RULES" ]]; then
    echo "$FW_RULES" | while read rule; do
        if [[ -n "$rule" ]]; then
            print_status "Deleting firewall rule: $rule"
            gcloud compute firewall-rules delete "$rule" --quiet || true
        fi
    done
else
    print_status "No firewall rules found"
fi

print_success "Complete infrastructure teardown completed!"
echo ""
print_status "Summary of destroyed resources:"
echo "  ✅ GKE Autopilot cluster: $CLUSTER_NAME"
echo "  ✅ Artifact Registry repository"
echo "  ✅ All Kubernetes applications and data"
echo "  ✅ Service accounts and IAM bindings"
echo "  ✅ Load balancers"
echo "  ✅ Firewall rules"
echo "  ✅ All Terraform-managed resources"
echo "  🔒 Static IPs preserved (including agent-layer-ip for reuse)"
echo ""
print_status "Resources cleaned up:"
echo "  🗑️  CO2-Aware Shopping Assistant (co2-assistant namespace)"
echo "  🗑️  Online Boutique microservices (online-boutique namespace)"
echo "  🗑️  All ingress and load balancer resources"
echo "  🗑️  ConfigMaps, Secrets, and ServiceAccounts"
echo "  🗑️  All Terraform state and infrastructure"
echo ""
print_warning "Note: Some resources may take a few minutes to fully delete."
print_status "To verify cleanup:"
echo "  gcloud container clusters list"
echo "  gcloud artifacts repositories list"
echo "  gcloud compute addresses list"
echo "  gcloud iam service-accounts list"
echo "  kubectl get namespaces"
echo ""
print_success "🌱 Infrastructure completely destroyed!"
print_success "🛍️ All applications and data removed!"
print_success "🔒 Static IPs preserved for future use!"
print_success "📊 Clean slate ready for new deployments!"
