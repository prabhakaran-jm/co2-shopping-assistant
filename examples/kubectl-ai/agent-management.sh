#!/bin/bash

# 🤖 kubectl-ai Agent Management Workflows for CO2-Aware Shopping Assistant
# This script demonstrates AI agent management workflows using kubectl-ai

set -e

echo "🤖 kubectl-ai Agent Management Workflows"
echo "========================================"

# Check if kubectl-ai is installed
if ! command -v kubectl-ai &> /dev/null; then
    echo "❌ kubectl-ai is not installed. Please install it first:"
    echo "   curl -L https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai-linux-amd64.tar.gz | tar xz"
    echo "   sudo mv kubectl-ai /usr/local/bin/kubectl-ai"
    echo "   chmod +x /usr/local/bin/kubectl-ai"
    exit 1
fi

# Check if API key is configured
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY is not set. Please set it:"
    echo "   export OPENAI_API_KEY='your-openai-api-key'"
    exit 1
fi

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

# 1. Agent Discovery and Status
echo "🔍 1. Agent Discovery and Status"
echo "==============================="

run_kubectl_ai "Show me all AI agents in the CO2-Aware Shopping Assistant and their current status" "Discover all AI agents"

run_kubectl_ai "Explain the role and responsibilities of each AI agent in the system" "Explain agent roles"

run_kubectl_ai "Check the health status of all AI agents and identify any issues" "Check agent health"

# 2. Host Agent Management
echo "🎯 2. Host Agent Management"
echo "=========================="

run_kubectl_ai "Analyze the Host Agent's performance and routing capabilities" "Analyze Host Agent"

run_kubectl_ai "Check if the Host Agent is properly orchestrating other agents" "Check agent orchestration"

run_kubectl_ai "Verify that the Host Agent is handling user requests correctly" "Verify request handling"

# 3. Product Discovery Agent
echo "🔍 3. Product Discovery Agent"
echo "============================="

run_kubectl_ai "Check the Product Discovery Agent's search capabilities and performance" "Check Product Discovery Agent"

run_kubectl_ai "Verify that the Product Discovery Agent is finding eco-friendly products" "Verify eco-friendly search"

run_kubectl_ai "Analyze the Product Discovery Agent's environmental impact scoring" "Analyze environmental scoring"

# 4. CO2 Calculator Agent
echo "🌍 4. CO2 Calculator Agent"
echo "=========================="

run_kubectl_ai "Check the CO2 Calculator Agent's calculation accuracy and performance" "Check CO2 Calculator Agent"

run_kubectl_ai "Verify that the CO2 Calculator Agent is providing accurate environmental impact data" "Verify CO2 calculations"

run_kubectl_ai "Analyze the CO2 Calculator Agent's lifecycle analysis capabilities" "Analyze lifecycle analysis"

# 5. Cart Management Agent
echo "🛒 5. Cart Management Agent"
echo "=========================="

run_kubectl_ai "Check the Cart Management Agent's cart operations and CO2 awareness" "Check Cart Management Agent"

run_kubectl_ai "Verify that the Cart Management Agent is calculating cart CO2 impact correctly" "Verify cart CO2 calculations"

run_kubectl_ai "Analyze the Cart Management Agent's eco-friendly suggestions" "Analyze eco-friendly suggestions"

# 6. Checkout Agent
echo "💳 6. Checkout Agent"
echo "===================="

run_kubectl_ai "Check the Checkout Agent's order processing and eco-friendly shipping" "Check Checkout Agent"

run_kubectl_ai "Verify that the Checkout Agent is offering sustainable shipping options" "Verify sustainable shipping"

run_kubectl_ai "Analyze the Checkout Agent's payment processing and confirmation" "Analyze payment processing"

# 7. Comparison Agent
echo "⚖️ 7. Comparison Agent"
echo "====================="

run_kubectl_ai "Check the Comparison Agent's product comparison capabilities" "Check Comparison Agent"

run_kubectl_ai "Verify that the Comparison Agent is providing accurate environmental comparisons" "Verify environmental comparisons"

run_kubectl_ai "Analyze the Comparison Agent's ranking algorithms" "Analyze ranking algorithms"

# 8. ADK Eco Agent
echo "🌟 8. ADK Eco Agent"
echo "==================="

run_kubectl_ai "Check the ADK Eco Agent's Google ADK integration and performance" "Check ADK Eco Agent"

run_kubectl_ai "Verify that the ADK Eco Agent is using Gemini 2.0 Flash correctly" "Verify Gemini integration"

run_kubectl_ai "Analyze the ADK Eco Agent's eco recommendation tool" "Analyze eco recommendation tool"

# 9. A2A Protocol Communication
echo "🔗 9. A2A Protocol Communication"
echo "==============================="

run_kubectl_ai "Check the A2A protocol communication between all agents" "Check A2A communication"

run_kubectl_ai "Verify that agents are properly discovering and registering with each other" "Verify agent discovery"

run_kubectl_ai "Analyze the A2A protocol message flow and routing" "Analyze message flow"

# 10. Agent Performance Optimization
echo "⚡ 10. Agent Performance Optimization"
echo "===================================="

run_kubectl_ai "Analyze the performance of all AI agents and identify optimization opportunities" "Analyze agent performance"

run_kubectl_ai "Check if any agents are experiencing bottlenecks or slow responses" "Check for bottlenecks"

run_kubectl_ai "Suggest ways to improve agent communication and coordination" "Suggest improvements"

# 11. Agent Error Handling
echo "🛠️ 11. Agent Error Handling"
echo "==========================="

run_kubectl_ai "Check if agents are handling errors gracefully and providing fallbacks" "Check error handling"

run_kubectl_ai "Verify that agents are logging errors appropriately for debugging" "Verify error logging"

run_kubectl_ai "Analyze agent recovery mechanisms and resilience" "Analyze recovery mechanisms"

# 12. Agent Scaling and Load Management
echo "📈 12. Agent Scaling and Load Management"
echo "======================================="

run_kubectl_ai "Check if agents are scaling properly under load" "Check agent scaling"

run_kubectl_ai "Verify that agents are distributing load evenly" "Verify load distribution"

run_kubectl_ai "Analyze agent resource usage and suggest scaling optimizations" "Analyze resource usage"

# 13. Agent Security
echo "🔒 13. Agent Security"
echo "===================="

run_kubectl_ai "Check the security posture of all AI agents" "Check agent security"

run_kubectl_ai "Verify that agents are properly authenticated and authorized" "Verify authentication"

run_kubectl_ai "Analyze agent communication security and data protection" "Analyze communication security"

# 14. Agent Monitoring and Observability
echo "📊 14. Agent Monitoring and Observability"
echo "========================================"

run_kubectl_ai "Check if agents are properly instrumented for monitoring" "Check agent instrumentation"

run_kubectl_ai "Verify that agent metrics are being collected and exposed" "Verify metrics collection"

run_kubectl_ai "Analyze agent observability and debugging capabilities" "Analyze observability"

# 15. Agent Integration Testing
echo "🧪 15. Agent Integration Testing"
echo "==============================="

run_kubectl_ai "Test the integration between all AI agents" "Test agent integration"

run_kubectl_ai "Verify that agents can handle complex multi-agent workflows" "Verify multi-agent workflows"

run_kubectl_ai "Analyze agent integration test results and identify issues" "Analyze integration tests"

echo "🎉 Agent management workflows completed!"
echo ""
echo "📚 Next steps:"
echo "   - Run troubleshooting.sh for advanced troubleshooting"
echo "   - Run monitoring.sh for monitoring and observability"
echo "   - Check individual agent logs for detailed analysis"
echo ""
echo "🔗 Useful resources:"
echo "   - Documentation: docs/kubectl-ai-workflows.md"
echo "   - Live demo: https://assistant.cloudcarta.com/"
echo "   - Repository: https://github.com/prabhakaran-jm/co2-shopping-assistant"
echo ""
echo "🤖 Agent-specific commands:"
echo "   - Check agent status: kubectl get pods -n co2-assistant | grep agent"
echo "   - View agent logs: kubectl logs -f deployment/co2-assistant -n co2-assistant"
echo "   - Test agent communication: curl http://assistant.cloudcarta.com/api/a2a/status"
