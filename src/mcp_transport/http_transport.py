"""
HTTP Transport for MCP Server

This module provides HTTP-based transport for MCP servers,
enabling web-based tool discovery and execution.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .mcp_server import MCPServer

logger = structlog.get_logger(__name__)


class MCPHTTPTransport:
    """
    HTTP Transport layer for MCP servers
    
    Provides RESTful endpoints for:
    - Tool discovery
    - Tool execution
    - Resource access
    - Prompt templates
    """
    
    def __init__(self, mcp_server: MCPServer, host: str = "0.0.0.0", port: int = 8001):
        """
        Initialize HTTP transport
        
        Args:
            mcp_server: MCP server instance
            host: Host to bind to
            port: Port to bind to
        """
        self.mcp_server = mcp_server
        self.host = host
        self.port = port
        self.app = FastAPI(
            title=f"MCP Server - {mcp_server.name}",
            description=f"Model Context Protocol server for {mcp_server.name}",
            version=mcp_server.version
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes for MCP endpoints"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with server info"""
            return {
                "name": self.mcp_server.name,
                "version": self.mcp_server.version,
                "protocol": "MCP",
                "transport": "HTTP",
                "endpoints": {
                    "tools": "/tools",
                    "resources": "/resources", 
                    "prompts": "/prompts",
                    "health": "/health"
                }
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "server": self.mcp_server.name,
                "running": self.mcp_server.running,
                "tools_count": len(self.mcp_server.tools),
                "resources_count": len(self.mcp_server.resources),
                "prompts_count": len(self.mcp_server.prompts)
            }
        
        @self.app.post("/mcp")
        async def mcp_endpoint(request: Request):
            """Main MCP JSON-RPC endpoint"""
            try:
                body = await request.json()
                response = await self.mcp_server.handle_request(body)
                return JSONResponse(content=response)
            except Exception as e:
                logger.error("MCP endpoint error", error=str(e))
                return JSONResponse(
                    status_code=500,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                )
        
        @self.app.get("/tools")
        async def list_tools():
            """List available tools"""
            try:
                result = await self.mcp_server._handle_tools_list({})
                return result
            except Exception as e:
                logger.error("Tools list error", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/tools/{tool_name}")
        async def execute_tool(tool_name: str, request: Request):
            """Execute a specific tool"""
            try:
                body = await request.json()
                params = {
                    "name": tool_name,
                    "arguments": body
                }
                result = await self.mcp_server._handle_tools_call(params)
                return result
            except Exception as e:
                logger.error("Tool execution error", tool_name=tool_name, error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tools/{tool_name}")
        async def get_tool_info(tool_name: str):
            """Get tool information"""
            if tool_name not in self.mcp_server.tools:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
            tool = self.mcp_server.tools[tool_name]
            return {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
        
        @self.app.get("/resources")
        async def list_resources():
            """List available resources"""
            try:
                result = await self.mcp_server._handle_resources_list({})
                return result
            except Exception as e:
                logger.error("Resources list error", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/resources/{resource_uri:path}")
        async def read_resource(resource_uri: str):
            """Read a specific resource"""
            try:
                params = {"uri": resource_uri}
                result = await self.mcp_server._handle_resources_read(params)
                return result
            except Exception as e:
                logger.error("Resource read error", resource_uri=resource_uri, error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/prompts")
        async def list_prompts():
            """List available prompts"""
            try:
                result = await self.mcp_server._handle_prompts_list({})
                return result
            except Exception as e:
                logger.error("Prompts list error", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/prompts/{prompt_name}")
        async def render_prompt(prompt_name: str, request: Request):
            """Render a prompt template"""
            try:
                body = await request.json()
                params = {
                    "name": prompt_name,
                    "arguments": body
                }
                result = await self.mcp_server._handle_prompts_get(params)
                return result
            except Exception as e:
                logger.error("Prompt render error", prompt_name=prompt_name, error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start(self):
        """Start the HTTP transport server"""
        await self.mcp_server.start()
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        logger.info("Starting MCP HTTP transport", host=self.host, port=self.port)
        await server.serve()
    
    async def stop(self):
        """Stop the HTTP transport server"""
        await self.mcp_server.stop()
        logger.info("MCP HTTP transport stopped")
