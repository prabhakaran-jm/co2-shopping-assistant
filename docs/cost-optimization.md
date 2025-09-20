# Resource Optimization and Cost Management

## Overview
This document outlines the resource optimization strategies implemented in the CO2-Aware Shopping Assistant to ensure cost-effective deployment on Google Kubernetes Engine (GKE). By carefully configuring resource requests, limits, and autoscaling, we have achieved significant cost savings while maintaining high performance and reliability.

## Resource Configuration

### CPU and Memory Limits
- **CPU Request**: 100m
- **CPU Limit**: 300m
- **Memory Request**: 256Mi
- **Memory Limit**: 512Mi

### Rationale
These values were chosen based on performance testing and resource utilization analysis. The requests are set to a level that ensures the application has enough resources to start and operate under normal load, while the limits prevent the application from consuming excessive resources and impacting other workloads.

## Horizontal Pod Autoscaling (HPA)

### Configuration
- **Min Replicas**: 1
- **Max Replicas**: 1 (cost control measure)
- **Target CPU Utilization**: 80%
- **Target Memory Utilization**: 80%

### Cost Benefits
By setting `maxReplicas: 1`, we are intentionally limiting the application to a single pod to control costs for the hackathon. This ensures that the application does not scale up and incur additional costs, even if there is a spike in traffic. For a production deployment, this value would be increased to handle higher loads.

## Cost Optimization Techniques

### GKE Autopilot Benefits
The application is designed to be deployed on GKE Autopilot, which provides automatic resource optimization and cost savings. Autopilot automatically adjusts the resources allocated to the application based on its needs, so you only pay for what you use.

### Efficient Scaling
The HPA configuration, combined with the resource requests and limits, ensures that the application scales efficiently. The application will only scale up when there is a sustained increase in traffic, and it will scale down when the traffic decreases, further reducing costs.

## Monitoring and Alerting

### Resource Metrics
The following Prometheus metrics can be used to monitor resource usage:
- `container_cpu_usage_seconds_total`
- `container_memory_working_set_bytes`
- `kube_pod_container_resource_requests`
- `kube_pod_container_resource_limits`

### Cost Alerts
Cost alerts can be configured in Google Cloud Billing to notify you when your costs exceed a certain threshold. This can be combined with the resource metrics in Prometheus to create more advanced alerting rules.

## Performance Benchmarks

### Resource Utilization Targets
- **CPU**: Maintain average CPU utilization below 80%.
- **Memory**: Maintain average memory utilization below 80%.

### Cost Savings
By implementing these resource optimization techniques, we estimate a cost saving of **up to 50%** compared to a non-optimized deployment. This is achieved by preventing over-provisioning of resources and ensuring that the application only uses what it needs.

## Best Practices

### Further Optimization
- **Right-sizing**: Continuously monitor resource usage and adjust requests and limits as needed.
- **Autoscaling**: For production deployments, increase `maxReplicas` to allow the application to scale to meet demand.
- **Spot VMs**: For non-critical workloads, consider using Spot VMs to further reduce costs.

### Cost Monitoring
- **Google Cloud Billing Reports**: Use the built-in billing reports to track your GKE costs.
- **Prometheus and Grafana**: Create dashboards in Grafana to visualize your resource usage and costs over time.
