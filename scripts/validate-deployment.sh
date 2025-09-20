#!/bin/bash

# Deployment Validation Script for CO2-Aware Shopping Assistant

# Exit on any error
set -e

# --- Helper Functions ---

# Log a message in green
log_success() {
    echo -e "\033[0;32m✅  $1\033[0m"
}

# Log a message in red
log_error() {
    echo -e "\033[0;31m❌  $1\033[0m"
}

# Log a message in yellow
log_info() {
    echo -e "\033[0;33mℹ️  $1\033[0m"
}

# --- Validation Steps ---

log_info "Starting Deployment Validation..."

# 1. Check Pods
log_info "1. Checking Pods..."

log_info "   - Checking co2-assistant namespace..."
kubectl get pods -n co2-assistant
if ! kubectl get pods -n co2-assistant | grep -q "Running"; then
    log_error "   - No running pods found in co2-assistant namespace."
    exit 1
fi
log_success "   - All pods in co2-assistant namespace are running."

log_info "   - Checking online-boutique namespace..."
kubectl get pods -n online-boutique
if ! kubectl get pods -n online-boutique | grep -q "Running"; then
    log_error "   - No running pods found in online-boutique namespace."
    exit 1
fi
log_success "   - All pods in online-boutique namespace are running."

# 2. Check Services
log_info "2. Checking Services..."

log_info "   - Checking co2-assistant-service..."
kubectl get svc -n co2-assistant co2-assistant-service
if ! kubectl get svc -n co2-assistant co2-assistant-service > /dev/null; then
    log_error "   - co2-assistant-service not found."
    exit 1
fi
log_success "   - co2-assistant-service found."

# 3. Check Health Endpoint
log_info "3. Checking Health Endpoint..."

# Port-forward the service to localhost
log_info "   - Setting up port-forwarding for co2-assistant-service..."
kubectl port-forward svc/co2-assistant-service 8080:80 -n co2-assistant > /dev/null 2>&1 &
PORT_FORWARD_PID=$!

# Give it a moment to establish the connection
sleep 5

log_info "   - Curling the /health endpoint..."
if ! curl -s http://localhost:8080/health | grep -q "healthy"; then
    log_error "   - Health check failed."
    kill $PORT_FORWARD_PID
    exit 1
fi
log_success "   - Health check passed."

# 4. Test a simple user workflow
log_info "4. Testing a simple user workflow..."

log_info "   - Sending a test message to the chat endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8080/api/chat -H "Content-Type: application/json" -d '{"message": "hello", "session_id": "validation-test"}')

if ! echo "$RESPONSE" | grep -q "response"; then
    log_error "   - Did not receive a valid response from the chat endpoint."
    kill $PORT_FORWARD_PID
    exit 1
fi
log_success "   - Received a valid response from the chat endpoint."

# --- Cleanup ---

log_info "Cleaning up..."
kill $PORT_FORWARD_PID

log_success "Deployment Validation Completed Successfully!"
