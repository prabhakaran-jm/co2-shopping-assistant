"""
CO2 Data MCP Server for CO2-Aware Shopping Assistant

This MCP server provides environmental impact calculations,
CO2 emission data, and sustainability metrics.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import structlog
import httpx

logger = structlog.get_logger(__name__)


class CO2MCPServer:
    """
    MCP Server for CO2 and environmental impact data.
    
    This server provides:
    - CO2 emission calculations
    - Environmental impact scoring
    - Sustainability metrics
    - Carbon footprint analysis
    """
    
    def __init__(self, co2_data_api_url: str = "https://api.carbonintensity.org.uk"):
        """
        Initialize the CO2 MCP Server.
        
        Args:
            co2_data_api_url: Base URL for CO2 data API
        """
        self.co2_data_api_url = co2_data_api_url
        self.running = False
        
        # HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # CO2 emission factors (kg CO2 per unit)
        self.emission_factors = {
            "manufacturing": {
                "electronics": 25.0,  # kg CO2 per $100
                "clothing": 15.0,
                "books": 5.0,
                "home": 20.0,
                "sports": 18.0,
                "beauty": 12.0,
                "automotive": 50.0,
                "food": 8.0,
                "furniture": 22.0,
                "toys": 10.0
            },
            "shipping": {
                "ground": 0.5,      # kg CO2 per mile
                "air": 2.0,
                "sea": 0.1,
                "rail": 0.3,
                "express": 2.5,
                "standard": 0.5,
                "eco_friendly": 0.3
            },
            "packaging": {
                "standard": 0.5,     # kg CO2 per package
                "eco_friendly": 0.2,
                "minimal": 0.1,
                "biodegradable": 0.15,
                "recycled": 0.25
            },
            "energy": {
                "electricity": 0.4,  # kg CO2 per kWh
                "natural_gas": 0.2,  # kg CO2 per kWh
                "renewable": 0.05    # kg CO2 per kWh
            }
        }
        
        # Material impact factors
        self.material_factors = {
            "recycled_plastic": 0.3,
            "virgin_plastic": 1.0,
            "organic_cotton": 0.4,
            "conventional_cotton": 1.0,
            "bamboo": 0.2,
            "wood": 0.6,
            "metal": 1.2,
            "glass": 0.8,
            "paper": 0.5,
            "leather": 1.5
        }
        
        logger.info("CO2 MCP Server initialized", api_url=co2_data_api_url)
    
    async def start(self):
        """Start the MCP server."""
        self.running = True
        
        # Test connectivity to CO2 data API
        await self._test_connectivity()
        
        logger.info("CO2 MCP Server started")
    
    async def stop(self):
        """Stop the MCP server."""
        self.running = False
        await self.client.aclose()
        logger.info("CO2 MCP Server stopped")
    
    async def _test_connectivity(self):
        """Test connectivity to CO2 data API."""
        try:
            # Test with a simple API call
            response = await self.client.get(f"{self.co2_data_api_url}/intensity", timeout=5.0)
            if response.status_code == 200:
                logger.info("CO2 data API connectivity test passed")
            else:
                logger.warning("CO2 data API connectivity test failed", status=response.status_code)
        except Exception as e:
            logger.warning("CO2 data API connectivity test failed", error=str(e))
    
    # Product CO2 Calculations
    
    async def calculate_product_co2(
        self,
        product_data: Dict[str, Any],
        include_lifecycle: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate CO2 emissions for a product.
        
        Args:
            product_data: Product information including price, category, materials
            include_lifecycle: Whether to include full lifecycle emissions
            
        Returns:
            CO2 calculation results
        """
        try:
            co2_data = {
                "product_id": product_data.get("id"),
                "product_name": product_data.get("name"),
                "manufacturing_co2": 0.0,
                "shipping_co2": 0.0,
                "packaging_co2": 0.0,
                "usage_co2": 0.0,
                "disposal_co2": 0.0,
                "total_co2": 0.0,
                "breakdown": {},
                "rating": "Unknown",
                "equivalent": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Manufacturing CO2
            category = product_data.get("category", "general")
            price = product_data.get("price", 0.0)
            
            if category in self.emission_factors["manufacturing"]:
                factor = self.emission_factors["manufacturing"][category]
                co2_data["manufacturing_co2"] = (price / 100) * factor
                
                # Apply material factors
                materials = product_data.get("materials", [])
                material_factor = 1.0
                for material in materials:
                    if material in self.material_factors:
                        material_factor *= self.material_factors[material]
                
                co2_data["manufacturing_co2"] *= material_factor
            
            # Packaging CO2
            packaging_type = product_data.get("packaging_type", "standard")
            if packaging_type in self.emission_factors["packaging"]:
                co2_data["packaging_co2"] = self.emission_factors["packaging"][packaging_type]
            
            # Usage CO2 (for electronics)
            if category == "electronics":
                usage_hours = product_data.get("usage_hours_per_day", 8)
                lifespan_years = product_data.get("lifespan_years", 3)
                power_consumption = product_data.get("power_consumption_watts", 50)
                
                # Convert to kWh and calculate CO2
                total_kwh = (power_consumption / 1000) * usage_hours * 365 * lifespan_years
                co2_data["usage_co2"] = total_kwh * self.emission_factors["energy"]["electricity"]
            
            # Disposal CO2
            disposal_method = product_data.get("disposal_method", "landfill")
            if disposal_method == "recycling":
                co2_data["disposal_co2"] = co2_data["manufacturing_co2"] * 0.1  # 10% of manufacturing
            elif disposal_method == "incineration":
                co2_data["disposal_co2"] = co2_data["manufacturing_co2"] * 0.2  # 20% of manufacturing
            else:  # landfill
                co2_data["disposal_co2"] = co2_data["manufacturing_co2"] * 0.05  # 5% of manufacturing
            
            # Calculate total
            co2_data["total_co2"] = (
                co2_data["manufacturing_co2"] +
                co2_data["packaging_co2"] +
                co2_data["usage_co2"] +
                co2_data["disposal_co2"]
            )
            
            # Create breakdown
            if co2_data["total_co2"] > 0:
                co2_data["breakdown"] = {
                    "manufacturing": {
                        "co2": co2_data["manufacturing_co2"],
                        "percentage": (co2_data["manufacturing_co2"] / co2_data["total_co2"]) * 100
                    },
                    "packaging": {
                        "co2": co2_data["packaging_co2"],
                        "percentage": (co2_data["packaging_co2"] / co2_data["total_co2"]) * 100
                    },
                    "usage": {
                        "co2": co2_data["usage_co2"],
                        "percentage": (co2_data["usage_co2"] / co2_data["total_co2"]) * 100
                    },
                    "disposal": {
                        "co2": co2_data["disposal_co2"],
                        "percentage": (co2_data["disposal_co2"] / co2_data["total_co2"]) * 100
                    }
                }
            
            # Determine rating
            co2_data["rating"] = self._get_co2_rating(co2_data["total_co2"])
            
            # Add equivalents
            co2_data["equivalent"] = self._calculate_equivalents(co2_data["total_co2"])
            
            logger.info("Product CO2 calculated", product_id=product_data.get("id"), total_co2=co2_data["total_co2"])
            return co2_data
            
        except Exception as e:
            logger.error("Product CO2 calculation failed", error=str(e))
            return {"error": str(e)}
    
    async def calculate_shipping_co2(
        self,
        shipping_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate CO2 emissions for shipping.
        
        Args:
            shipping_data: Shipping information including method, distance, weight
            
        Returns:
            Shipping CO2 calculation results
        """
        try:
            method = shipping_data.get("method", "ground")
            distance = shipping_data.get("distance_miles", 500)
            weight = shipping_data.get("weight_kg", 1.0)
            
            # Base CO2 per mile
            if method in self.emission_factors["shipping"]:
                base_co2_per_mile = self.emission_factors["shipping"][method]
            else:
                base_co2_per_mile = self.emission_factors["shipping"]["ground"]
            
            # Calculate total CO2
            total_co2 = distance * base_co2_per_mile * weight
            
            # Add packaging CO2
            packaging_type = shipping_data.get("packaging_type", "standard")
            packaging_co2 = self.emission_factors["packaging"].get(packaging_type, 0.5)
            
            shipping_co2_data = {
                "method": method,
                "distance_miles": distance,
                "weight_kg": weight,
                "base_co2": total_co2,
                "packaging_co2": packaging_co2,
                "total_co2": total_co2 + packaging_co2,
                "co2_per_mile": base_co2_per_mile,
                "rating": self._get_co2_rating(total_co2 + packaging_co2),
                "equivalent": self._calculate_equivalents(total_co2 + packaging_co2),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Shipping CO2 calculated", method=method, distance=distance, total_co2=shipping_co2_data["total_co2"])
            return shipping_co2_data
            
        except Exception as e:
            logger.error("Shipping CO2 calculation failed", error=str(e))
            return {"error": str(e)}
    
    async def calculate_cart_co2(
        self,
        cart_data: Dict[str, Any],
        shipping_method: str = "ground"
    ) -> Dict[str, Any]:
        """
        Calculate total CO2 emissions for a shopping cart.
        
        Args:
            cart_data: Cart contents with items
            shipping_method: Shipping method to use
            
        Returns:
            Cart CO2 calculation results
        """
        try:
            items = cart_data.get("items", [])
            
            cart_co2_data = {
                "items_co2": 0.0,
                "shipping_co2": 0.0,
                "packaging_co2": 0.0,
                "total_co2": 0.0,
                "item_breakdown": [],
                "rating": "Unknown",
                "equivalent": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Calculate CO2 for each item
            for item in items:
                item_co2 = await self.calculate_product_co2(item)
                if "total_co2" in item_co2:
                    cart_co2_data["items_co2"] += item_co2["total_co2"]
                    cart_co2_data["item_breakdown"].append({
                        "product_id": item.get("id"),
                        "name": item.get("name"),
                        "co2": item_co2["total_co2"],
                        "rating": item_co2.get("rating", "Unknown")
                    })
            
            # Calculate shipping CO2
            shipping_data = {
                "method": shipping_method,
                "distance_miles": 500,  # Default distance
                "weight_kg": len(items) * 1.0  # Estimate weight
            }
            shipping_co2 = await self.calculate_shipping_co2(shipping_data)
            cart_co2_data["shipping_co2"] = shipping_co2.get("total_co2", 0.0)
            
            # Calculate packaging CO2
            cart_co2_data["packaging_co2"] = len(items) * self.emission_factors["packaging"]["standard"]
            
            # Calculate total
            cart_co2_data["total_co2"] = (
                cart_co2_data["items_co2"] +
                cart_co2_data["shipping_co2"] +
                cart_co2_data["packaging_co2"]
            )
            
            # Determine rating
            cart_co2_data["rating"] = self._get_co2_rating(cart_co2_data["total_co2"])
            
            # Add equivalents
            cart_co2_data["equivalent"] = self._calculate_equivalents(cart_co2_data["total_co2"])
            
            logger.info("Cart CO2 calculated", items_count=len(items), total_co2=cart_co2_data["total_co2"])
            return cart_co2_data
            
        except Exception as e:
            logger.error("Cart CO2 calculation failed", error=str(e))
            return {"error": str(e)}
    
    # Environmental Impact Analysis
    
    async def analyze_environmental_impact(
        self,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive environmental impact analysis.
        
        Args:
            analysis_data: Data for analysis including products, shipping, etc.
            
        Returns:
            Environmental impact analysis results
        """
        try:
            analysis = {
                "overall_impact": "Unknown",
                "key_factors": [],
                "recommendations": [],
                "sustainability_score": 0,
                "improvement_potential": "Unknown",
                "co2_breakdown": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Analyze products
            products = analysis_data.get("products", [])
            if products:
                total_product_co2 = 0
                high_impact_products = []
                
                for product in products:
                    product_co2 = await self.calculate_product_co2(product)
                    if "total_co2" in product_co2:
                        total_product_co2 += product_co2["total_co2"]
                        if product_co2["total_co2"] > 50:  # High impact threshold
                            high_impact_products.append(product.get("name", "Unknown"))
                
                analysis["co2_breakdown"]["products"] = total_product_co2
                
                if high_impact_products:
                    analysis["key_factors"].append(f"High-impact products: {', '.join(high_impact_products)}")
                    analysis["recommendations"].append("Consider eco-friendly alternatives for high-impact products")
            
            # Analyze shipping
            shipping_method = analysis_data.get("shipping_method", "ground")
            shipping_co2 = await self.calculate_shipping_co2({"method": shipping_method})
            analysis["co2_breakdown"]["shipping"] = shipping_co2.get("total_co2", 0.0)
            
            if shipping_method in ["air", "express"]:
                analysis["key_factors"].append("High-impact shipping method")
                analysis["recommendations"].append("Choose ground or eco-friendly shipping")
            
            # Calculate sustainability score
            total_co2 = sum(analysis["co2_breakdown"].values())
            if total_co2 < 50:
                analysis["sustainability_score"] = 9
                analysis["overall_impact"] = "Very Low"
            elif total_co2 < 100:
                analysis["sustainability_score"] = 7
                analysis["overall_impact"] = "Low"
            elif total_co2 < 200:
                analysis["sustainability_score"] = 5
                analysis["overall_impact"] = "Medium"
            elif total_co2 < 400:
                analysis["sustainability_score"] = 3
                analysis["overall_impact"] = "High"
            else:
                analysis["sustainability_score"] = 1
                analysis["overall_impact"] = "Very High"
            
            # Determine improvement potential
            if analysis["sustainability_score"] < 5:
                analysis["improvement_potential"] = "High"
                analysis["recommendations"].extend([
                    "Choose eco-friendly products",
                    "Select sustainable shipping options",
                    "Consider minimal packaging"
                ])
            elif analysis["sustainability_score"] < 7:
                analysis["improvement_potential"] = "Medium"
                analysis["recommendations"].append("Minor adjustments can further reduce environmental impact")
            else:
                analysis["improvement_potential"] = "Low"
                analysis["recommendations"].append("Excellent environmental choices!")
            
            logger.info("Environmental impact analysis completed", sustainability_score=analysis["sustainability_score"])
            return analysis
            
        except Exception as e:
            logger.error("Environmental impact analysis failed", error=str(e))
            return {"error": str(e)}
    
    # Sustainability Recommendations
    
    async def get_sustainability_recommendations(
        self,
        context_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get sustainability recommendations based on context.
        
        Args:
            context_data: Context information for recommendations
            
        Returns:
            List of sustainability recommendations
        """
        try:
            recommendations = []
            
            # Analyze current context
            products = context_data.get("products", [])
            shipping_method = context_data.get("shipping_method", "ground")
            budget = context_data.get("budget", 0)
            
            # Product recommendations
            if products:
                high_co2_products = []
                for product in products:
                    product_co2 = await self.calculate_product_co2(product)
                    if product_co2.get("total_co2", 0) > 50:
                        high_co2_products.append(product.get("name", "Unknown"))
                
                if high_co2_products:
                    recommendations.append({
                        "category": "Products",
                        "title": "Choose Eco-Friendly Alternatives",
                        "description": f"Consider eco-friendly alternatives for: {', '.join(high_co2_products)}",
                        "co2_reduction": "30-50%",
                        "impact": "High",
                        "cost_impact": "Minimal"
                    })
            
            # Shipping recommendations
            if shipping_method in ["air", "express"]:
                recommendations.append({
                    "category": "Shipping",
                    "title": "Switch to Ground Shipping",
                    "description": "Ground shipping has significantly lower CO2 emissions than air shipping",
                    "co2_reduction": "60-80%",
                    "impact": "High",
                    "cost_impact": "Lower cost"
                })
            
            # General recommendations
            recommendations.extend([
                {
                    "category": "Packaging",
                    "title": "Choose Minimal Packaging",
                    "description": "Select minimal or eco-friendly packaging options",
                    "co2_reduction": "70-90%",
                    "impact": "High",
                    "cost_impact": "Minimal"
                },
                {
                    "category": "General",
                    "title": "Support Sustainable Brands",
                    "description": "Look for products with eco-certifications and sustainable practices",
                    "co2_reduction": "20-40%",
                    "impact": "Medium",
                    "cost_impact": "Minimal"
                }
            ])
            
            logger.info("Sustainability recommendations generated", count=len(recommendations))
            return recommendations
            
        except Exception as e:
            logger.error("Sustainability recommendations generation failed", error=str(e))
            return []
    
    # Helper Methods
    
    def _get_co2_rating(self, co2_amount: float) -> str:
        """Get CO2 impact rating based on amount."""
        if co2_amount < 20:
            return "Very Low"
        elif co2_amount < 50:
            return "Low"
        elif co2_amount < 100:
            return "Medium"
        elif co2_amount < 200:
            return "High"
        else:
            return "Very High"
    
    def _calculate_equivalents(self, co2_amount: float) -> Dict[str, float]:
        """Calculate CO2 equivalents in understandable terms."""
        return {
            "miles_driven": co2_amount * 2.5,  # Rough conversion
            "trees_needed": co2_amount * 0.1,  # Trees to offset
            "days_electricity": co2_amount * 0.5,  # Days of home electricity
            "plastic_bottles": co2_amount * 20,  # Equivalent plastic bottles
            "car_miles": co2_amount * 0.4  # Miles driven in average car
        }
    
    # Health and Status
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the MCP server."""
        try:
            health_status = {
                "status": "healthy",
                "running": self.running,
                "emission_factors_loaded": len(self.emission_factors),
                "material_factors_loaded": len(self.material_factors),
                "timestamp": datetime.now().isoformat()
            }
            
            # Test CO2 calculation
            test_product = {
                "id": "test",
                "name": "Test Product",
                "category": "electronics",
                "price": 100.0
            }
            
            test_result = await self.calculate_product_co2(test_product)
            if "error" in test_result:
                health_status["status"] = "degraded"
                health_status["error"] = "CO2 calculation test failed"
            else:
                health_status["co2_calculation_test"] = "passed"
            
            return health_status
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get server metrics."""
        return {
            "running": self.running,
            "emission_factors": len(self.emission_factors),
            "material_factors": len(self.material_factors),
            "api_url": self.co2_data_api_url,
            "timestamp": datetime.now().isoformat()
        }
    
    def __str__(self) -> str:
        """String representation of the MCP server."""
        return f"CO2MCPServer(api_url={self.co2_data_api_url}, running={self.running})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the MCP server."""
        return (
            f"CO2MCPServer("
            f"api_url={self.co2_data_api_url}, "
            f"running={self.running}, "
            f"emission_factors={len(self.emission_factors)}"
            f")"
        )
