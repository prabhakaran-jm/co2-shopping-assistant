# CO2-Aware Shopping Assistant - Architecture Documentation

## Overview

The CO2-Aware Shopping Assistant is a revolutionary AI-powered shopping system that helps users make environmentally conscious purchasing decisions. Built with Google's Agent Development Kit (ADK), it combines multiple specialized AI agents, MCP servers, and A2A communication protocols to provide intelligent, eco-friendly shopping assistance.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CO2-Aware Shopping Assistant                 │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React UI)                                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Chat Interface with Environmental Features             │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  Backend Services (FastAPI)                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Main Application (src/main.py)                         │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  AI Agents (Google ADK)                                         │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐      │
│  │ Host Agent  │ Product     │ CO2        │ Cart        │      │
│  │ (Router)    │ Discovery   │ Calculator │ Management  │      │
│  │             │ Agent       │ Agent      │ Agent       │      │
│  └─────────────┴─────────────┴─────────────┴─────────────┘      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Checkout Agent                              │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  Communication Protocols                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  A2A Protocol (Agent-to-Agent Communication)           │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  MCP Servers (Model Context Protocol)                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Boutique MCP Server    │  CO2 Data MCP Server         │    │
│  │  (Online Boutique APIs) │  (Environmental Data)        │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  External Services                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Online Boutique        │  Google Gemini AI             │    │
│  │  (Product Catalog)      │  (LLM Processing)            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. AI Agents (Built with Google ADK)

#### Host Agent (Router)
- **Purpose**: Central orchestration and request routing
- **Responsibilities**:
  - Process natural language user queries
  - Analyze user intent and route to appropriate agents
  - Coordinate multi-agent workflows
  - Manage session state and context
- **Key Features**:
  - Intent analysis and classification
  - Dynamic agent routing
  - Session management
  - Response aggregation

#### Product Discovery Agent
- **Purpose**: Intelligent product search and recommendations
- **Responsibilities**:
  - Search products with environmental impact scoring
  - Provide context-aware recommendations
  - Validate inventory and availability
  - Suggest eco-friendly alternatives
- **Key Features**:
  - Environmental impact scoring
  - Category-based filtering
  - Price optimization with sustainability
  - Real-time inventory checking

#### CO2 Calculator Agent
- **Purpose**: Environmental impact calculations and analysis
- **Responsibilities**:
  - Calculate CO2 emissions for products and shipping
  - Provide environmental impact scoring
  - Suggest eco-friendly alternatives
  - Analyze sustainability metrics
- **Key Features**:
  - Real-time CO2 calculations
  - Lifecycle analysis
  - Environmental equivalencies
  - Sustainability recommendations

#### Cart Management Agent
- **Purpose**: Intelligent cart operations with environmental awareness
- **Responsibilities**:
  - Manage cart operations (add, remove, update)
  - Provide CO2-aware cart suggestions
  - Calculate cart totals including environmental impact
  - Manage session persistence
- **Key Features**:
  - CO2-aware cart optimization
  - Quantity validation
  - Environmental impact tracking
  - Session state management

#### Checkout Agent
- **Purpose**: Order processing with environmental consciousness
- **Responsibilities**:
  - Process orders with eco-friendly shipping selection
  - Coordinate payment and confirmation
  - Validate transactions and handle errors
  - Provide order tracking and status updates
- **Key Features**:
  - Eco-friendly shipping options
  - Payment processing
  - Order confirmation
  - Tracking and status updates

### 2. Communication Protocols

#### A2A Protocol (Agent-to-Agent)
- **Purpose**: Standardized inter-agent communication
- **Features**:
  - Message routing between agents
  - Request/response patterns
  - Message queuing and delivery
  - Error handling and retries
  - Protocol discovery and negotiation
- **Implementation**:
  - HTTP-based communication
  - JSON message format
  - Timeout and retry mechanisms
  - Health monitoring

#### MCP Protocol (Model Context Protocol)
- **Purpose**: Standardized tool integration with external APIs
- **Features**:
  - Tool definition and discovery
  - Standardized API integration
  - Context management
  - Error handling
- **Implementation**:
  - RESTful API integration
  - Tool abstraction layer
  - Context passing
  - Response formatting

### 3. MCP Servers

#### Boutique MCP Server
- **Purpose**: Integration with Online Boutique microservices
- **Capabilities**:
  - Product catalog access
  - Cart operations
  - Order management
  - Inventory checking
  - Recommendation services
- **API Endpoints**:
  - Product search and details
  - Cart management
  - Checkout processing
  - Currency conversion

#### CO2 Data MCP Server
- **Purpose**: Environmental impact calculations and data
- **Capabilities**:
  - CO2 emission calculations
  - Environmental impact scoring
  - Sustainability metrics
  - Carbon footprint analysis
- **Data Sources**:
  - Emission factor databases
  - Material impact factors
  - Shipping method data
  - Environmental equivalencies

## Data Flow

### 1. User Request Processing

```
User Query → Host Agent → Intent Analysis → Agent Routing → Response
```

1. **User Input**: Natural language query via web interface
2. **Host Agent**: Receives and analyzes the query
3. **Intent Analysis**: Determines the type of request and required agents
4. **Agent Routing**: Routes to appropriate specialized agent(s)
5. **Response**: Aggregates and formats response for user

### 2. Product Search Flow

```
Search Query → Product Discovery Agent → Boutique MCP → CO2 MCP → Response
```

1. **Search Query**: User requests product search
2. **Product Discovery Agent**: Processes search parameters
3. **Boutique MCP**: Searches product catalog
4. **CO2 MCP**: Calculates environmental impact
5. **Response**: Returns products with CO2 data

### 3. Cart Management Flow

```
Cart Operation → Cart Management Agent → Boutique MCP → CO2 MCP → Response
```

1. **Cart Operation**: Add/remove/update cart items
2. **Cart Management Agent**: Processes cart operation
3. **Boutique MCP**: Updates cart in Online Boutique
4. **CO2 MCP**: Calculates cart environmental impact
5. **Response**: Returns updated cart with CO2 data

### 4. Checkout Flow

```
Checkout Request → Checkout Agent → Boutique MCP → CO2 MCP → Payment → Order
```

1. **Checkout Request**: User initiates checkout
2. **Checkout Agent**: Processes checkout request
3. **Boutique MCP**: Validates cart and processes order
4. **CO2 MCP**: Calculates final environmental impact
5. **Payment**: Processes payment
6. **Order**: Creates order with tracking

## Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **AI Framework**: Google Agent Development Kit (ADK)
- **LLM**: Google Gemini 2.0 Flash
- **HTTP Client**: httpx
- **Logging**: structlog

### Frontend
- **Technology**: HTML5, CSS3, JavaScript
- **UI Framework**: Vanilla JavaScript with modern CSS
- **Styling**: CSS Grid, Flexbox, CSS Variables
- **Features**: Real-time chat, responsive design, environmental badges

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Google Kubernetes Engine (GKE)
- **Service Mesh**: Kubernetes Services
- **Load Balancing**: GKE Ingress
- **Monitoring**: Prometheus, Grafana
- **Logging**: Google Cloud Logging

### External Services
- **Base Application**: Online Boutique (Google's microservices demo)
- **AI Services**: Google Gemini AI
- **Data Sources**: CO2 emission databases
- **APIs**: RESTful APIs for all integrations

## Deployment Architecture

### Kubernetes Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                        GKE Cluster                              │
├─────────────────────────────────────────────────────────────────┤
│  Namespace: co2-assistant                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  CO2 Assistant Deployment (3 replicas)                 │    │
│  │  ┌─────────────┬─────────────┬─────────────┐           │    │
│  │  │   Pod 1     │   Pod 2     │   Pod 3     │           │    │
│  │  └─────────────┴─────────────┴─────────────┘           │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  UI Deployment (2 replicas)                            │    │
│  │  ┌─────────────┬─────────────┐                           │    │
│  │  │   Pod 1     │   Pod 2     │                           │    │
│  │  └─────────────┴─────────────┘                           │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  Services                                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  co2-assistant-service (ClusterIP)                      │    │
│  │  co2-assistant-ui-service (ClusterIP)                  │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  Ingress                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  co2-assistant-ingress (External Access)               │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Container Images
- **Backend**: Custom Python application with FastAPI
- **Frontend**: Nginx serving static HTML/CSS/JS
- **Registry**: Google Artifact Registry

### Networking
- **Internal**: Kubernetes Services for inter-pod communication
- **External**: GKE Ingress for external access
- **Load Balancing**: Google Cloud Load Balancer

## Security Considerations

### Authentication & Authorization
- **API Keys**: Secure storage of Google AI API keys
- **Secrets Management**: Kubernetes Secrets for sensitive data
- **Network Policies**: Pod-to-pod communication restrictions

### Data Protection
- **Encryption**: TLS for all external communications
- **Data Privacy**: No persistent storage of user data
- **Session Management**: Stateless session handling

### Monitoring & Observability
- **Health Checks**: Kubernetes liveness and readiness probes
- **Metrics**: Prometheus metrics collection
- **Logging**: Structured logging with Google Cloud Logging
- **Tracing**: Distributed tracing for request flows

## Scalability & Performance

### Horizontal Scaling
- **Auto-scaling**: GKE cluster auto-scaling
- **Load Distribution**: Multiple replicas with load balancing
- **Resource Management**: CPU and memory limits

### Performance Optimization
- **Caching**: In-memory caching for frequently accessed data
- **Connection Pooling**: HTTP client connection pooling
- **Async Processing**: Asynchronous request handling

### Monitoring
- **SLOs**: Service Level Objectives for response times
- **Alerting**: Automated alerts for system issues
- **Dashboards**: Real-time system monitoring

## Future Enhancements

### Planned Features
- **Machine Learning**: Enhanced recommendation algorithms
- **Real-time Data**: Live CO2 emission data integration
- **Mobile App**: Native mobile application
- **Advanced Analytics**: User behavior and environmental impact analytics

### Technical Improvements
- **Service Mesh**: Istio integration for advanced networking
- **Event Streaming**: Apache Kafka for real-time events
- **Database**: Persistent storage for user preferences
- **CDN**: Global content delivery for improved performance

## Cost Optimization

The CO2-Aware Shopping Assistant implements comprehensive resource optimization strategies to ensure cost-effective deployment on Google Kubernetes Engine. Key optimizations include:

- **Resource Requests/Limits**: Carefully tuned CPU and memory allocations
- **Horizontal Pod Autoscaling (HPA)**: Intelligent scaling with cost controls
- **GKE Autopilot**: Automatic resource optimization and cost savings
- **Monitoring**: Comprehensive resource usage tracking and alerting

📖 **Detailed Documentation**: See [Cost Optimization Guide](../docs/cost-optimization.md) for comprehensive resource optimization strategies, specific configurations, and cost savings analysis.

## Conclusion

The CO2-Aware Shopping Assistant represents a significant advancement in environmentally conscious e-commerce. By combining Google's ADK with specialized AI agents, MCP servers, and A2A communication protocols, it provides users with intelligent, eco-friendly shopping assistance while maintaining high performance and scalability on Google Kubernetes Engine.

The architecture is designed to be modular, scalable, and maintainable, with clear separation of concerns and standardized communication protocols. This enables easy extension and modification of individual components while maintaining system integrity and performance.
