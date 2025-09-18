"""
CO2 Calculator Agent for CO2-Aware Shopping Assistant

This agent specializes in calculating CO2 emissions, environmental impact analysis,
and providing sustainability recommendations.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import structlog

from .base_agent import BaseAgent

logger = structlog.get_logger(__name__)


class CO2CalculatorAgent(BaseAgent):
    """
    CO2 Calculator Agent that handles environmental impact calculations and analysis.
    
    This agent:
    - Calculates CO2 emissions for products and shipping
    - Provides environmental impact scoring
    - Suggests eco-friendly alternatives
    - Analyzes sustainability metrics
    """
    
    def __init__(self):
        """Initialize the CO2 Calculator Agent."""
        super().__init__(
            name="CO2CalculatorAgent",
            description="Environmental impact calculator and sustainability advisor",
            instruction=self._get_co2_calculator_instruction()
        )
        
        # CO2 emission factors (kg CO2 per unit)
        self.emission_factors = {
            "manufacturing": {
                "electronics": 25.0,  # kg CO2 per $100
                "clothing": 15.0,
                "books": 5.0,
                "home": 20.0,
                "sports": 18.0,
                "beauty": 12.0,
                "automotive": 50.0
            },
            "shipping": {
                "ground": 0.5,      # kg CO2 per mile
                "air": 2.0,
                "sea": 0.1,
                "rail": 0.3
            },
            "packaging": {
                "standard": 0.5,     # kg CO2 per package
                "eco_friendly": 0.2,
                "minimal": 0.1
            }
        }
        
        logger.info("CO2 Calculator Agent initialized")
    
    def _get_co2_calculator_instruction(self) -> str:
        """Get instruction for the CO2 calculator agent."""
        return """You are the CO2 Calculator Agent, specialized in environmental impact analysis and sustainability guidance.

Your capabilities:
1. Calculate CO2 emissions for products, shipping, and packaging
2. Provide environmental impact scoring and ratings
3. Suggest eco-friendly alternatives and optimizations
4. Analyze sustainability metrics and trends
5. Compare environmental impact between options

Key principles:
- Always provide accurate CO2 calculations with clear explanations
- Explain the environmental impact in understandable terms
- Suggest practical ways to reduce carbon footprint
- Highlight the most significant environmental factors
- Provide context for CO2 numbers (e.g., "equivalent to driving X miles")

When calculating CO2 emissions:
- Include manufacturing, shipping, packaging, and usage phases
- Provide breakdown by emission source
- Suggest alternatives with lower environmental impact
- Explain the environmental benefits of eco-friendly options
- Use clear, actionable language

Always help users understand their environmental impact and guide them toward more sustainable choices."""
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process CO2 calculation and environmental analysis requests.
        
        Args:
            message: User's message/query
            session_id: Session identifier
            
        Returns:
            Dictionary containing the response
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("Processing CO2 calculation request", message=message, session_id=session_id)
            
            # Parse the request type
            request_type = await self._parse_co2_request_type(message)
            
            if request_type == "calculate":
                response = await self._handle_co2_calculation(message, session_id)
            elif request_type == "compare":
                response = await self._handle_co2_comparison(message, session_id)
            elif request_type == "analyze":
                response = await self._handle_environmental_analysis(message, session_id)
            elif request_type == "suggest":
                response = await self._handle_sustainability_suggestions(message, session_id)
            else:
                response = await self._handle_general_co2_inquiry(message, session_id)
            
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
            logger.error("CO2 calculation processing failed", error=str(e), session_id=session_id)
            response_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(success=False, response_time=response_time)
            
            return {
                "response": "I apologize, but I encountered an error while calculating CO2 emissions. Please try again.",
                "error": str(e),
                "agent": self.name
            }
    
    async def _parse_co2_request_type(self, message: str) -> str:
        """Parse the type of CO2-related request."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["calculate", "co2", "emission", "carbon", "footprint"]):
            return "calculate"
        elif any(word in message_lower for word in ["compare", "vs", "versus", "difference", "better"]):
            return "compare"
        elif any(word in message_lower for word in ["analyze", "impact", "environmental", "sustainability"]):
            return "analyze"
        elif any(word in message_lower for word in ["suggest", "recommend", "alternative", "eco", "green"]):
            return "suggest"
        else:
            return "general"
    
    async def _handle_co2_calculation(self, message: str, session_id: str) -> str:
        """Handle CO2 calculation requests."""
        try:
            # Extract calculation parameters
            calc_params = await self._extract_calculation_parameters(message)
            
            if not calc_params:
                return "I need more information to calculate CO2 emissions. Please specify the product, shipping method, or what you'd like me to calculate."
            
            # Perform CO2 calculation
            co2_data = await self._calculate_co2_emissions(calc_params)
            
            # Format response
            response = self._format_co2_calculation_response(co2_data, calc_params)
            
            return response
            
        except Exception as e:
            logger.error("CO2 calculation failed", error=str(e))
            return "I encountered an error while calculating CO2 emissions. Please try again with more specific details."
    
    async def _handle_co2_comparison(self, message: str, session_id: str) -> str:
        """Handle CO2 comparison requests."""
        try:
            # Extract comparison parameters
            comparison_params = await self._extract_comparison_parameters(message)
            
            if len(comparison_params.get("items", [])) < 2:
                return "I need at least 2 items to compare their CO2 emissions. Please specify which products or options you'd like to compare."
            
            # Calculate CO2 for each item
            comparison_results = []
            for item in comparison_params["items"]:
                co2_data = await self._calculate_co2_emissions(item)
                comparison_results.append({
                    "item": item,
                    "co2_data": co2_data
                })
            
            # Format comparison response
            response = self._format_co2_comparison_response(comparison_results)
            
            return response
            
        except Exception as e:
            logger.error("CO2 comparison failed", error=str(e))
            return "I encountered an error while comparing CO2 emissions. Please try again."
    
    async def _handle_environmental_analysis(self, message: str, session_id: str) -> str:
        """Handle environmental analysis requests."""
        try:
            # Extract analysis parameters
            analysis_params = await self._extract_analysis_parameters(message)
            
            # Perform environmental analysis
            analysis_results = await self._perform_environmental_analysis(analysis_params)
            
            # Format analysis response
            response = self._format_environmental_analysis_response(analysis_results)
            
            return response
            
        except Exception as e:
            logger.error("Environmental analysis failed", error=str(e))
            return "I encountered an error while performing environmental analysis. Please try again."
    
    async def _handle_sustainability_suggestions(self, message: str, session_id: str) -> str:
        """Handle sustainability suggestion requests."""
        try:
            # Extract suggestion parameters
            suggestion_params = await self._extract_suggestion_parameters(message)
            
            # Generate sustainability suggestions
            suggestions = await self._generate_sustainability_suggestions(suggestion_params)
            
            # Format suggestions response
            response = self._format_sustainability_suggestions_response(suggestions)
            
            return response
            
        except Exception as e:
            logger.error("Sustainability suggestions failed", error=str(e))
            return "I encountered an error while generating sustainability suggestions. Please try again."
    
    async def _handle_general_co2_inquiry(self, message: str, session_id: str) -> str:
        """Handle general CO2-related inquiries."""
        return """🌱 I'm your CO2 Calculator Agent, here to help you understand and reduce your environmental impact!

I can help you with:
- **CO2 Calculations**: "What's the carbon footprint of this laptop?"
- **Environmental Comparisons**: "Compare the CO2 emissions of ground vs air shipping"
- **Impact Analysis**: "Analyze the environmental impact of my shopping cart"
- **Sustainability Tips**: "Suggest ways to reduce my carbon footprint"

**Quick CO2 Facts**:
- Manufacturing typically accounts for 60-80% of a product's total CO2 emissions
- Shipping adds 5-15% depending on distance and method
- Eco-friendly packaging can reduce emissions by 60-80%

What would you like to calculate or analyze? I'll provide detailed CO2 breakdowns and suggest eco-friendly alternatives! 🌍"""
    
    async def _extract_calculation_parameters(self, message: str) -> Dict[str, Any]:
        """Extract parameters for CO2 calculation."""
        import re
        
        params = {
            "product_name": None,
            "product_type": None,
            "price": None,
            "shipping_method": None,
            "shipping_distance": None,
            "packaging_type": "standard"
        }
        
        # First, try to extract product name from the message
        product_name = await self._extract_product_name(message)
        if product_name:
            params["product_name"] = product_name
            # Get actual product data if we found a product name
            product_data = await self._get_product_by_name(product_name)
            if product_data:
                params["price"] = product_data.get("price")
                params["product_type"] = product_data.get("category")
        
        # Extract product type from categories
        categories = ["electronics", "clothing", "books", "home", "sports", "beauty", "automotive", "accessories"]
        for category in categories:
            if category in message.lower():
                params["product_type"] = category
                break
        
        # Extract price if not already set
        if not params["price"]:
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', message)
            if price_match:
                params["price"] = float(price_match.group(1))
        
        # Extract shipping method
        shipping_methods = ["ground", "air", "sea", "rail", "express", "standard"]
        for method in shipping_methods:
            if method in message.lower():
                params["shipping_method"] = method
                break
        
        # Extract distance
        distance_match = re.search(r'(\d+)\s*(?:miles?|km|kilometers?)', message.lower())
        if distance_match:
            params["shipping_distance"] = float(distance_match.group(1))
        
        # Extract packaging type
        if "eco" in message.lower() or "green" in message.lower():
            params["packaging_type"] = "eco_friendly"
        elif "minimal" in message.lower():
            params["packaging_type"] = "minimal"
        
        return params
    
    async def _extract_product_name(self, message: str) -> Optional[str]:
        """Extract product name from the message."""
        # Common product names in the catalog
        product_names = [
            "sunglasses", "tank top", "watch", "loafers", "hairdryer", 
            "candle holder", "salt & pepper shakers", "bamboo glass jar", "mug",
            "salt", "pepper", "shakers", "jar", "holder", "dryer"
        ]
        
        message_lower = message.lower()
        for product in product_names:
            if product in message_lower:
                return product
        
        return None
    
    async def _get_product_by_name(self, product_name: str) -> Optional[Dict[str, Any]]:
        """Get actual product data from the catalog."""
        # This matches the mock_products data from cart_management_agent.py
        mock_products = [
            {"id": "sunglasses", "name": "Sunglasses", "price": 19.99, "category": "accessories", "co2_emissions": 49.0, "eco_score": 9},
            {"id": "tank-top", "name": "Tank Top", "price": 18.99, "category": "clothing", "co2_emissions": 49.1, "eco_score": 9},
            {"id": "watch", "name": "Watch", "price": 109.99, "category": "accessories", "co2_emissions": 44.5, "eco_score": 4},
            {"id": "loafers", "name": "Loafers", "price": 89.99, "category": "clothing", "co2_emissions": 45.5, "eco_score": 5},
            {"id": "hairdryer", "name": "Hairdryer", "price": 24.99, "category": "home", "co2_emissions": 48.8, "eco_score": 8},
            {"id": "candle-holder", "name": "Candle Holder", "price": 18.99, "category": "home", "co2_emissions": 49.1, "eco_score": 9},
            {"id": "salt-and-pepper-shakers", "name": "Salt & Pepper Shakers", "price": 18.49, "category": "home", "co2_emissions": 49.1, "eco_score": 9},
            {"id": "bamboo-glass-jar", "name": "Bamboo Glass Jar", "price": 5.49, "category": "home", "co2_emissions": 49.7, "eco_score": 9},
            {"id": "mug", "name": "Mug", "price": 8.99, "category": "home", "co2_emissions": 49.6, "eco_score": 9}
        ]
        
        # Normalize product name for matching
        product_name_lower = product_name.lower()
        
        # Direct name matching
        for product in mock_products:
            if (product_name_lower in product["name"].lower() or 
                product_name_lower in product["id"].lower()):
                return product
        
        # Handle aliases
        alias_map = {
            "salt": "salt-and-pepper-shakers",
            "pepper": "salt-and-pepper-shakers", 
            "shakers": "salt-and-pepper-shakers",
            "jar": "bamboo-glass-jar",
            "holder": "candle-holder",
            "dryer": "hairdryer"
        }
        
        if product_name_lower in alias_map:
            alias_id = alias_map[product_name_lower]
            for product in mock_products:
                if product["id"] == alias_id:
                    return product
        
        return None
    
    async def _extract_comparison_parameters(self, message: str) -> Dict[str, Any]:
        """Extract parameters for CO2 comparison."""
        params = {
            "items": [],
            "comparison_criteria": ["total_co2", "manufacturing", "shipping"]
        }
        
        # Simplified extraction - in real implementation would use NLP
        # Look for product mentions or shipping methods
        if "ground" in message.lower() and "air" in message.lower():
            params["items"] = [
                {"shipping_method": "ground", "shipping_distance": 500},
                {"shipping_method": "air", "shipping_distance": 500}
            ]
        elif "express" in message.lower() and "standard" in message.lower():
            params["items"] = [
                {"shipping_method": "air", "shipping_distance": 500},
                {"shipping_method": "ground", "shipping_distance": 500}
            ]
        
        return params
    
    async def _extract_analysis_parameters(self, message: str) -> Dict[str, Any]:
        """Extract parameters for environmental analysis."""
        params = {
            "analysis_type": "general",
            "scope": "product",
            "include_recommendations": True
        }
        
        if "cart" in message.lower():
            params["scope"] = "cart"
        elif "order" in message.lower():
            params["scope"] = "order"
        
        return params
    
    async def _extract_suggestion_parameters(self, message: str) -> Dict[str, Any]:
        """Extract parameters for sustainability suggestions."""
        params = {
            "suggestion_type": "general",
            "focus_area": None,
            "budget_constraint": None
        }
        
        # Extract focus area
        focus_areas = ["shipping", "packaging", "products", "lifestyle"]
        for area in focus_areas:
            if area in message.lower():
                params["focus_area"] = area
                break
        
        return params
    
    async def _calculate_co2_emissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate CO2 emissions based on parameters."""
        co2_data = {
            "manufacturing_co2": 0.0,
            "shipping_co2": 0.0,
            "packaging_co2": 0.0,
            "total_co2": 0.0,
            "breakdown": {},
            "rating": "Unknown",
            "equivalent": {},
            "product_name": params.get("product_name")
        }
        
        # If we have a specific product, use its actual CO2 data
        if params.get("product_name"):
            product_data = await self._get_product_by_name(params["product_name"])
            if product_data and "co2_emissions" in product_data:
                # Use actual product CO2 emissions
                actual_co2 = product_data["co2_emissions"]
                co2_data["manufacturing_co2"] = actual_co2 * 0.8  # Assume 80% manufacturing
                co2_data["packaging_co2"] = actual_co2 * 0.2     # Assume 20% packaging
                co2_data["total_co2"] = actual_co2
                
                co2_data["breakdown"]["manufacturing"] = {
                    "co2": co2_data["manufacturing_co2"],
                    "factor": "Actual product data",
                    "percentage": 80.0
                }
                co2_data["breakdown"]["packaging"] = {
                    "co2": co2_data["packaging_co2"],
                    "type": "standard",
                    "percentage": 20.0
                }
                
                # Determine rating based on actual data
                if actual_co2 < 30:
                    co2_data["rating"] = "Very Low"
                elif actual_co2 < 45:
                    co2_data["rating"] = "Low"
                elif actual_co2 < 50:
                    co2_data["rating"] = "Medium"
                elif actual_co2 < 60:
                    co2_data["rating"] = "High"
                else:
                    co2_data["rating"] = "Very High"
                    
                # Add equivalents
                co2_data["equivalent"] = {
                    "miles_driven": actual_co2 * 2.5,  # Rough conversion
                    "trees_needed": actual_co2 * 0.1,  # Trees to offset
                    "days_electricity": actual_co2 * 0.5  # Days of home electricity
                }
                
                return co2_data
        
        # Fallback to generic calculation if no specific product found
        # Manufacturing CO2
        if params.get("product_type") and params.get("price"):
            product_type = params["product_type"]
            price = params["price"]
            
            if product_type in self.emission_factors["manufacturing"]:
                factor = self.emission_factors["manufacturing"][product_type]
                co2_data["manufacturing_co2"] = (price / 100) * factor
                co2_data["breakdown"]["manufacturing"] = {
                    "co2": co2_data["manufacturing_co2"],
                    "factor": f"{factor} kg CO2 per $100",
                    "percentage": 0
                }
        
        # Shipping CO2
        if params.get("shipping_method") and params.get("shipping_distance"):
            shipping_method = params["shipping_method"]
            distance = params["shipping_distance"]
            
            if shipping_method in self.emission_factors["shipping"]:
                factor = self.emission_factors["shipping"][shipping_method]
                co2_data["shipping_co2"] = distance * factor
                co2_data["breakdown"]["shipping"] = {
                    "co2": co2_data["shipping_co2"],
                    "method": shipping_method,
                    "distance": distance,
                    "factor": f"{factor} kg CO2 per mile",
                    "percentage": 0
                }
        
        # Packaging CO2
        packaging_type = params.get("packaging_type", "standard")
        if packaging_type in self.emission_factors["packaging"]:
            co2_data["packaging_co2"] = self.emission_factors["packaging"][packaging_type]
            co2_data["breakdown"]["packaging"] = {
                "co2": co2_data["packaging_co2"],
                "type": packaging_type,
                "percentage": 0
            }
        
        # Calculate total
        co2_data["total_co2"] = (
            co2_data["manufacturing_co2"] + 
            co2_data["shipping_co2"] + 
            co2_data["packaging_co2"]
        )
        
        # Calculate percentages
        if co2_data["total_co2"] > 0:
            for key in co2_data["breakdown"]:
                co2_data["breakdown"][key]["percentage"] = (
                    co2_data["breakdown"][key]["co2"] / co2_data["total_co2"] * 100
                )
        
        # Determine rating
        if co2_data["total_co2"] < 20:
            co2_data["rating"] = "Very Low"
        elif co2_data["total_co2"] < 50:
            co2_data["rating"] = "Low"
        elif co2_data["total_co2"] < 100:
            co2_data["rating"] = "Medium"
        elif co2_data["total_co2"] < 200:
            co2_data["rating"] = "High"
        else:
            co2_data["rating"] = "Very High"
        
        # Add equivalents
        co2_data["equivalent"] = {
            "miles_driven": co2_data["total_co2"] * 2.5,  # Rough conversion
            "trees_needed": co2_data["total_co2"] * 0.1,  # Trees to offset
            "days_electricity": co2_data["total_co2"] * 0.5  # Days of home electricity
        }
        
        return co2_data
    
    async def _perform_environmental_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform environmental analysis."""
        analysis = {
            "overall_impact": "Unknown",
            "key_factors": [],
            "recommendations": [],
            "sustainability_score": 0,
            "improvement_potential": "Unknown"
        }
        
        # Mock analysis based on parameters
        if params["scope"] == "cart":
            analysis["overall_impact"] = "Medium"
            analysis["key_factors"] = [
                "High-impact electronics in cart",
                "Standard shipping methods",
                "Mixed packaging types"
            ]
            analysis["recommendations"] = [
                "Consider eco-friendly alternatives for electronics",
                "Choose ground shipping over air",
                "Select minimal packaging options"
            ]
            analysis["sustainability_score"] = 6.5
            analysis["improvement_potential"] = "High"
        
        return analysis
    
    async def _generate_sustainability_suggestions(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate sustainability suggestions."""
        suggestions = []
        
        if params["focus_area"] == "shipping":
            suggestions = [
                {
                    "category": "Shipping",
                    "suggestion": "Choose ground shipping over air freight",
                    "co2_reduction": "60-80%",
                    "impact": "High"
                },
                {
                    "category": "Shipping",
                    "suggestion": "Consolidate orders to reduce shipping frequency",
                    "co2_reduction": "30-50%",
                    "impact": "Medium"
                }
            ]
        elif params["focus_area"] == "packaging":
            suggestions = [
                {
                    "category": "Packaging",
                    "suggestion": "Select minimal packaging options",
                    "co2_reduction": "70-90%",
                    "impact": "High"
                },
                {
                    "category": "Packaging",
                    "suggestion": "Choose eco-friendly packaging materials",
                    "co2_reduction": "40-60%",
                    "impact": "Medium"
                }
            ]
        else:
            suggestions = [
                {
                    "category": "General",
                    "suggestion": "Choose products with eco-certifications",
                    "co2_reduction": "20-40%",
                    "impact": "Medium"
                },
                {
                    "category": "General",
                    "suggestion": "Support local manufacturers when possible",
                    "co2_reduction": "15-30%",
                    "impact": "Medium"
                }
            ]
        
        return suggestions
    
    def _format_co2_calculation_response(self, co2_data: Dict[str, Any], params: Dict[str, Any]) -> str:
        """Format CO2 calculation response."""
        response = f"🌍 **CO2 Emission Calculation**\n\n"
        
        # Show product name if available
        if co2_data.get("product_name"):
            response += f"**Product**: {co2_data['product_name'].title()}\n"
        
        response += f"**Total CO2 Emissions**: {co2_data['total_co2']:.1f} kg CO2 ({co2_data['rating']} Impact)\n\n"
        
        response += "📊 **Breakdown by Source**:\n"
        for source, data in co2_data["breakdown"].items():
            response += f"• **{source.title()}**: {data['co2']:.1f} kg CO2 ({data['percentage']:.1f}%)\n"
        
        response += f"\n🌱 **Environmental Context**:\n"
        response += f"• Equivalent to driving {co2_data['equivalent']['miles_driven']:.1f} miles\n"
        response += f"• Would need {co2_data['equivalent']['trees_needed']:.1f} trees to offset\n"
        response += f"• Equal to {co2_data['equivalent']['days_electricity']:.1f} days of home electricity\n\n"
        
        if co2_data["rating"] in ["High", "Very High"]:
            response += "💡 **Reduction Tips**:\n"
            response += "• Consider eco-friendly alternatives\n"
            response += "• Choose ground shipping over air\n"
            response += "• Select minimal packaging options\n"
        
        return response
    
    def _format_co2_comparison_response(self, comparison_results: List[Dict[str, Any]]) -> str:
        """Format CO2 comparison response."""
        response = "🔄 **CO2 Emission Comparison**\n\n"
        
        for i, result in enumerate(comparison_results, 1):
            item = result["item"]
            co2_data = result["co2_data"]
            
            response += f"**Option {i}**: {item.get('shipping_method', 'Unknown')} Shipping\n"
            response += f"• Total CO2: {co2_data['total_co2']:.1f} kg\n"
            response += f"• Rating: {co2_data['rating']}\n\n"
        
        # Find the most eco-friendly option
        best_option = min(comparison_results, key=lambda r: r["co2_data"]["total_co2"])
        best_index = comparison_results.index(best_option) + 1
        
        response += f"🏆 **Most Eco-Friendly**: Option {best_index} with {best_option['co2_data']['total_co2']:.1f} kg CO2 emissions!"
        
        return response
    
    def _format_environmental_analysis_response(self, analysis: Dict[str, Any]) -> str:
        """Format environmental analysis response."""
        response = f"📈 **Environmental Analysis**\n\n"
        response += f"**Overall Impact**: {analysis['overall_impact']}\n"
        response += f"**Sustainability Score**: {analysis['sustainability_score']}/10\n"
        response += f"**Improvement Potential**: {analysis['improvement_potential']}\n\n"
        
        response += "🔍 **Key Environmental Factors**:\n"
        for factor in analysis["key_factors"]:
            response += f"• {factor}\n"
        
        response += "\n💡 **Recommendations**:\n"
        for rec in analysis["recommendations"]:
            response += f"• {rec}\n"
        
        return response
    
    def _format_sustainability_suggestions_response(self, suggestions: List[Dict[str, Any]]) -> str:
        """Format sustainability suggestions response."""
        response = "🌱 **Sustainability Suggestions**\n\n"
        
        for suggestion in suggestions:
            response += f"**{suggestion['category']}**: {suggestion['suggestion']}\n"
            response += f"• CO2 Reduction: {suggestion['co2_reduction']}\n"
            response += f"• Impact: {suggestion['impact']}\n\n"
        
        response += "💡 These suggestions can help you reduce your environmental impact while shopping!"
        
        return response
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task assigned to this agent."""
        task_type = task.get("type", "unknown")
        
        if task_type == "calculate_co2":
            return await self._execute_co2_calculation_task(task)
        elif task_type == "compare_co2":
            return await self._execute_co2_comparison_task(task)
        elif task_type == "analyze_environmental_impact":
            return await self._execute_environmental_analysis_task(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _execute_co2_calculation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CO2 calculation task."""
        params = task.get("parameters", {})
        co2_data = await self._calculate_co2_emissions(params)
        
        return {
            "co2_data": co2_data,
            "parameters": params
        }
    
    async def _execute_co2_comparison_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CO2 comparison task."""
        items = task.get("items", [])
        comparison_results = []
        
        for item in items:
            co2_data = await self._calculate_co2_emissions(item)
            comparison_results.append({
                "item": item,
                "co2_data": co2_data
            })
        
        return {
            "comparison_results": comparison_results,
            "best_option": min(comparison_results, key=lambda r: r["co2_data"]["total_co2"])
        }
    
    async def _execute_environmental_analysis_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute environmental analysis task."""
        params = task.get("parameters", {})
        analysis = await self._perform_environmental_analysis(params)
        
        return {
            "analysis": analysis,
            "parameters": params
        }
