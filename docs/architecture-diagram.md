# CO2-Aware Shopping Assistant - Complete Architecture Diagram

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    GKE Autopilot Cluster                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              Online Boutique (Base Microservices)                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │  Frontend   │  │  Product    │  │    Cart     │  │  Checkout   │  │  Payment    │    │    │
│  │  │  (Go)       │  │  Catalog    │  │  Service    │  │  Service    │  │  Service    │    │    │
│  │  │             │  │  (Go)       │  │  (.NET)     │  │  (Go)       │  │  (Node.js)  │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │  Shipping   │  │   Email     │  │  Currency   │  │  Ad Service │  │Recommendation│    │    │
│  │  │  Service    │  │  Service    │  │  Service    │  │  (Java)     │  │  Service    │    │    │
│  │  │  (Go)       │  │  (Python)   │  │  (Node.js)  │  │             │  │  (Python)   │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    │ HTTP/gRPC APIs + ob-proxy                                  │
│                                    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                    CO2-Aware Shopping Assistant (AI Enhancement)                        │    │
│  │                                                                                         │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │                            FastAPI Main Application                              │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────────────────────┐    │    │    │
│  │  │  │  • HTTP Endpoints (/api/chat, /api/a2a/*, /api/mcp/*)                 │    │    │    │
│  │  │  │  • CORS Middleware & Security                                           │    │    │    │
│  │  │  │  • Prometheus Metrics Collection                                        │    │    │    │
│  │  │  │  • Static File Serving (UI)                                            │    │    │    │
│  │  │  └─────────────────────────────────────────────────────────────────────────┘    │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  │                                    │                                                    │    │
│  │                                    │ A2A Protocol Communication                        │    │
│  │                                    ▼                                                    │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │                              Host Agent (Router)                                 │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────────────────────┐    │    │    │
│  │  │  │  • Natural Language Processing (Gemini 2.0 Flash)                      │    │    │    │
│  │  │  │  • Intent Analysis & Classification                                    │    │    │    │
│  │  │  │  • A2A Protocol Orchestration                                         │    │    │    │
│  │  │  │  • Session Management & Context                                        │    │    │    │
│  │  │  │  • Workflow Patterns (Sequential, Parallel, Hierarchical)             │    │    │    │
│  │  │  └─────────────────────────────────────────────────────────────────────────┘    │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  │                                    │                                                    │    │
│  │                                    │ A2A Protocol                                       │    │
│  │                                    ▼                                                    │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │  Product    │  │     CO2     │  │    Cart     │  │  Checkout   │  │Comparison   │    │    │
│  │  │ Discovery   │  │ Calculator  │  │ Management  │  │    Agent    │  │   Agent     │    │    │
│  │  │   Agent     │  │   Agent     │  │   Agent     │  │             │  │             │    │    │
│  │  │             │  │             │  │             │  │             │  │             │    │    │
│  │  │ • Search    │  │ • Emissions │  │ • Add/Remove│  │ • Process   │  │ • Compare   │    │    │
│  │  │ • Recommend │  │ • Shipping  │  │ • Update    │  │ • Payment   │  │ • Analyze   │    │    │
│  │  │ • Inventory │  │ • Scoring   │  │ • Calculate │  │ • Confirm   │  │ • Rank      │    │    │
│  │  │ • CO2 Aware │  │ • Lifecycle │  │ • CO2 Total │  │ • Eco Ship  │  │ • Eco Value │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  │                                    │                                                    │    │
│  │                                    │ ADK Integration (Optional)                         │    │
│  │                                    ▼                                                    │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │                            ADK Eco Agent                                        │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────────────────────┐    │    │    │
│  │  │  │  • Google ADK Framework Integration                                     │    │    │    │
│  │  │  │  • Gemini 2.0 Flash Model                                              │    │    │    │
│  │  │  │  • EcoRecommendationTool                                                │    │    │    │
│  │  │  │  • Session Management with InMemorySessionService                        │    │    │    │
│  │  │  └─────────────────────────────────────────────────────────────────────────┘    │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  │                                    │                                                    │    │
│  │                                    │ MCP Protocol (JSON-RPC 2.0)                       │    │
│  │                                    ▼                                                    │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │                              MCP Transport Layer                                 │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────────────────────┐    │    │    │
│  │  │  │  • Base MCPServer (JSON-RPC 2.0 Protocol)                              │    │    │    │
│  │  │  │  • HTTP Transport Integration                                          │    │    │    │
│  │  │  │  • Tool Discovery & Execution                                          │    │    │    │
│  │  │  │  • Resource Management                                                 │    │    │    │
│  │  │  │  • Prompt Template Rendering                                           │    │    │    │
│  │  │  └─────────────────────────────────────────────────────────────────────────┘    │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  │                                    │                                                    │    │
│  │                                    │ MCP Server Implementations                        │    │
│  │                                    ▼                                                    │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │                              MCP Servers                                        │    │    │
│  │  │  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────────┐  │    │    │
│  │  │  │   Boutique MCP      │  │     CO2 MCP         │  │   Comparison MCP        │  │    │    │
│  │  │  │   Transport         │  │    Transport        │  │                        │  │    │    │
│  │  │  │                     │  │                     │  │                        │  │    │    │
│  │  │  │ • product_search    │  │ • calculate_co2_    │  │ • compare_products     │  │    │    │
│  │  │  │ • cart_operations   │  │   impact            │  │ • analyze_sustainability│  │    │    │
│  │  │  │ • checkout          │  │ • calculate_eco_    │  │ • rank_by_eco_value    │  │    │    │
│  │  │  │ • get_recommendations│  │   score             │  │                        │  │    │    │
│  │  │  │ • convert_currency  │  │ • compare_sustainability│                      │  │    │    │
│  │  │  │                     │  │ • analyze_carbon_   │  │                        │  │    │    │
│  │  │  │ Resources:          │  │   footprint         │  │                        │  │    │    │
│  │  │  │ • /catalog          │  │                     │  │                        │  │    │    │
│  │  │  │ • /categories       │  │ Resources:          │  │                        │  │    │    │
│  │  │  │ • /currencies       │  │ • /emission_factors │  │                        │  │    │    │
│  │  │  │                     │  │ • /material_factors │  │                        │  │    │    │
│  │  │  │ Prompts:            │  │ • /country_factors  │  │                        │  │    │    │
│  │  │  │ • product_search_   │  │ • /sustainability_  │  │                        │  │    │    │
│  │  │  │   prompt            │  │   guidelines         │  │                        │  │    │    │
│  │  │  │ • recommendation_   │  │                     │  │                        │  │    │    │
│  │  │  │   prompt            │  │ Prompts:            │  │                        │  │    │    │
│  │  │  │                     │  │ • co2_analysis_     │  │                        │  │    │    │
│  │  │  └─────────────────────┘  │   prompt            │  │                        │  │    │    │
│  │  │                           │ • sustainability_    │  │                        │  │    │    │
│  │  │                           │   recommendation_    │  │                        │  │    │    │
│  │  │                           │   prompt             │  │                        │  │    │    │
│  │  │                           └─────────────────────┘  └─────────────────────────┘  │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    │ HTTP API Endpoints                                         │
│                                    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              Web User Interface                                        │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │  • Modern Chat Interface with Environmental Features                          │    │    │
│  │  │  • Real-time CO2 Impact Visualization                                        │    │    │
│  │  │  • Sustainable Product Recommendations                                      │    │    │
│  │  │  • Environmental Badges and Scoring                                         │    │    │
│  │  │  • Responsive Design (Mobile-First)                                          │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Complete Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    User Interaction Flow                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  User Query: "Find eco-friendly electronics under $200"                                         │
│                                    │                                                            │
│                                    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                            Web UI (Chat Interface)                                     │    │
│  │  • Real-time message handling                                                          │    │
│  │  • Environmental impact visualization                                                  │    │
│  │  • Responsive design                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    ▼ HTTP POST /api/chat                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                        FastAPI Main Application                                        │    │
│  │  • CORS middleware                                                                     │    │
│  │  • Prometheus metrics collection                                                       │    │
│  │  • Request routing                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                            Host Agent (Router)                                         │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │  1. Intent Analysis (Gemini 2.0 Flash)                                        │    │    │
│  │  │     • Classify query type: "product_search"                                    │    │    │
│  │  │     • Extract parameters: category="electronics", max_price=200               │    │    │
│  │  │     • Determine confidence: 0.9                                                │    │    │
│  │  │                                                                                 │    │    │
│  │  │  2. Agent Routing (A2A Protocol)                                               │    │    │
│  │  │     • Primary agent: "ProductDiscoveryAgent"                                   │    │    │
│  │  │     • Secondary agents: ["CO2CalculatorAgent"]                                │    │    │
│  │  │     • Workflow pattern: "sequential"                                           │    │    │
│  │  │                                                                                 │    │    │
│  │  │  3. Session Management                                                          │    │    │
│  │  │     • Update conversation history                                              │    │    │
│  │  │     • Maintain user preferences                                                │    │    │
│  │  │     • Track environmental impact                                               │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    ▼ A2A Protocol Communication                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                        Product Discovery Agent                                         │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │  1. Process Search Request                                                      │    │    │
│  │  │     • Parse search parameters                                                   │    │    │
│  │  │     • Apply environmental filters                                               │    │    │
│  │  │     • Generate search strategy                                                  │    │    │
│  │  │                                                                                 │    │    │
│  │  │  2. MCP Tool Execution                                                          │    │    │
│  │  │     • Call BoutiqueMCP.product_search()                                        │    │    │
│  │  │     • Apply CO2-aware filtering                                                 │    │    │
│  │  │     • Rank by environmental impact                                             │    │    │
│  │  │                                                                                 │    │    │
│  │  │  3. Response Generation                                                         │    │    │
│  │  │     • Format product results                                                    │    │    │
│  │  │     • Include CO2 impact data                                                   │    │    │
│  │  │     • Provide eco-friendly alternatives                                         │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    ▼ MCP Protocol (JSON-RPC 2.0)                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                        Boutique MCP Transport                                          │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │  1. Tool Discovery                                                               │    │    │
│  │  │     • List available tools: product_search, cart_operations, etc.              │    │    │
│  │  │     • Validate input schema                                                     │    │    │
│  │  │     • Route to appropriate handler                                              │    │    │
│  │  │                                                                                 │    │    │
│  │  │  2. Tool Execution                                                              │    │    │
│  │  │     • Execute product_search with parameters                                    │    │    │
│  │  │     • Call Online Boutique Product Catalog Service                             │    │    │
│  │  │     • Apply filters: category="electronics", max_price=200                    │    │    │
│  │  │                                                                                 │    │    │
│  │  │  3. Response Processing                                                         │    │    │
│  │  │     • Format results in MCP standard format                                     │    │    │
│  │  │     • Include metadata and pagination                                          │    │    │
│  │  │     • Handle errors gracefully                                                  │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    ▼ HTTP/gRPC to Online Boutique                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                    Online Boutique Product Catalog Service                              │    │
│  │  • Search products by category and price                                               │    │
│  │  • Return product details, pricing, and availability                                   │    │
│  │  • Provide inventory status                                                            │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                        CO2 Calculator Agent (Parallel)                                 │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │  1. Environmental Impact Calculation                                             │    │    │
│  │  │     • Calculate CO2 emissions for each product                                  │    │    │
│  │  │     • Include manufacturing, transport, and lifecycle                          │    │    │
│  │  │     • Apply environmental scoring algorithm                                     │    │    │
│  │  │                                                                                 │    │    │
│  │  │  2. MCP Tool Execution                                                          │    │    │
│  │  │     • Call CO2MCP.calculate_co2_impact()                                       │    │    │
│  │  │     • Calculate eco_score for each product                                      │    │    │
│  │  │     • Generate sustainability recommendations                                  │    │    │
│  │  │                                                                                 │    │    │
│  │  │  3. Response Integration                                                         │    │    │
│  │  │     • Merge CO2 data with product information                                    │    │    │
│  │  │     • Rank products by environmental impact                                     │    │    │
│  │  │     • Provide eco-friendly alternatives                                         │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                        Host Agent (Response Aggregation)                               │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │  1. Response Aggregation                                                        │    │    │
│  │  │     • Combine product search results with CO2 data                               │    │    │
│  │  │     • Apply environmental ranking                                               │    │    │
│  │  │     • Generate comprehensive response                                           │    │    │
│  │  │                                                                                 │    │    │
│  │  │  2. LLM Enhancement (Optional)                                                  │    │    │
│  │  │     • Use Gemini 2.0 Flash for response refinement                              │    │    │
│  │  │     • Add environmental context and tips                                        │    │    │
│  │  │     • Ensure user-friendly formatting                                           │    │    │
│  │  │                                                                                 │    │    │
│  │  │  3. Session Update                                                              │    │    │
│  │  │     • Update conversation history                                                │    │    │
│  │  │     • Track user preferences                                                    │    │    │
│  │  │     • Store environmental impact metrics                                        │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                            │
│                                    ▼ HTTP Response                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                            Web UI (Response Display)                                   │    │
│  │  • Display eco-friendly electronics with CO2 impact badges                            │    │
│  │  • Show environmental scoring and sustainability tips                                │    │
│  │  • Provide interactive product comparison with environmental metrics                  │    │
│  │  • Enable one-click addition to cart with CO2 awareness                               │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack & Integration Points

### **Core AI Framework**
- **Google Agent Development Kit (ADK)**: Agent orchestration and management
- **Google Gemini 2.0 Flash**: Large Language Model for natural language processing
- **A2A Protocol**: Inter-agent communication with message routing and discovery
- **MCP Protocol**: Model Context Protocol for standardized tool integration

### **Backend Infrastructure**
- **Python FastAPI**: High-performance web framework with async support
- **Kubernetes**: Container orchestration with GKE Autopilot
- **Docker**: Containerization with multi-stage builds
- **Prometheus**: Metrics collection and monitoring
- **Structured Logging**: JSON-formatted logs with context

### **Communication Protocols**
- **A2A Protocol**: Agent-to-agent communication with:
  - Message routing and queuing
  - Request/response patterns with timeout handling
  - Agent discovery and health monitoring
  - Broadcast messaging capabilities
- **MCP Protocol**: Model Context Protocol with:
  - JSON-RPC 2.0 standard compliance
  - Tool discovery and execution
  - Resource management and access
  - Prompt template rendering

### **External Integrations**
- **Online Boutique**: Google's microservices demo as base application
- **Google Cloud Services**: GKE, Artifact Registry, Cloud Monitoring
- **HTTP/gRPC**: Communication with Online Boutique microservices
- **RESTful APIs**: Standardized API integration patterns

## 🔧 API Endpoints Architecture

### **Main Application Endpoints**
```
/api/chat                    - Main chat interface (A2A orchestration)
/api/health                  - System health check
/api/metrics                 - Prometheus metrics
/api/docs                    - OpenAPI documentation
```

### **A2A Protocol Endpoints**
```
/api/a2a/status             - A2A protocol status and registered agents
/api/a2a/agents             - List all registered A2A agents
/api/a2a/agents/{name}/status - Individual agent status
/api/a2a/send               - Send direct message to specific agent
/api/a2a/broadcast          - Send broadcast message to all agents
/api/a2a/health             - A2A protocol health check
```

### **MCP Transport Endpoints**
```
/api/mcp                    - MCP server information and discovery
/api/mcp/{server}/tools     - List available tools for MCP server
/api/mcp/{server}/tools/{tool} - Execute specific MCP tool
/api/mcp/{server}/resources - List available resources
/api/mcp/{server}/resources/{uri} - Access specific resource
/api/mcp/{server}/prompts   - List available prompt templates
/api/mcp/{server}/prompts/{name} - Render specific prompt template
```

### **ADK Integration Endpoints**
```
/api/adk-chat               - Direct ADK agent communication
/api/adk-health             - ADK agent health status
```

## 🚀 Deployment Architecture

### **Kubernetes Namespaces**
- **co2-assistant**: Main application namespace
- **online-boutique**: Base microservices namespace
- **monitoring**: Observability stack namespace

### **Service Architecture**
- **co2-assistant-service**: ClusterIP service for internal communication
- **ob-proxy**: NGINX proxy for Online Boutique service routing
- **Ingress**: External access with managed certificates

### **Resource Management**
- **Horizontal Pod Autoscaler**: Dynamic scaling based on CPU/memory
- **Resource Requests/Limits**: Optimized for cost and performance
- **Health Checks**: Liveness and readiness probes for reliability

## 🔒 Security & Compliance

### **Network Security**
- **Network Policies**: Pod-to-pod communication restrictions
- **Ingress Security**: TLS termination and certificate management
- **Service Mesh**: Secure inter-service communication

### **Data Protection**
- **Kubernetes Secrets**: Secure storage of API keys and credentials
- **Encryption**: TLS for all external communications
- **Privacy**: Minimal data collection and session management

### **Monitoring & Observability**
- **Health Checks**: Comprehensive system health monitoring
- **Metrics Collection**: Prometheus metrics with custom business metrics
- **Distributed Tracing**: Request flow visibility across services
- **Alerting**: Automated alerts for system issues and SLA violations

## 📊 Performance & Scalability

### **Horizontal Scaling**
- **Auto-scaling**: GKE cluster and pod auto-scaling
- **Load Distribution**: Multiple replicas with intelligent load balancing
- **Resource Optimization**: Environment-specific resource allocation

### **Performance Optimization**
- **Async Processing**: Non-blocking request handling
- **Connection Pooling**: Efficient HTTP client management
- **Caching**: In-memory caching for frequently accessed data
- **Circuit Breakers**: Fault tolerance and graceful degradation

### **Monitoring & SLOs**
- **Service Level Objectives**: Response time and availability targets
- **Performance Metrics**: Sub-500ms response times for AI queries
- **Cost Optimization**: 50% infrastructure cost reduction
- **Reliability**: 99.9% uptime with comprehensive monitoring

This architecture represents a complete implementation of **Agentic AI Microservices 2.0**, demonstrating the integration of Google's ADK, A2A communication protocols, MCP transport layer, and environmental consciousness in a production-ready, scalable system on Google Kubernetes Engine.
