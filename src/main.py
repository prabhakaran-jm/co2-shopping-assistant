"""
CO2-Aware Shopping Assistant - Main Application Entry Point

This is the main entry point for the CO2-Aware Shopping Assistant,
a multi-agent system built with Google's Agent Development Kit (ADK).
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from .agents.host_agent import HostAgent
from .agents.product_discovery_agent import ProductDiscoveryAgent
from .agents.co2_calculator_agent import CO2CalculatorAgent
from .agents.cart_management_agent import CartManagementAgent
from .agents.checkout_agent import CheckoutAgent
from .agents.comparison_agent import ComparisonAgent
from .agents.adk_agent import ADKEcoAgent
from .mcp_servers.boutique_mcp import BoutiqueMCPServer
from .mcp_servers.co2_mcp import CO2MCPServer
from .mcp_servers.comparison_mcp import ComparisonMCPServer
from .a2a.protocol import A2AProtocol

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
AGENT_REQUESTS = Counter('agent_requests_total', 'Total agent requests', ['agent_name', 'status'])
AGENT_DURATION = Histogram('agent_request_duration_seconds', 'Agent request duration', ['agent_name'])

# Global agent instances
agents: Dict[str, Any] = {}
mcp_servers: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info("Starting CO2-Aware Shopping Assistant")
    print("LIFESPAN: Starting CO2-Aware Shopping Assistant")
    
    try:
        # Initialize MCP Servers
        logger.info("Initializing MCP servers...")
        mcp_servers["boutique"] = BoutiqueMCPServer()
        mcp_servers["co2"] = CO2MCPServer()
        mcp_servers["comparison"] = ComparisonMCPServer(boutique_mcp_server=mcp_servers["boutique"])
        
        await mcp_servers["boutique"].start()
        await mcp_servers["co2"].start()
        
        # Initialize A2A Protocol first
        logger.info("Initializing A2A protocol...")
        a2a_protocol = A2AProtocol()
        await a2a_protocol.initialize()
        
        # Initialize Agents
        logger.info("Initializing AI agents...")
        agents["ProductDiscoveryAgent"] = ProductDiscoveryAgent(
            boutique_mcp_server=mcp_servers["boutique"]
        )
        agents["CO2CalculatorAgent"] = CO2CalculatorAgent()
        agents["CartManagementAgent"] = CartManagementAgent()
        agents["CheckoutAgent"] = CheckoutAgent()
        agents["ComparisonAgent"] = ComparisonAgent(comparison_mcp_server=mcp_servers["comparison"])
        
        # Initialize ADK-based agent (optional)
        enable_adk = os.getenv("ENABLE_ADK_AGENT", "true").lower() in ("true", "1", "yes")
        if enable_adk:
            logger.info("Initializing ADK Eco Agent...")
            agents["ADKEcoAgent"] = ADKEcoAgent(boutique_mcp_server=mcp_servers["boutique"])
        else:
            logger.info("ADK agent disabled via environment variable")
        
        agents["host"] = HostAgent(sub_agents=list(agents.values()))
        
        # Register all agents with A2A protocol
        logger.info("Registering agents with A2A protocol...")
        print("LIFESPAN: Registering agents with A2A protocol...")
        for agent_name, agent_instance in agents.items():
            if agent_name != "host":  # Don't register the host agent itself
                await a2a_protocol.register_agent(agent_name, agent_instance)
                logger.info(f"Registered agent: {agent_name}")
                print(f"LIFESPAN: Registered agent: {agent_name}")
        
        # Update host agent with A2A protocol reference
        agents["host"].a2a_protocol = a2a_protocol
        
        logger.info("CO2-Aware Shopping Assistant started successfully")
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down CO2-Aware Shopping Assistant")
    
    # Stop MCP servers
    for server in mcp_servers.values():
        await server.stop()
    
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="CO2-Aware Shopping Assistant",
    description="AI-powered shopping assistant with environmental consciousness",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure latest UI script is always fetched (avoid stale cached JS during demo)
@app.middleware("http")
async def no_cache_for_script_js(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/static/") and "script.js" in path:
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Mount static files
app.mount("/static", StaticFiles(directory="src/ui"), name="static")


@app.get("/")
async def root():
    """Serve the main UI page."""
    return FileResponse("src/ui/index.html")


@app.get("/api/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": "CO2-Aware Shopping Assistant",
        "version": "1.0.0",
        "status": "running",
        "agents": list(agents.keys()),
        "mcp_servers": list(mcp_servers.keys())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with fast timeout for readiness probes."""
    try:
        # Check if all agents are healthy (fast)
        agent_status = {}
        for name, agent in agents.items():
            try:
                # Add timeout to prevent hanging
                agent_status[name] = await asyncio.wait_for(agent.health_check(), timeout=2.0)
            except asyncio.TimeoutError:
                agent_status[name] = {"status": "timeout", "error": "Health check timed out"}
            except Exception as e:
                agent_status[name] = {"status": "error", "error": str(e)}
        
        # Check MCP servers with timeout (fast)
        mcp_status = {}
        for name, server in mcp_servers.items():
            try:
                # Add timeout to prevent hanging on connectivity checks
                mcp_status[name] = await asyncio.wait_for(server.health_check(), timeout=2.0)
            except asyncio.TimeoutError:
                mcp_status[name] = {"status": "timeout", "error": "Health check timed out"}
            except Exception as e:
                mcp_status[name] = {"status": "error", "error": str(e)}
        
        return {
            "status": "healthy",
            "agents": agent_status,
            "mcp_servers": mcp_status
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/chat")
async def chat_endpoint(payload: Dict[str, Any], request: Request):
    """Main chat endpoint for user interactions."""
    try:
        user_message = payload.get("message", "")
        # Derive a stable session id: prefer explicit payload, then cookie, else generate
        session_id = payload.get("session_id")
        cookie_sid = request.cookies.get("assistant_sid")
        if not session_id or str(session_id).strip() == "":
            session_id = cookie_sid
        if not session_id or str(session_id).strip() == "":
            import uuid
            session_id = f"sid_{uuid.uuid4().hex}"
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info("Processing user message", message=user_message, session_id=session_id)
        print(f"MAIN: Processing user message: {user_message}")
        
        # Route to host agent for processing
        host_agent = agents["host"]
        print(f"MAIN: Calling host agent process_message")
        response = await host_agent.process_message(user_message, session_id)
        print(f"MAIN: Received response from host agent: {type(response)}")
        
        # Return JSON with a Set-Cookie for assistant_sid to keep sessions consistent
        data = {
            "response": response,
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        json_resp = JSONResponse(content=data)
        # Only set cookie if not present
        if cookie_sid != session_id:
            json_resp.set_cookie(
                key="assistant_sid",
                value=session_id,
                httponly=True,
                secure=(request.url.scheme == "https"),
                samesite="Lax",
                path="/",
                max_age=60 * 60 * 24 * 7
            )
        return json_resp
        
    except Exception as e:
        logger.error("Chat processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get status of a specific agent."""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_name]
    status = await agent.get_status()
    
    return {
        "agent": agent_name,
        "status": status
    }


@app.post("/api/adk-chat")
async def adk_chat_endpoint(payload: Dict[str, Any], request: Request):
    """ADK-specific chat endpoint for testing ADK agent functionality."""
    try:
        user_message = payload.get("message", "")
        session_id = payload.get("session_id", f"adk_sid_{asyncio.get_event_loop().time()}")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info("Processing ADK chat message", message=user_message, session_id=session_id)
        
        # Route to ADK agent
        if "ADKEcoAgent" not in agents:
            raise HTTPException(status_code=503, detail="ADK agent not available")
        
        adk_agent = agents["ADKEcoAgent"]
        response = await adk_agent.process_message(user_message, session_id)
        
        return {
            "response": response,
            "session_id": session_id,
            "agent_type": "ADK",
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error("ADK chat processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


# MCP Transport Endpoints
@app.get("/api/mcp")
async def mcp_info():
    """Get MCP server information and available endpoints."""
    return {
        "protocol": "MCP",
        "version": "2024-11-05",
        "servers": {
            "boutique": {
                "name": "BoutiqueMCP",
                "version": "1.0.0",
                "endpoints": {
                    "tools": "/api/mcp/boutique/tools",
                    "resources": "/api/mcp/boutique/resources",
                    "prompts": "/api/mcp/boutique/prompts"
                }
            },
            "co2": {
                "name": "CO2MCP", 
                "version": "1.0.0",
                "endpoints": {
                    "tools": "/api/mcp/co2/tools",
                    "resources": "/api/mcp/co2/resources",
                    "prompts": "/api/mcp/co2/prompts"
                }
            }
        }
    }


@app.get("/api/mcp/{server_name}/tools")
async def list_mcp_tools(server_name: str):
    """List available tools for an MCP server."""
    if server_name not in mcp_servers:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
    
    try:
        # Create MCP transport instance
        if server_name == "boutique":
            from .mcp_servers.boutique_mcp_transport import BoutiqueMCPTransport
            mcp_transport = BoutiqueMCPTransport()
        elif server_name == "co2":
            from .mcp_servers.co2_mcp_transport import CO2MCPTransport
            mcp_transport = CO2MCPTransport()
        else:
            raise HTTPException(status_code=404, detail=f"MCP transport for '{server_name}' not implemented")
        
        result = await mcp_transport._handle_tools_list({})
        return result
        
    except Exception as e:
        logger.error("MCP tools list error", server=server_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mcp/{server_name}/tools/{tool_name}")
async def execute_mcp_tool(server_name: str, tool_name: str, request: Request):
    """Execute a tool on an MCP server."""
    if server_name not in mcp_servers:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
    
    try:
        body = await request.json()
        
        # Create MCP transport instance
        if server_name == "boutique":
            from .mcp_servers.boutique_mcp_transport import BoutiqueMCPTransport
            mcp_transport = BoutiqueMCPTransport()
        elif server_name == "co2":
            from .mcp_servers.co2_mcp_transport import CO2MCPTransport
            mcp_transport = CO2MCPTransport()
        else:
            raise HTTPException(status_code=404, detail=f"MCP transport for '{server_name}' not implemented")
        
        params = {
            "name": tool_name,
            "arguments": body
        }
        result = await mcp_transport._handle_tools_call(params)
        return result
        
    except Exception as e:
        logger.error("MCP tool execution error", server=server_name, tool=tool_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mcp/{server_name}/resources")
async def list_mcp_resources(server_name: str):
    """List available resources for an MCP server."""
    if server_name not in mcp_servers:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
    
    try:
        # Create MCP transport instance
        if server_name == "boutique":
            from .mcp_servers.boutique_mcp_transport import BoutiqueMCPTransport
            mcp_transport = BoutiqueMCPTransport()
        elif server_name == "co2":
            from .mcp_servers.co2_mcp_transport import CO2MCPTransport
            mcp_transport = CO2MCPTransport()
        else:
            raise HTTPException(status_code=404, detail=f"MCP transport for '{server_name}' not implemented")
        
        result = await mcp_transport._handle_resources_list({})
        return result
        
    except Exception as e:
        logger.error("MCP resources list error", server=server_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mcp/{server_name}/resources/{resource_uri:path}")
async def read_mcp_resource(server_name: str, resource_uri: str):
    """Read a resource from an MCP server."""
    if server_name not in mcp_servers:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
    
    try:
        # Create MCP transport instance
        if server_name == "boutique":
            from .mcp_servers.boutique_mcp_transport import BoutiqueMCPTransport
            mcp_transport = BoutiqueMCPTransport()
        elif server_name == "co2":
            from .mcp_servers.co2_mcp_transport import CO2MCPTransport
            mcp_transport = CO2MCPTransport()
        else:
            raise HTTPException(status_code=404, detail=f"MCP transport for '{server_name}' not implemented")
        
        params = {"uri": resource_uri}
        result = await mcp_transport._handle_resources_read(params)
        return result
        
    except Exception as e:
        logger.error("MCP resource read error", server=server_name, resource=resource_uri, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mcp/{server_name}/prompts")
async def list_mcp_prompts(server_name: str):
    """List available prompts for an MCP server."""
    if server_name not in mcp_servers:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
    
    try:
        # Create MCP transport instance
        if server_name == "boutique":
            from .mcp_servers.boutique_mcp_transport import BoutiqueMCPTransport
            mcp_transport = BoutiqueMCPTransport()
        elif server_name == "co2":
            from .mcp_servers.co2_mcp_transport import CO2MCPTransport
            mcp_transport = CO2MCPTransport()
        else:
            raise HTTPException(status_code=404, detail=f"MCP transport for '{server_name}' not implemented")
        
        result = await mcp_transport._handle_prompts_list({})
        return result
        
    except Exception as e:
        logger.error("MCP prompts list error", server=server_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mcp/{server_name}/prompts/{prompt_name}")
async def render_mcp_prompt(server_name: str, prompt_name: str, request: Request):
    """Render a prompt template from an MCP server."""
    if server_name not in mcp_servers:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
    
    try:
        body = await request.json()
        
        # Create MCP transport instance
        if server_name == "boutique":
            from .mcp_servers.boutique_mcp_transport import BoutiqueMCPTransport
            mcp_transport = BoutiqueMCPTransport()
        elif server_name == "co2":
            from .mcp_servers.co2_mcp_transport import CO2MCPTransport
            mcp_transport = CO2MCPTransport()
        else:
            raise HTTPException(status_code=404, detail=f"MCP transport for '{server_name}' not implemented")
        
        params = {
            "name": prompt_name,
            "arguments": body
        }
        result = await mcp_transport._handle_prompts_get(params)
        return result
        
    except Exception as e:
        logger.error("MCP prompt render error", server=server_name, prompt=prompt_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
async def get_system_metrics():
    """Get system metrics for monitoring."""
    metrics = {}
    
    for name, agent in agents.items():
        metrics[f"agent_{name}"] = await agent.get_metrics()
    
    for name, server in mcp_servers.items():
        metrics[f"mcp_{name}"] = await server.get_metrics()
    
    return metrics


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configure logging level
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(level=getattr(logging, log_level))
    
    # Run the application
    port = int(os.getenv("HOST_AGENT_PORT", 8000))
    # Disable reload in production to prevent metric registration issues
    reload = os.getenv("ENVIRONMENT", "dev").lower() == "dev"
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_level=log_level.lower()
    )
