"""
Product Discovery Agent for CO2-Aware Shopping Assistant

This agent specializes in intelligent product search, recommendations,
and catalog operations with environmental consciousness.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from .base_agent import BaseAgent

logger = structlog.get_logger(__name__)


class ProductDiscoveryAgent(BaseAgent):
    """
    Product Discovery Agent that handles intelligent product search and recommendations.
    
    This agent:
    - Searches products with environmental impact scoring
    - Provides context-aware recommendations
    - Validates inventory and availability
    - Suggests eco-friendly alternatives
    """
    
    def __init__(self, boutique_mcp_server=None):
        """Initialize the Product Discovery Agent."""
        super().__init__(
            name="ProductDiscoveryAgent",
            description="Intelligent product search and recommendations with environmental consciousness",
            instruction=self._get_product_discovery_instruction()
        )
        
        # Store reference to MCP server
        self.boutique_mcp_server = boutique_mcp_server
        
        # Initialize tools (will be connected to MCP servers)
        self.boutique_tools = []
        self.co2_tools = []
        
        logger.info("Product Discovery Agent initialized")
    
    def _get_product_discovery_instruction(self) -> str:
        """Get instruction for the product discovery agent."""
        return """You are the Product Discovery Agent, specialized in helping users find products with environmental consciousness.

Your capabilities:
1. Intelligent product search with environmental impact scoring
2. Context-aware recommendations based on user preferences
3. Real-time inventory checking and availability validation
4. Eco-friendly product alternatives and suggestions
5. Price optimization with sustainability considerations

Key principles:
- Always prioritize environmentally friendly options
- Provide clear explanations of environmental benefits
- Consider user preferences while suggesting sustainable alternatives
- Include CO2 emission information when available
- Suggest products that align with sustainable shopping goals

When searching for products:
- Include environmental impact scores
- Highlight eco-friendly features
- Suggest sustainable alternatives
- Provide clear product comparisons
- Include availability and pricing information

Always explain why certain products are more environmentally friendly and help users make informed decisions."""
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process product discovery requests.
        
        Args:
            message: User's message/query
            session_id: Session identifier
            
        Returns:
            Dictionary containing the response
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("Processing product discovery request", message=message, session_id=session_id)
            
            # Parse the request to understand what the user is looking for
            request_type = await self._parse_request_type(message)
            
            if request_type == "search":
                response = await self._handle_product_search(message, session_id)
            elif request_type == "recommend":
                response = await self._handle_recommendations(message, session_id)
            elif request_type == "compare":
                response = await self._handle_product_comparison(message, session_id)
            elif request_type == "details":
                response = await self._handle_product_details(message, session_id)
            else:
                response = await self._handle_general_inquiry(message, session_id)
            
            # Update metrics
            response_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(success=True, response_time=response_time)
            
            return {
                "response": response,
                "agent": self.name,
                "request_type": request_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Product discovery processing failed", error=str(e), session_id=session_id)
            response_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(success=False, response_time=response_time)
            
            return {
                "response": "I apologize, but I encountered an error while searching for products. Please try again.",
                "error": str(e),
                "agent": self.name
            }
    
    async def _parse_request_type(self, message: str) -> str:
        """Parse the type of product discovery request."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["find", "search", "look for", "show me"]):
            return "search"
        elif any(word in message_lower for word in ["recommend", "suggest", "best", "top"]):
            return "recommend"
        elif any(word in message_lower for word in ["compare", "vs", "versus", "difference"]):
            return "compare"
        elif any(word in message_lower for word in ["details", "info", "about", "specifications"]):
            return "details"
        else:
            return "general"
    
    async def _handle_product_search(self, message: str, session_id: str) -> str:
        """Handle product search requests."""
        try:
            # Extract search parameters
            search_params = await self._extract_search_parameters(message)
            
            # Search products using boutique MCP
            products = await self._search_products(search_params)
            
            # Get CO2 impact for products
            products_with_co2 = await self._enrich_with_co2_data(products)
            
            # Format response
            if products_with_co2:
                response = self._format_product_search_response(products_with_co2, search_params)
            else:
                response = "I couldn't find any products matching your criteria. Could you try different search terms or broaden your search?"
            
            return response
            
        except Exception as e:
            logger.error("Product search failed", error=str(e))
            return "I encountered an error while searching for products. Please try again."
    
    async def _handle_recommendations(self, message: str, session_id: str) -> str:
        """Handle product recommendation requests."""
        try:
            # Extract recommendation parameters
            rec_params = await self._extract_recommendation_parameters(message)
            
            # Get recommendations
            recommendations = await self._get_recommendations(rec_params)
            
            # Enrich with CO2 data
            recommendations_with_co2 = await self._enrich_with_co2_data(recommendations)
            
            # Format response
            response = self._format_recommendation_response(recommendations_with_co2, rec_params)
            
            return response
            
        except Exception as e:
            logger.error("Recommendation generation failed", error=str(e))
            return "I encountered an error while generating recommendations. Please try again."
    
    async def _handle_product_comparison(self, message: str, session_id: str) -> str:
        """Handle product comparison requests."""
        try:
            # Extract comparison parameters
            comparison_params = await self._extract_comparison_parameters(message)
            
            # Get products to compare
            products = await self._get_products_for_comparison(comparison_params)
            
            # Get CO2 data for comparison
            products_with_co2 = await self._enrich_with_co2_data(products)
            
            # Format comparison response
            response = self._format_comparison_response(products_with_co2)
            
            return response
            
        except Exception as e:
            logger.error("Product comparison failed", error=str(e))
            return "I encountered an error while comparing products. Please try again."
    
    async def _handle_product_details(self, message: str, session_id: str) -> str:
        """Handle product details requests."""
        try:
            # Extract product identifier
            product_id = await self._extract_product_identifier(message)
            
            if not product_id:
                return "I need a product ID or name to get details. Could you specify which product you'd like to know more about?"
            
            # Get product details
            product_details = await self._get_product_details(product_id)
            
            if not product_details:
                return f"I couldn't find details for product '{product_id}'. Please check the product name or ID."
            
            # Get CO2 impact
            co2_data = await self._get_product_co2_impact(product_id)
            
            # Format detailed response
            response = self._format_product_details_response(product_details, co2_data)
            
            return response
            
        except Exception as e:
            logger.error("Product details retrieval failed", error=str(e))
            return "I encountered an error while retrieving product details. Please try again."
    
    async def _handle_general_inquiry(self, message: str, session_id: str) -> str:
        """Handle general product-related inquiries."""
        return """I'm here to help you discover products with environmental consciousness! 

I can help you with:
- **Product Search**: "Find eco-friendly electronics under $200"
- **Recommendations**: "Recommend sustainable clothing brands"
- **Product Comparison**: "Compare the environmental impact of these laptops"
- **Product Details**: "Tell me about the sustainability features of this product"

What would you like to explore? I'll make sure to highlight the environmental benefits and CO2 impact of any products I suggest! 🌱"""
    
    async def _extract_search_parameters(self, message: str) -> Dict[str, Any]:
        """Extract search parameters from user message."""
        import re
        
        params = {
            "query": message,
            "category": None,
            "max_price": None,
            "min_price": None,
            "eco_friendly": True,  # Default to eco-friendly
            "sort_by": "relevance"
        }
        
        # Extract price range
        price_match = re.search(r'\$(\d+(?:\.\d{2})?)', message)
        if price_match:
            params["max_price"] = float(price_match.group(1))
        
        # Extract category
        categories = ["electronics", "clothing", "books", "home", "sports", "beauty", "automotive"]
        for category in categories:
            if category in message.lower():
                params["category"] = category
                break
        
        # Check for eco-friendly keywords
        eco_keywords = ["eco", "green", "sustainable", "environmental", "organic", "recycled"]
        if any(keyword in message.lower() for keyword in eco_keywords):
            params["eco_friendly"] = True
        
        return params
    
    async def _extract_recommendation_parameters(self, message: str) -> Dict[str, Any]:
        """Extract recommendation parameters from user message."""
        params = {
            "query": message,
            "category": None,
            "max_price": None,
            "user_preferences": {},
            "limit": 5
        }
        
        # Extract category
        categories = ["electronics", "clothing", "books", "home", "sports", "beauty", "automotive"]
        for category in categories:
            if category in message.lower():
                params["category"] = category
                break
        
        # Extract price limit
        import re
        price_match = re.search(r'\$(\d+(?:\.\d{2})?)', message)
        if price_match:
            params["max_price"] = float(price_match.group(1))
        
        return params
    
    async def _extract_comparison_parameters(self, message: str) -> Dict[str, Any]:
        """Extract comparison parameters from user message."""
        params = {
            "products": [],
            "comparison_criteria": ["price", "co2_impact", "features"]
        }
        
        # Extract product names/IDs (simplified)
        # In a real implementation, this would use NLP to identify product names
        words = message.lower().split()
        product_indicators = ["product", "item", "laptop", "phone", "book", "shirt", "shoes"]
        
        for word in words:
            if word in product_indicators:
                params["products"].append(word)
        
        return params
    
    async def _extract_product_identifier(self, message: str) -> Optional[str]:
        """Extract product identifier from message."""
        # Simplified extraction - in real implementation would use NLP
        import re
        
        # Look for product IDs (alphanumeric patterns)
        id_match = re.search(r'[A-Z0-9]{6,}', message)
        if id_match:
            return id_match.group(0)
        
        # Look for product names
        words = message.lower().split()
        product_words = [word for word in words if len(word) > 3 and word.isalpha()]
        
        if product_words:
            return " ".join(product_words[:3])  # Take first 3 words as product name
        
        return None
    
    async def _search_products(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search products using boutique MCP."""
        try:
            if not self.boutique_mcp_server:
                logger.warning("Boutique MCP server not available, using fallback data")
                return await self._get_fallback_products(search_params)
            
            # Call the boutique MCP server to search products
            products = await self.boutique_mcp_server.search_products(
                query=search_params.get("query", ""),
                category=search_params.get("category"),
                max_price=search_params.get("max_price"),
                min_price=search_params.get("min_price"),
                limit=search_params.get("limit", 10)
            )
            
            logger.info("Retrieved products from boutique MCP", count=len(products))
            return products
            
        except Exception as e:
            logger.error("Failed to search products via MCP, using fallback", error=str(e))
            return await self._get_fallback_products(search_params)
    
    async def _get_fallback_products(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fallback products when MCP server is unavailable."""
        mock_products = [
            {
                "id": "ECO-LAPTOP-001",
                "name": "Eco-Friendly Laptop",
                "category": "electronics",
                "price": 899.99,
                "description": "Energy-efficient laptop made from recycled materials",
                "eco_score": 8.5,
                "availability": True
            },
            {
                "id": "GREEN-PHONE-002",
                "name": "Sustainable Smartphone",
                "category": "electronics",
                "price": 599.99,
                "description": "Phone with biodegradable components and solar charging",
                "eco_score": 9.2,
                "availability": True
            }
        ]
        
        # Filter based on search parameters
        filtered_products = []
        for product in mock_products:
            if search_params.get("category") and product["category"] != search_params["category"]:
                continue
            
            if search_params.get("max_price") and product["price"] > search_params["max_price"]:
                continue
            
            if search_params.get("eco_friendly") and product["eco_score"] < 7.0:
                continue
            
            filtered_products.append(product)
        
        return filtered_products
    
    async def _enrich_with_co2_data(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich products with CO2 emission data."""
        # Mock implementation - in real implementation would call CO2 MCP
        for product in products:
            # Extract price from the gRPC response structure
            price_usd = product.get("price_usd", {})
            price_units = price_usd.get("units", 0) + (price_usd.get("nanos", 0) / 1e9)
            
            # Mock CO2 data based on product type and price
            base_co2 = 50.0  # Base CO2 in kg
            # Use price as a proxy for eco-friendliness (lower price = more eco-friendly)
            eco_factor = max(0.1, min(1.0, (1000 - price_units) / 1000))
            product["co2_emissions"] = base_co2 * eco_factor
            product["co2_rating"] = "Low" if product["co2_emissions"] < 30 else "Medium" if product["co2_emissions"] < 60 else "High"
            
            # Add eco_score for compatibility with response formatting
            product["eco_score"] = max(1, min(10, int(10 * eco_factor)))
            
            # Add price field for compatibility
            product["price"] = price_units
        
        return products
    
    async def _get_recommendations(self, rec_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get product recommendations."""
        # Mock implementation
        return await self._search_products(rec_params)
    
    async def _get_products_for_comparison(self, comparison_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get products for comparison."""
        # Mock implementation
        return await self._search_products({"category": comparison_params.get("category")})
    
    async def _get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed product information."""
        try:
            if not self.boutique_mcp_server:
                logger.warning("Boutique MCP server not available, using fallback data")
                return await self._get_fallback_product_details(product_id)
            
            # Call the boutique MCP server to get product details
            product_details = await self.boutique_mcp_server.get_product_details(product_id)
            
            logger.info("Retrieved product details from boutique MCP", product_id=product_id)
            return product_details
            
        except Exception as e:
            logger.error("Failed to get product details via MCP, using fallback", error=str(e))
            return await self._get_fallback_product_details(product_id)
    
    async def _get_fallback_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get fallback product details when MCP server is unavailable."""
        mock_products = await self._get_fallback_products({})
        for product in mock_products:
            if product["id"] == product_id or product_id.lower() in product["name"].lower():
                return product
        return None
    
    async def _get_product_co2_impact(self, product_id: str) -> Dict[str, Any]:
        """Get CO2 impact data for a specific product."""
        # Mock implementation
        return {
            "manufacturing_co2": 25.5,
            "shipping_co2": 8.2,
            "usage_co2": 15.3,
            "disposal_co2": 2.1,
            "total_co2": 51.1,
            "eco_rating": "Low"
        }
    
    def _format_product_search_response(self, products: List[Dict[str, Any]], search_params: Dict[str, Any]) -> str:
        """Format product search results."""
        if not products:
            return "I couldn't find any products matching your criteria. Try adjusting your search terms."
        
        response = f"🌱 Found {len(products)} eco-friendly products for you:\n\n"
        
        for i, product in enumerate(products[:5], 1):  # Show top 5
            response += f"{i}. **{product['name']}** (${product['price']})\n"
            response += f"   • CO2 Impact: {product['co2_emissions']:.1f}kg ({product['co2_rating']})\n"
            response += f"   • Eco Score: {product['eco_score']}/10\n"
            response += f"   • {product['description']}\n\n"
        
        response += "💡 **Environmental Benefits**: These products are selected for their low carbon footprint and sustainable materials. Would you like more details about any specific product?"
        
        return response
    
    def _format_recommendation_response(self, recommendations: List[Dict[str, Any]], rec_params: Dict[str, Any]) -> str:
        """Format recommendation results."""
        if not recommendations:
            return "I couldn't generate recommendations based on your criteria. Could you provide more details about what you're looking for?"
        
        response = f"🌱 Here are my top {len(recommendations)} sustainable recommendations:\n\n"
        
        for i, product in enumerate(recommendations, 1):
            response += f"{i}. **{product['name']}** (${product['price']})\n"
            response += f"   • Environmental Impact: {product['co2_emissions']:.1f}kg CO2\n"
            response += f"   • Why it's eco-friendly: {product['description']}\n\n"
        
        response += "💡 These recommendations prioritize environmental sustainability while meeting your needs. Would you like to compare any of these products?"
        
        return response
    
    def _format_comparison_response(self, products: List[Dict[str, Any]]) -> str:
        """Format product comparison results."""
        if len(products) < 2:
            return "I need at least 2 products to make a comparison. Could you specify which products you'd like to compare?"
        
        response = "🔄 **Product Comparison** (Environmental Impact Focus):\n\n"
        
        for product in products:
            response += f"**{product['name']}** (${product['price']})\n"
            response += f"• CO2 Emissions: {product['co2_emissions']:.1f}kg\n"
            response += f"• Eco Score: {product['eco_score']}/10\n"
            response += f"• Rating: {product['co2_rating']}\n\n"
        
        # Find the most eco-friendly option
        best_eco = min(products, key=lambda p: p['co2_emissions'])
        response += f"🏆 **Most Eco-Friendly**: {best_eco['name']} with only {best_eco['co2_emissions']:.1f}kg CO2 emissions!"
        
        return response
    
    def _format_product_details_response(self, product: Dict[str, Any], co2_data: Dict[str, Any]) -> str:
        """Format detailed product information."""
        response = f"📋 **Product Details: {product['name']}**\n\n"
        response += f"💰 **Price**: ${product['price']}\n"
        response += f"📦 **Category**: {product['category'].title()}\n"
        response += f"📝 **Description**: {product['description']}\n\n"
        
        response += "🌱 **Environmental Impact**:\n"
        response += f"• Manufacturing: {co2_data['manufacturing_co2']}kg CO2\n"
        response += f"• Shipping: {co2_data['shipping_co2']}kg CO2\n"
        response += f"• Usage: {co2_data['usage_co2']}kg CO2\n"
        response += f"• Disposal: {co2_data['disposal_co2']}kg CO2\n"
        response += f"• **Total**: {co2_data['total_co2']}kg CO2 ({co2_data['eco_rating']} impact)\n\n"
        
        response += f"⭐ **Eco Score**: {product['eco_score']}/10\n"
        response += f"✅ **Availability**: {'In Stock' if product['availability'] else 'Out of Stock'}\n\n"
        
        response += "💡 This product is selected for its environmental consciousness and sustainable features!"
        
        return response
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task assigned to this agent."""
        task_type = task.get("type", "unknown")
        
        if task_type == "search_products":
            return await self._execute_product_search_task(task)
        elif task_type == "get_recommendations":
            return await self._execute_recommendation_task(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _execute_product_search_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute product search task."""
        search_params = task.get("parameters", {})
        products = await self._search_products(search_params)
        products_with_co2 = await self._enrich_with_co2_data(products)
        
        return {
            "products": products_with_co2,
            "count": len(products_with_co2),
            "search_params": search_params
        }
    
    async def _execute_recommendation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recommendation task."""
        rec_params = task.get("parameters", {})
        recommendations = await self._get_recommendations(rec_params)
        recommendations_with_co2 = await self._enrich_with_co2_data(recommendations)
        
        return {
            "recommendations": recommendations_with_co2,
            "count": len(recommendations_with_co2),
            "parameters": rec_params
        }
