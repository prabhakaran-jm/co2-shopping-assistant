# 🤖 kubectl-ai Workflows for CO2-Aware Shopping Assistant

This guide demonstrates how to use kubectl-ai to interact with the CO2-Aware Shopping Assistant deployment, manage AI agents, and perform intelligent Kubernetes operations.

## 📋 Prerequisites

### **Install kubectl-ai**
```bash
# Install kubectl-ai plugin
curl -L https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai-linux-amd64.tar.gz | tar xz
sudo mv kubectl-ai /usr/local/bin/kubectl-ai
chmod +x /usr/local/bin/kubectl-ai

# Verify installation
kubectl ai --version
```

### **Configure AI Provider**
```bash
# Set Google AI API key (kubectl-ai uses Gemini by default)
export GOOGLE_AI_API_KEY="your-gemini-api-key"

# kubectl-ai expects GEMINI_API_KEY, so we set it from GOOGLE_AI_API_KEY
export GEMINI_API_KEY="$GOOGLE_AI_API_KEY"

# kubectl-ai uses Gemini as the default provider
# No additional configuration needed!
```

## 🚀 Basic kubectl-ai Workflows

### **1. Intelligent Pod Management**

#### **Find and Troubleshoot Pod Issues**
```bash
# Ask kubectl-ai to analyze pod issues
kubectl ai "Find all pods in co2-assistant namespace that are not running and explain why"

# Expected output:
# kubectl-ai will analyze pod status and provide intelligent explanations
```

#### **Resource Optimization Suggestions**
```bash
# Get AI-powered resource optimization recommendations
kubectl ai "Analyze resource usage in co2-assistant namespace and suggest optimizations"

# Expected output:
# kubectl-ai will analyze CPU/memory usage and suggest resource adjustments
```

#### **Health Check Analysis**
```bash
# Analyze health check failures
kubectl ai "Check health status of all services in co2-assistant namespace and identify any issues"

# Expected output:
# kubectl-ai will check readiness/liveness probes and identify problems
```

### **2. AI Agent Management**

#### **Monitor AI Agent Status**
```bash
# Check status of all AI agents
kubectl ai "Show me the status of all AI agents in the co2-assistant deployment and explain what each agent does"

# Expected output:
# kubectl-ai will list agents and explain their roles:
# - Host Agent: Central orchestrator
# - Product Discovery Agent: Eco-friendly product search
# - CO2 Calculator Agent: Environmental impact calculations
# - Cart Management Agent: CO2-aware cart operations
# - Checkout Agent: Sustainable shipping and payment
# - Comparison Agent: Product comparison with environmental metrics
```

#### **Agent Communication Analysis**
```bash
# Analyze A2A protocol communication
kubectl ai "Check the A2A protocol status and show me which agents are communicating with each other"

# Expected output:
# kubectl-ai will analyze A2A protocol logs and show agent interactions
```

#### **MCP Transport Monitoring**
```bash
# Monitor MCP transport layer
kubectl ai "Show me the MCP transport status and list all available tools and resources"

# Expected output:
# kubectl-ai will show MCP server status and available tools
```

### **3. Performance Analysis**

#### **Response Time Analysis**
```bash
# Analyze AI response times
kubectl ai "Analyze the response times of AI queries in the co2-assistant and identify any performance bottlenecks"

# Expected output:
# kubectl-ai will analyze metrics and identify performance issues
```

#### **Cost Optimization Analysis**
```bash
# Get cost optimization recommendations
kubectl ai "Analyze the current resource usage and suggest ways to reduce costs while maintaining performance"

# Expected output:
# kubectl-ai will provide specific cost optimization recommendations
```

## 🔧 Advanced kubectl-ai Workflows

### **1. Intelligent Troubleshooting**

#### **Debug AI Agent Issues**
```bash
# Debug specific agent problems
kubectl ai "The Product Discovery Agent is not responding properly. Help me debug this issue by checking logs, metrics, and configuration"

# Expected output:
# kubectl-ai will:
# 1. Check agent logs for errors
# 2. Analyze metrics for performance issues
# 3. Verify configuration settings
# 4. Suggest fixes
```

#### **Network Policy Analysis**
```bash
# Analyze network connectivity issues
kubectl ai "Check network policies in co2-assistant namespace and identify any connectivity issues between agents"

# Expected output:
# kubectl-ai will analyze network policies and identify connectivity problems
```

#### **Certificate and TLS Issues**
```bash
# Debug SSL/TLS problems
kubectl ai "Check SSL certificate status for the co2-assistant ingress and identify any certificate issues"

# Expected output:
# kubectl-ai will check certificate status and identify issues
```

### **2. Intelligent Scaling**

#### **Auto-scaling Analysis**
```bash
# Analyze HPA behavior
kubectl ai "Analyze the Horizontal Pod Autoscaler behavior for co2-assistant and suggest optimal scaling parameters"

# Expected output:
# kubectl-ai will analyze HPA metrics and suggest optimal scaling parameters
```

#### **Load Testing Recommendations**
```bash
# Get load testing suggestions
kubectl ai "Suggest a load testing strategy for the CO2-Aware Shopping Assistant to validate performance under high load"

# Expected output:
# kubectl-ai will suggest comprehensive load testing strategies
```

### **3. Security Analysis**

#### **Security Policy Review**
```bash
# Review security policies
kubectl ai "Review all security policies in co2-assistant namespace and identify any security gaps or misconfigurations"

# Expected output:
# kubectl-ai will analyze security policies and identify issues
```

#### **Secret Management Analysis**
```bash
# Analyze secret management
kubectl ai "Check secret management in co2-assistant namespace and ensure all sensitive data is properly secured"

# Expected output:
# kubectl-ai will analyze secret management and security
```

## 🎯 CO2-Aware Shopping Assistant Specific Workflows

### **1. Environmental Impact Monitoring**

#### **CO2 Calculation Analysis**
```bash
# Monitor CO2 calculation performance
kubectl ai "Analyze the performance of CO2 calculations in the CO2 Calculator Agent and identify any issues"

# Expected output:
# kubectl-ai will analyze CO2 calculation metrics and performance
```

#### **Sustainability Metrics**
```bash
# Check sustainability metrics
kubectl ai "Show me the current sustainability metrics and environmental impact data from the CO2-Aware Shopping Assistant"

# Expected output:
# kubectl-ai will display current sustainability metrics
```

### **2. AI Agent Orchestration**

#### **Agent Workflow Analysis**
```bash
# Analyze agent workflows
kubectl ai "Show me how the AI agents are working together to process a user request for eco-friendly products"

# Expected output:
# kubectl-ai will trace the agent workflow and show the process
```

#### **A2A Protocol Monitoring**
```bash
# Monitor A2A communication
kubectl ai "Monitor the A2A protocol communication between agents and show me the message flow"

# Expected output:
# kubectl-ai will show A2A message flow between agents
```

### **3. MCP Transport Analysis**

#### **Tool Discovery Analysis**
```bash
# Analyze MCP tool discovery
kubectl ai "Show me all available MCP tools and resources in the CO2-Aware Shopping Assistant"

# Expected output:
# kubectl-ai will list all MCP tools and resources
```

#### **MCP Performance Analysis**
```bash
# Analyze MCP performance
kubectl ai "Analyze the performance of MCP transport layer and identify any bottlenecks"

# Expected output:
# kubectl-ai will analyze MCP performance metrics
```

## 🔍 Troubleshooting Workflows

### **1. Common Issues**

#### **Pod Startup Issues**
```bash
# Debug pod startup problems
kubectl ai "The co2-assistant pods are failing to start. Help me identify the root cause and fix it"

# Expected output:
# kubectl-ai will analyze startup logs and identify issues
```

#### **Service Connectivity Issues**
```bash
# Debug service connectivity
kubectl ai "The co2-assistant service is not accessible. Help me debug the connectivity issue"

# Expected output:
# kubectl-ai will analyze service configuration and connectivity
```

#### **AI Agent Communication Issues**
```bash
# Debug agent communication
kubectl ai "The AI agents are not communicating properly via A2A protocol. Help me debug this issue"

# Expected output:
# kubectl-ai will analyze A2A protocol logs and identify issues
```

### **2. Performance Issues**

#### **Slow Response Times**
```bash
# Debug slow responses
kubectl ai "The AI responses are slow. Help me identify the bottleneck and optimize performance"

# Expected output:
# kubectl-ai will analyze performance metrics and suggest optimizations
```

#### **High Resource Usage**
```bash
# Debug high resource usage
kubectl ai "The co2-assistant is using too many resources. Help me optimize resource usage"

# Expected output:
# kubectl-ai will analyze resource usage and suggest optimizations
```

## 📊 Monitoring and Observability

### **1. Metrics Analysis**

#### **Custom Metrics Analysis**
```bash
# Analyze custom business metrics
kubectl ai "Show me the custom metrics for CO2 calculations and environmental impact"

# Expected output:
# kubectl-ai will display custom business metrics
```

#### **SLO Monitoring**
```bash
# Monitor SLO compliance
kubectl ai "Check if the CO2-Aware Shopping Assistant is meeting its SLOs for response time and availability"

# Expected output:
# kubectl-ai will analyze SLO compliance
```

### **2. Log Analysis**

#### **AI Agent Logs**
```bash
# Analyze AI agent logs
kubectl ai "Analyze the logs from all AI agents and identify any errors or performance issues"

# Expected output:
# kubectl-ai will analyze agent logs and identify issues
```

#### **Application Logs**
```bash
# Analyze application logs
kubectl ai "Analyze the application logs for the CO2-Aware Shopping Assistant and identify any issues"

# Expected output:
# kubectl-ai will analyze application logs and identify issues
```

## 🚀 Best Practices

### **1. Effective kubectl-ai Usage**

#### **Specific Queries**
```bash
# Good: Specific and actionable
kubectl ai "Check the health status of the CO2 Calculator Agent and suggest fixes if there are issues"

# Bad: Too vague
kubectl ai "Check everything"
```

#### **Context-Rich Queries**
```bash
# Good: Include context
kubectl ai "The Product Discovery Agent is not finding eco-friendly products. Check its configuration and suggest fixes"

# Bad: Missing context
kubectl ai "Fix the agent"
```

### **2. Security Considerations**

#### **Sensitive Data**
```bash
# Avoid exposing sensitive data in queries
# Good: Use generic descriptions
kubectl ai "Check if API keys are properly configured"

# Bad: Include actual API keys
kubectl ai "Check if API key abc123 is working"
```

### **3. Performance Optimization**

#### **Efficient Queries**
```bash
# Use specific namespaces and resources
kubectl ai "Check pod status in co2-assistant namespace"

# Rather than checking all namespaces
kubectl ai "Check all pods everywhere"
```

## 📚 Example Scenarios

### **Scenario 1: New User Onboarding**
```bash
# Help a new user understand the system
kubectl ai "I'm new to the CO2-Aware Shopping Assistant. Show me the architecture and explain how the AI agents work together"

# Expected output:
# kubectl-ai will provide a comprehensive overview of the system
```

### **Scenario 2: Performance Optimization**
```bash
# Optimize system performance
kubectl ai "The system is running slow. Analyze the performance and suggest optimizations for better response times"

# Expected output:
# kubectl-ai will analyze performance and suggest optimizations
```

### **Scenario 3: Security Audit**
```bash
# Perform security audit
kubectl ai "Perform a security audit of the CO2-Aware Shopping Assistant and identify any security issues"

# Expected output:
# kubectl-ai will perform a comprehensive security audit
```

### **Scenario 4: Disaster Recovery**
```bash
# Plan disaster recovery
kubectl ai "Help me create a disaster recovery plan for the CO2-Aware Shopping Assistant"

# Expected output:
# kubectl-ai will suggest a comprehensive disaster recovery plan
```

## 🔧 Integration with CI/CD

### **Automated kubectl-ai Checks**
```bash
# Add to CI/CD pipeline
kubectl ai "Check if the CO2-Aware Shopping Assistant deployment is healthy and all AI agents are functioning properly"

# Use in deployment validation
kubectl ai "Validate that the new deployment of CO2-Aware Shopping Assistant is working correctly"
```

## 📈 Advanced Use Cases

### **1. Predictive Analysis**
```bash
# Predict resource needs
kubectl ai "Based on current usage patterns, predict the resource needs for the CO2-Aware Shopping Assistant in the next month"

# Expected output:
# kubectl-ai will analyze usage patterns and predict resource needs
```

### **2. Capacity Planning**
```bash
# Plan capacity
kubectl ai "Help me plan the capacity for the CO2-Aware Shopping Assistant to handle 10x current load"

# Expected output:
# kubectl-ai will suggest capacity planning strategies
```

### **3. Cost Optimization**
```bash
# Optimize costs
kubectl ai "Analyze the current costs of the CO2-Aware Shopping Assistant and suggest ways to reduce costs by 30%"

# Expected output:
# kubectl-ai will analyze costs and suggest optimization strategies
```

This comprehensive guide demonstrates how kubectl-ai can be used to intelligently manage and troubleshoot the CO2-Aware Shopping Assistant deployment, providing AI-powered insights into system behavior, performance, and optimization opportunities.
