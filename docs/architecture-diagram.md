# CO2-Aware Shopping Assistant - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           GKE Autopilot Cluster                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    Online Boutique (Base Microservices)                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │  Frontend   │  │  Product    │  │    Cart     │  │  Checkout   │    │    │
│  │  │  (Go)       │  │  Catalog    │  │  Service    │  │  Service    │    │    │
│  │  │             │  │  (Go)       │  │  (.NET)     │  │  (Go)       │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │  Payment    │  │  Shipping   │  │   Email     │  │  Currency   │    │    │
│  │  │  Service    │  │  Service    │  │  Service    │  │  Service    │    │    │
│  │  │  (Node.js)  │  │  (Go)       │  │  (Python)   │  │  (Node.js)  │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                            │
│                                    │ HTTP/gRPC APIs                            │
│                                    ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │              CO2-Aware Shopping Assistant (AI Enhancement)              │    │
│  │                                                                         │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │    │
│  │  │                    Host Agent (Router)                          │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐    │    │    │
│  │  │  │  • Natural Language Processing                          │    │    │    │
│  │  │  │  • A2A Protocol Communication                          │    │    │    │
│  │  │  │  • Task Delegation & Orchestration                     │    │    │    │
│  │  │  │  • Google Gemini 2.0 Flash Integration                 │    │    │    │
│  │  │  └─────────────────────────────────────────────────────────┘    │    │    │
│  │  └─────────────────────────────────────────────────────────────────┘    │    │
│  │                                    │                                    │    │
│  │                                    │ A2A Protocol                       │    │
│  │                                    ▼                                    │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │  Product    │  │     CO2     │  │    Cart     │  │  Checkout   │    │    │
│  │  │ Discovery   │  │ Calculator  │  │ Management  │  │    Agent    │    │    │
│  │  │   Agent     │  │   Agent     │  │   Agent     │  │             │    │    │
│  │  │             │  │             │  │             │  │             │    │    │
│  │  │ • Search    │  │ • Emissions │  │ • Add/Remove│  │ • Process   │    │    │
│  │  │ • Recommend │  │ • Shipping  │  │ • Update    │  │ • Payment   │    │    │
│  │  │ • Inventory │  │ • Scoring   │  │ • Calculate │  │ • Confirm   │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  │                                    │                                    │    │
│  │                                    │ MCP Protocol                       │    │
│  │                                    ▼                                    │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │    │
│  │  │                    MCP Servers                                 │    │    │
│  │  │  ┌─────────────────────┐  ┌─────────────────────────────────┐  │    │    │
│  │  │  │   Boutique MCP      │  │        CO2 Data MCP            │  │    │    │
│  │  │  │                     │  │                                 │  │    │    │
│  │  │  │ • Product APIs      │  │ • CO2 Calculation APIs         │  │    │    │
│  │  │  │ • Cart APIs         │  │ • Environmental Data APIs     │  │    │    │
│  │  │  │ • Checkout APIs     │  │ • Sustainability Metrics APIs │  │    │    │
│  │  │  └─────────────────────┘  └─────────────────────────────────┘  │    │    │
│  │  └─────────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                            │
│                                    │ HTTP API                                   │
│                                    ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        Web User Interface                              │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │    │
│  │  │  • Modern Chat Interface                                       │    │    │
│  │  │  • CO2 Impact Visualization                                    │    │    │
│  │  │  • Real-time Environmental Feedback                            │    │    │
│  │  │  • Sustainable Product Recommendations                        │    │    │
│  │  └─────────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Query
    │
    ▼
┌─────────────────┐
│   Web UI        │
│   (Chat Input)  │
└─────────────────┘
    │
    ▼ HTTP POST
┌─────────────────┐
│   Host Agent    │
│   (Router)      │
└─────────────────┘
    │
    ▼ A2A Protocol
┌─────────────────┐
│ Specialized     │
│ Agents          │
└─────────────────┘
    │
    ▼ MCP Protocol
┌─────────────────┐
│   MCP Servers   │
│   (API Gateway) │
└─────────────────┘
    │
    ▼ HTTP/gRPC
┌─────────────────┐
│ Online Boutique │
│ Microservices   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   Response      │
│   (with CO2)    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   Web UI        │
│   (Chat Output) │
└─────────────────┘
```

## Technology Stack

### Frontend
- **HTML5/CSS3/JavaScript**: Modern web interface
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: Dynamic CO2 tracking

### Backend (AI Agents)
- **Google Agent Development Kit (ADK)**: Agent framework
- **Google Gemini 2.0 Flash**: Large Language Model
- **Python FastAPI**: Web framework
- **A2A Protocol**: Inter-agent communication
- **MCP Protocol**: External API integration

### Infrastructure
- **Google Kubernetes Engine (GKE) Autopilot**: Container orchestration
- **Terraform**: Infrastructure as Code
- **Google Artifact Registry**: Container images
- **Google Cloud Monitoring**: Observability

### Base Application
- **Online Boutique**: Google's microservices demo
- **Multiple Languages**: Go, .NET, Node.js, Python, Java
- **Service Mesh**: Inter-service communication

## Key Features

### Environmental Intelligence
- **Real-time CO2 Calculations**: Live emission tracking
- **Eco-friendly Recommendations**: Sustainable alternatives
- **Environmental Scoring**: Product impact assessment
- **Carbon Footprint Visualization**: User-friendly metrics

### AI-Powered Shopping
- **Natural Language Processing**: Conversational interface
- **Context-aware Recommendations**: Personalized suggestions
- **Intelligent Routing**: Smart task delegation
- **Multi-agent Collaboration**: Specialized AI agents

### System Reliability
- **SLO-aware Behavior**: Performance monitoring
- **Graceful Degradation**: Fault tolerance
- **Auto-scaling**: Dynamic resource allocation
- **Comprehensive Monitoring**: Full observability

## Security & Compliance

### Authentication & Authorization
- **Workload Identity**: Secure service-to-service communication
- **IAM Roles**: Least privilege access
- **Network Policies**: Inter-pod security

### Data Protection
- **Encryption in Transit**: TLS/HTTPS
- **Encryption at Rest**: Data encryption
- **Privacy by Design**: Minimal data collection

## Scalability & Performance

### Horizontal Scaling
- **GKE Autopilot**: Automatic node management
- **Container Orchestration**: Kubernetes
- **Load Balancing**: Traffic distribution

### Performance Optimization
- **Caching**: Response optimization
- **Connection Pooling**: Database efficiency
- **CDN**: Content delivery

## Monitoring & Observability

### Metrics
- **Google Cloud Monitoring**: System metrics
- **Prometheus**: Custom metrics
- **Grafana**: Visualization dashboards

### Logging
- **Google Cloud Logging**: Centralized logs
- **Structured Logging**: JSON format
- **Log Aggregation**: Search and analysis

### Tracing
- **Google Cloud Trace**: Request tracing
- **Distributed Tracing**: End-to-end visibility
- **Performance Analysis**: Bottleneck identification

## Deployment Architecture

### Infrastructure as Code
- **Terraform**: Infrastructure provisioning
- **GitOps**: Configuration management
- **Environment Separation**: Dev/Staging/Prod

### CI/CD Pipeline
- **Automated Testing**: Unit and integration tests
- **Container Building**: Docker image creation
- **Automated Deployment**: Kubernetes manifests
- **Rollback Capability**: Quick recovery

## Innovation Highlights

### Agentic AI Microservices 2.0
- **Multi-agent Architecture**: Specialized AI agents
- **A2A Communication**: Agent-to-agent protocol
- **MCP Integration**: Standardized API access
- **Environmental Consciousness**: CO2-aware decisions

### Modern DevOps Practices
- **Infrastructure as Code**: Terraform automation
- **Container Orchestration**: Kubernetes management
- **Observability**: Comprehensive monitoring
- **Security**: Defense in depth

This architecture represents a significant evolution from traditional microservices to **Agentic AI Microservices 2.0**, where AI agents enhance existing applications with intelligent, environmentally conscious capabilities.
