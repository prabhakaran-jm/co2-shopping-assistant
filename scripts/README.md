# Deployment Scripts Overview

This directory contains all deployment and teardown scripts for the CO2 Shopping Assistant project.

## Script Comparison

### 🚀 Deployment Scripts

| Script | Purpose | What it Creates | Prerequisites |
|--------|---------|----------------|---------------|
| `deploy-k8s.sh` | **Quick K8s deployment** | Only Kubernetes resources | Existing cluster |
| `deploy-app.sh` | **Application deployment** | K8s resources + Docker builds | Existing cluster + Docker |
| `deploy-infra.sh` | **Complete infrastructure** | Everything from scratch | GCP project + Terraform |

### 🧹 Cleanup Scripts

| Script | Purpose | What it Destroys | Safety |
|--------|---------|------------------|---------|
| `cleanup-k8s.sh` | **K8s cleanup only** | Kubernetes resources only | Safe |
| `teardown-infra.sh` | **Complete teardown** | Everything (cluster, etc.) | ⚠️ Destructive |

## Detailed Script Descriptions

### `deploy-k8s.sh` - CO2 Assistant Only (Quick)
- **Use when**: You have an existing cluster and want to deploy only CO2 Assistant
- **Creates**: CO2 Assistant namespaces, deployments, services, ingress, ConfigMaps
- **Does NOT include**: Online Boutique deployment
- **Time**: ~2-3 minutes
- **Safe**: Yes, only affects Kubernetes resources

### `deploy-app.sh` - Full Application Deployment
- **Use when**: You have an existing cluster and want to deploy the full application
- **Creates**: CO2 Assistant + Online Boutique + Docker builds + managed certificates
- **Time**: ~5-10 minutes (includes Docker builds)
- **Safe**: Yes, only affects Kubernetes and Docker registry

### `deploy-infra.sh` - Complete Infrastructure Deployment
- **Use when**: You want to create everything from scratch
- **Creates**: GKE cluster, Artifact Registry, Docker builds, K8s resources, IAM, etc.
- **Time**: ~15-20 minutes
- **Safe**: Yes, creates new resources (may incur costs)

### `cleanup-k8s.sh` - Kubernetes Cleanup
- **Use when**: You want to remove only the Kubernetes applications
- **Destroys**: All K8s resources (pods, services, ingress, etc.)
- **Time**: ~1-2 minutes
- **Safe**: Yes, preserves cluster and infrastructure

### `teardown-infra.sh` - Complete Infrastructure Teardown
- **Use when**: You want to completely destroy everything
- **Destroys**: GKE cluster, Artifact Registry, IAM bindings, load balancers, etc.
- **Preserves**: Static IPs (including agent-layer-ip for reuse)
- **Time**: ~10-15 minutes
- **Safety**: ⚠️ **DESTRUCTIVE** - Requires confirmation

## Usage Examples

### Quick Development Workflow
```bash
# Deploy to existing cluster (fastest)
./scripts/deploy-k8s.sh

# Clean up when done
./scripts/cleanup-k8s.sh
```

### Application Development Workflow
```bash
# Deploy with Docker builds
./scripts/deploy-app.sh

# Clean up when done
./scripts/cleanup-k8s.sh
```

### Complete Infrastructure Workflow
```bash
# Create everything from scratch
./scripts/deploy-infra.sh --project-id my-project-123 --gemini-api-key YOUR_KEY

# When completely done, destroy everything
./scripts/teardown-infra.sh --project-id my-project-123
```

## Cost Considerations

- **`deploy-k8s.sh`**: No additional costs (uses existing cluster)
- **`deploy-app.sh`**: Minimal costs (Docker registry storage)
- **`deploy-infra.sh`**: Higher costs (GKE cluster, load balancers, static IPs)
- **`teardown-infra.sh`**: Stops all costs (destroys all billable resources)

## Safety Guidelines

1. **Always use `cleanup-k8s.sh` first** before `teardown-infra.sh`
2. **Never run `teardown-infra.sh` in production** without careful review
3. **Test with `deploy-k8s.sh`** before running full infrastructure deployment
4. **Keep your project ID and API keys secure** - never commit them to version control

## Troubleshooting

### If `deploy-infra.sh` fails:
1. Check your GCP project permissions
2. Ensure billing is enabled
3. Verify API quotas aren't exceeded
4. Run `teardown-infra.sh` to clean up partial deployments

### If Kubernetes deployments fail:
1. Check cluster connectivity: `kubectl cluster-info`
2. Verify namespaces: `kubectl get namespaces`
3. Check pod status: `kubectl get pods --all-namespaces`
4. Use `cleanup-k8s.sh` and try again

### If you need to start over:
```bash
# Clean up everything
./scripts/teardown-infra.sh --project-id YOUR_PROJECT_ID --force

# Start fresh
./scripts/deploy-infra.sh --project-id YOUR_PROJECT_ID --gemini-api-key YOUR_KEY
```
