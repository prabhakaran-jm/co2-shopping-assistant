# 🌱 CO2-Aware Shopping Assistant

A revolutionary AI-powered shopping assistant that helps users make environmentally conscious purchasing decisions by providing real-time CO2 emission calculations and eco-friendly recommendations.

## 🎯 Hackathon Alignment

This project follows the GKE Turns 10 Hackathon guidelines by:
- **Enhancing Online Boutique** with agentic AI capabilities
- **Using Google Gemini AI** for intelligent decision-making
- **Implementing ADK, MCP, and A2A** protocols for agent orchestration
- **Deploying on GKE** with proper microservices architecture

> **Built for Google Kubernetes Engine (GKE) Turns 10 Hackathon** 🎉
> 
> This project demonstrates the power of AI agents, MCP (Model Context Protocol), and A2A (Agent-to-Agent) communication on Google Kubernetes Engine.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🏗️ Architecture

### Core Agents (Built with Google ADK)

1. **Product Discovery Agent** (`LlmAgent`)
   - Intelligent product search with environmental impact scoring
   - Context-aware recommendations based on user preferences
   - Real-time inventory checking

2. **CO2 Calculator Agent** (`LlmAgent`)
   - Real-time CO2 emission calculations for products
   - Shipping method optimization (eco vs speed vs cost)
   - Environmental impact scoring and recommendations

3. **Cart Management Agent** (`LlmAgent`)
   - Smart cart operations with CO2-aware suggestions
   - Cart total calculations including environmental impact
   - Session persistence and state management

4. **Checkout Agent** (`LlmAgent`)
   - Order processing with eco-friendly shipping selection
   - Payment coordination and confirmation
   - Transaction validation

5. **Host Agent** (`LlmAgent` - Router)
   - Central orchestration using A2A protocol
   - Natural language query processing
   - Intelligent task delegation

### MCP Servers

1. **Boutique MCP Server**
   - Product catalog integration
   - Cart and checkout operations
   - Order management

2. **CO2 Data MCP Server**
   - Environmental impact calculations
   - Shipping method data
   - Sustainability metrics

### Communication Protocols

- **A2A Protocol**: Inter-agent communication for task delegation
- **MCP Protocol**: Standardized tool integration with external APIs
- **HTTP/gRPC**: Communication with Online Boutique microservices

## 🚀 Quick Start

### 🔒 **IMPORTANT: Security Setup First**

Before deploying, you **MUST** configure sensitive information:

```bash
# 1. Clone the repository
git clone https://github.com/prabhakaran-jm/co2-shopping-assistant.git
cd co2-shopping-assistant

# 2. Configure Terraform variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars with your actual values

# 3. Configure Terraform backend
cp terraform/backend.hcl.example terraform/backend.hcl
# Edit terraform/backend.hcl with your actual bucket name

# 4. Set environment variables (OPTIONAL - scripts can read from .env file)
# Option A: Create .env file
echo "GOOGLE_PROJECT_ID=your-gcp-project-id" > .env
echo "GOOGLE_AI_API_KEY=your-gemini-api-key" >> .env

# Option B: Export environment variables
export GOOGLE_AI_API_KEY="your-gemini-api-key"
export GOOGLE_PROJECT_ID="your-gcp-project-id"
```

> ⚠️ **Security Note**: Never commit `terraform.tfvars` or files with real project IDs to version control! See [SECURITY.md](SECURITY.md) for detailed security guidelines.

### Prerequisites
- Python 3.11+
- Google Cloud Project with GKE cluster
- Google AI API key for Gemini integration
- kubectl configured for your cluster

### Installation

```bash
# Clone the repository (if not done above)
git clone https://github.com/prabhakaran-jm/co2-shopping-assistant.git
cd co2-shopping-assistant

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the development server
python -m src.main
```

### Deployment to GKE

```bash
# Option 1: Using .env file (recommended)
./scripts/deploy-infra.sh

# Option 2: Using command line parameters
./scripts/deploy-infra.sh \
  --project-id YOUR_PROJECT_ID \
  --gemini-api-key YOUR_API_KEY

# Option 3: Using environment variables
export GOOGLE_PROJECT_ID="your-project-id"
export GOOGLE_AI_API_KEY="your-api-key"
./scripts/deploy-infra.sh
```

## 📊 Key Features

### Environmental Intelligence
- Real-time CO2 emission calculations
- Eco-friendly product recommendations
- Sustainable shipping options
- Environmental impact scoring

### AI-Powered Shopping
- Natural language product search
- Context-aware recommendations
- Intelligent cart management
- Automated checkout optimization

### System Reliability
- SLO-aware adaptive behavior
- Graceful degradation during high load
- Automatic recovery mechanisms
- Comprehensive monitoring

## 🛠️ Technology Stack

- **AI Framework**: Google Agent Development Kit (ADK)
- **LLM**: Google Gemini 2.0 Flash
- **Communication**: A2A Protocol, MCP Protocol
- **Backend**: Python FastAPI
- **Frontend**: React with TypeScript
- **Infrastructure**: Terraform (Infrastructure as Code)
- **Deployment**: Google Kubernetes Engine (GKE) Autopilot
- **Base Application**: Online Boutique (Google's microservices demo)

## 📁 Project Structure

```
co2-shopping-assistant/
├── src/
│   ├── agents/           # AI agents built with ADK
│   ├── mcp_servers/      # MCP servers for external APIs
│   ├── a2a/              # A2A protocol implementation
│   ├── ui/               # React frontend
│   └── main.py           # Application entry point
├── terraform/            # Infrastructure as Code
│   ├── main.tf           # Main Terraform configuration
│   ├── variables.tf      # Variable definitions
│   ├── outputs.tf        # Output definitions
│   └── backend.tf        # Backend configuration
├── k8s/                  # Kubernetes manifests
├── scripts/              # Deployment script
├── docs/                 # Documentation
└── tests/                # Test suites
```

## 🎯 Success Metrics

- **Environmental Impact**: Reduce average CO2 emissions per order by 25%
- **User Experience**: Sub-2 second response times for AI queries
- **System Reliability**: 99.9% uptime with SLO monitoring
- **Innovation**: Novel integration of environmental data with AI agents


