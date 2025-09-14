"""
Comparison MCP Server

This MCP server provides comparison-specific functionality including:
- Fetching products for comparison
- Analyzing product data
- Providing comparison insights
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

class ComparisonMCPServer:
    """MCP Server for product comparison functionality"""
    
    def __init__(self, boutique_mcp_server=None):
        """
        Initialize the Comparison MCP Server
        
        Args:
            boutique_mcp_server: Reference to the boutique MCP server for product data
        """
        self.boutique_mcp_server = boutique_mcp_server
        logger.info("ComparisonMCPServer initialized")
    
    async def get_products_for_comparison(
        self, 
        comparison_type: str = "all",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get products for comparison analysis
        
        Args:
            comparison_type: Type of comparison (all, electronics, clothing, accessories, home)
            limit: Maximum number of products to return
        
        Returns:
            Dictionary containing products and metadata
        """
        try:
            logger.info(f"Fetching products for {comparison_type} comparison")
            
            # Get products from boutique MCP server
            if not self.boutique_mcp_server:
                return {
                    "success": False,
                    "error": "Boutique MCP server not available",
                    "products": []
                }
            
            # Search for products
            products = await self.boutique_mcp_server.search_products("")
            
            if not products:
                return {
                    "success": False,
                    "error": "Failed to fetch products from boutique",
                    "products": []
                }
            
            # Filter products based on comparison type
            if comparison_type != "all":
                filtered_products = self._filter_products_by_category(products, comparison_type)
            else:
                filtered_products = products
            
            # Limit results
            limited_products = filtered_products[:limit]
            
            return {
                "success": True,
                "products": limited_products,
                "total_count": len(limited_products),
                "comparison_type": comparison_type,
                "metadata": {
                    "fetched_at": asyncio.get_event_loop().time(),
                    "source": "boutique_mcp_server"
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching products for comparison: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "products": []
            }
    
    def _filter_products_by_category(self, products: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """Filter products by category"""
        category_keywords = {
            "electronics": ["watch", "hairdryer"],
            "clothing": ["tank top", "loafers"],
            "accessories": ["sunglasses", "watch"],
            "home": ["candle holder", "salt", "pepper", "bamboo", "mug"]
        }
        
        keywords = category_keywords.get(category.lower(), [])
        if not keywords:
            return products
        
        filtered = []
        for product in products:
            product_name = product.get("name", "").lower()
            if any(keyword in product_name for keyword in keywords):
                filtered.append(product)
        
        return filtered
    
    async def analyze_comparison_criteria(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze products to determine available comparison criteria
        
        Args:
            products: List of products to analyze
        
        Returns:
            Analysis of available comparison criteria
        """
        try:
            if not products:
                return {
                    "success": False,
                    "error": "No products to analyze",
                    "criteria": {}
                }
            
            # Analyze price range
            prices = []
            eco_scores = []
            co2_emissions = []
            
            for product in products:
                try:
                    # Parse price
                    price_str = product.get("price", "$0")
                    price = float(price_str.replace("$", "").replace(",", ""))
                    prices.append(price)
                    
                    # Parse eco score
                    eco_score_str = product.get("eco_score", "0/10")
                    eco_score = float(eco_score_str.split("/")[0])
                    eco_scores.append(eco_score)
                    
                    # Parse CO2 emissions
                    co2_str = product.get("co2_emissions", "0kg")
                    co2_match = co2_str.split("kg")[0] if "kg" in co2_str else "0"
                    co2_emissions.append(float(co2_match))
                    
                except (ValueError, TypeError):
                    continue
            
            if not prices:
                return {
                    "success": False,
                    "error": "No valid product data found",
                    "criteria": {}
                }
            
            # Calculate criteria availability
            criteria = {
                "eco_value": {
                    "available": len(prices) > 1 and any(p > 0 for p in prices),
                    "description": "Eco-score per dollar spent",
                    "products_count": len(prices)
                },
                "co2_efficiency": {
                    "available": len(co2_emissions) > 1 and any(p > 0 for p in prices),
                    "description": "CO2 emissions per dollar spent",
                    "products_count": len(co2_emissions)
                },
                "price_optimization": {
                    "available": len(prices) > 1,
                    "description": "Best value for eco-conscious shopping",
                    "products_count": len(prices)
                },
                "comprehensive": {
                    "available": len(prices) > 1 and len(eco_scores) > 1 and len(co2_emissions) > 1,
                    "description": "Multi-criteria analysis",
                    "products_count": min(len(prices), len(eco_scores), len(co2_emissions))
                }
            }
            
            # Add statistics
            stats = {
                "price_range": {
                    "min": min(prices),
                    "max": max(prices),
                    "average": sum(prices) / len(prices)
                },
                "eco_score_range": {
                    "min": min(eco_scores) if eco_scores else 0,
                    "max": max(eco_scores) if eco_scores else 0,
                    "average": sum(eco_scores) / len(eco_scores) if eco_scores else 0
                },
                "co2_range": {
                    "min": min(co2_emissions) if co2_emissions else 0,
                    "max": max(co2_emissions) if co2_emissions else 0,
                    "average": sum(co2_emissions) / len(co2_emissions) if co2_emissions else 0
                }
            }
            
            return {
                "success": True,
                "criteria": criteria,
                "statistics": stats,
                "total_products": len(products)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing comparison criteria: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "criteria": {}
            }
    
    async def get_comparison_insights(self, comparison_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights from comparison results
        
        Args:
            comparison_result: Result from comparison analysis
        
        Returns:
            Enhanced insights and recommendations
        """
        try:
            if not comparison_result.get("success", False):
                return {
                    "success": False,
                    "error": "Invalid comparison result",
                    "insights": []
                }
            
            rankings = comparison_result.get("rankings", [])
            comparison_type = comparison_result.get("comparison_type", "unknown")
            
            if not rankings:
                return {
                    "success": False,
                    "error": "No rankings available",
                    "insights": []
                }
            
            insights = []
            
            # Generate type-specific insights
            if comparison_type == "eco_value":
                insights.extend(self._generate_eco_value_insights(rankings))
            elif comparison_type == "co2_efficiency":
                insights.extend(self._generate_co2_efficiency_insights(rankings))
            elif comparison_type == "price_optimization":
                insights.extend(self._generate_price_optimization_insights(rankings))
            elif comparison_type == "comprehensive":
                insights.extend(self._generate_comprehensive_insights(rankings))
            
            # Add general insights
            insights.extend(self._generate_general_insights(rankings))
            
            return {
                "success": True,
                "insights": insights,
                "comparison_type": comparison_type,
                "total_products_analyzed": len(rankings)
            }
            
        except Exception as e:
            logger.error(f"Error generating comparison insights: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "insights": []
            }
    
    def _generate_eco_value_insights(self, rankings: List[Dict[str, Any]]) -> List[str]:
        """Generate eco-value specific insights"""
        insights = []
        
        if len(rankings) >= 2:
            best = rankings[0]
            worst = rankings[-1]
            
            insights.append(f"🏆 **Best Eco-Value**: {best['name']} offers {best.get('eco_value', 0):.3f} eco-points per dollar")
            insights.append(f"📊 **Value Gap**: {best['name']} provides {best.get('eco_value', 0) / worst.get('eco_value', 1):.1f}x better eco-value than {worst['name']}")
        
        return insights
    
    def _generate_co2_efficiency_insights(self, rankings: List[Dict[str, Any]]) -> List[str]:
        """Generate CO2 efficiency specific insights"""
        insights = []
        
        if len(rankings) >= 2:
            best = rankings[0]
            worst = rankings[-1]
            
            insights.append(f"🌍 **Most Efficient**: {best['name']} emits only {best.get('co2_efficiency', 0):.2f}kg CO2 per dollar")
            insights.append(f"💡 **Efficiency Difference**: {best['name']} is {worst.get('co2_efficiency', 1) / best.get('co2_efficiency', 1):.1f}x more CO2-efficient than {worst['name']}")
        
        return insights
    
    def _generate_price_optimization_insights(self, rankings: List[Dict[str, Any]]) -> List[str]:
        """Generate price optimization specific insights"""
        insights = []
        
        if len(rankings) >= 2:
            best = rankings[0]
            worst = rankings[-1]
            
            insights.append(f"💰 **Best Value**: {best['name']} at ${best['price']:.2f} offers optimal price-sustainability balance")
            insights.append(f"📈 **Value Score**: {best['name']} scores {best.get('value_score', 0):.3f} vs {worst['name']}'s {worst.get('value_score', 0):.3f}")
        
        return insights
    
    def _generate_comprehensive_insights(self, rankings: List[Dict[str, Any]]) -> List[str]:
        """Generate comprehensive analysis insights"""
        insights = []
        
        if len(rankings) >= 2:
            best = rankings[0]
            worst = rankings[-1]
            
            insights.append(f"🎯 **Top Performer**: {best['name']} leads in comprehensive sustainability analysis")
            insights.append(f"📊 **Composite Score**: {best['name']} scores {best.get('composite_score', 0):.3f} vs {worst['name']}'s {worst.get('composite_score', 0):.3f}")
        
        return insights
    
    def _generate_general_insights(self, rankings: List[Dict[str, Any]]) -> List[str]:
        """Generate general insights applicable to all comparison types"""
        insights = []
        
        if len(rankings) >= 3:
            # Price analysis
            prices = [p['price'] for p in rankings]
            price_range = max(prices) - min(prices)
            insights.append(f"💰 **Price Range**: ${min(prices):.2f} - ${max(prices):.2f} (${price_range:.2f} spread)")
            
            # Eco-score analysis
            eco_scores = [p['eco_score'] for p in rankings]
            avg_eco_score = sum(eco_scores) / len(eco_scores)
            insights.append(f"🌱 **Average Eco-Score**: {avg_eco_score:.1f}/10 across all products")
            
            # CO2 analysis
            co2_emissions = [p['co2_emissions'] for p in rankings]
            total_co2 = sum(co2_emissions)
            insights.append(f"🌍 **Total CO2 Impact**: {total_co2:.1f}kg across all products")
        
        return insights
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for this MCP server"""
        try:
            # Basic health checks
            status = "healthy"
            issues = []
            
            # Check if boutique MCP server is available
            if not self.boutique_mcp_server:
                status = "unhealthy"
                issues.append("Boutique MCP server not available")
            
            return {
                "server_name": "ComparisonMCPServer",
                "status": status,
                "issues": issues,
                "capabilities": [
                    "product_comparison",
                    "criteria_analysis",
                    "insights_generation"
                ],
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Health check failed for ComparisonMCPServer: {str(e)}")
            return {
                "server_name": "ComparisonMCPServer",
                "status": "unhealthy",
                "issues": [str(e)],
                "capabilities": [],
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get server metrics"""
        return {
            "server_name": "ComparisonMCPServer",
            "status": "healthy",
            "capabilities": [
                "product_comparison",
                "criteria_analysis",
                "insights_generation"
            ],
            "timestamp": asyncio.get_event_loop().time()
        }
