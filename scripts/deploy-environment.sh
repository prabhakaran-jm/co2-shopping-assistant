#!/bin/bash

# Environment-Specific Deployment Script
# Usage: ./deploy-environment.sh dev|prod

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Load environment variables from .env file if it exists
if [[ -f ".env" ]]; then
    print_status "Loading environment variables from .env file"
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
else
    print_warning ".env file not found - using defaults only"
fi

# Get environment from command line
ENVIRONMENT=${1:-dev}

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    print_error "Environment must be 'dev' or 'prod'"
    exit 1
fi

# Domain configuration with defaults
BASE_DOMAIN="${BASE_DOMAIN:-yourdomain.com}"
ASSISTANT_DOMAIN="${ASSISTANT_DOMAIN:-assistant.${BASE_DOMAIN}}"
ONLINE_BOUTIQUE_DOMAIN="${ONLINE_BOUTIQUE_DOMAIN:-ob.${BASE_DOMAIN}}"

print_status "Deploying to $ENVIRONMENT environment..."
print_status "Domain configuration:"
print_status "  Assistant Domain: $ASSISTANT_DOMAIN"
print_status "  Online Boutique Domain: $ONLINE_BOUTIQUE_DOMAIN"

# Deploy with environment-specific configuration
print_status "Applying Terraform configuration for $ENVIRONMENT..."
cd terraform
terraform init -backend-config=backend.hcl
terraform apply -var-file="envs/${ENVIRONMENT}.tfvars" -auto-approve

# Apply environment-specific security policies
print_status "Applying security policies for $ENVIRONMENT..."
cd ..

if [[ "$ENVIRONMENT" == "prod" ]]; then
    print_status "Applying strict production security policies..."
    kubectl apply -f security/network-policy-prod.yaml
    kubectl apply -f security/pod-security-policy.yaml
else
    print_status "Applying permissive development security policies..."
    kubectl apply -f security/network-policy-dev.yaml
fi

# Apply environment-specific monitoring
print_status "Configuring monitoring for $ENVIRONMENT..."
kubectl apply -f monitoring/prometheus-config-${ENVIRONMENT}.yaml

if [[ "$ENVIRONMENT" == "prod" ]]; then
    print_status "Deploying production observability stack..."
    kubectl apply -f monitoring/observability-stack.yaml -l environment=prod
    
    # Deploy Grafana for production
    helm repo add grafana https://grafana.github.io/helm-charts
    helm upgrade --install grafana grafana/grafana \
        --namespace co2-assistant \
        --set persistence.enabled=true \
        --set adminPassword=admin123 \
        --values monitoring/grafana-values-prod.yaml
else
    print_status "Deploying basic monitoring for development..."
    kubectl apply -f monitoring/observability-stack.yaml -l environment=dev
fi

# Deploy optimized Online Boutique
print_status "Deploying Online Boutique with $ENVIRONMENT configuration..."
if [[ "$ENVIRONMENT" == "prod" ]]; then
    helm upgrade --install online-boutique online-boutique/helm-chart \
        --namespace online-boutique \
        --values online-boutique/helm-chart/values-optimized.yaml \
        --set loadGenerator.create=false
else
    helm upgrade --install online-boutique online-boutique/helm-chart \
        --namespace online-boutique \
        --values online-boutique/helm-chart/values-optimized.yaml \
        --set loadGenerator.create=true
fi

# Generate and deploy ingress with environment-specific domains
print_status "Generating ingress configuration with domains: $ASSISTANT_DOMAIN, $ONLINE_BOUTIQUE_DOMAIN..."
if [[ -f "k8s/https-ingress.yaml.template" ]]; then
    envsubst < k8s/https-ingress.yaml.template > k8s/https-ingress.yaml
    kubectl apply -f k8s/https-ingress.yaml
    print_success "Ingress configuration deployed with custom domains"
else
    print_warning "Ingress template not found, skipping ingress deployment"
fi

# Deploy CO2 Assistant
print_status "Deploying CO2 Assistant..."
kubectl apply -f k8s/namespaces.yaml
kubectl apply -f k8s/co2-assistant-deployment.yaml
kubectl apply -f k8s/hpa.yaml

print_success "✅ $ENVIRONMENT environment deployed successfully!"

# Show environment-specific information
if [[ "$ENVIRONMENT" == "prod" ]]; then
    print_status "🔒 Production Features Enabled:"
    echo "  - Strict network policies"
    echo "  - Comprehensive monitoring"
    echo "  - SLA alerting"
    echo "  - Distributed tracing"
    echo "  - Grafana dashboards"
    echo ""
    print_status "🌐 Application Access URLs:"
    echo "  🌱 CO2-Aware Shopping Assistant: https://$ASSISTANT_DOMAIN"
    echo "  🛍️ Online Boutique: https://$ONLINE_BOUTIQUE_DOMAIN"
    echo ""
    print_status "📊 Monitoring Access URLs:"
    echo "  - Grafana: kubectl port-forward svc/grafana 3000:80 -n co2-assistant"
    echo "  - Jaeger: kubectl port-forward svc/jaeger-all-in-one 16686:16686 -n co2-assistant"
else
    print_status "🛠️ Development Features:"
    echo "  - Permissive network policies"
    echo "  - Basic monitoring"
    echo "  - Load generator enabled"
    echo "  - Cost-optimized configuration"
    echo ""
    print_status "🌐 Application Access URLs:"
    echo "  🌱 CO2-Aware Shopping Assistant: https://$ASSISTANT_DOMAIN"
    echo "  🛍️ Online Boutique: https://$ONLINE_BOUTIQUE_DOMAIN"
fi

print_status "💰 Estimated Daily Cost: $([[ $ENVIRONMENT == 'prod' ]] && echo '$15-25' || echo '$5-8')"
