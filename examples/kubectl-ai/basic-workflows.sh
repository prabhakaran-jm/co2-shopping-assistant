#!/bin/bash

# 🤖 kubectl-ai Basic Workflows for CO2-Aware Shopping Assistant
# This script demonstrates basic kubectl-ai workflows for managing the deployment

set -e

echo "🤖 kubectl-ai Basic Workflows for CO2-Aware Shopping Assistant"
echo "=============================================================="

# Check if kubectl-ai is installed
if ! command -v kubectl-ai &> /dev/null; then
    echo "❌ kubectl-ai is not installed. Please install it first:"
    echo "   curl -L https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai-linux-amd64.tar.gz | tar xz"
    echo "   sudo mv kubectl-ai /usr/local/bin/kubectl-ai"
    echo "   chmod +x /usr/local/bin/kubectl-ai"
    exit 1
fi

# Check if API key is configured
if [ -z "$GOOGLE_AI_API_KEY" ]; then
    echo "❌ GOOGLE_AI_API_KEY is not set. Please set it:"
    echo "   export GOOGLE_AI_API_KEY='your-gemini-api-key'"
    exit 1
fi

# Set GEMINI_API_KEY for kubectl-ai (it expects this variable name)
export GEMINI_API_KEY="$GOOGLE_AI_API_KEY"

echo "✅ kubectl-ai is installed and configured"
echo ""

# Function to run kubectl-ai command with error handling
run_kubectl_ai() {
    local query="$1"
    local description="$2"
    
    echo "🔍 $description"
    echo "Query: $query"
    echo "---"
    
    if kubectl-ai "$query"; then
        echo "✅ Command completed successfully"
    else
        echo "❌ Command failed"
    fi
    
    echo ""
    echo "Press Enter to continue..."
    read -r
    echo ""
}

# 1. Basic Pod Management
echo "📦 1. Basic Pod Management"
echo "=========================="

run_kubectl_ai "Show me all pods in co2-assistant namespace and their status" "List all pods in co2-assistant namespace"

run_kubectl_ai "Find any pods in co2-assistant namespace that are not running and explain why" "Identify problematic pods"

run_kubectl_ai "Check the resource usage of co2-assistant pods and suggest optimizations" "Analyze resource usage"

# 2. Service Health Checks
echo "🏥 2. Service Health Checks"
echo "============================"

run_kubectl_ai "Check the health status of all services in co2-assistant namespace" "Check service health"

run_kubectl_ai "Verify that the co2-assistant service is accessible and responding" "Verify service accessibility"

run_kubectl_ai "Check if the ingress is properly configured and routing traffic" "Check ingress configuration"

# 3. AI Agent Status
echo "🤖 3. AI Agent Status"
echo "===================="

run_kubectl_ai "Show me the status of all AI agents in the co2-assistant deployment" "Check AI agent status"

run_kubectl_ai "Explain what each AI agent does in the CO2-Aware Shopping Assistant" "Explain AI agent roles"

run_kubectl_ai "Check if the A2A protocol is working properly between agents" "Verify A2A protocol"

# 4. MCP Transport Status
echo "🔗 4. MCP Transport Status"
echo "========================="

run_kubectl_ai "Check the MCP transport status and list available tools" "Check MCP transport"

run_kubectl_ai "Verify that MCP servers are responding correctly" "Verify MCP servers"

run_kubectl_ai "Show me the available MCP tools and resources" "List MCP tools"

# 5. Performance Analysis
echo "📊 5. Performance Analysis"
echo "========================="

run_kubectl_ai "Analyze the performance metrics of the co2-assistant deployment" "Analyze performance"

run_kubectl_ai "Check if the Horizontal Pod Autoscaler is working correctly" "Check HPA status"

run_kubectl_ai "Identify any performance bottlenecks in the system" "Identify bottlenecks"

# 6. Security Check
echo "🔒 6. Security Check"
echo "==================="

run_kubectl_ai "Check the security policies in co2-assistant namespace" "Check security policies"

run_kubectl_ai "Verify that secrets are properly configured and secured" "Verify secrets"

run_kubectl_ai "Check network policies and ensure proper isolation" "Check network policies"

# 7. Troubleshooting Common Issues
echo "🔧 7. Troubleshooting Common Issues"
echo "==================================="

run_kubectl_ai "The co2-assistant pods are not starting. Help me debug this issue" "Debug pod startup issues"

run_kubectl_ai "The AI agents are not responding. Help me troubleshoot this problem" "Debug agent issues"

run_kubectl_ai "The MCP transport is not working. Help me identify and fix the issue" "Debug MCP issues"

# 8. Cost Optimization
echo "💰 8. Cost Optimization"
echo "======================="

run_kubectl_ai "Analyze the current resource usage and suggest cost optimizations" "Analyze resource usage"

run_kubectl_ai "Check if there are any unused resources that can be removed" "Check for unused resources"

run_kubectl_ai "Suggest ways to reduce costs while maintaining performance" "Suggest cost reductions"

# 9. Monitoring Setup
echo "📈 9. Monitoring Setup"
echo "====================="

run_kubectl_ai "Check if monitoring is properly configured for the co2-assistant" "Check monitoring setup"

run_kubectl_ai "Verify that Prometheus metrics are being collected" "Verify metrics collection"

run_kubectl_ai "Check if alerting is configured for critical issues" "Check alerting setup"

# 10. Deployment Validation
echo "✅ 10. Deployment Validation"
echo "============================"

run_kubectl_ai "Validate that the CO2-Aware Shopping Assistant deployment is working correctly" "Validate deployment"

run_kubectl_ai "Check if all components are properly integrated and communicating" "Check integration"

run_kubectl_ai "Verify that the system meets all requirements and is production-ready" "Verify production readiness"

echo "🎉 Basic workflows completed!"
echo ""
echo "📚 Next steps:"
echo "   - Run agent-management.sh for AI agent specific workflows"
echo "   - Run troubleshooting.sh for advanced troubleshooting"
echo "   - Run monitoring.sh for monitoring and observability"
echo ""
echo "🔗 Useful resources:"
echo "   - Documentation: docs/kubectl-ai-workflows.md"
echo "   - Live demo: https://assistant.cloudcarta.com/"
echo "   - Repository: https://github.com/prabhakaran-jm/co2-shopping-assistant"
