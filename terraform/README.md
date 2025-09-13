# Terraform Infrastructure for CO2-Aware Shopping Assistant

This directory contains the Terraform configuration for deploying the complete CO2-Aware Shopping Assistant infrastructure on Google Kubernetes Engine (GKE) Autopilot.

## Architecture

The Terraform configuration creates:

- **GKE Autopilot Cluster**: Managed Kubernetes cluster with automatic scaling
- **Artifact Registry**: Docker repository for application images
- **Service Accounts**: Workload Identity for secure access to Google Cloud services
- **Kubernetes Namespaces**: Separate namespaces for Online Boutique and CO2 Assistant
- **Network Policies**: Security policies for inter-service communication
- **Monitoring**: Google Cloud Managed Service for Prometheus

## Prerequisites

1. **Google Cloud Project**: Active GCP project with billing enabled
2. **Terraform**: Version >= 1.5.0 installed
3. **Google Cloud SDK**: `gcloud` CLI installed and authenticated
4. **kubectl**: Kubernetes CLI installed
5. **Docker**: For building and pushing images
6. **Existing Terraform Backend**: GCS bucket for state storage

## Configuration Setup

Before running Terraform, you need to set up your configuration files:

1. **Copy the example files:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   cp backend.hcl.example backend.hcl
   ```

2. **Update `terraform.tfvars`** with your specific values:
   - `project_id`: Your GCP project ID
   - `region`: Your preferred GCP region
   - `cluster_name`: Name for your GKE cluster

3. **Update `backend.hcl`** with your Terraform state bucket:
   - `bucket`: Your GCS bucket name for Terraform state
   - `prefix`: Path prefix for your state files

> **Note**: `backend.hcl` and `terraform.tfvars` are in `.gitignore` and will not be committed to the repository. This ensures your specific configuration remains private.

## Quick Start

### 1. Set up Terraform variables

```bash
# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars
```

Required variables:
- `project_id`: Your GCP project ID
- `region`: GCP region (default: us-central1)

### 2. Initialize Terraform with backend configuration

```bash
# Initialize Terraform using backend.hcl
terraform init -backend-config=backend.hcl
```

### 3. Deploy infrastructure

```bash
# Plan the deployment
terraform plan

# Apply the deployment
terraform apply
```

### 4. Deploy applications

```bash
# Use the automated deployment script
../scripts/deploy.sh \
  --project-id YOUR_PROJECT_ID \
  --gemini-api-key YOUR_API_KEY
```

## Manual Deployment Steps

If you prefer to deploy manually:

### 1. Configure kubectl

```bash
# Get cluster credentials
gcloud container clusters get-credentials co2-assistant-cluster --region us-central1
```

### 2. Configure Docker authentication

```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 3. Build and push images

```bash
# Build CO2 Assistant image
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/co2-assistant-repo/co2-assistant:latest .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/co2-assistant-repo/co2-assistant:latest
```

### 4. Deploy Online Boutique

```bash
# Clone Online Boutique
git clone https://github.com/GoogleCloudPlatform/microservices-demo.git online-boutique

# Deploy to Kubernetes
kubectl apply -f online-boutique/release/kubernetes-manifests.yaml
```

### 5. Deploy CO2-Aware Shopping Assistant

```bash
# Deploy Kubernetes manifests
kubectl apply -f ../k8s/

# Create secrets
kubectl create secret generic co2-assistant-secrets \
  --namespace=co2-assistant \
  --from-literal=google-ai-api-key="YOUR_API_KEY"
```

## Configuration

### Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `project_id` | GCP Project ID | - | Yes |
| `region` | GCP Region | `us-central1` | No |
| `cluster_name` | GKE Cluster Name | `co2-assistant-cluster` | No |
| `co2_assistant_namespace` | CO2 Assistant Namespace | `co2-assistant` | No |
| `online_boutique_namespace` | Online Boutique Namespace | `default` | No |
| `artifact_registry_repo_name` | Artifact Registry Repository | `co2-assistant-repo` | No |
| `deletion_protection` | Enable Deletion Protection | `false` | No |
| `enable_network_policy` | Enable Network Policies | `true` | No |
| `enable_managed_prometheus` | Enable Managed Prometheus | `true` | No |

### Backend Configuration

The Terraform configuration uses a backend configuration file (`backend.hcl`) for state management:

```hcl
bucket = "your-terraform-bucket"
prefix = "co2-shopping-assistant/dev"
```

This provides:
- Centralized state management
- Environment separation
- CI/CD pipeline compatibility

## Resources Created

### Google Cloud Resources

- **GKE Autopilot Cluster**: `google_container_cluster.autopilot`
- **Artifact Registry Repository**: `google_artifact_registry_repository.co2_assistant_repo`
- **Service Account**: `google_service_account.co2_assistant_sa`
- **IAM Bindings**: Various roles for the service account
- **Project Services**: Required APIs enabled

### Kubernetes Resources

- **Namespaces**: `kubernetes_namespace.co2_assistant`, `kubernetes_namespace.online_boutique`
- **Secrets**: `kubernetes_secret.co2_assistant_secrets`
- **ConfigMaps**: `kubernetes_config_map.co2_assistant_config`
- **Service Account**: `kubernetes_service_account.co2_assistant_sa`
- **Network Policy**: `kubernetes_network_policy.co2_assistant_network_policy`

## Outputs

The Terraform configuration provides several useful outputs:

- `cluster_name`: GKE cluster name
- `cluster_endpoint`: Cluster API endpoint
- `docker_repository_url`: Artifact Registry URL
- `service_account_email`: Service account email
- `kubectl_config_command`: Command to configure kubectl
- `deployment_instructions`: Step-by-step deployment guide

## Monitoring and Observability

The infrastructure includes:

- **Google Cloud Managed Service for Prometheus**: Automatic metrics collection
- **Google Cloud Logging**: Centralized log aggregation
- **Google Cloud Monitoring**: Dashboards and alerting
- **Workload Identity**: Secure access to Google Cloud services

## Security Features

- **Network Policies**: Restrict inter-pod communication
- **Workload Identity**: No service account keys required
- **IAM Roles**: Least privilege access
- **Encryption**: Data encrypted at rest and in transit

## Troubleshooting

### Common Issues

1. **API Not Enabled**: Ensure all required APIs are enabled
   ```bash
   gcloud services enable container.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   ```

2. **Permission Denied**: Check IAM roles and service account permissions

3. **Image Pull Errors**: Verify Artifact Registry permissions and Docker authentication

4. **Cluster Not Ready**: Wait for Autopilot to provision nodes

### Useful Commands

```bash
# Check cluster status
gcloud container clusters describe co2-assistant-cluster --region us-central1

# View Terraform state
terraform show

# Check Kubernetes resources
kubectl get all -n co2-assistant
kubectl get all -n default

# View logs
kubectl logs -f deployment/co2-assistant -n co2-assistant
```

## Cleanup

To destroy the infrastructure:

```bash
# Destroy Terraform resources
terraform destroy

# Note: This will destroy the GKE cluster and all resources
# Make sure to backup any important data first
```

## Integration with Existing Infrastructure

This Terraform configuration is designed to integrate with existing infrastructure:

- **Backend Reuse**: Uses existing Terraform state bucket
- **Project Integration**: Works within existing GCP project
- **CI/CD Integration**: Compatible with existing deployment pipelines
- **Monitoring Integration**: Leverages existing monitoring setup

## Next Steps

After infrastructure deployment:

1. **Deploy Applications**: Use the deployment scripts
2. **Configure Monitoring**: Set up dashboards and alerts
3. **Test Integration**: Verify Online Boutique and CO2 Assistant communication
4. **Performance Tuning**: Optimize based on usage patterns
5. **Security Review**: Audit IAM roles and network policies

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review Terraform and Kubernetes logs
3. Consult Google Cloud documentation
4. Check the project's GitHub issues

## Contributing

To contribute to the Terraform configuration:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Remember to:
- Update documentation
- Add appropriate tests
- Follow Terraform best practices
- Maintain backward compatibility
