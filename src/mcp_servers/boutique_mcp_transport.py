"""
MCP Transport-enabled Boutique Server

This module extends the existing BoutiqueMCPServer with MCP transport capabilities,
providing JSON-RPC tool discovery and standardized communication.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from ..mcp_transport import MCPServer, MCPTool, MCPResource, MCPPrompt
from .boutique_mcp import BoutiqueMCPServer

logger = structlog.get_logger(__name__)


class BoutiqueMCPTransport(BoutiqueMCPServer, MCPServer):
    """
    MCP Transport-enabled Boutique Server
    
    Extends the existing BoutiqueMCPServer with MCP transport capabilities:
    - JSON-RPC tool discovery
    - Standardized tool execution
    - Resource management
    - Prompt templates
    """
    
    def __init__(self, boutique_base_url: str = "http://online-boutique.online-boutique.svc.cluster.local"):
        """
        Initialize the MCP-enabled Boutique Server
        
        Args:
            boutique_base_url: Base URL for Online Boutique services
        """
        # Initialize both parent classes
        BoutiqueMCPServer.__init__(self, boutique_base_url)
        MCPServer.__init__(self, "BoutiqueMCP", "1.0.0")
        
        # Register MCP tools
        self._register_mcp_tools()
        
        # Register MCP resources
        self._register_mcp_resources()
        
        # Register MCP prompts
        self._register_mcp_prompts()
    
    def _register_mcp_tools(self):
        """Register MCP tools for boutique operations"""
        
        # Product Search Tool
        product_search_tool = MCPTool(
            name="product_search",
            description="Search for products in the Online Boutique catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for products"
                    },
                    "category": {
                        "type": "string",
                        "description": "Product category filter",
                        "enum": ["electronics", "clothing", "books", "home", "sports", "beauty"]
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price filter"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )
        self.register_tool(product_search_tool)
        
        # Cart Operations Tool
        cart_tool = MCPTool(
            name="cart_operations",
            description="Perform cart operations (add, remove, get, clear)",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Cart operation to perform",
                        "enum": ["add", "remove", "get", "clear"]
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID for cart operations"
                    },
                    "product_id": {
                        "type": "string",
                        "description": "Product ID (required for add/remove operations)"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity (required for add operation)",
                        "default": 1
                    }
                },
                "required": ["operation", "user_id"]
            }
        )
        self.register_tool(cart_tool)
        
        # Checkout Tool
        checkout_tool = MCPTool(
            name="checkout",
            description="Process order checkout",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID for checkout"
                    },
                    "email": {
                        "type": "string",
                        "description": "User email address"
                    },
                    "street_address": {
                        "type": "string",
                        "description": "Street address"
                    },
                    "zip_code": {
                        "type": "string",
                        "description": "ZIP code"
                    },
                    "city": {
                        "type": "string",
                        "description": "City"
                    },
                    "state": {
                        "type": "string",
                        "description": "State"
                    },
                    "country": {
                        "type": "string",
                        "description": "Country"
                    },
                    "credit_card_number": {
                        "type": "string",
                        "description": "Credit card number"
                    },
                    "credit_card_cvv": {
                        "type": "string",
                        "description": "Credit card CVV"
                    },
                    "credit_card_expiration_month": {
                        "type": "integer",
                        "description": "Credit card expiration month"
                    },
                    "credit_card_expiration_year": {
                        "type": "integer",
                        "description": "Credit card expiration year"
                    },
                    "currency_code": {
                        "type": "string",
                        "description": "Currency code",
                        "default": "USD"
                    }
                },
                "required": ["user_id", "email", "street_address", "zip_code", "city", "state", "country"]
            }
        )
        self.register_tool(checkout_tool)
        
        # Recommendations Tool
        recommendations_tool = MCPTool(
            name="get_recommendations",
            description="Get product recommendations for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID for recommendations"
                    },
                    "product_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of product IDs to base recommendations on"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recommendations",
                        "default": 5
                    }
                },
                "required": ["user_id"]
            }
        )
        self.register_tool(recommendations_tool)
        
        # Currency Conversion Tool
        currency_tool = MCPTool(
            name="convert_currency",
            description="Convert currency amounts",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code"
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount to convert"
                    }
                },
                "required": ["from_currency", "to_currency", "amount"]
            }
        )
        self.register_tool(currency_tool)
    
    def _register_mcp_resources(self):
        """Register MCP resources for boutique data"""
        
        # Product Catalog Resource
        catalog_resource = MCPResource(
            uri="boutique://catalog",
            name="Product Catalog",
            description="Complete product catalog from Online Boutique",
            mimeType="application/json"
        )
        self.register_resource(catalog_resource)
        
        # Categories Resource
        categories_resource = MCPResource(
            uri="boutique://categories",
            name="Product Categories",
            description="Available product categories",
            mimeType="application/json"
        )
        self.register_resource(categories_resource)
        
        # Currencies Resource
        currencies_resource = MCPResource(
            uri="boutique://currencies",
            name="Supported Currencies",
            description="List of supported currencies",
            mimeType="application/json"
        )
        self.register_resource(currencies_resource)
    
    def _register_mcp_prompts(self):
        """Register MCP prompt templates"""
        
        # Product Search Prompt
        search_prompt = MCPPrompt(
            name="product_search_prompt",
            description="Generate a product search query based on user intent",
            arguments=[
                {
                    "name": "user_intent",
                    "description": "User's shopping intent or query",
                    "required": True
                },
                {
                    "name": "context",
                    "description": "Additional context about the search",
                    "required": False
                }
            ]
        )
        self.register_prompt(search_prompt)
        
        # Recommendation Prompt
        recommendation_prompt = MCPPrompt(
            name="recommendation_prompt",
            description="Generate product recommendations based on user preferences",
            arguments=[
                {
                    "name": "user_preferences",
                    "description": "User's preferences and interests",
                    "required": True
                },
                {
                    "name": "budget",
                    "description": "User's budget constraints",
                    "required": False
                }
            ]
        )
        self.register_prompt(recommendation_prompt)
    
    # Implement abstract methods from MCPServer
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute boutique tools"""
        
        if tool_name == "product_search":
            return await self._execute_product_search(arguments)
        elif tool_name == "cart_operations":
            return await self._execute_cart_operations(arguments)
        elif tool_name == "checkout":
            return await self._execute_checkout(arguments)
        elif tool_name == "get_recommendations":
            return await self._execute_recommendations(arguments)
        elif tool_name == "convert_currency":
            return await self._execute_currency_conversion(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource(self, uri: str) -> str:
        """Read boutique resources"""
        
        if uri == "boutique://catalog":
            products = await self.get_products()
            return json.dumps(products, indent=2)
        elif uri == "boutique://categories":
            categories = await self.get_categories()
            return json.dumps(categories, indent=2)
        elif uri == "boutique://currencies":
            currencies = await self.get_supported_currencies()
            return json.dumps(currencies, indent=2)
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    async def _render_prompt(self, name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Render boutique prompt templates"""
        
        if name == "product_search_prompt":
            user_intent = arguments.get("user_intent", "")
            context = arguments.get("context", "")
            
            prompt_text = f"""
            Based on the user's shopping intent: "{user_intent}"
            {f"Additional context: {context}" if context else ""}
            
            Generate a structured product search query that includes:
            1. Search keywords
            2. Relevant categories
            3. Price range suggestions
            4. Additional filters that might be helpful
            
            Format the response as a JSON object with search parameters.
            """
            
            return [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_text.strip()
                    }
                }
            ]
        
        elif name == "recommendation_prompt":
            user_preferences = arguments.get("user_preferences", "")
            budget = arguments.get("budget", "")
            
            prompt_text = f"""
            Based on the user's preferences: "{user_preferences}"
            {f"Budget constraints: {budget}" if budget else ""}
            
            Generate personalized product recommendations that include:
            1. Recommended product categories
            2. Specific product suggestions
            3. Reasoning for each recommendation
            4. Alternative options within budget
            
            Format the response as a structured recommendation list.
            """
            
            return [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_text.strip()
                    }
                }
            ]
        
        else:
            raise ValueError(f"Unknown prompt: {name}")
    
    # Tool execution methods
    async def _execute_product_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute product search tool"""
        query = arguments.get("query", "")
        category = arguments.get("category")
        max_price = arguments.get("max_price")
        limit = arguments.get("limit", 10)
        
        # Use existing boutique server methods
        products = await self.search_products(query, category, max_price, limit)
        
        return {
            "query": query,
            "filters": {
                "category": category,
                "max_price": max_price,
                "limit": limit
            },
            "results": products,
            "count": len(products)
        }
    
    async def _execute_cart_operations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cart operations tool"""
        operation = arguments.get("operation")
        user_id = arguments.get("user_id")
        product_id = arguments.get("product_id")
        quantity = arguments.get("quantity", 1)
        
        if operation == "add":
            result = await self.add_to_cart(user_id, product_id, quantity)
        elif operation == "remove":
            result = await self.remove_from_cart(user_id, product_id)
        elif operation == "get":
            result = await self.get_cart(user_id)
        elif operation == "clear":
            result = await self.clear_cart(user_id)
        else:
            raise ValueError(f"Unknown cart operation: {operation}")
        
        return {
            "operation": operation,
            "user_id": user_id,
            "result": result
        }
    
    async def _execute_checkout(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute checkout tool"""
        # Extract checkout parameters
        checkout_data = {
            "user_id": arguments.get("user_id"),
            "email": arguments.get("email"),
            "address": {
                "street_address": arguments.get("street_address"),
                "zip_code": arguments.get("zip_code"),
                "city": arguments.get("city"),
                "state": arguments.get("state"),
                "country": arguments.get("country")
            },
            "credit_card": {
                "credit_card_number": arguments.get("credit_card_number"),
                "credit_card_cvv": arguments.get("credit_card_cvv"),
                "credit_card_expiration_month": arguments.get("credit_card_expiration_month"),
                "credit_card_expiration_year": arguments.get("credit_card_expiration_year")
            },
            "currency_code": arguments.get("currency_code", "USD")
        }
        
        result = await self.checkout(checkout_data)
        
        return {
            "checkout_data": checkout_data,
            "result": result
        }
    
    async def _execute_recommendations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recommendations tool"""
        user_id = arguments.get("user_id")
        product_ids = arguments.get("product_ids", [])
        limit = arguments.get("limit", 5)
        
        recommendations = await self.get_recommendations(user_id, product_ids, limit)
        
        return {
            "user_id": user_id,
            "base_products": product_ids,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    
    async def _execute_currency_conversion(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute currency conversion tool"""
        from_currency = arguments.get("from_currency")
        to_currency = arguments.get("to_currency")
        amount = arguments.get("amount")
        
        converted_amount = await self.convert_currency(from_currency, to_currency, amount)
        
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "original_amount": amount,
            "converted_amount": converted_amount
        }
