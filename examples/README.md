# 🚀 CO2-Aware Shopping Assistant Examples

This directory contains practical examples and scripts for interacting with the CO2-Aware Shopping Assistant using various tools and APIs.

## 📁 Directory Structure

```
examples/
├── README.md                           # This file
├── kubectl-ai/                         # kubectl-ai examples
│   ├── basic-workflows.sh              # Basic kubectl-ai workflows
│   ├── agent-management.sh             # AI agent management
│   ├── troubleshooting.sh              # Troubleshooting workflows
│   └── monitoring.sh                   # Monitoring and observability
├── gemini-cli/                         # Gemini CLI examples
│   ├── chat-interface.py               # Interactive chat interface
│   ├── product-search.py               # Intelligent product search
│   ├── co2-calculator.py               # CO2 impact calculator
│   ├── sustainability-advisor.py       # Personal sustainability advisor
│   └── batch-processing.py             # Batch processing examples
├── api-examples/                       # Direct API examples
│   ├── curl-examples.sh                # cURL examples
│   ├── python-api-client.py            # Python API client
│   ├── javascript-api-client.js        # JavaScript API client
│   └── postman-collection.json         # Postman collection
├── integration/                        # Integration examples
│   ├── ci-cd-integration.sh            # CI/CD pipeline integration
│   ├── monitoring-integration.py       # Monitoring integration
│   └── webhook-integration.py          # Webhook integration
└── advanced/                           # Advanced examples
    ├── custom-agents.py                # Custom agent creation
    ├── mcp-server-extension.py         # MCP server extension
    └── a2a-protocol-extension.py       # A2A protocol extension
```

## 🚀 Quick Start

### **1. kubectl-ai Examples**
```bash
# Navigate to kubectl-ai examples
cd examples/kubectl-ai

# Run basic workflows
chmod +x basic-workflows.sh
./basic-workflows.sh

# Manage AI agents
chmod +x agent-management.sh
./agent-management.sh
```

### **2. Gemini CLI Examples**
```bash
# Navigate to Gemini CLI examples
cd examples/gemini-cli

# Run interactive chat
python chat-interface.py

# Intelligent product search
python product-search.py

# CO2 impact calculator
python co2-calculator.py
```

### **3. API Examples**
```bash
# Navigate to API examples
cd examples/api-examples

# Run cURL examples
chmod +x curl-examples.sh
./curl-examples.sh

# Python API client
python python-api-client.py
```

## 📚 Example Categories

### **🤖 kubectl-ai Examples**
- **Basic Workflows**: Pod management, resource optimization, health checks
- **Agent Management**: AI agent status monitoring and communication
- **Troubleshooting**: Debug pod issues, network problems, performance issues
- **Monitoring**: System health analysis, metrics interpretation

### **🌟 Gemini CLI Examples**
- **Chat Interface**: Interactive conversation with the assistant
- **Product Search**: AI-enhanced product discovery and recommendations
- **CO2 Calculator**: Environmental impact analysis and calculations
- **Sustainability Advisor**: Personalized sustainability recommendations
- **Batch Processing**: Process multiple requests efficiently

### **🔌 API Examples**
- **cURL Examples**: Command-line API interactions
- **Python Client**: Python SDK for API integration
- **JavaScript Client**: Browser and Node.js integration
- **Postman Collection**: API testing and documentation

### **🔗 Integration Examples**
- **CI/CD Integration**: Automated testing and deployment
- **Monitoring Integration**: System health monitoring
- **Webhook Integration**: Real-time event processing

### **⚡ Advanced Examples**
- **Custom Agents**: Create specialized AI agents
- **MCP Server Extension**: Extend MCP functionality
- **A2A Protocol Extension**: Custom agent communication patterns

## 🛠️ Prerequisites

### **For kubectl-ai Examples**
```bash
# Install kubectl-ai
curl -L https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai-linux-amd64.tar.gz | tar xz
sudo mv kubectl-ai /usr/local/bin/kubectl-ai
chmod +x /usr/local/bin/kubectl-ai

# Configure API key
export OPENAI_API_KEY="your-openai-api-key"
```

### **For Gemini CLI Examples**
```bash
# Install Google Generative AI
pip install google-generativeai

# Configure API key
export GOOGLE_AI_API_KEY="your-gemini-api-key"
```

### **For API Examples**
```bash
# Install required packages
pip install requests httpx

# For JavaScript examples
npm install axios
```

## 🎯 Use Cases

### **1. Development & Testing**
- Test AI agent functionality
- Validate API endpoints
- Debug system issues
- Performance testing

### **2. Operations & Monitoring**
- System health monitoring
- Performance analysis
- Troubleshooting issues
- Capacity planning

### **3. Integration & Automation**
- CI/CD pipeline integration
- Automated testing
- Webhook processing
- Batch operations

### **4. User Experience**
- Interactive chat interfaces
- Product search and recommendations
- Environmental impact analysis
- Sustainability guidance

## 📖 Documentation

Each example includes:
- **README.md**: Detailed explanation and usage instructions
- **Code comments**: Inline documentation and explanations
- **Configuration**: Environment setup and configuration
- **Examples**: Sample inputs and expected outputs
- **Troubleshooting**: Common issues and solutions

## 🔧 Customization

All examples are designed to be:
- **Modular**: Easy to modify and extend
- **Configurable**: Environment-based configuration
- **Reusable**: Can be adapted for different use cases
- **Well-documented**: Clear instructions and examples

## 🤝 Contributing

To add new examples:
1. Create a new directory under the appropriate category
2. Add a README.md with documentation
3. Include sample code with comments
4. Add configuration examples
5. Update this main README.md

## 📞 Support

For questions or issues with examples:
- Check the individual example README files
- Review the main documentation in `/docs/`
- Open an issue on GitHub
- Join the community discussions

---

**Happy coding with the CO2-Aware Shopping Assistant! 🌱🤖**
