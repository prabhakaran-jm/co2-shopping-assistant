#!/bin/bash

# Deploy CO2 Assistant Kubernetes Resources Only
# This script deploys only the CO2 Assistant Kubernetes resources (no Online Boutique)
# For full deployment including Online Boutique, use deploy-app.sh

set -e

echo "🚀 Deploying CO2 Shopping Assistant Kubernetes resources..."

# Apply namespaces first
echo "📁 Creating namespaces..."
kubectl apply -f namespaces.yaml

# Apply ConfigMap for UI
echo "⚙️  Creating UI ConfigMap..."
kubectl apply -f ui-configmap.yaml

# Apply CO2 Assistant deployments
echo "🌱 Deploying CO2 Assistant backend..."
kubectl apply -f co2-assistant-deployment.yaml

echo "🎨 Deploying CO2 Assistant UI..."
kubectl apply -f ui-deployment.yaml

# Note: ob-proxy is only needed if Online Boutique is deployed
# For full deployment including Online Boutique, use deploy-app.sh

# Apply managed certificate and ingress last
echo "🔒 Deploying managed certificate..."
kubectl apply -f managed-certificate.yaml

echo "🌐 Deploying HTTPS ingress..."
kubectl apply -f https-ingress.yaml

echo "✅ Deployment complete!"
echo ""
echo "📊 Checking deployment status..."
kubectl get pods -n co2-assistant
echo ""
echo "🌐 Access your application:"
echo "   CO2 Assistant: https://assistant.cloudcarta.com"
echo ""
echo "ℹ️  Note: Online Boutique is not deployed by this script."
echo "   For full deployment including Online Boutique, use deploy-app.sh"
echo ""
echo "🔍 To check ingress status:"
echo "   kubectl get ingress https-ingress -n co2-assistant"
