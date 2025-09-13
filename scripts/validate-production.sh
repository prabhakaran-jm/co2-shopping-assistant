#!/bin/bash

# Production-Grade Validation Script for CO2 Shopping Assistant
# 
# This script validates that all production-grade components are properly deployed
# and functioning correctly.

set -e

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

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        print_error "kubectl is not connected to a cluster"
        exit 1
    fi
    
    print_success "kubectl is available and connected to cluster"
}

# Function to validate security components
validate_security() {
    print_status "Validating security components..."
    
    local security_score=0
    local total_security=5
    
    # Check Pod Security Policy
    if kubectl get podsecuritypolicy co2-assistant-psp >/dev/null 2>&1; then
        print_success "✓ Pod Security Policy is active"
        ((security_score++))
    else
        print_warning "⚠ Pod Security Policy not found"
    fi
    
    # Check Network Policies
    if kubectl get networkpolicy co2-assistant-netpol -n co2-assistant >/dev/null 2>&1; then
        print_success "✓ Network Policy is active"
        ((security_score++))
    else
        print_warning "⚠ Network Policy not found"
    fi
    
    # Check RBAC
    if kubectl get role co2-assistant-psp-user -n co2-assistant >/dev/null 2>&1; then
        print_success "✓ RBAC roles configured"
        ((security_score++))
    else
        print_warning "⚠ RBAC roles not found"
    fi
    
    # Check if pods are running as non-root
    local non_root_pods=$(kubectl get pods -n co2-assistant -o jsonpath='{.items[*].spec.securityContext.runAsNonRoot}' | grep -c true || echo "0")
    if [[ "$non_root_pods" -gt 0 ]]; then
        print_success "✓ Pods running as non-root"
        ((security_score++))
    else
        print_warning "⚠ Some pods may be running as root"
    fi
    
    # Check resource limits
    local limited_pods=$(kubectl get pods -n co2-assistant -o jsonpath='{.items[*].spec.containers[*].resources.limits}' | grep -c "memory\|cpu" || echo "0")
    if [[ "$limited_pods" -gt 0 ]]; then
        print_success "✓ Resource limits configured"
        ((security_score++))
    else
        print_warning "⚠ Resource limits not configured"
    fi
    
    print_status "Security Score: $security_score/$total_security"
    return $security_score
}

# Function to validate monitoring components
validate_monitoring() {
    print_status "Validating monitoring components..."
    
    local monitoring_score=0
    local total_monitoring=4
    
    # Check Prometheus configuration
    if kubectl get configmap prometheus-config -n co2-assistant >/dev/null 2>&1; then
        print_success "✓ Prometheus configuration deployed"
        ((monitoring_score++))
    else
        print_warning "⚠ Prometheus configuration not found"
    fi
    
    # Check Prometheus rules
    if kubectl get configmap prometheus-rules -n co2-assistant >/dev/null 2>&1; then
        print_success "✓ Prometheus alert rules configured"
        ((monitoring_score++))
    else
        print_warning "⚠ Prometheus alert rules not found"
    fi
    
    # Check HPA
    if kubectl get hpa co2-assistant-hpa -n co2-assistant >/dev/null 2>&1; then
        print_success "✓ Horizontal Pod Autoscaler is active"
        kubectl get hpa co2-assistant-hpa -n co2-assistant
        ((monitoring_score++))
    else
        print_warning "⚠ Horizontal Pod Autoscaler not found"
    fi
    
    # Check metrics endpoint
    if kubectl get service co2-assistant-service -n co2-assistant >/dev/null 2>&1; then
        print_status "Testing metrics endpoint..."
        if kubectl run test-metrics --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s http://co2-assistant-service.co2-assistant.svc.cluster.local/metrics >/dev/null 2>&1; then
            print_success "✓ Metrics endpoint accessible"
            ((monitoring_score++))
        else
            print_warning "⚠ Metrics endpoint not accessible"
        fi
    else
        print_warning "⚠ Service not found for metrics testing"
    fi
    
    print_status "Monitoring Score: $monitoring_score/$total_monitoring"
    return $monitoring_score
}

# Function to validate application health
validate_application() {
    print_status "Validating application health..."
    
    local app_score=0
    local total_app=4
    
    # Check if pods are running
    local running_pods=$(kubectl get pods -n co2-assistant --field-selector=status.phase=Running --no-headers | wc -l)
    if [[ "$running_pods" -gt 0 ]]; then
        print_success "✓ Application pods are running ($running_pods pods)"
        ((app_score++))
    else
        print_error "✗ No application pods are running"
    fi
    
    # Check health endpoint
    print_status "Testing health endpoint..."
    if kubectl run test-health --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s http://co2-assistant-service.co2-assistant.svc.cluster.local/health >/dev/null 2>&1; then
        print_success "✓ Health endpoint accessible"
        ((app_score++))
    else
        print_warning "⚠ Health endpoint not accessible"
    fi
    
    # Check if services are available
    local services=$(kubectl get services -n co2-assistant --no-headers | wc -l)
    if [[ "$services" -gt 0 ]]; then
        print_success "✓ Services are configured ($services services)"
        ((app_score++))
    else
        print_warning "⚠ No services found"
    fi
    
    # Check ingress
    if kubectl get ingress https-ingress -n co2-assistant >/dev/null 2>&1; then
        print_success "✓ Ingress is configured"
        ((app_score++))
    else
        print_warning "⚠ Ingress not found"
    fi
    
    print_status "Application Score: $app_score/$total_app"
    return $app_score
}

# Function to validate performance
validate_performance() {
    print_status "Validating performance configuration..."
    
    local perf_score=0
    local total_perf=3
    
    # Check resource requests and limits
    local resources=$(kubectl get deployment co2-assistant -n co2-assistant -o jsonpath='{.spec.template.spec.containers[0].resources}' 2>/dev/null || echo "{}")
    if echo "$resources" | grep -q "requests\|limits"; then
        print_success "✓ Resource requests and limits configured"
        ((perf_score++))
    else
        print_warning "⚠ Resource requests and limits not configured"
    fi
    
    # Check replica count
    local replicas=$(kubectl get deployment co2-assistant -n co2-assistant -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
    if [[ "$replicas" -ge 2 ]]; then
        print_success "✓ Multiple replicas configured ($replicas replicas)"
        ((perf_score++))
    else
        print_warning "⚠ Single replica deployment (not production-ready)"
    fi
    
    # Check readiness and liveness probes
    local probes=$(kubectl get deployment co2-assistant -n co2-assistant -o jsonpath='{.spec.template.spec.containers[0].readinessProbe}' 2>/dev/null || echo "{}")
    if echo "$probes" | grep -q "httpGet"; then
        print_success "✓ Health probes configured"
        ((perf_score++))
    else
        print_warning "⚠ Health probes not configured"
    fi
    
    print_status "Performance Score: $perf_score/$total_perf"
    return $perf_score
}

# Main validation function
main() {
    print_status "Starting production-grade validation..."
    echo ""
    
    check_kubectl
    echo ""
    
    validate_security
    local security_score=$?
    echo ""
    
    validate_monitoring
    local monitoring_score=$?
    echo ""
    
    validate_application
    local app_score=$?
    echo ""
    
    validate_performance
    local perf_score=$?
    echo ""
    
    # Calculate overall score
    local total_score=$((security_score + monitoring_score + app_score + perf_score))
    local max_score=16
    
    print_status "=== PRODUCTION READINESS SUMMARY ==="
    echo "Security Score:     $security_score/5"
    echo "Monitoring Score:   $monitoring_score/4"
    echo "Application Score:  $app_score/4"
    echo "Performance Score:  $perf_score/3"
    echo "----------------------------------------"
    echo "Overall Score:      $total_score/$max_score"
    echo ""
    
    if [[ "$total_score" -ge 14 ]]; then
        print_success "🎉 PRODUCTION READY! Excellent configuration."
    elif [[ "$total_score" -ge 12 ]]; then
        print_warning "⚠️  MOSTLY READY. Minor improvements needed."
    elif [[ "$total_score" -ge 10 ]]; then
        print_warning "⚠️  NEEDS IMPROVEMENT. Several issues to address."
    else
        print_error "❌ NOT PRODUCTION READY. Major issues to fix."
    fi
    
    echo ""
    print_status "Next steps:"
    if [[ "$security_score" -lt 4 ]]; then
        echo "  🔒 Deploy security policies: kubectl apply -f security/"
    fi
    if [[ "$monitoring_score" -lt 3 ]]; then
        echo "  📊 Deploy monitoring: kubectl apply -f monitoring/"
    fi
    if [[ "$app_score" -lt 3 ]]; then
        echo "  🚀 Check application deployment: kubectl get pods -n co2-assistant"
    fi
    if [[ "$perf_score" -lt 2 ]]; then
        echo "  ⚡ Configure HPA: kubectl apply -f k8s/hpa.yaml"
    fi
}

# Run main function
main "$@"
