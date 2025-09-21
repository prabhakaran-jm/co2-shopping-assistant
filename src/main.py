"""
CO2-Aware Shopping Assistant - Main Application Entry Point

This is the main entry point for the CO2-Aware Shopping Assistant,
a multi-agent system built with Google's Agent Development Kit (ADK).
"""

import asyncio
import logging
import os
import re
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
import structlog
from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
)

# Rate limiting imports
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    print("Warning: slowapi not available. Rate limiting disabled.")

from .agents.host_agent import HostAgent
from .agents.product_discovery_agent import ProductDiscoveryAgent
from .agents.co2_calculator_agent import CO2CalculatorAgent
from .agents.cart_management_agent import CartManagementAgent
from .agents.checkout_agent import CheckoutAgent
from .agents.comparison_agent import ComparisonAgent
from .agents.adk_agent import ADKEcoAgent
from .mcp_servers.boutique_mcp import BoutiqueMCPServer
from .mcp_servers.boutique_mcp_transport import BoutiqueMCPTransport
from .mcp_servers.co2_mcp_transport import CO2MCPTransport
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

REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint']
)
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
AGENT_REQUESTS = Counter(
    'agent_requests_total', 'Total agent requests', ['agent_name', 'status']
)
AGENT_DURATION = Histogram(
    'agent_request_duration_seconds', 'Agent request duration', ['agent_name']
)

# Security metrics
SECURITY_VIOLATIONS = Counter(
    'security_violations_total', 'Security violations', ['violation_type']
)
RATE_LIMIT_HITS = Counter(
    'rate_limit_hits_total', 'Rate limit violations', ['endpoint']
)

# Initialize rate limiter if available
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None

# Global agent instances
agents: Dict[str, Any] = {}
mcp_servers: Dict[str, Any] = {}


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    sanitized = sanitized[:max_length]
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized


def validate_request_size(request: Request) -> bool:
    """
    Validate request size to prevent large payload attacks.
    
    Args:
        request: FastAPI request object
        
    Returns:
        True if request size is acceptable
    """
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            size = int(content_length)
            if size > 1024 * 1024:  # 1MB limit
                SECURITY_VIOLATIONS.labels(violation_type="large_request").inc()
                logger.warning("Large request detected", size=size, client_ip=request.client.host)
                return False
        except ValueError:
            pass
    
    return True


def log_security_event(event_type: str, request: Request, details: Dict[str, Any] = None):
    """
    Log security events for monitoring.
    
    Args:
        event_type: Type of security event
        request: FastAPI request object
        details: Additional details to log
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    log_data = {
        "event_type": event_type,
        "client_ip": client_ip,
        "user_agent": user_agent,
        "path": request.url.path,
        "method": request.method
    }
    
    if details:
        log_data.update(details)
    
    logger.warning("Security event detected", **log_data)
    SECURITY_VIOLATIONS.labels(violation_type=event_type).inc()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info("Starting CO2-Aware Shopping Assistant")
    
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
        for agent_name, agent_instance in agents.items():
            if agent_name != "host":  # Don't register the host agent itself
                await a2a_protocol.register_agent(agent_name, agent_instance)
                logger.info(f"Registered agent: {agent_name}")
        
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

# Add rate limiting exception handler if available
if RATE_LIMITING_AVAILABLE and limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware with restricted origins
allowed_origins = [
    "https://assistant.cloudcarta.com",
    "https://medium.com",
    "https://www.medium.com"
]

# Add localhost for development
if os.getenv("ENVIRONMENT", "production").lower() == "dev":
    allowed_origins.extend([
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Security middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware for request validation and monitoring."""
    # Validate request size
    if not validate_request_size(request):
        log_security_event("large_request", request)
        return JSONResponse(
            status_code=413,
            content={"error": "Request too large"}
        )
    
    # Check for suspicious patterns
    user_agent = request.headers.get("user-agent", "").lower()
    if any(pattern in user_agent for pattern in ["bot", "crawler", "scanner", "curl", "wget"]):
        # Allow legitimate bots but log them
        if not any(allowed in user_agent for allowed in ["googlebot", "bingbot", "slurp"]):
            log_security_event("suspicious_user_agent", request, {"user_agent": user_agent})
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# Ensure latest UI files are always fetched (avoid stale cached files during demo)
@app.middleware("http")
async def no_cache_for_static_files(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/static/") and ("script.js" in path or "style.css" in path):
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
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Rate limiting decorator function
def rate_limit_if_available(limit: str):
    """Apply rate limiting if slowapi is available."""
    def decorator(func):
        if RATE_LIMITING_AVAILABLE and limiter:
            return limiter.limit(limit)(func)
        return func
    return decorator

@app.post("/api/chat")
@rate_limit_if_available("10/minute")
async def chat_endpoint(payload: Dict[str, Any], request: Request):
    """Main chat endpoint for user interactions."""
    try:
        # Sanitize and validate input
        user_message = sanitize_input(payload.get("message", ""))
        
        if not user_message:
            log_security_event("empty_message", request)
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Validate message length
        if len(user_message) < 2:
            log_security_event("message_too_short", request, {"length": len(user_message)})
            raise HTTPException(status_code=400, detail="Message too short")
        
        # Derive a stable session id: prefer explicit payload, then cookie, else generate
        import uuid
        session_id = payload.get("session_id")
        cookie_sid = request.cookies.get("assistant_sid")
        if not session_id or str(session_id).strip() == "":
            session_id = cookie_sid
        if not session_id or str(session_id).strip() == "":
            session_id = f"sid_{uuid.uuid4().hex}"
        
        # Validate session ID format
        if not re.match(r'^sid_[a-f0-9]{32}$', session_id) and not re.match(r'^[a-f0-9\-]{36}$', session_id):
            log_security_event("invalid_session_id", request, {"session_id": session_id})
            session_id = f"sid_{uuid.uuid4().hex}"
        
        logger.info("Processing user message", message=user_message[:100], session_id=session_id, client_ip=request.client.host)
        
        # Route to host agent for processing
        host_agent = agents["host"]
        response = await host_agent.process_message(user_message, session_id)
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Chat processing failed", error=str(e), client_ip=request.client.host)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/agents/{agent_name}/status")
async def get_agent_status_endpoint(agent_name: str):
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
@rate_limit_if_available("5/minute")
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


async def get_mcp_transport(server_name: str):
    """FastAPI dependency to get the correct MCP transport instance."""
    if server_name not in mcp_servers:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")

    if server_name == "boutique":
        return BoutiqueMCPTransport()
    elif server_name == "co2":
        return CO2MCPTransport()
    else:
        raise HTTPException(status_code=404, detail=f"MCP transport for '{server_name}' not implemented")


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
async def list_mcp_tools(server_name: str, mcp_transport = Depends(get_mcp_transport)):
    """List available tools for an MCP server."""
    try:
        result = await mcp_transport._handle_tools_list({})
        return result
    except Exception as e:
        logger.error("MCP tools list error", server=server_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mcp/{server_name}/tools/{tool_name}")
@rate_limit_if_available("20/minute")
async def execute_mcp_tool(server_name: str, tool_name: str, request: Request, mcp_transport = Depends(get_mcp_transport)):
    """Execute a tool on an MCP server."""
    try:
        body = await request.json()

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
async def list_mcp_resources(server_name: str, mcp_transport = Depends(get_mcp_transport)):
    """List available resources for an MCP server."""
    try:
        result = await mcp_transport._handle_resources_list({})
        return result
    except Exception as e:
        logger.error("MCP resources list error", server=server_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mcp/{server_name}/resources/{resource_uri:path}")
async def read_mcp_resource(server_name: str, resource_uri: str, mcp_transport = Depends(get_mcp_transport)):
    """Read a resource from an MCP server."""
    try:
        params = {"uri": resource_uri}
        result = await mcp_transport._handle_resources_read(params)
        return result
        
    except Exception as e:
        logger.error("MCP resource read error", server=server_name, resource=resource_uri, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mcp/{server_name}/prompts")
async def list_mcp_prompts(server_name: str, mcp_transport = Depends(get_mcp_transport)):
    """List available prompts for an MCP server."""
    try:
        result = await mcp_transport._handle_prompts_list({})
        return result
    except Exception as e:
        logger.error("MCP prompts list error", server=server_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mcp/{server_name}/prompts/{prompt_name}")
async def render_mcp_prompt(server_name: str, prompt_name: str, request: Request, mcp_transport = Depends(get_mcp_transport)):
    """Render a prompt template from an MCP server."""
    try:
        body = await request.json()

        params = {
            "name": prompt_name,
            "arguments": body
        }
        result = await mcp_transport._handle_prompts_get(params)
        return result
        
    except Exception as e:
        logger.error("MCP prompt render error", server=server_name, prompt=prompt_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# A2A Protocol Endpoints
@app.get("/api/a2a/status")
async def get_a2a_status():
    """Get A2A protocol status and registered agents."""
    try:
        # Get A2A protocol from host agent
        host_agent = agents.get("host")
        if not host_agent or not hasattr(host_agent, 'a2a_protocol'):
            raise HTTPException(status_code=503, detail="A2A protocol not available")
        
        a2a_protocol = host_agent.a2a_protocol
        status = await a2a_protocol.get_protocol_status()
        return status
        
    except Exception as e:
        logger.error("A2A status error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/a2a/agents")
async def list_a2a_agents():
    """List all registered A2A agents."""
    try:
        # Get A2A protocol from host agent
        host_agent = agents.get("host")
        if not host_agent or not hasattr(host_agent, 'a2a_protocol'):
            raise HTTPException(status_code=503, detail="A2A protocol not available")
        
        a2a_protocol = host_agent.a2a_protocol
        agent_list = []
        
        for agent_name in a2a_protocol.agents.keys():
            agent_status = await a2a_protocol.get_agent_status(agent_name)
            agent_list.append({
                "name": agent_name,
                "status": agent_status["status"],
                "health": agent_status["health"],
                "registered_at": agent_status["registered_at"],
                "endpoint": agent_status["endpoint"]
            })
        
        return {
            "agents": agent_list,
            "total_count": len(agent_list)
        }
        
    except Exception as e:
        logger.error("A2A agents list error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/a2a/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get status of a specific A2A agent."""
    try:
        # Get A2A protocol from host agent
        host_agent = agents.get("host")
        if not host_agent or not hasattr(host_agent, 'a2a_protocol'):
            raise HTTPException(status_code=503, detail="A2A protocol not available")
        
        a2a_protocol = host_agent.a2a_protocol
        status = await a2a_protocol.get_agent_status(agent_name)
        
        if status.get("status") == "not_registered":
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not registered")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("A2A agent status error", agent=agent_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/a2a/send")
async def send_a2a_message(request: Request):
    """Send a message via A2A protocol."""
    try:
        body = await request.json()
        
        # Validate required fields
        required_fields = ["agent_name", "task"]
        for field in required_fields:
            if field not in body:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        agent_name = body["agent_name"]
        task = body["task"]
        message_type = body.get("message_type", "task_request")
        timeout = body.get("timeout", 30.0)
        
        # Get A2A protocol from host agent
        host_agent = agents.get("host")
        if not host_agent or not hasattr(host_agent, 'a2a_protocol'):
            raise HTTPException(status_code=503, detail="A2A protocol not available")
        
        a2a_protocol = host_agent.a2a_protocol
        
        # Send the message
        response = await a2a_protocol.send_request(
            agent_name=agent_name,
            task=task,
            message_type=message_type,
            timeout=timeout
        )
        
        return {
            "success": True,
            "agent_name": agent_name,
            "message_type": message_type,
            "response": response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("A2A message send error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/a2a/broadcast")
async def send_a2a_broadcast(request: Request):
    """Send a broadcast message via A2A protocol."""
    try:
        body = await request.json()
        
        # Validate required fields
        if "message_type" not in body:
            raise HTTPException(status_code=400, detail="Missing required field: message_type")
        if "payload" not in body:
            raise HTTPException(status_code=400, detail="Missing required field: payload")
        
        message_type = body["message_type"]
        payload = body["payload"]
        exclude_agents = body.get("exclude_agents", [])
        
        # Get A2A protocol from host agent
        host_agent = agents.get("host")
        if not host_agent or not hasattr(host_agent, 'a2a_protocol'):
            raise HTTPException(status_code=503, detail="A2A protocol not available")
        
        a2a_protocol = host_agent.a2a_protocol
        
        # Send the broadcast
        responses = await a2a_protocol.send_broadcast(
            message_type=message_type,
            payload=payload,
            exclude_agents=exclude_agents
        )
        
        return {
            "success": True,
            "message_type": message_type,
            "responses": responses,
            "total_agents": len(responses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("A2A broadcast error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/a2a/health")
async def get_a2a_health():
    """Get A2A protocol health status."""
    try:
        # Get A2A protocol from host agent
        host_agent = agents.get("host")
        if not host_agent or not hasattr(host_agent, 'a2a_protocol'):
            raise HTTPException(status_code=503, detail="A2A protocol not available")
        
        a2a_protocol = host_agent.a2a_protocol
        health_status = await a2a_protocol.health_check()
        
        return health_status
        
    except Exception as e:
        logger.error("A2A health check error", error=str(e))
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
