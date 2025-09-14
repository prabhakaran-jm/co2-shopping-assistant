#!/bin/bash

# Application Teardown Script for CO2 Shopping Assistant
# This script removes CO2 Assistant and Online Boutique applications from the cluster

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Script configuration
SCRIPT_NAME="CO2 Assistant Application Teardown"
SCRIPT_DESCRIPTION="Removes CO2 Assistant and Online Boutique applications from cluster"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Teardown CO2 Assistant and Online Boutique applications"
    echo ""
    echo "Options:"
    echo "  --environment ENV         Environment: dev or prod (default: dev)"
    echo "                             Removes environment-specific resources"
    echo "  --force                   Skip confirmation prompts"
    echo "  --keep-certificates       Keep managed certificates (DEFAULT: preserved)"
    echo "  --delete-certificates     Delete managed certificates (DANGEROUS)"
    echo "  --keep-ingress            Keep ingress resources"
    echo "  --dry-run                 Show what would be deleted without actually deleting"
    echo "  --help                    Show this help message"
    echo ""
    echo "Environment-specific cleanup:"
    echo "  dev:  Removes development-specific monitoring and security policies"
    echo "  prod: Removes production-grade security policies and monitoring"
    echo ""
    echo "Examples:"
    echo "  $0                        # Interactive teardown (certificates preserved)"
    echo "  $0 --force                # Force teardown without prompts (certificates preserved)"
    echo "  $0 --environment prod      # Remove production-specific resources"
    echo "  $0 --delete-certificates  # DANGEROUS: Delete certificates (takes 15-30 min to recreate)"
    echo "  $0 --dry-run              # Show what would be deleted"
    echo ""
    echo "🔒 Certificate Protection:"
    echo "  Certificates are preserved by default to avoid 15-30 minute recreation time."
    echo "  Use --delete-certificates only if you need to recreate certificates."
}

# Default values
ENVIRONMENT="dev"
FORCE_TEARDOWN=false
KEEP_CERTIFICATES=true  # Changed default to preserve certificates
KEEP_INGRESS=false
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --force)
            FORCE_TEARDOWN=true
            shift
            ;;
        --keep-certificates)
            KEEP_CERTIFICATES=true
            shift
            ;;
        --delete-certificates)
            KEEP_CERTIFICATES=false
            shift
            ;;
        --keep-ingress)
            KEEP_INGRESS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
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

# Main teardown function
teardown_applications() {
    local project_root
    project_root="$(get_project_root)"
    
    # Change to project root
    cd "$project_root"
    
    log_info "Starting application teardown for CO2 Shopping Assistant..."
    
    # Check kubectl connectivity
    if ! check_kubectl_connectivity; then
        exit 1
    fi
    
    # Show what will be cleaned up
    log_info "Applications to be removed:"
    echo "  - CO2 Assistant (co2-assistant namespace)"
    echo "  - Online Boutique (online-boutique namespace)"
    if [[ "$KEEP_CERTIFICATES" == "false" ]]; then
        echo "  - Managed certificates (DANGEROUS: will be deleted)"
        log_warning "⚠️  Certificates will be deleted! This will take 15-30 minutes to recreate."
    else
        echo "  - Managed certificates (preserved - SAFE)"
        log_success "✅ Certificates will be preserved to avoid recreation time."
    fi
    if [[ "$KEEP_INGRESS" == "false" ]]; then
        echo "  - Ingress resources"
    fi
    echo "  - ConfigMaps, Secrets, Services, Deployments"
    echo ""
    
    # Confirmation prompt
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN MODE - No resources will actually be deleted"
    elif [[ "$FORCE_TEARDOWN" == "false" ]]; then
        if ! confirm_action "Are you sure you want to delete all applications?"; then
            log_info "Teardown cancelled by user"
            exit 0
        fi
    fi
    
    # Cleanup Online Boutique resources first
    log_info "Cleaning up Online Boutique resources..."
    if namespace_exists "online-boutique"; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "Would delete all resources in online-boutique namespace"
            kubectl get all -n online-boutique 2>/dev/null || log_warning "No resources found in online-boutique namespace"
        else
            kubectl delete all --all -n online-boutique --ignore-not-found=true
            kubectl delete configmap --all -n online-boutique --ignore-not-found=true
            kubectl delete secret --all -n online-boutique --ignore-not-found=true
            kubectl delete serviceaccount --all -n online-boutique --ignore-not-found=true
            log_success "Online Boutique resources cleaned up"
        fi
    else
        log_info "Online Boutique namespace not found"
    fi
    
    # Cleanup CO2 Assistant resources
    log_info "Cleaning up CO2 Assistant resources..."
    if namespace_exists "co2-assistant"; then
        # Delete ingress and certificate first to avoid load balancer issues
        if [[ "$KEEP_INGRESS" == "false" ]]; then
            log_info "Removing ingress resources..."
            if [[ "$DRY_RUN" == "true" ]]; then
                kubectl get ingress -n co2-assistant 2>/dev/null || log_warning "No ingress resources found"
            else
                kubectl delete ingress https-ingress -n co2-assistant --ignore-not-found=true
                kubectl delete ingress co2-assistant-ingress -n co2-assistant --ignore-not-found=true
            fi
        fi
        
        if [[ "$KEEP_CERTIFICATES" == "false" ]]; then
            log_warning "⚠️  DANGEROUS: About to delete managed certificates!"
            log_warning "This will take 15-30 minutes to recreate and provision."
            
            if [[ "$FORCE_TEARDOWN" == "false" ]]; then
                echo ""
                read -p "Are you sure you want to delete certificates? (yes/no): " confirm
                if [[ "$confirm" != "yes" ]]; then
                    log_info "Certificate deletion cancelled. Preserving certificates."
                    KEEP_CERTIFICATES=true
                fi
            fi
            
            if [[ "$KEEP_CERTIFICATES" == "false" ]]; then
                log_info "Removing managed certificates..."
                if [[ "$DRY_RUN" == "true" ]]; then
                    kubectl get managedcertificate -n co2-assistant 2>/dev/null || log_warning "No managed certificates found"
                else
                    kubectl delete managedcertificate co2-assistant-cert -n co2-assistant --ignore-not-found=true
                    log_warning "Certificates deleted. Recreation will take 15-30 minutes."
                fi
            fi
        fi
        
        # Delete deployments and services
        log_info "Removing deployments and services..."
        if [[ "$DRY_RUN" == "true" ]]; then
            kubectl get all -n co2-assistant 2>/dev/null || log_warning "No resources found in co2-assistant namespace"
        else
            kubectl delete -f k8s/ob-proxy.yaml --ignore-not-found=true
            kubectl delete -f k8s/ui-deployment.yaml --ignore-not-found=true
            kubectl delete -f k8s/co2-assistant-deployment.yaml --ignore-not-found=true
        fi
        
        # Delete ConfigMaps
        log_info "Removing ConfigMaps..."
        if [[ "$DRY_RUN" == "true" ]]; then
            kubectl get configmap -n co2-assistant 2>/dev/null || log_warning "No ConfigMaps found"
        else
            kubectl delete -f k8s/ui-configmap.yaml --ignore-not-found=true
            kubectl delete configmap co2-assistant-ui-config -n co2-assistant --ignore-not-found=true
        fi
        
        # Delete secrets
        log_info "Removing secrets..."
        if [[ "$DRY_RUN" == "true" ]]; then
            kubectl get secret -n co2-assistant 2>/dev/null || log_warning "No secrets found"
        else
            kubectl delete secret co2-assistant-secrets -n co2-assistant --ignore-not-found=true
        fi
        
        # Delete production-grade components
        log_info "Removing production-grade components..."
        if [[ "$DRY_RUN" == "true" ]]; then
            kubectl get hpa,networkpolicy,podsecuritypolicy -n co2-assistant 2>/dev/null || log_warning "No production components found"
        else
            kubectl delete hpa co2-assistant-hpa -n co2-assistant --ignore-not-found=true
            kubectl delete networkpolicy co2-assistant-netpol -n co2-assistant --ignore-not-found=true
            kubectl delete networkpolicy deny-all-egress -n co2-assistant --ignore-not-found=true
            kubectl delete podsecuritypolicy co2-assistant-psp --ignore-not-found=true
            kubectl delete role co2-assistant-psp-user -n co2-assistant --ignore-not-found=true
            kubectl delete rolebinding co2-assistant-psp-binding -n co2-assistant --ignore-not-found=true
        fi
        
        log_success "CO2 Assistant resources cleaned up"
    else
        log_info "CO2 Assistant namespace not found"
    fi
    
    # Clean up environment-specific resources
    log_info "Cleaning up environment-specific resources for $ENVIRONMENT..."
    
    # Load environment-specific configuration if available
    local env_config_file="terraform/envs/${ENVIRONMENT}.tfvars"
    local enable_network_policy="false"
    local enable_managed_prometheus="true"
    
    if [[ -f "$env_config_file" ]]; then
        log_info "Loading environment configuration from $env_config_file"
        enable_network_policy=$(grep "enable_network_policy" "$env_config_file" | cut -d'=' -f2 | tr -d ' ' || echo "false")
        enable_managed_prometheus=$(grep "enable_managed_prometheus" "$env_config_file" | cut -d'=' -f2 | tr -d ' ' || echo "true")
    fi
    
    # Remove environment-specific network policies
    if [[ "$enable_network_policy" == "true" ]]; then
        log_info "Removing environment-specific network policies..."
        if [[ "$DRY_RUN" == "true" ]]; then
            kubectl get networkpolicy -l environment="$ENVIRONMENT" --all-namespaces 2>/dev/null || log_warning "No environment-specific network policies found"
        else
            kubectl delete networkpolicy -l environment="$ENVIRONMENT" --all-namespaces --ignore-not-found=true
            if [[ -f "security/network-policy-${ENVIRONMENT}.yaml" ]]; then
                kubectl delete -f "security/network-policy-${ENVIRONMENT}.yaml" --ignore-not-found=true
            fi
            log_success "Environment-specific network policies removed"
        fi
    else
        log_info "Skipping network policy cleanup (disabled in $ENVIRONMENT configuration)"
    fi
    
    # Remove environment-specific monitoring
    if [[ "$enable_managed_prometheus" == "true" ]]; then
        log_info "Removing environment-specific monitoring..."
        if [[ "$DRY_RUN" == "true" ]]; then
            kubectl get prometheus,servicemonitor -l environment="$ENVIRONMENT" --all-namespaces 2>/dev/null || log_warning "No environment-specific monitoring found"
        else
            kubectl delete prometheus -l environment="$ENVIRONMENT" --all-namespaces --ignore-not-found=true
            kubectl delete servicemonitor -l environment="$ENVIRONMENT" --all-namespaces --ignore-not-found=true
            if [[ -f "monitoring/prometheus-config-${ENVIRONMENT}.yaml" ]]; then
                kubectl delete -f "monitoring/prometheus-config-${ENVIRONMENT}.yaml" --ignore-not-found=true
            fi
            log_success "Environment-specific monitoring removed"
        fi
    else
        log_info "Skipping monitoring cleanup (disabled in $ENVIRONMENT configuration)"
    fi
    
    # Delete namespaces (this will clean up any remaining resources)
    log_info "Removing namespaces..."
    if [[ "$DRY_RUN" == "true" ]]; then
        kubectl get namespace co2-assistant online-boutique 2>/dev/null || log_warning "No target namespaces found"
    else
        kubectl delete namespace co2-assistant --ignore-not-found=true
        kubectl delete namespace online-boutique --ignore-not-found=true
        kubectl delete -f k8s/namespaces.yaml --ignore-not-found=true
    fi
    
    log_success "Application teardown completed successfully!"
    
    # Show remaining resources
    echo ""
    log_info "Checking remaining resources..."
    kubectl get pods --all-namespaces | grep -E "(co2-assistant|ob-proxy)" || log_info "No CO2 Assistant resources found"
    
    return 0
}

# Show script header
show_script_header "$SCRIPT_NAME" "$SCRIPT_DESCRIPTION"

# Run teardown
if teardown_applications; then
    show_script_footer "$SCRIPT_NAME" "success"
    exit 0
else
    show_script_footer "$SCRIPT_NAME" "failure"
    exit 1
fi
