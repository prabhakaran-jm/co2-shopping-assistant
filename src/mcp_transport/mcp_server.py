"""
MCP Transport Server Implementation

This module implements the Model Context Protocol (MCP) transport layer
with JSON-RPC 2.0 communication, tool discovery, and resource management.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import structlog
from dataclasses import dataclass, asdict
from enum import Enum

logger = structlog.get_logger(__name__)


class MCPErrorCode(Enum):
    """MCP Error codes as per specification"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000


@dataclass
class MCPError:
    """MCP Error structure"""
    code: int
    message: str
    data: Optional[Any] = None


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class MCPResource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


@dataclass
class MCPPrompt:
    """MCP Prompt template definition"""
    name: str
    description: str
    arguments: List[Dict[str, Any]]


class MCPServer:
    """
    MCP Server implementation with JSON-RPC 2.0 transport
    
    This server provides:
    - Tool discovery and execution
    - Resource management
    - Prompt templates
    - Standardized MCP communication
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize MCP Server
        
        Args:
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        self.running = False
        
        # Register core MCP methods
        self._register_core_methods()
    
    def _register_core_methods(self):
        """Register core MCP methods"""
        self.methods = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "resources/read": self._handle_resources_read,
            "prompts/list": self._handle_prompts_list,
            "prompts/get": self._handle_prompts_get,
        }
    
    def register_tool(self, tool: MCPTool):
        """Register a tool with the MCP server"""
        self.tools[tool.name] = tool
        logger.info("Registered MCP tool", tool_name=tool.name)
    
    def register_resource(self, resource: MCPResource):
        """Register a resource with the MCP server"""
        self.resources[resource.uri] = resource
        logger.info("Registered MCP resource", resource_uri=resource.uri)
    
    def register_prompt(self, prompt: MCPPrompt):
        """Register a prompt template with the MCP server"""
        self.prompts[prompt.name] = prompt
        logger.info("Registered MCP prompt", prompt_name=prompt.name)
    
    async def handle_request(self, request_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle incoming MCP request
        
        Args:
            request_data: JSON-RPC request (string or dict)
            
        Returns:
            JSON-RPC response
        """
        try:
            # Parse request
            if isinstance(request_data, str):
                request = json.loads(request_data)
            else:
                request = request_data
            
            # Validate JSON-RPC 2.0 structure
            if not self._validate_request(request):
                return self._create_error_response(
                    None, MCPErrorCode.INVALID_REQUEST, "Invalid JSON-RPC request"
                )
            
            # Extract method and params
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            # Handle the request
            if method in self.methods:
                result = await self.methods[method](params)
                return self._create_success_response(request_id, result)
            else:
                return self._create_error_response(
                    request_id, MCPErrorCode.METHOD_NOT_FOUND, f"Method '{method}' not found"
                )
                
        except json.JSONDecodeError:
            return self._create_error_response(
                None, MCPErrorCode.PARSE_ERROR, "Invalid JSON"
            )
        except Exception as e:
            logger.error("MCP request handling error", error=str(e))
            return self._create_error_response(
                request.get("id") if isinstance(request, dict) else None,
                MCPErrorCode.INTERNAL_ERROR, f"Internal error: {str(e)}"
            )
    
    def _validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate JSON-RPC 2.0 request structure"""
        return (
            isinstance(request, dict) and
            "jsonrpc" in request and
            request["jsonrpc"] == "2.0" and
            "method" in request and
            isinstance(request["method"], str)
        )
    
    def _create_success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Create JSON-RPC success response"""
        response = {
            "jsonrpc": "2.0",
            "result": result
        }
        if request_id is not None:
            response["id"] = request_id
        return response
    
    def _create_error_response(self, request_id: Any, error_code: MCPErrorCode, message: str, data: Any = None) -> Dict[str, Any]:
        """Create JSON-RPC error response"""
        error = {
            "code": error_code.value,
            "message": message
        }
        if data is not None:
            error["data"] = data
        
        response = {
            "jsonrpc": "2.0",
            "error": error
        }
        if request_id is not None:
            response["id"] = request_id
        return response
    
    # Core MCP Methods
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }
    
    async def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": [asdict(tool) for tool in self.tools.values()]
        }
    
    async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # This would be implemented by subclasses
        result = await self._execute_tool(tool_name, arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    
    async def _handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        return {
            "resources": [asdict(resource) for resource in self.resources.values()]
        }
    
    async def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        
        if uri not in self.resources:
            raise ValueError(f"Resource '{uri}' not found")
        
        # This would be implemented by subclasses
        content = await self._read_resource(uri)
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": self.resources[uri].mimeType or "text/plain",
                    "text": content
                }
            ]
        }
    
    async def _handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request"""
        return {
            "prompts": [asdict(prompt) for prompt in self.prompts.values()]
        }
    
    async def _handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name not in self.prompts:
            raise ValueError(f"Prompt '{name}' not found")
        
        # This would be implemented by subclasses
        messages = await self._render_prompt(name, arguments)
        
        return {
            "messages": messages
        }
    
    # Abstract methods to be implemented by subclasses
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_tool")
    
    async def _read_resource(self, uri: str) -> str:
        """Read a resource - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _read_resource")
    
    async def _render_prompt(self, name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Render a prompt template - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _render_prompt")
    
    async def start(self):
        """Start the MCP server"""
        self.running = True
        logger.info("MCP server started", server_name=self.name)
    
    async def stop(self):
        """Stop the MCP server"""
        self.running = False
        logger.info("MCP server stopped", server_name=self.name)
