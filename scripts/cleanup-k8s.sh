#!/bin/bash

# Cleanup Kubernetes Resources
# This script removes all CO2 Assistant and related resources

set -e

echo "🧹 Cleaning up CO2 Shopping Assistant resources..."

# Delete ingress and certificate first to avoid load balancer issues
echo "🌐 Removing ingress and certificate..."
kubectl delete -f https-ingress.yaml --ignore-not-found=true
kubectl delete -f managed-certificate.yaml --ignore-not-found=true

# Delete deployments and services
echo "🗑️  Removing deployments and services..."
kubectl delete -f ob-proxy.yaml --ignore-not-found=true
kubectl delete -f ui-deployment.yaml --ignore-not-found=true
kubectl delete -f co2-assistant-deployment.yaml --ignore-not-found=true

# Delete ConfigMap
echo "⚙️  Removing ConfigMap..."
kubectl delete -f ui-configmap.yaml --ignore-not-found=true

# Delete namespace (this will clean up any remaining resources)
echo "📁 Removing namespace..."
kubectl delete -f namespaces.yaml --ignore-not-found=true

echo "✅ Cleanup complete!"
echo ""
echo "📊 Checking remaining resources..."
kubectl get pods --all-namespaces | grep -E "(co2-assistant|ob-proxy)" || echo "No CO2 Assistant resources found"
