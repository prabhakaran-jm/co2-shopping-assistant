# Scripts Directory Overview

This directory contains the essential deployment scripts for the CO2 Shopping Assistant project. All scripts use a common framework for consistent behavior, error handling, and logging.

## 📁 Core Scripts

### 🚀 Infrastructure Scripts

| Script | Purpose | What it Creates/Destroys | Prerequisites |
|--------|---------|-------------------------|---------------|
| `deploy-infra.sh` | **Complete infrastructure** | GKE cluster, Artifact Registry, IAM, etc. | GCP project + Terraform |
| `teardown-infra.sh` | **Complete infrastructure teardown** | Everything (cluster, registry, etc.) | ⚠️ Destructive |

### 🛠️ Application Scripts

| Script | Purpose | What it Creates/Destroys | Prerequisites |
|--------|---------|-------------------------|---------------|
| `deploy-app.sh` | **Application deployment** | CO2 Assistant + Online Boutique apps | Existing cluster |
| `teardown-app.sh` | **Application teardown** | Applications only (preserves cluster) | Safe |

## 📋 Detailed Script Descriptions

### `deploy-infra.sh` - Infrastructure-Only Deployment
- **Use when**: You want to create the infrastructure foundation
- **Creates**: GKE cluster, Artifact Registry, service accounts, IAM bindings, Terraform state
- **Time**: ~10-15 minutes
- **Safe**: Yes, creates new resources (may incur costs)
- **Features**: Environment variable loading from .env, infrastructure-only focus, guides to deploy-app.sh

### `teardown-infra.sh` - Complete Infrastructure Teardown
- **Use when**: You want to completely destroy everything
- **Destroys**: GKE cluster, Artifact Registry, IAM bindings, load balancers, etc.
- **Preserves**: Static IPs (including agent-layer-ip for reuse)
- **Time**: ~10-15 minutes
- **Safety**: ⚠️ **DESTRUCTIVE** - Requires confirmation
- **Features**: Force mode, comprehensive cleanup, state management

### `deploy-app.sh` - Application Deployment
- **Use when**: You have an existing cluster and want to deploy applications
- **Creates**: CO2 Assistant + Online Boutique applications, Docker builds, ingress, certificates
- **Time**: ~5-10 minutes (with optimizations), ~30-45 minutes (full deployment)
- **Safe**: Yes, only affects applications (preserves cluster)
- **Features**: 
  - Environment variable loading from .env file
  - Speed optimizations (--minimal, --no-cert, --clean flags)
  - Non-blocking certificate provisioning
  - Resource constraint handling
  - Environment-specific configs (dev/prod)

### `teardown-app.sh` - Application Teardown
- **Use when**: You want to remove applications but keep the cluster
- **Destroys**: All application resources (pods, services, ingress, etc.)
- **Preserves**: Cluster, infrastructure, static IPs
- **Time**: ~1-2 minutes
- **Safe**: Yes, preserves cluster and infrastructure
- **Features**: Dry-run mode, selective cleanup, confirmation prompts

## 🚀 Usage Examples

### Complete Infrastructure Workflow
```bash
# Step 1: Create infrastructure foundation
./scripts/deploy-infra.sh --project-id my-project-123 --gemini-api-key YOUR_KEY

# Step 2: Deploy applications to the cluster
./scripts/deploy-app.sh --project-id my-project-123 --gemini-api-key YOUR_KEY

# When completely done, destroy everything
./scripts/teardown-infra.sh --project-id my-project-123 --force
```

### Fast Development Workflow (Recommended)
```bash
# Infrastructure (one-time setup)
./scripts/deploy-infra.sh --project-id my-project-123 --gemini-api-key YOUR_KEY

# Fast application deployment (5-10 minutes)
./scripts/deploy-app.sh --minimal --no-cert

# Clean up when done
./scripts/teardown-app.sh --force
```

### Application-Only Workflow
```bash
# Deploy applications to existing cluster
./scripts/deploy-app.sh --project-id my-project-123 --gemini-api-key YOUR_KEY

# Clean up applications when done
./scripts/teardown-app.sh --force
```

### Development Workflow
```bash
# Deploy for development
./scripts/deploy-app.sh --project-id my-project-123 --gemini-api-key YOUR_KEY --environment dev

# Clean up when done
./scripts/teardown-app.sh --dry-run  # See what would be deleted
./scripts/teardown-app.sh --force    # Actually delete
```

### Production Workflow
```bash
# Deploy for production
./scripts/deploy-app.sh --project-id my-project-123 --gemini-api-key YOUR_KEY --environment prod

# Clean up applications (preserves cluster)
./scripts/teardown-app.sh --force
```

## ⚡ Speed Optimization Flags

### `deploy-app.sh` Optimization Options

| Flag | Purpose | Time Savings | Use Case |
|------|---------|--------------|----------|
| `--minimal` | Use minimal resources (1 replica) | ~15-20 min | Development, resource constraints |
| `--no-cert` | Skip certificate creation | ~15-30 min | Development, HTTP-only testing |
| `--clean` | Clean existing resources first | -5-10 min | Troubleshooting, method changes |
| `--force` | Skip confirmation prompts | ~1-2 min | Automated deployments |

### Speed Comparison

| Deployment Type | Time | Flags | Use Case |
|-----------------|------|-------|----------|
| **Fastest** | ~5-10 min | `--minimal --no-cert` | Development, testing |
| **Fast** | ~15-20 min | `--minimal` | Development with HTTPS |
| **Standard** | ~30-45 min | Default | Production deployment |
| **Thorough** | ~35-50 min | `--clean` | Troubleshooting, clean state |

### Environment Variable Support

Both scripts now automatically load from `.env` file:
```bash
# .env file example
PROJECT_ID=gke10-ai-hackathon
GOOGLE_AI_API_KEY=your-api-key-here
CLUSTER_NAME=co2-assistant-cluster
ENVIRONMENT=development
```

**Priority order**: Command line → .env file → Default values

## 💰 Cost Considerations

- **`deploy-app.sh`**: Minimal costs (uses existing cluster)
- **`deploy-infra.sh`**: Higher costs (GKE cluster, load balancers, static IPs)
- **`teardown-infra.sh`**: Stops all costs (destroys all billable resources)
- **`teardown-app.sh`**: No additional costs (preserves cluster)

## 🔒 Safety Guidelines

1. **Always use `teardown-app.sh` first** before `teardown-infra.sh`
2. **Never run `teardown-infra.sh` in production** without careful review
3. **Test with `deploy-app.sh --environment dev`** before running production deployments
4. **Keep your project ID and API keys secure** - never commit them to version control
5. **Use `--dry-run` flag** to preview what will be deleted before teardown
6. **Use `--force` flag** only when you're certain about the operation

## 🛠️ Common Framework Features

All scripts now use a shared framework (`common.sh`) that provides:

### Consistent Logging
- **Colored output**: INFO (blue), SUCCESS (green), WARNING (yellow), ERROR (red)
- **Structured messages**: Consistent format across all scripts
- **Debug mode**: Enable with `DEBUG=true` environment variable

### Error Handling
- **Automatic error detection**: Scripts exit on first error
- **Cleanup on exit**: Temporary files are automatically cleaned up
- **Error reporting**: Detailed error messages with context

### Validation
- **Tool checking**: Verifies required tools are installed
- **Environment validation**: Checks required environment variables
- **Project structure**: Validates project directory structure

### User Experience
- **Help system**: All scripts support `--help` flag
- **Confirmation prompts**: Interactive confirmation for destructive operations
- **Progress indicators**: Clear progress reporting
- **Script headers/footers**: Professional script presentation

## 🔧 Troubleshooting

### If `deploy-infra.sh` fails:
1. Check your GCP project permissions
2. Ensure billing is enabled
3. Verify API quotas aren't exceeded
4. Run `teardown-infra.sh` to clean up partial deployments

### If `deploy-app.sh` times out on "1 out of 2 replicas":
**This is a common resource constraint issue. Solutions:**
```bash
# Option 1: Use minimal resources (recommended)
./scripts/deploy-app.sh --minimal

# Option 2: Clean deployment
./scripts/deploy-app.sh --clean

# Option 3: Skip certificate for faster deployment
./scripts/deploy-app.sh --minimal --no-cert
```

### If certificate provisioning is slow:
**Certificates take 15-30 minutes. Solutions:**
```bash
# Option 1: Skip certificate (HTTP only)
./scripts/deploy-app.sh --no-cert

# Option 2: Check certificate status separately
kubectl get managedcertificate co2-assistant-cert -n co2-assistant -w
```

### If Kubernetes deployments fail:
1. Check cluster connectivity: `kubectl cluster-info`
2. Verify namespaces: `kubectl get namespaces`
3. Check pod status: `kubectl get pods --all-namespaces`
4. Use `teardown-app.sh` and try again

### If application deployment fails:
1. Check cluster connectivity: `kubectl cluster-info`
2. Verify Docker authentication: `gcloud auth configure-docker`
3. Check namespace status: `kubectl get namespaces`
4. Use `teardown-app.sh` to clean up and try again

### Environment Variable Issues:
```bash
# Check if .env file is loaded
cat .env

# Verify environment variables
echo $PROJECT_ID
echo $GOOGLE_AI_API_KEY

# Use command line override if needed
./scripts/deploy-app.sh --project-id YOUR_PROJECT_ID --gemini-api-key YOUR_KEY
```

### If you need to start over:
```bash
# Clean up everything
./scripts/teardown-infra.sh --project-id YOUR_PROJECT_ID --force

# Start fresh
./scripts/deploy-infra.sh --project-id YOUR_PROJECT_ID --gemini-api-key YOUR_KEY
```

## 🔒 Certificate Protection & Management

### Certificate Safety Features:
- **Auto-renewal**: Google Managed Certificates renew automatically
- **Deployment protection**: `deploy-app.sh` never deletes existing certificates
- **Teardown protection**: Certificates preserved by default with explicit flags required for deletion

### Safe Certificate Operations:

#### ✅ **SAFE - Certificate Preserved:**
```bash
# Regular deployments (certificate never deleted)
./scripts/deploy-app.sh
./scripts/deploy-app.sh --minimal
./scripts/deploy-app.sh --clean

# App teardown with certificate preservation
./scripts/teardown-app.sh --keep-certificates

# Infrastructure teardown (certificates preserved by default)
./scripts/teardown-infra.sh
```

#### ⚠️ **DANGEROUS - Certificate Deleted:**
```bash
# App teardown that deletes certificates (requires explicit flag)
./scripts/teardown-app.sh --delete-certificates

# Infrastructure teardown that deletes certificates
./scripts/teardown-infra.sh --delete-certificates
```

### Certificate Status Commands:
```bash
# Check certificate status
kubectl get managedcertificate co2-assistant-cert -n co2-assistant

# Watch certificate provisioning
kubectl get managedcertificate co2-assistant-cert -n co2-assistant -w

# Check certificate details
kubectl describe managedcertificate co2-assistant-cert -n co2-assistant
```

### Certificate Recovery:
If certificate is accidentally deleted:
```bash
# Recreate certificate
kubectl apply -f k8s/managed-certificate.yaml

# Check status (takes 15-30 minutes to provision)
kubectl get managedcertificate co2-assistant-cert -n co2-assistant -w
```

### Best Practices:
1. **Always use `--keep-certificates` flag** with teardown scripts
2. **Never use `--delete-certificates`** unless absolutely necessary
3. **Check certificate status** before major operations
4. **Keep certificate YAML file** (`k8s/managed-certificate.yaml`) for recovery
