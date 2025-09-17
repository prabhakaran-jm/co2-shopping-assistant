# 🚀 Complete Deployment Guide
## CO2-Aware Shopping Assistant

This comprehensive guide covers all deployment options for the CO2-Aware Shopping Assistant, from quick start to production-ready deployments.

## 📋 Deployment Options Overview

| Deployment Method | Use Case | Security | Monitoring | Cost | Time | Recommended For |
|------------------|----------|----------|------------|------|------|-----------------|
| **Quick Start** | Demo/Testing | Basic | Minimal | $5-8/day | 10 min | **First-time users** |
| **Environment-Specific** | Production/Dev | Full/Relaxed | Comprehensive/Basic | Optimized | 20 min | **Most Use Cases** |
| **Complete Infrastructure** | Full Setup | Basic | Basic | Standard | 30 min | **Complete control** |
| **Terraform Only** | Infrastructure Only | None | None | Infrastructure Only | 15 min | **Advanced Users** |

## 🎯 Quick Start (Recommended for First-Time Users)

### **Prerequisites**
- Google Cloud Project with billing enabled
- Google Gemini API key
- `gcloud` CLI installed and authenticated
- `kubectl` configured for your GKE cluster

### **Step 1: Clone and Setup**
```bash
# Clone the repository
git clone https://github.com/prabhakaran-jm/co2-shopping-assistant.git
cd co2-shopping-assistant

# Set environment variables
export GOOGLE_PROJECT_ID="your-gcp-project-id"
export GOOGLE_AI_API_KEY="your-gemini-api-key"
```

### **Step 2: Deploy Infrastructure**
```bash
# Deploy GKE cluster and basic infrastructure
./scripts/deploy-infra.sh --project-id $GOOGLE_PROJECT_ID --gemini-api-key $GOOGLE_AI_API_KEY

# Choose option 1: Infrastructure Only
# This will create:
# - GKE Autopilot cluster
# - Artifact Registry
# - Basic security policies
# - Basic monitoring
```

### **Step 3: Deploy Application**
```bash
# Deploy the CO2-Aware Shopping Assistant
kubectl apply -f k8s/namespaces.yaml
kubectl apply -f k8s/co2-assistant-deployment.yaml
kubectl apply -f k8s/ob-proxy.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/managed-certificate.yaml
kubectl apply -f k8s/https-ingress.yaml
```

### **Step 4: Verify Deployment**
```bash
# Check all pods are running
kubectl get pods --all-namespaces

# Access the application
kubectl port-forward svc/co2-assistant-service 8000:80 -n co2-assistant

# Open browser to http://localhost:8000
```

**✅ Quick Start Complete!** You now have a working CO2-Aware Shopping Assistant.

## 🏗️ Environment-Specific Deployment (Recommended for Production)

### **Development Environment**
```bash
# Cost-optimized with permissive security for easy testing
./scripts/deploy-app.sh dev
```

**Development Features:**
- ✅ **Cost-optimized**: $5-8/day
- ✅ **Permissive network policies** (easy testing)
- ✅ **Basic monitoring** (Prometheus only)
- ✅ **Load generator enabled** (for testing)
- ✅ **Pod security policies** (security baseline)

### **Production Environment**
```bash
# Full security and comprehensive monitoring
./scripts/deploy-app.sh prod
```

**Production Features:**
- 🔒 **Strict security**: Zero-trust network policies
- 📊 **Full monitoring**: Prometheus + Grafana + Jaeger
- 🚫 **Load generator disabled** (cost savings)
- 💰 **Production-ready**: $15-25/day
- 🎯 **SLA monitoring**: 99.9% availability tracking

## 🔧 Complete Infrastructure Deployment

### **Interactive Deployment**
```bash
# Interactive deployment with full control
./scripts/deploy-infra.sh --project-id YOUR_PROJECT_ID --gemini-api-key YOUR_API_KEY

# Choose option 2: Environment-Specific Deployment
# This will redirect to deploy-app.sh with environment selection
```

### **Manual Infrastructure Setup**
```bash
# 1. Create GKE cluster
gcloud container clusters create co2-assistant-cluster \
  --zone=us-central1-a \
  --cluster-version=latest \
  --machine-type=e2-standard-2 \
  --num-nodes=3 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10

# 2. Create Artifact Registry
gcloud artifacts repositories create co2-assistant-repo \
  --repository-format=docker \
  --location=us-central1

# 3. Configure kubectl
gcloud container clusters get-credentials co2-assistant-cluster --zone=us-central1-a
```

## 🐳 Docker Deployment

### **Build and Push Images**
```bash
# Build the application image
docker build -t us-central1-docker.pkg.dev/$GOOGLE_PROJECT_ID/co2-assistant-repo/co2-assistant:latest .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/$GOOGLE_PROJECT_ID/co2-assistant-repo/co2-assistant:latest
```

### **Deploy with Docker Compose (Local Testing)**
```bash
# Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  co2-assistant:
    image: us-central1-docker.pkg.dev/$GOOGLE_PROJECT_ID/co2-assistant-repo/co2-assistant:latest
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_AI_API_KEY=$GOOGLE_AI_API_KEY
      - GOOGLE_PROJECT_ID=$GOOGLE_PROJECT_ID
    restart: unless-stopped
EOF

# Run locally
docker-compose up -d
```

## ☸️ Kubernetes Deployment

### **Namespace Setup**
```bash
# Create namespaces
kubectl apply -f k8s/namespaces.yaml

# Verify namespaces
kubectl get namespaces | grep -E "(co2-assistant|online-boutique)"
```

### **Secrets Management**
```bash
# Create secrets
kubectl create secret generic co2-assistant-secrets \
  --from-literal=google-ai-api-key="$GOOGLE_AI_API_KEY" \
  --from-literal=google-project-id="$GOOGLE_PROJECT_ID" \
  -n co2-assistant

# Verify secrets
kubectl get secrets -n co2-assistant
```

### **Application Deployment**
```bash
# Deploy main application
kubectl apply -f k8s/co2-assistant-deployment.yaml

# Deploy Online Boutique proxy
kubectl apply -f k8s/ob-proxy.yaml

# Deploy horizontal pod autoscaler
kubectl apply -f k8s/hpa.yaml

# Deploy managed certificate
kubectl apply -f k8s/managed-certificate.yaml

# Deploy ingress
kubectl apply -f k8s/https-ingress.yaml
```

### **Verification**
```bash
# Check deployment status
kubectl get deployments -n co2-assistant
kubectl get pods -n co2-assistant
kubectl get services -n co2-assistant
kubectl get ingress -n co2-assistant

# Check HPA status
kubectl get hpa -n co2-assistant

# Check certificate status
kubectl describe managedcertificate co2-assistant-cert -n co2-assistant
```

## 🔒 Security Configuration

### **Network Policies**

#### **Development (Permissive)**
```bash
# Apply permissive network policies for development
kubectl apply -f security/network-policy-dev.yaml
```

#### **Production (Strict)**
```bash
# Apply strict network policies for production
kubectl apply -f security/network-policy-prod.yaml
```

### **Pod Security Policies**
```bash
# Apply pod security policies
kubectl apply -f security/pod-security-policy.yaml
```

### **RBAC Configuration**
```bash
# Create service account
kubectl create serviceaccount co2-assistant-sa -n co2-assistant

# Create cluster role binding
kubectl create clusterrolebinding co2-assistant-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=co2-assistant:co2-assistant-sa
```

## 📊 Monitoring Setup

### **Development Monitoring**
```bash
# Deploy basic Prometheus monitoring
kubectl apply -f monitoring/prometheus-config-dev.yaml
```

### **Production Monitoring**
```bash
# Deploy comprehensive monitoring stack
kubectl apply -f monitoring/prometheus-config-prod.yaml
kubectl apply -f monitoring/observability-stack.yaml
```

### **Access Monitoring Tools**
```bash
# Grafana Dashboard
kubectl port-forward svc/grafana 3000:80 -n co2-assistant
# Access: http://localhost:3000

# Jaeger Tracing
kubectl port-forward svc/jaeger-all-in-one 16686:16686 -n co2-assistant
# Access: http://localhost:16686

# Prometheus Metrics
kubectl port-forward svc/prometheus 9090:9090 -n co2-assistant
# Access: http://localhost:9090
```

## 🌐 Domain Configuration

### **Custom Domain Setup**
```bash
# Update ingress with your domain
kubectl patch ingress co2-assistant-ingress -n co2-assistant --type='merge' -p='{
  "spec": {
    "rules": [
      {
        "host": "assistant.yourdomain.com",
        "http": {
          "paths": [
            {
              "path": "/",
              "pathType": "Prefix",
              "backend": {
                "service": {
                  "name": "co2-assistant-service",
                  "port": {
                    "number": 80
                  }
                }
              }
            }
          ]
        }
      }
    ]
  }
}'
```

### **DNS Configuration**
```bash
# Get the external IP
kubectl get ingress co2-assistant-ingress -n co2-assistant

# Add DNS records:
# A record: assistant.yourdomain.com -> EXTERNAL_IP
# A record: ob.yourdomain.com -> EXTERNAL_IP
```

## 🧪 Testing & Validation

### **Health Checks**
```bash
# Check application health
curl http://assistant.cloudcarta.com/api/health

# Check A2A protocol health
curl http://assistant.cloudcarta.com/api/a2a/health

# Check MCP transport health
curl http://assistant.cloudcarta.com/api/mcp
```

### **Functional Testing**
```bash
# Test chat functionality
curl -X POST "http://assistant.cloudcarta.com/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Find eco-friendly electronics", "session_id": "test-session"}'

# Test A2A communication
curl -X POST "http://assistant.cloudcarta.com/api/a2a/send" \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "ProductDiscoveryAgent", "task": {"message": "Hello"}}'

# Test MCP transport
curl "http://assistant.cloudcarta.com/api/mcp/boutique/tools"
```

### **Performance Testing**
```bash
# Run load tests
python -m pytest tests/performance/ -v

# Monitor resource usage
kubectl top pods -n co2-assistant
kubectl top nodes
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **Pods Pending**
```bash
# Check resource constraints
kubectl describe pod <pod-name> -n co2-assistant

# Check node capacity
kubectl top nodes

# Check events
kubectl get events -n co2-assistant --sort-by='.lastTimestamp'
```

#### **Network Policy Issues**
```bash
# Check network policies
kubectl get networkpolicy --all-namespaces

# Test connectivity
kubectl exec -it <pod-name> -n co2-assistant -- curl <service-url>

# Check DNS resolution
kubectl exec -it <pod-name> -n co2-assistant -- nslookup <service-name>
```

#### **Certificate Issues**
```bash
# Check certificate status
kubectl describe managedcertificate co2-assistant-cert -n co2-assistant

# Check certificate provisioning
kubectl get certificaterequests -n co2-assistant

# Check ingress status
kubectl describe ingress co2-assistant-ingress -n co2-assistant
```

#### **Monitoring Issues**
```bash
# Check Prometheus config
kubectl get configmap prometheus-config-dev -n co2-assistant -o yaml

# Check metrics endpoint
kubectl port-forward svc/co2-assistant-service 8000:80 -n co2-assistant
curl http://localhost:8000/metrics

# Check logs
kubectl logs -f deployment/co2-assistant -n co2-assistant
```

### **Debug Commands**
```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n co2-assistant

# Check pod logs
kubectl logs <pod-name> -n co2-assistant --tail=100

# Execute commands in pod
kubectl exec -it <pod-name> -n co2-assistant -- /bin/bash

# Check service endpoints
kubectl get endpoints -n co2-assistant

# Check ingress status
kubectl describe ingress -n co2-assistant
```

## 📈 Scaling & Optimization

### **Horizontal Scaling**
```bash
# Check HPA status
kubectl get hpa -n co2-assistant

# Scale manually if needed
kubectl scale deployment co2-assistant --replicas=5 -n co2-assistant

# Update HPA configuration
kubectl patch hpa co2-assistant-hpa -n co2-assistant --type='merge' -p='{
  "spec": {
    "minReplicas": 3,
    "maxReplicas": 10,
    "targetCPUUtilizationPercentage": 70
  }
}'
```

### **Resource Optimization**
```bash
# Check resource usage
kubectl top pods -n co2-assistant
kubectl top nodes

# Update resource requests/limits
kubectl patch deployment co2-assistant -n co2-assistant --type='merge' -p='{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "co2-assistant",
            "resources": {
              "requests": {
                "cpu": "200m",
                "memory": "256Mi"
              },
              "limits": {
                "cpu": "500m",
                "memory": "512Mi"
              }
            }
          }
        ]
      }
    }
  }
}'
```

## 🔄 Updates & Maintenance

### **Application Updates**
```bash
# Build new image
docker build -t us-central1-docker.pkg.dev/$GOOGLE_PROJECT_ID/co2-assistant-repo/co2-assistant:v2.0 .

# Push new image
docker push us-central1-docker.pkg.dev/$GOOGLE_PROJECT_ID/co2-assistant-repo/co2-assistant:v2.0

# Update deployment
kubectl set image deployment/co2-assistant co2-assistant=us-central1-docker.pkg.dev/$GOOGLE_PROJECT_ID/co2-assistant-repo/co2-assistant:v2.0 -n co2-assistant

# Check rollout status
kubectl rollout status deployment/co2-assistant -n co2-assistant
```

### **Rollback**
```bash
# Rollback to previous version
kubectl rollout undo deployment/co2-assistant -n co2-assistant

# Check rollout history
kubectl rollout history deployment/co2-assistant -n co2-assistant
```

## 🧹 Cleanup

### **Remove Application**
```bash
# Remove application resources
kubectl delete -f k8s/https-ingress.yaml
kubectl delete -f k8s/managed-certificate.yaml
kubectl delete -f k8s/hpa.yaml
kubectl delete -f k8s/ob-proxy.yaml
kubectl delete -f k8s/co2-assistant-deployment.yaml
kubectl delete -f k8s/namespaces.yaml
```

### **Remove Infrastructure**
```bash
# Remove GKE cluster
gcloud container clusters delete co2-assistant-cluster --zone=us-central1-a

# Remove Artifact Registry
gcloud artifacts repositories delete co2-assistant-repo --location=us-central1
```

## 📚 Additional Resources

- **[Production Checklist](PRODUCTION_CHECKLIST.md)** - Complete production deployment guide
- **[Architecture Guide](architecture.md)** - Detailed system architecture
- **[Security Guide](../SECURITY.md)** - Security best practices
- **[README](../README.md)** - Project overview and features

## 💡 Best Practices

1. **Use environment-specific deployments** for production
2. **Always validate** network policies in development first
3. **Monitor resource usage** to optimize costs
4. **Use Grafana dashboards** for production monitoring
5. **Enable Jaeger tracing** for performance debugging
6. **Test security policies** before production deployment
7. **Keep images updated** with security patches
8. **Monitor certificate expiration** and renewal
9. **Use HPA** for automatic scaling
10. **Implement proper logging** and monitoring

This deployment guide provides comprehensive coverage of all deployment scenarios, from quick start to production-ready deployments with full security and monitoring.
