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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from .agents.host_agent import HostAgent
from .agents.product_discovery_agent import ProductDiscoveryAgent
from .agents.co2_calculator_agent import CO2CalculatorAgent
from .agents.cart_management_agent import CartManagementAgent
from .agents.checkout_agent import CheckoutAgent
from .mcp_servers.boutique_mcp import BoutiqueMCPServer
from .mcp_servers.co2_mcp import CO2MCPServer
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

# Global agent instances
agents: Dict[str, Any] = {}
mcp_servers: Dict[str, Any] = {}


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
        
        await mcp_servers["boutique"].start()
        await mcp_servers["co2"].start()
        
        # Initialize Agents
        logger.info("Initializing AI agents...")
        agents["product_discovery"] = ProductDiscoveryAgent()
        agents["co2_calculator"] = CO2CalculatorAgent()
        agents["cart_management"] = CartManagementAgent()
        agents["checkout"] = CheckoutAgent()
        agents["host"] = HostAgent(sub_agents=list(agents.values()))
        
        # Initialize A2A Protocol
        logger.info("Initializing A2A protocol...")
        a2a_protocol = A2AProtocol()
        await a2a_protocol.initialize()
        
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


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "name": "CO2-Aware Shopping Assistant",
        "version": "1.0.0",
        "status": "running",
        "agents": list(agents.keys()),
        "mcp_servers": list(mcp_servers.keys())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if all agents are healthy
        agent_status = {}
        for name, agent in agents.items():
            agent_status[name] = await agent.health_check()
        
        # Check if all MCP servers are healthy
        mcp_status = {}
        for name, server in mcp_servers.items():
            mcp_status[name] = await server.health_check()
        
        return {
            "status": "healthy",
            "agents": agent_status,
            "mcp_servers": mcp_status
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/chat")
async def chat_endpoint(request: Dict[str, Any]):
    """Main chat endpoint for user interactions."""
    try:
        user_message = request.get("message", "")
        session_id = request.get("session_id", "default")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info("Processing user message", message=user_message, session_id=session_id)
        
        # Route to host agent for processing
        host_agent = agents["host"]
        response = await host_agent.process_message(user_message, session_id)
        
        return {
            "response": response,
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        
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


@app.get("/metrics")
async def get_metrics():
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
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level=log_level.lower()
    )
