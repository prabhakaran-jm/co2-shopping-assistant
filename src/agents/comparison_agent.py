"""
Intelligent Product Comparison Agent

This agent provides sophisticated product comparison capabilities including:
- Multi-criteria analysis (eco-value, CO2 efficiency, price optimization)
- Cross-category comparisons
- Smart ranking algorithms
- Visual comparison charts
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

@dataclass
class ComparisonCriteria:
    """Defines comparison criteria and weights"""
    eco_value_weight: float = 0.4  # Eco-score per dollar
    co2_efficiency_weight: float = 0.3  # CO2 per dollar
    price_weight: float = 0.2  # Price optimization
    eco_score_weight: float = 0.1  # Raw eco-score

class ComparisonAgent(BaseAgent):
    """Intelligent product comparison agent"""
    
    def __init__(self, comparison_mcp_server=None):
        super().__init__(
            name="ComparisonAgent",
            description="Intelligent product comparison agent with multi-criteria analysis",
            instruction="You are an intelligent product comparison agent that analyzes products using multiple criteria including eco-value, CO2 efficiency, price optimization, and comprehensive analysis."
        )
        self.criteria = ComparisonCriteria()
        self.comparison_mcp_server = comparison_mcp_server
        logger.info("ComparisonAgent initialized")
    
    async def process_request(self, request: Dict[str, Any]) -> str:
        """
        Main processing method called by HostAgent
        
        Args:
            request: Request dictionary containing message and context
        
        Returns:
            Formatted response string
        """
        try:
            message = request.get("message", "")
            context = request.get("context", {})
            
            logger.info(f"Processing comparison request: {message}")
            
            # Extract comparison type from message
            comparison_type = self._extract_comparison_type(message)
            
            # Get products for comparison
            if self.comparison_mcp_server:
                products_result = await self.comparison_mcp_server.get_products_for_comparison(
                    comparison_type="all",
                    limit=10
                )
                
                if not products_result.get("success", False):
                    return f"❌ **Comparison Error**: {products_result.get('error', 'Failed to fetch products')}"
                
                products = products_result.get("products", [])
            else:
                return "❌ **Comparison Error**: Comparison service not available"
            
            if len(products) < 2:
                return "❌ **Comparison Error**: Need at least 2 products to compare"
            
            # Perform comparison
            comparison_result = await self.compare_products(products, comparison_type)
            
            # Format response
            return self._format_comparison_response(comparison_result)
            
        except Exception as e:
            logger.error(f"Error processing comparison request: {str(e)}")
            return f"❌ **Comparison Error**: {str(e)}"
    
    def _extract_comparison_type(self, message: str) -> str:
        """Extract comparison type from user message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["eco-value", "eco value", "eco-value"]):
            return "eco_value"
        elif any(word in message_lower for word in ["co2 efficiency", "co2-efficiency", "carbon efficiency"]):
            return "co2_efficiency"
        elif any(word in message_lower for word in ["price optimization", "price-optimization", "best value", "value"]):
            return "price_optimization"
        elif any(word in message_lower for word in ["comprehensive", "overall", "complete", "full analysis"]):
            return "comprehensive"
        else:
            return "eco_value"  # Default to eco-value
    
    def _format_comparison_response(self, comparison_result: Dict[str, Any]) -> str:
        """Format comparison results into user-friendly response"""
        if not comparison_result.get("rankings"):
            return "❌ **Comparison Error**: No products available for comparison"
        
        rankings = comparison_result["rankings"]
        winner = comparison_result.get("winner")
        criteria = comparison_result.get("criteria", "Unknown")
        description = comparison_result.get("description", "")
        
        response = f"🔍 **{criteria} Analysis**\n\n"
        response += f"*{description}*\n\n"
        
        if winner:
            response += f"🏆 **Winner**: {winner['name']}\n"
            response += f"💰 **Price**: ${winner['price']:.2f}\n"
            response += f"🌱 **Eco-Score**: {winner['eco_score']}/10\n"
            response += f"🌍 **CO2 Impact**: {winner['co2_emissions']:.1f}kg\n\n"
        
        response += "📊 **Rankings**:\n\n"
        
        for i, product in enumerate(rankings[:5], 1):  # Show top 5
            response += f"**{i}. {product['name']}**\n"
            response += f"   💰 ${product['price']:.2f} | 🌱 {product['eco_score']}/10 | 🌍 {product['co2_emissions']:.1f}kg\n"
            
            # Add comparison-specific metric
            if comparison_result.get("comparison_type") == "eco_value":
                response += f"   📈 Eco-Value: {product.get('eco_value', 0):.3f}\n"
            elif comparison_result.get("comparison_type") == "co2_efficiency":
                response += f"   📈 CO2 Efficiency: {product.get('co2_efficiency', 0):.2f}kg/$\n"
            elif comparison_result.get("comparison_type") == "price_optimization":
                response += f"   📈 Value Score: {product.get('value_score', 0):.3f}\n"
            elif comparison_result.get("comparison_type") == "comprehensive":
                response += f"   📈 Composite Score: {product.get('composite_score', 0):.3f}\n"
            
            response += "\n"
        
        # Add insights
        insights = comparison_result.get("insights", [])
        if insights:
            response += "💡 **Key Insights**:\n"
            for insight in insights[:3]:  # Show top 3 insights
                response += f"• {insight}\n"
            response += "\n"
        
        # Add recommendations
        recommendations = comparison_result.get("recommendations", [])
        if recommendations:
            response += "🎯 **Recommendations**:\n"
            for rec in recommendations[:2]:  # Show top 2 recommendations
                response += f"• {rec}\n"
        
        return response
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            message: User message to process
            session_id: Session identifier
            
        Returns:
            Response dictionary
        """
        try:
            logger.info(f"Processing comparison message: {message}")
            
            # Create request format expected by process_request
            request = {
                "message": message,
                "context": {"session_id": session_id}
            }
            
            # Process the request
            response_text = await self.process_request(request)
            
            return {
                "success": True,
                "response": response_text,
                "agent": self.name,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing comparison message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name,
                "session_id": session_id
            }
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task assigned to this agent.
        
        Args:
            task: Task dictionary containing task details
            
        Returns:
            Task execution result
        """
        try:
            logger.info(f"Executing comparison task: {task}")
            
            task_type = task.get("type", "compare_products")
            parameters = task.get("parameters", {})
            
            if task_type == "compare_products":
                # Extract comparison parameters
                comparison_type = parameters.get("comparison_type", "eco_value")
                products = parameters.get("products", [])
                
                if not products:
                    # Get products from MCP server if not provided
                    if self.comparison_mcp_server:
                        products_result = await self.comparison_mcp_server.get_products_for_comparison(
                            comparison_type="all",
                            limit=10
                        )
                        products = products_result.get("products", [])
                
                if len(products) < 2:
                    return {
                        "success": False,
                        "error": "Need at least 2 products to compare",
                        "task_type": task_type
                    }
                
                # Perform comparison
                comparison_result = await self.compare_products(products, comparison_type)
                
                return {
                    "success": True,
                    "result": comparison_result,
                    "task_type": task_type,
                    "products_compared": len(products)
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}",
                    "task_type": task_type
                }
                
        except Exception as e:
            logger.error(f"Error executing comparison task: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task.get("type", "unknown")
            }
    
    async def compare_products(
        self, 
        products: List[Dict[str, Any]], 
        comparison_type: str = "eco_value",
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare products using intelligent algorithms
        
        Args:
            products: List of product dictionaries
            comparison_type: Type of comparison (eco_value, co2_efficiency, price_optimization, comprehensive)
            user_preferences: User's shopping preferences and constraints
        
        Returns:
            Comparison results with rankings, insights, and recommendations
        """
        try:
            logger.info(f"Comparing {len(products)} products using {comparison_type} criteria")
            
            # Validate and clean product data
            validated_products = self._validate_products(products)
            
            if len(validated_products) < 2:
                return self._create_error_response("Need at least 2 products to compare")
            
            # Perform comparison based on type
            if comparison_type == "eco_value":
                results = await self._compare_eco_value(validated_products)
            elif comparison_type == "co2_efficiency":
                results = await self._compare_co2_efficiency(validated_products)
            elif comparison_type == "price_optimization":
                results = await self._compare_price_optimization(validated_products)
            elif comparison_type == "comprehensive":
                results = await self._compare_comprehensive(validated_products, user_preferences)
            else:
                return self._create_error_response(f"Unknown comparison type: {comparison_type}")
            
            # Add insights and recommendations
            results["insights"] = self._generate_insights(results, comparison_type)
            results["recommendations"] = self._generate_recommendations(results, user_preferences)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in product comparison: {str(e)}")
            return self._create_error_response(f"Comparison failed: {str(e)}")
    
    def _validate_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and clean product data"""
        validated = []
        
        for product in products:
            try:
                # Extract and validate required fields
                name = product.get('name', 'Unknown Product')
                price_str = product.get('price', '$0')
                co2_str = product.get('co2_emissions', '0kg')
                eco_score_str = product.get('eco_score', '0/10')
                
                # Parse price (remove $ and convert to float)
                price = float(price_str.replace('$', '').replace(',', ''))
                
                # Parse CO2 emissions (extract number from string like "49.0kg (Medium)")
                co2_match = co2_str.split('kg')[0] if 'kg' in co2_str else '0'
                co2_emissions = float(co2_match)
                
                # Parse eco score (extract number from string like "9/10")
                eco_score = float(eco_score_str.split('/')[0]) if '/' in eco_score_str else 0
                
                validated_product = {
                    'name': name,
                    'price': price,
                    'co2_emissions': co2_emissions,
                    'eco_score': eco_score,
                    'description': product.get('description', ''),
                    'image_url': product.get('image_url', ''),
                    'original_data': product
                }
                
                validated.append(validated_product)
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid product {product.get('name', 'Unknown')}: {str(e)}")
                continue
        
        return validated
    
    async def _compare_eco_value(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare products by eco-value (eco-score per dollar)"""
        # Calculate eco-value for each product
        for product in products:
            if product['price'] > 0:
                product['eco_value'] = product['eco_score'] / product['price']
            else:
                product['eco_value'] = 0
        
        # Sort by eco-value (higher is better)
        sorted_products = sorted(products, key=lambda p: p['eco_value'], reverse=True)
        
        return {
            "comparison_type": "eco_value",
            "criteria": "Eco-Score per Dollar Spent",
            "description": "Products ranked by environmental value for money",
            "rankings": sorted_products,
            "winner": sorted_products[0] if sorted_products else None,
            "metrics": {
                "best_eco_value": sorted_products[0]['eco_value'] if sorted_products else 0,
                "average_eco_value": sum(p['eco_value'] for p in products) / len(products),
                "eco_value_range": {
                    "min": min(p['eco_value'] for p in products),
                    "max": max(p['eco_value'] for p in products)
                }
            }
        }
    
    async def _compare_co2_efficiency(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare products by CO2 efficiency (CO2 per dollar)"""
        # Calculate CO2 efficiency for each product
        for product in products:
            if product['price'] > 0:
                product['co2_efficiency'] = product['co2_emissions'] / product['price']
            else:
                product['co2_efficiency'] = float('inf')
        
        # Sort by CO2 efficiency (lower is better)
        sorted_products = sorted(products, key=lambda p: p['co2_efficiency'])
        
        return {
            "comparison_type": "co2_efficiency",
            "criteria": "CO2 Emissions per Dollar Spent",
            "description": "Products ranked by carbon efficiency",
            "rankings": sorted_products,
            "winner": sorted_products[0] if sorted_products else None,
            "metrics": {
                "best_co2_efficiency": sorted_products[0]['co2_efficiency'] if sorted_products else 0,
                "average_co2_efficiency": sum(p['co2_efficiency'] for p in products) / len(products),
                "co2_efficiency_range": {
                    "min": min(p['co2_efficiency'] for p in products),
                    "max": max(p['co2_efficiency'] for p in products)
                }
            }
        }
    
    async def _compare_price_optimization(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare products by price optimization (best value for eco-conscious shopping)"""
        # Calculate value score combining price and eco-score
        for product in products:
            # Higher eco-score is better, lower price is better
            # Normalize eco-score (0-10 scale) and price (inverse relationship)
            eco_normalized = product['eco_score'] / 10.0
            price_normalized = 1.0 / (product['price'] + 1)  # Avoid division by zero
            
            product['value_score'] = (eco_normalized * 0.7) + (price_normalized * 0.3)
        
        # Sort by value score (higher is better)
        sorted_products = sorted(products, key=lambda p: p['value_score'], reverse=True)
        
        return {
            "comparison_type": "price_optimization",
            "criteria": "Best Value for Eco-Conscious Shopping",
            "description": "Products ranked by optimal balance of price and sustainability",
            "rankings": sorted_products,
            "winner": sorted_products[0] if sorted_products else None,
            "metrics": {
                "best_value_score": sorted_products[0]['value_score'] if sorted_products else 0,
                "average_value_score": sum(p['value_score'] for p in products) / len(products),
                "price_range": {
                    "min": min(p['price'] for p in products),
                    "max": max(p['price'] for p in products)
                }
            }
        }
    
    async def _compare_comprehensive(
        self, 
        products: List[Dict[str, Any]], 
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive comparison using multiple criteria"""
        # Calculate weighted scores
        for product in products:
            # Normalize all metrics to 0-1 scale
            eco_score_norm = product['eco_score'] / 10.0
            price_norm = 1.0 / (product['price'] + 1)  # Lower price is better
            co2_norm = 1.0 / (product['co2_emissions'] + 1)  # Lower CO2 is better
            
            # Calculate weighted composite score
            composite_score = (
                eco_score_norm * self.criteria.eco_score_weight +
                price_norm * self.criteria.price_weight +
                co2_norm * self.criteria.co2_efficiency_weight +
                (eco_score_norm / (product['price'] + 1)) * self.criteria.eco_value_weight
            )
            
            product['composite_score'] = composite_score
        
        # Sort by composite score
        sorted_products = sorted(products, key=lambda p: p['composite_score'], reverse=True)
        
        return {
            "comparison_type": "comprehensive",
            "criteria": "Multi-Criteria Analysis",
            "description": "Products ranked by comprehensive sustainability and value metrics",
            "rankings": sorted_products,
            "winner": sorted_products[0] if sorted_products else None,
            "metrics": {
                "best_composite_score": sorted_products[0]['composite_score'] if sorted_products else 0,
                "average_composite_score": sum(p['composite_score'] for p in products) / len(products),
                "criteria_weights": {
                    "eco_score": self.criteria.eco_score_weight,
                    "price": self.criteria.price_weight,
                    "co2_efficiency": self.criteria.co2_efficiency_weight,
                    "eco_value": self.criteria.eco_value_weight
                }
            }
        }
    
    def _generate_insights(self, results: Dict[str, Any], comparison_type: str) -> List[str]:
        """Generate intelligent insights from comparison results"""
        insights = []
        
        if not results.get('rankings'):
            return ["No products available for comparison"]
        
        rankings = results['rankings']
        winner = results.get('winner')
        
        if winner:
            insights.append(f"🏆 **Best Choice**: {winner['name']} leads in {results['criteria']}")
        
        # Price analysis
        prices = [p['price'] for p in rankings]
        if len(prices) > 1:
            price_range = max(prices) - min(prices)
            insights.append(f"💰 **Price Range**: ${min(prices):.2f} - ${max(prices):.2f} (${price_range:.2f} difference)")
        
        # Eco-score analysis
        eco_scores = [p['eco_score'] for p in rankings]
        if len(eco_scores) > 1:
            avg_eco_score = sum(eco_scores) / len(eco_scores)
            insights.append(f"🌱 **Eco-Score Average**: {avg_eco_score:.1f}/10 across all products")
        
        # CO2 analysis
        co2_emissions = [p['co2_emissions'] for p in rankings]
        if len(co2_emissions) > 1:
            total_co2 = sum(co2_emissions)
            insights.append(f"🌍 **Total CO2 Impact**: {total_co2:.1f}kg across all products")
        
        # Specific insights based on comparison type
        if comparison_type == "eco_value":
            best_value = winner.get('eco_value', 0) if winner else 0
            insights.append(f"💡 **Eco-Value**: Best product offers {best_value:.3f} eco-points per dollar")
        
        elif comparison_type == "co2_efficiency":
            best_efficiency = winner.get('co2_efficiency', 0) if winner else 0
            insights.append(f"💡 **CO2 Efficiency**: Most efficient product emits {best_efficiency:.2f}kg CO2 per dollar")
        
        return insights
    
    def _generate_recommendations(
        self, 
        results: Dict[str, Any], 
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if not results.get('rankings'):
            return ["Unable to generate recommendations"]
        
        rankings = results['rankings']
        winner = results.get('winner')
        
        if winner:
            recommendations.append(f"🎯 **Top Pick**: {winner['name']} - {results['description']}")
        
        # Budget-conscious recommendation
        budget_products = [p for p in rankings if p['price'] < 50]
        if budget_products:
            budget_winner = budget_products[0]
            recommendations.append(f"💵 **Budget-Friendly**: {budget_winner['name']} at ${budget_winner['price']:.2f}")
        
        # High eco-score recommendation
        high_eco_products = [p for p in rankings if p['eco_score'] >= 9]
        if high_eco_products:
            eco_winner = high_eco_products[0]
            recommendations.append(f"🌿 **Eco-Champion**: {eco_winner['name']} with {eco_winner['eco_score']}/10 eco-score")
        
        # Value recommendation
        if len(rankings) >= 3:
            mid_range = rankings[len(rankings)//2]
            recommendations.append(f"⚖️ **Balanced Choice**: {mid_range['name']} offers good balance of price and sustainability")
        
        return recommendations
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "comparison_type": "error",
            "criteria": "Error",
            "description": error_message,
            "rankings": [],
            "winner": None,
            "metrics": {},
            "insights": [f"❌ {error_message}"],
            "recommendations": ["Please try again with valid product data"]
        }
