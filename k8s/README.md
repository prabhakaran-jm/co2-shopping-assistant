# CO2 Shopping Assistant - Kubernetes Deployment

This directory contains the Kubernetes deployment configurations for the CO2 Shopping Assistant system with Online Boutique integration.

## Architecture Overview

The system is deployed across two namespaces:
- **`co2-assistant`**: CO2 Shopping Assistant services (API and UI)
- **`online-boutique`**: Online Boutique microservices

## File Structure

### Core Deployment Files
- `namespaces.yaml` - Namespace definitions for both services
- `https-ingress.yaml` - HTTPS-only ingress configuration with SSL certificates
- `managed-certificate.yaml` - Google Managed Certificate for SSL
- `co2-assistant-deployment.yaml` - CO2 Assistant API deployment
- `ui-deployment.yaml` - CO2 Assistant UI deployment
- `ui-configmap.yaml` - ConfigMap containing the UI HTML content
- `ob-proxy.yaml` - Nginx proxy for cross-namespace routing to Online Boutique

### External Scripts
- `../scripts/deploy-k8s.sh` - Deploy only Kubernetes resources (quick)
- `../scripts/cleanup-k8s.sh` - Clean up only Kubernetes resources
- `../scripts/deploy-app.sh` - Application-only deployment script (includes Docker builds)
- `../scripts/deploy-infra.sh` - Full infrastructure deployment script (Terraform + everything)
- `../scripts/teardown-infra.sh` - Complete infrastructure teardown script

## Deployment

### Prerequisites

**For Application-Only Deployment (`k8s/deploy.sh`):**
- Existing Kubernetes cluster (GKE recommended)
- `kubectl` configured and connected to cluster
- `helm` installed
- Online Boutique helm chart available at `../online-boutique/helm-chart`

**For Full Infrastructure Deployment (`scripts/deploy.sh`):**
- Google Cloud Project with billing enabled
- `gcloud` CLI configured
- `terraform` installed
- `kubectl` installed
- `docker` installed
- `helm` installed

### Quick Deployment

**Option 1: Kubernetes Resources Only (Quick)**
```bash
# Deploy only k8s resources to existing cluster
./scripts/deploy-k8s.sh
```

**Option 2: Application-Only Deployment (Recommended)**
```bash
# Deploy applications to existing cluster (includes Docker builds)
./scripts/deploy-app.sh
```

**Option 3: Full Infrastructure Deployment**
```bash
# Deploy everything from scratch (infrastructure + applications)
./scripts/deploy-infra.sh --project-id YOUR_PROJECT_ID --gemini-api-key YOUR_API_KEY
```

**Cleanup Options:**
```bash
# Clean up only Kubernetes resources
./scripts/cleanup-k8s.sh

# Complete infrastructure teardown (destroys everything)
./scripts/teardown-infra.sh --project-id YOUR_PROJECT_ID
```

### Manual Deployment Steps
1. Create namespaces:
   ```bash
   kubectl apply -f namespaces.yaml
   ```

2. Deploy Online Boutique:
   ```bash
   helm install online-boutique ../online-boutique/helm-chart \
     --namespace online-boutique \
     --create-namespace \
     --values online-boutique-namespace-config.yaml
   ```

3. Deploy CO2 Assistant:
   ```bash
   kubectl apply -f co2-assistant-deployment.yaml
   kubectl apply -f ui-deployment.yaml
   ```

4. Deploy managed certificate and ingress:
   ```bash
   kubectl apply -f managed-certificate.yaml
   kubectl apply -f https-ingress.yaml
   ```

## Access Points

After deployment, the services will be available at:
- **CO2 Assistant UI**: `https://assistant.cloudcarta.com`
- **CO2 Assistant API**: `https://assistant.cloudcarta.com/api`
- **Online Boutique**: `https://ob.cloudcarta.com`

## Deployment Scripts Comparison

### `scripts/deploy-app.sh` - Application-Only Deployment
- **Use case**: Deploy to existing cluster
- **Namespaces**: `co2-assistant` and `online-boutique`
- **Domains**: `assistant.cloudcarta.com` and `ob.cloudcarta.com`
- **Online Boutique**: Deployed via Helm chart
- **Duration**: ~5-10 minutes
- **Requirements**: Existing cluster, kubectl, helm

### `scripts/deploy-infra.sh` - Full Infrastructure Deployment
- **Use case**: Complete deployment from scratch
- **Namespaces**: `co2-assistant` and `online-boutique`
- **Domains**: `assistant.cloudcarta.com` and `ob.cloudcarta.com`
- **Online Boutique**: Deployed via Helm chart (with kubectl fallback)
- **Duration**: ~15-20 minutes
- **Requirements**: GCP project, terraform, gcloud, docker, kubectl, helm

## Key Features

### HTTPS Ingress Configuration
- Single ingress controller for both services
- **HTTPS enforcement** - HTTP traffic is completely blocked
- Automatic SSL certificate management with Google Managed Certificates
- Host-based routing to different namespaces
- **Advanced Security Features**:
  - TLS 1.2+ only with secure cipher suites
  - HSTS headers with preload (1 year max-age)
  - Security headers (XSS, CSRF, clickjacking protection)
  - Content Security Policy (CSP)
  - Rate limiting (100 requests/minute)
  - CORS disabled by default

### Namespace Separation
- **co2-assistant**: Contains the CO2 shopping assistant services
- **online-boutique**: Contains all Online Boutique microservices
- Cross-namespace communication via service discovery

### SSL/TLS & Security
- **Automatic certificate provisioning** via Google Managed Certificates
- **HTTPS enforcement** for all services (HTTP traffic blocked)
- **TLS 1.2+ only** with secure cipher suites
- **HSTS headers** with preload for 1 year
- Certificate domains:
  - `assistant.cloudcarta.com`
  - `ob.cloudcarta.com`

### Security Headers
- **Strict-Transport-Security**: Forces HTTPS for 1 year
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-XSS-Protection**: Enables XSS filtering
- **Referrer-Policy**: Controls referrer information
- **Content-Security-Policy**: Prevents XSS and data injection attacks
- **Rate Limiting**: 100 requests per minute per IP

## Monitoring and Troubleshooting

### Check Deployment Status
```bash
# Check CO2 Assistant pods
kubectl get pods -n co2-assistant

# Check Online Boutique pods
kubectl get pods -n online-boutique

# Check ingress status
kubectl get ingress -n co2-assistant
```

### View Logs
```bash
# CO2 Assistant API logs
kubectl logs -f deployment/co2-assistant -n co2-assistant

# CO2 Assistant UI logs
kubectl logs -f deployment/co2-assistant-ui -n co2-assistant

# Online Boutique frontend logs
kubectl logs -f deployment/frontend -n online-boutique
```

### Cleanup
```bash
# Remove all deployments
kubectl delete namespace co2-assistant online-boutique
```

## Configuration Notes

### Environment Variables
The CO2 Assistant connects to Online Boutique using the service name:
```
BOUTIQUE_BASE_URL=http://frontend.online-boutique.svc.cluster.local:80
```

### Resource Limits
- CO2 Assistant API: 256Mi memory, 200m CPU
- CO2 Assistant UI: 128Mi memory, 100m CPU
- Online Boutique services use default Helm values

### Health Checks
All services include liveness and readiness probes for reliable operation.

## Cleaned Up Structure

This setup has been cleaned up and simplified:
- ❌ `simple-ingress.yaml` (removed - HTTP only)
- ❌ `unified-ingress.yaml` (removed - redundant)
- ✅ `https-ingress.yaml` (main HTTPS ingress)
- ✅ `managed-certificate.yaml` (separate certificate management)
- ✅ `namespaces.yaml` (namespace definitions)

The cleaned up structure provides:
- ✅ Single HTTPS ingress configuration
- ✅ Separate managed certificate for better control
- ✅ Proper namespace separation
- ✅ Simplified deployment process
- ✅ Better security and monitoring
