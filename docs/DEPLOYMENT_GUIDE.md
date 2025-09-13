# 🚀 Deployment Guide

This guide explains the different deployment options and when to use each one.

## 📋 Deployment Options Overview

| Deployment Method | Use Case | Security | Monitoring | Cost | Recommended For |
|------------------|----------|----------|------------|------|-----------------|
| **Environment-Specific** | Production/Dev | Full/Relaxed | Comprehensive/Basic | Optimized | **Most Use Cases** |
| **Complete Infrastructure** | Quick Setup | Basic | Basic | Standard | Testing/Demo |
| **Terraform Only** | Infrastructure Only | None | None | Infrastructure Only | Advanced Users |

## 🎯 Recommended Deployment Methods

### **1. Environment-Specific Deployment (Recommended)**

#### **Development Environment**
```bash
# Cost-optimized with permissive security for easy testing
./scripts/deploy-environment.sh dev
```

**Features:**
- ✅ **Cost-optimized**: $5-8/day
- ✅ **Permissive network policies** (easy testing)
- ✅ **Basic monitoring** (Prometheus only)
- ✅ **Load generator enabled** (for testing)
- ✅ **Pod security policies** (security baseline)

#### **Production Environment**
```bash
# Full security and comprehensive monitoring
./scripts/deploy-environment.sh prod
```

**Features:**
- 🔒 **Strict security**: Zero-trust network policies
- 📊 **Full monitoring**: Prometheus + Grafana + Jaeger
- 🚫 **Load generator disabled** (cost savings)
- 💰 **Production-ready**: $15-25/day
- 🎯 **SLA monitoring**: 99.9% availability tracking

### **2. Interactive Infrastructure Deployment**

```bash
# Interactive deployment with Terraform infrastructure
./scripts/deploy-infra.sh --project-id YOUR_PROJECT_ID --gemini-api-key YOUR_API_KEY
```

**Interactive Options:**
- **Option 1**: Infrastructure Only (Terraform + Basic Kubernetes)
- **Option 2**: Environment-Specific Deployment (Redirects to deploy-environment.sh)

**Features (Option 1):**
- ✅ **Full Terraform infrastructure** (GKE cluster, Artifact Registry)
- ✅ **Basic security policies** (Pod Security Policy)
- ✅ **Basic monitoring** (Prometheus dev config)
- ⚠️ **No environment-specific** network policies
- ⚠️ **No comprehensive observability**

**When to use:**
- Quick setup for demos
- Testing infrastructure components
- When you need full Terraform deployment
- When you want to choose deployment approach interactively

## 🔧 Deployment Scripts Comparison

### **deploy-environment.sh**
- ✅ **Environment-aware** (dev/prod specific)
- ✅ **Security policies** (network + pod security)
- ✅ **Monitoring stack** (environment-appropriate)
- ✅ **Cost optimization** (resource right-sizing)
- ✅ **Production-ready** features

### **deploy-infra.sh**
- ✅ **Complete infrastructure** (Terraform + Kubernetes)
- ✅ **Basic security** (pod security policies)
- ✅ **Basic monitoring** (Prometheus)
- ⚠️ **Generic deployment** (not environment-specific)
- ⚠️ **Limited observability**

## 📊 Security & Monitoring Comparison

### **Development Environment**
```yaml
Network Policies: Permissive (allows all traffic)
Pod Security: Non-root containers
Monitoring: Basic Prometheus (60s intervals)
Observability: Grafana dashboard only
Alerting: Basic health checks
Cost: $5-8/day
```

### **Production Environment**
```yaml
Network Policies: Strict zero-trust
Pod Security: Hardened (no privileges)
Monitoring: Full Prometheus (15s intervals)
Observability: Grafana + Jaeger tracing
Alerting: SLA alerts + PagerDuty
Cost: $15-25/day
```

## 🚀 Quick Start Commands

### **Interactive Deployment (Recommended)**
```bash
# 1. Clone and setup
git clone https://github.com/prabhakaran-jm/co2-shopping-assistant.git
cd co2-shopping-assistant

# 2. Configure environment
echo "GOOGLE_PROJECT_ID=your-project-id" > .env
echo "GOOGLE_AI_API_KEY=your-api-key" >> .env

# 3. Run interactive deployment
./scripts/deploy-infra.sh --project-id your-project-id --gemini-api-key your-api-key

# The script will ask:
# Choose your deployment approach:
#   1) Infrastructure Only (Terraform + Basic Kubernetes) - Quick setup
#   2) Environment-Specific Deployment (Recommended) - Full security & monitoring
# Enter your choice (1 or 2):
```

### **Direct Environment Deployment**
```bash
# For Development
./scripts/deploy-environment.sh dev

# For Production
./scripts/deploy-environment.sh prod

# Access monitoring tools (Production only)
kubectl port-forward svc/grafana 3000:80 -n co2-assistant
kubectl port-forward svc/jaeger-all-in-one 16686:16686 -n co2-assistant
```

## 🔍 Post-Deployment Validation

### **Check Deployment Status**
```bash
# Verify all pods are running
kubectl get pods --all-namespaces

# Check HPA status
kubectl get hpa -n co2-assistant

# Verify network policies
kubectl get networkpolicy --all-namespaces

# Check monitoring
kubectl get configmap -n co2-assistant | grep prometheus
```

### **Access Applications**
```bash
# CO2 Assistant
kubectl port-forward svc/co2-assistant-service 8000:80 -n co2-assistant

# Online Boutique
kubectl port-forward svc/frontend 8080:80 -n online-boutique

# Grafana (Production only)
kubectl port-forward svc/grafana 3000:80 -n co2-assistant
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **Pods Pending**
```bash
# Check resource constraints
kubectl describe pod <pod-name> -n <namespace>

# Check node capacity
kubectl top nodes
```

#### **Network Policy Issues**
```bash
# Check network policies
kubectl get networkpolicy --all-namespaces

# Test connectivity
kubectl exec -it <pod-name> -n <namespace> -- curl <service-url>
```

#### **Monitoring Not Working**
```bash
# Check Prometheus config
kubectl get configmap prometheus-config-dev -n co2-assistant -o yaml

# Check metrics endpoint
kubectl port-forward svc/co2-assistant-service 8000:80 -n co2-assistant
curl http://localhost:8000/metrics
```

## 💡 Best Practices

1. **Use environment-specific deployments** for production
2. **Always validate** network policies in development first
3. **Monitor resource usage** to optimize costs
4. **Use Grafana dashboards** for production monitoring
5. **Enable Jaeger tracing** for performance debugging
6. **Test security policies** before production deployment

## 📚 Additional Resources

- [Production Checklist](PRODUCTION_CHECKLIST.md)
- [Architecture Guide](architecture.md)
- [Security Guide](../SECURITY.md)
- [README](../README.md)
