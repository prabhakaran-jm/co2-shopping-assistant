"""
MCP Transport-enabled CO2 Server

This module extends the existing CO2MCPServer with MCP transport capabilities,
providing JSON-RPC tool discovery for environmental impact calculations.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from ..mcp_transport import MCPServer, MCPTool, MCPResource, MCPPrompt
from .co2_mcp import CO2MCPServer

logger = structlog.get_logger(__name__)


class CO2MCPTransport(CO2MCPServer, MCPServer):
    """
    MCP Transport-enabled CO2 Server
    
    Extends the existing CO2MCPServer with MCP transport capabilities:
    - JSON-RPC tool discovery
    - Standardized tool execution
    - Resource management
    - Prompt templates
    """
    
    def __init__(self, co2_data_api_url: str = "https://api.carbonintensity.org.uk"):
        """
        Initialize the MCP-enabled CO2 Server
        
        Args:
            co2_data_api_url: Base URL for CO2 data API
        """
        # Initialize both parent classes
        CO2MCPServer.__init__(self, co2_data_api_url)
        MCPServer.__init__(self, "CO2MCP", "1.0.0")
        
        # Register MCP tools
        self._register_mcp_tools()
        
        # Register MCP resources
        self._register_mcp_resources()
        
        # Register MCP prompts
        self._register_mcp_prompts()
    
    def _register_mcp_tools(self):
        """Register MCP tools for CO2 operations"""
        
        # CO2 Calculation Tool
        co2_calc_tool = MCPTool(
            name="calculate_co2_impact",
            description="Calculate CO2 emissions for products or activities",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_type": {
                        "type": "string",
                        "description": "Type of product",
                        "enum": ["electronics", "clothing", "books", "home", "sports", "beauty"]
                    },
                    "price": {
                        "type": "number",
                        "description": "Product price in USD"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity of items",
                        "default": 1
                    },
                    "manufacturing_location": {
                        "type": "string",
                        "description": "Country where product was manufactured",
                        "default": "global"
                    },
                    "transport_distance": {
                        "type": "number",
                        "description": "Transport distance in kilometers",
                        "default": 1000
                    }
                },
                "required": ["product_type", "price"]
            }
        )
        self.register_tool(co2_calc_tool)
        
        # Eco Score Tool
        eco_score_tool = MCPTool(
            name="calculate_eco_score",
            description="Calculate environmental impact score for products",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_data": {
                        "type": "object",
                        "description": "Product information",
                        "properties": {
                            "type": {"type": "string"},
                            "price": {"type": "number"},
                            "materials": {"type": "array", "items": {"type": "string"}},
                            "manufacturing_process": {"type": "string"},
                            "packaging": {"type": "string"}
                        },
                        "required": ["type", "price"]
                    },
                    "weight_factors": {
                        "type": "object",
                        "description": "Custom weight factors for scoring",
                        "properties": {
                            "manufacturing": {"type": "number", "default": 0.4},
                            "transport": {"type": "number", "default": 0.3},
                            "packaging": {"type": "number", "default": 0.2},
                            "disposal": {"type": "number", "default": 0.1}
                        }
                    }
                },
                "required": ["product_data"]
            }
        )
        self.register_tool(eco_score_tool)
        
        # Sustainability Comparison Tool
        sustainability_tool = MCPTool(
            name="compare_sustainability",
            description="Compare sustainability metrics between products",
            inputSchema={
                "type": "object",
                "properties": {
                    "products": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "price": {"type": "number"},
                                "materials": {"type": "array", "items": {"type": "string"}},
                                "manufacturing_location": {"type": "string"}
                            },
                            "required": ["name", "type", "price"]
                        },
                        "minItems": 2,
                        "description": "List of products to compare"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "enum": ["co2_emissions", "eco_score", "water_usage", "energy_consumption"],
                        "description": "Metrics to include in comparison"
                    }
                },
                "required": ["products"]
            }
        )
        self.register_tool(sustainability_tool)
        
        # Carbon Footprint Analysis Tool
        footprint_tool = MCPTool(
            name="analyze_carbon_footprint",
            description="Analyze carbon footprint across product lifecycle",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "object",
                        "description": "Product information",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "price": {"type": "number"},
                            "weight": {"type": "number"},
                            "manufacturing_location": {"type": "string"},
                            "materials": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["name", "type", "price"]
                    },
                    "lifecycle_stages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "enum": ["raw_materials", "manufacturing", "transport", "usage", "disposal"],
                        "description": "Lifecycle stages to analyze",
                        "default": ["raw_materials", "manufacturing", "transport", "usage", "disposal"]
                    }
                },
                "required": ["product"]
            }
        )
        self.register_tool(footprint_tool)
    
    def _register_mcp_resources(self):
        """Register MCP resources for CO2 data"""
        
        # Emission Factors Resource
        factors_resource = MCPResource(
            uri="co2://emission_factors",
            name="Emission Factors",
            description="CO2 emission factors for different product types and activities",
            mimeType="application/json"
        )
        self.register_resource(factors_resource)
        
        # Material Factors Resource
        materials_resource = MCPResource(
            uri="co2://material_factors",
            name="Material Factors",
            description="Environmental impact factors for different materials",
            mimeType="application/json"
        )
        self.register_resource(materials_resource)
        
        # Country Factors Resource
        countries_resource = MCPResource(
            uri="co2://country_factors",
            name="Country Factors",
            description="CO2 intensity factors by country",
            mimeType="application/json"
        )
        self.register_resource(countries_resource)
        
        # Sustainability Guidelines Resource
        guidelines_resource = MCPResource(
            uri="co2://sustainability_guidelines",
            name="Sustainability Guidelines",
            description="Best practices and guidelines for sustainable consumption",
            mimeType="text/plain"
        )
        self.register_resource(guidelines_resource)
    
    def _register_mcp_prompts(self):
        """Register MCP prompt templates"""
        
        # CO2 Analysis Prompt
        analysis_prompt = MCPPrompt(
            name="co2_analysis_prompt",
            description="Generate CO2 impact analysis for products",
            arguments=[
                {
                    "name": "product_info",
                    "description": "Product information for analysis",
                    "required": True
                },
                {
                    "name": "analysis_depth",
                    "description": "Depth of analysis (basic, detailed, comprehensive)",
                    "required": False
                }
            ]
        )
        self.register_prompt(analysis_prompt)
        
        # Sustainability Recommendation Prompt
        recommendation_prompt = MCPPrompt(
            name="sustainability_recommendation_prompt",
            description="Generate sustainability recommendations",
            arguments=[
                {
                    "name": "user_preferences",
                    "description": "User's sustainability preferences and constraints",
                    "required": True
                },
                {
                    "name": "product_options",
                    "description": "Available product options to evaluate",
                    "required": False
                }
            ]
        )
        self.register_prompt(recommendation_prompt)
    
    # Implement abstract methods from MCPServer
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute CO2 tools"""
        
        if tool_name == "calculate_co2_impact":
            return await self._execute_co2_calculation(arguments)
        elif tool_name == "calculate_eco_score":
            return await self._execute_eco_score(arguments)
        elif tool_name == "compare_sustainability":
            return await self._execute_sustainability_comparison(arguments)
        elif tool_name == "analyze_carbon_footprint":
            return await self._execute_footprint_analysis(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource(self, uri: str) -> str:
        """Read CO2 resources"""
        
        if uri == "co2://emission_factors":
            return json.dumps(self.emission_factors, indent=2)
        elif uri == "co2://material_factors":
            return json.dumps(self.material_factors, indent=2)
        elif uri == "co2://country_factors":
            return json.dumps(self.country_factors, indent=2)
        elif uri == "co2://sustainability_guidelines":
            return self._get_sustainability_guidelines()
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    async def _render_prompt(self, name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Render CO2 prompt templates"""
        
        if name == "co2_analysis_prompt":
            product_info = arguments.get("product_info", {})
            analysis_depth = arguments.get("analysis_depth", "basic")
            
            prompt_text = f"""
            Analyze the CO2 impact of the following product:
            {json.dumps(product_info, indent=2)}
            
            Provide a {analysis_depth} analysis that includes:
            1. Total CO2 emissions estimate
            2. Breakdown by lifecycle stage
            3. Comparison to industry averages
            4. Recommendations for reducing environmental impact
            
            Format the response as a structured analysis report.
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
        
        elif name == "sustainability_recommendation_prompt":
            user_preferences = arguments.get("user_preferences", "")
            product_options = arguments.get("product_options", [])
            
            prompt_text = f"""
            Based on the user's sustainability preferences: "{user_preferences}"
            {f"Available product options: {json.dumps(product_options, indent=2)}" if product_options else ""}
            
            Generate sustainability recommendations that include:
            1. Most environmentally friendly options
            2. Trade-offs between cost and environmental impact
            3. Alternative products or approaches
            4. Long-term sustainability considerations
            
            Format the response as actionable recommendations.
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
    async def _execute_co2_calculation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CO2 calculation tool"""
        product_type = arguments.get("product_type")
        price = arguments.get("price")
        quantity = arguments.get("quantity", 1)
        manufacturing_location = arguments.get("manufacturing_location", "global")
        transport_distance = arguments.get("transport_distance", 1000)
        
        # Prepare product data dictionary for the CO2 server
        product_data = {
            "type": product_type,
            "price": price,
            "quantity": quantity,
            "manufacturing_location": manufacturing_location,
            "transport_distance": transport_distance
        }
        
        # Use existing CO2 server methods
        co2_data = await self.calculate_product_co2(product_data, include_lifecycle=True)
        
        return {
            "product_type": product_type,
            "price": price,
            "quantity": quantity,
            "manufacturing_location": manufacturing_location,
            "transport_distance": transport_distance,
            "co2_impact": co2_data
        }
    
    async def _execute_eco_score(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute eco score calculation tool"""
        product_data = arguments.get("product_data")
        weight_factors = arguments.get("weight_factors", {})
        
        eco_score = await self.analyze_environmental_impact(product_data, weight_factors)
        
        return {
            "product_data": product_data,
            "weight_factors": weight_factors,
            "eco_score": eco_score
        }
    
    async def _execute_sustainability_comparison(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sustainability comparison tool"""
        products = arguments.get("products")
        metrics = arguments.get("metrics", ["co2_emissions", "eco_score"])
        
        # Use the sustainability recommendations method for comparison
        comparison = await self.get_sustainability_recommendations(products, metrics)
        
        return {
            "products": products,
            "metrics": metrics,
            "comparison": comparison
        }
    
    async def _execute_footprint_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute carbon footprint analysis tool"""
        product = arguments.get("product")
        lifecycle_stages = arguments.get("lifecycle_stages", ["raw_materials", "manufacturing", "transport", "usage", "disposal"])
        
        # Use the environmental impact analysis method
        analysis = await self.analyze_environmental_impact(product, lifecycle_stages)
        
        return {
            "product": product,
            "lifecycle_stages": lifecycle_stages,
            "analysis": analysis
        }
    
    def _get_sustainability_guidelines(self) -> str:
        """Get sustainability guidelines text"""
        return """
# Sustainability Guidelines for CO2-Aware Shopping

## General Principles

1. **Reduce Consumption**: Buy only what you need
2. **Choose Quality**: Invest in durable products that last longer
3. **Consider Lifecycle**: Think about the full environmental impact
4. **Support Sustainable Brands**: Choose companies with environmental commitments

## Product Categories

### Electronics
- Look for Energy Star certification
- Consider refurbished or second-hand options
- Choose products with replaceable batteries
- Recycle old electronics properly

### Clothing
- Choose natural, organic materials when possible
- Support fair trade and ethical manufacturing
- Buy timeless pieces that won't go out of style
- Consider second-hand or rental options

### Home Goods
- Choose energy-efficient appliances
- Look for products made from recycled materials
- Consider local manufacturing to reduce transport
- Choose products with minimal packaging

## Transportation Impact

- Consider local vs. imported products
- Look for products shipped via low-carbon methods
- Support companies with carbon offset programs
- Consider bulk purchases to reduce shipping frequency

## Disposal Considerations

- Choose products that are recyclable or biodegradable
- Look for take-back programs
- Consider products with minimal packaging
- Plan for end-of-life disposal before purchasing
        """.strip()
