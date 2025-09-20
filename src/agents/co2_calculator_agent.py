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
    
    async def process_message(self, message: str, session_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process CO2 calculation and environmental analysis requests.
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("Processing CO2 calculation request", message=message, session_id=session_id, context=context)
            
            # Extract product and cart context if available
            product_context = context.get("current_product_context", {}) if context else {}
            cart_context = context.get("cart_context", {}) if context else {}
            full_context = {**product_context, **cart_context}

            if full_context:
                logger.info("Using context for CO2 calculation", context=full_context)
            
            # Parse the request type
            request_type = await self._parse_co2_request_type(message, full_context)
            
            if request_type == "calculate":
                response = await self._handle_co2_calculation(message, session_id, full_context)
            elif request_type == "compare":
                response = await self._handle_co2_comparison(message, session_id, full_context)
            elif request_type == "analyze":
                response = await self._handle_environmental_analysis(message, session_id, full_context)
            elif request_type == "suggest":
                response = await self._handle_sustainability_suggestions(message, session_id, full_context)
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
            logger.error("CO2 calculation processing failed", error=str(e), session_id=session_id, exc_info=True)
            response_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(success=False, response_time=response_time)
            
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "error": str(e),
                "agent": self.name
            }
    
    async def _parse_co2_request_type(self, message: str, product_context: Dict[str, Any] = None) -> str:
        """Parse the type of CO2-related request with improved accuracy."""
        message_lower = message.lower()
        
        # More specific keywords first to avoid misclassification
        if any(word in message_lower for word in ["suggest", "recommend", "alternative", "eco", "green", "tips"]):
            logger.info("Parsed request type as 'suggest'")
            return "suggest"
        elif any(word in message_lower for word in ["compare", "comparison", "vs", "versus", "difference", "better"]):
            logger.info("Parsed request type as 'compare'")
            return "compare"
        elif any(word in message_lower for word in ["analyze", "impact", "environmental", "sustainability"]):
            logger.info("Parsed request type as 'analyze'")
            return "analyze"
        elif any(word in message_lower for word in ["calculate", "co2", "emission", "carbon", "footprint"]):
            logger.info("Parsed request type as 'calculate'")
            return "calculate"
        
        # Context-based parsing as a fallback
        if product_context and any(word in message_lower for word in ["this", "that", "it", "the product", "the item"]):
            if any(word in message_lower for word in ["co2", "carbon", "emission", "environmental", "impact"]):
                logger.info("Parsed request type as 'analyze' from context")
                return "analyze"
            elif any(word in message_lower for word in ["add", "cart", "buy", "purchase"]):
                logger.info("Parsed request type as 'calculate' from context")
                return "calculate"
        
        logger.info("Parsed request type as 'general'")
        return "general"
    
    async def _handle_co2_calculation(self, message: str, session_id: str, product_context: Dict[str, Any] = None) -> str:
        """Handle CO2 calculation requests, delegating to general inquiry if no parameters are found."""
        try:
            calc_params = await self._extract_calculation_parameters(message, product_context)
            
            # Check if any calculation-specific parameters were found.
            # If not, it's likely a general question that was mis-routed.
            is_general_query = not any([
                calc_params.get("product_name"),
                calc_params.get("product_type"),
                calc_params.get("price"),
                calc_params.get("shipping_method"),
                calc_params.get("shipping_distance"),
            ])

            if is_general_query:
                logger.info("No calculation parameters found, delegating to general inquiry.")
                return await self._handle_general_co2_inquiry(message, session_id)

            co2_data = await self._calculate_co2_emissions(calc_params)
            
            response = await self._format_co2_calculation_response(co2_data, calc_params)
            
            return response
            
        except Exception as e:
            logger.error("CO2 calculation failed", error=str(e), exc_info=True)
            return "I encountered an error while calculating CO2 emissions. Please try again with more specific details."
    
    async def _handle_co2_comparison(self, message: str, session_id: str, context: Dict[str, Any] = None) -> str:
        """Handle CO2 comparison requests."""
        try:
            logger.info("Handling CO2 comparison", context=context)
            comparison_params = await self._extract_comparison_parameters(message, context)
            
            if len(comparison_params.get("items", [])) < 2:
                return "I need at least 2 items to compare. Please specify them."

            comparison_results = []
            for item in comparison_params["items"]:
                co2_data = await self._calculate_co2_emissions(item)
                comparison_results.append({"item": item, "co2_data": co2_data})
            
            return await self._format_co2_comparison_response(comparison_results, message)

        except Exception as e:
            logger.error("CO2 comparison failed", error=str(e), exc_info=True)
            return "I encountered an error while comparing CO2 emissions."

    async def _handle_environmental_analysis(self, message: str, session_id: str, context: Dict[str, Any] = None) -> str:
        """Handle environmental analysis requests."""
        try:
            logger.info("Handling environmental analysis", context=context)
            analysis_params = await self._extract_analysis_parameters(message, context)
            analysis_results = await self._perform_environmental_analysis(analysis_params)
            return await self._format_environmental_analysis_response(analysis_results)

        except Exception as e:
            logger.error("Environmental analysis failed", error=str(e), exc_info=True)
            return "I encountered an error during the environmental analysis."

    async def _handle_sustainability_suggestions(self, message: str, session_id: str, context: Dict[str, Any] = None) -> str:
        """Handle sustainability suggestion requests."""
        try:
            logger.info("Handling sustainability suggestions", context=context)
            suggestion_params = await self._extract_suggestion_parameters(message, context)
            suggestions = await self._generate_sustainability_suggestions(suggestion_params)
            return await self._format_sustainability_suggestions_response(suggestions)

        except Exception as e:
            logger.error("Sustainability suggestions failed", error=str(e), exc_info=True)
            return "I encountered an error while generating sustainability suggestions."
    
    async def _handle_general_co2_inquiry(self, message: str, session_id: str) -> str:
        """Handle general CO2-related inquiries using Gemini AI."""
        try:
            prompt = f"""
            Act as a friendly and knowledgeable CO2 Calculator Agent.
            The user asked: '{message}'.
            
            Provide a conversational, informative, and engaging response that:
            - Explains your purpose (CO2 calculation, environmental analysis)
            - Highlights your key capabilities (calculations, comparisons, suggestions)
            - Includes a fun or interesting CO2/sustainability fact.
            - Encourages the user to ask a more specific question.
            """
            
            ai_response = await self._llm_generate_text(self.instruction, prompt)
            
            if not ai_response:
                raise ValueError("AI response was empty")

            return ai_response

        except Exception as e:
            logger.error("AI-powered general inquiry failed", error=str(e))
            return "I'm sorry, but I encountered an error while processing your request. Please try again."
    
    async def _extract_calculation_parameters(self, message: str, product_context: Dict[str, Any] = None) -> Dict[str, Any]:
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
        
        # Use product context if available
        if product_context:
            params["product_name"] = product_context.get("name")
            params["product_type"] = product_context.get("type")
            params["price"] = product_context.get("price")
            logger.info("Using product context for CO2 calculation", params=params)
        
        # First, try to extract product name from the message (override context if found)
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
    
    def _get_mock_products(self) -> List[Dict[str, Any]]:
        """Return the mock product database."""
        return [
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

    async def _get_product_by_name(self, product_name: str) -> Optional[Dict[str, Any]]:
        """Get actual product data from the catalog."""
        mock_products = self._get_mock_products()
        
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
    
    async def _extract_comparison_parameters(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract product names from comparison queries."""
        import re

        params = {
            "items": [],
            "comparison_criteria": ["total_co2", "manufacturing", "shipping"]
        }

        message_lower = message.lower()
        product_names = [p["name"].lower() for p in self._get_mock_products()]

        # Handle "between X and Y" format
        match = re.search(r"between\s+(.*?)\s+and\s+(.*)", message_lower)
        if match:
            product1 = match.group(1).strip()
            product2 = match.group(2).strip()
            logger.info(f"Regex 'between X and Y' matched. Group 1: '{product1}', Group 2: '{product2}'")
            logger.info(f"Product names from mock DB: {product_names}")

            product1_found = product1 in product_names
            product2_found = product2 in product_names
            logger.info(f"Validation results: product1_found={product1_found}, product2_found={product2_found}")

            # Validate that these are real products
            if product1_found and product2_found:
                params["items"] = [{"product_name": product1}, {"product_name": product2}]
                logger.info(f"Found products for comparison using 'between X and Y' pattern: {[product1, product2]}")
                return params
            else:
                logger.warning("Products from 'between X and Y' regex not found in product list.", product1=product1, product2=product2)

        # Use regex to find all occurrences of product names in the message
        found_products = []
        for product_name in product_names:
            if re.search(r'\b' + re.escape(product_name) + r'\b', message_lower):
                found_products.append(product_name)

        if len(found_products) >= 2:
            params["items"] = [{ "product_name": name } for name in found_products]
            logger.info(f"Found products for comparison: {found_products}")
            return params

        # Fallback for shipping comparison
        if "ground" in message.lower() and "air" in message.lower():
            params["items"] = [
                {"shipping_method": "ground", "shipping_distance": 500},
                {"shipping_method": "air", "shipping_distance": 500}
            ]
        
        return params

    async def _extract_analysis_parameters(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract parameters for environmental analysis."""
        params = {
            "analysis_type": "general",
            "scope": "product",
            "include_recommendations": True,
            "context": context or {}
        }
        
        if "cart" in message.lower() or (context and "cart_items" in context):
            params["scope"] = "cart"
        elif "order" in message.lower():
            params["scope"] = "order"
        
        return params

    async def _extract_suggestion_parameters(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract parameters for sustainability suggestions."""
        params = {
            "suggestion_type": "general",
            "focus_area": None,
            "budget_constraint": None,
            "context": context or {}
        }
        
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
        """Perform environmental analysis using Gemini AI."""
        try:
            prompt = f"""
            Analyze the environmental impact based on these parameters: {json.dumps(params)}.
            Provide a JSON response with:
            - 'overall_impact': (e.g., 'Low', 'Medium', 'High')
            - 'key_factors': (a list of strings)
            - 'recommendations': (a list of actionable strings)
            - 'sustainability_score': (a float between 0 and 10)
            - 'improvement_potential': (e.g., 'Low', 'Medium', 'High')
            """
            
            ai_response = await self._llm_generate_text(self.instruction, prompt)
            
            if not ai_response:
                raise ValueError("AI response was empty")

            cleaned_json = ai_response.strip().replace('`', '').replace('json', '')
            analysis = json.loads(cleaned_json)
            return analysis

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(
                "AI environmental analysis parsing failed", 
                error=str(e), 
                ai_response=ai_response
            )
        except Exception as e:
            logger.error("AI-powered environmental analysis failed", error=str(e))

        # Fallback to a default response with an error message
        return {
            "error": "Failed to perform environmental analysis.",
            "overall_impact": "Unknown",
            "key_factors": [],
            "recommendations": [],
            "sustainability_score": 0,
            "improvement_potential": "Unknown"
        }
    
    async def _generate_sustainability_suggestions(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate sustainability suggestions using Gemini AI."""
        ai_response = None
        try:
            prompt = f"""
            Generate sustainability suggestions based on these parameters: {json.dumps(params)}.
            Provide a JSON response as a list of dictionaries, each with:
            - 'category': (e.g., 'Shipping', 'Packaging', 'General')
            - 'suggestion': (a specific, actionable suggestion)
            - 'co2_reduction': (estimated percentage or range)
            - 'impact': (e.g., 'Low', 'Medium', 'High')
            """
            
            ai_response = await self._llm_generate_text(self.instruction, prompt)
            
            if not ai_response:
                raise ValueError("AI response was empty")

            cleaned_json = ai_response.strip().replace('`', '').replace('json', '')
            suggestions = json.loads(cleaned_json)
            return suggestions

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(
                "AI sustainability suggestions parsing failed",
                error=str(e),
                ai_response=ai_response
            )
        except Exception as e:
            logger.error("AI-powered sustainability suggestions failed", error=str(e))

        # Fallback to an empty list with an error message
        return [
            {
                "error": "Failed to generate sustainability suggestions.",
                "category": "Error",
                "suggestion": "Could not generate suggestions at this time.",
                "co2_reduction": "N/A",
                "impact": "Unknown"
            }
        ]
    

    
    async def _format_co2_comparison_response(self, comparison_results: List[Dict[str, Any]], user_message: str) -> str:
        """Format CO2 comparison response with intelligent, contextual, and personalized AI-generated content."""
        ai_response = None
        try:
            prompt = f"""
            As an expert sustainability advisor, your goal is to help the user make an informed environmental decision.

            The user asked: "{user_message}"

            Here are the CO2 emission details for the options being compared:
            {json.dumps(comparison_results)}

            Please provide a personalized and contextual comparison that:
            1.  **Addresses the user directly**: Use "you" and "your".
            2.  **Provides a clear recommendation**: State which option is more eco-friendly and why.
            3.  **Explains the trade-offs**: Discuss the pros and cons of each option, considering factors like CO2 emissions, shipping speed, etc.
            4.  **Gives a relatable analogy**: Frame the CO2 savings in terms of real-world equivalents (e.g., "equivalent to charging your phone X times").
            5.  **Offers a concluding thought**: End with an encouraging message that reinforces the value of making sustainable choices.

            Your response should be in markdown format, using emojis to make it more engaging.
            """
            
            ai_response = await self._llm_generate_text(self.instruction, prompt)
            
            if not ai_response:
                raise ValueError("AI response was empty")

            return f"🔄 **CO2 Emission Comparison**\n\n{ai_response}"

        except Exception as e:
            logger.error(
                "AI-powered comparison formatting failed",
                error=str(e),
                ai_response=ai_response
            )
            return "I'm sorry, but I encountered an error while processing your request. Please try again."
    
    async def _format_environmental_analysis_response(self, analysis: Dict[str, Any]) -> str:
        """Format environmental analysis response."""
        response = f"📈 **Environmental Analysis**\n\n"
        response += f"**Overall Impact**: {analysis.get('overall_impact', 'N/A')}\n"
        response += f"**Sustainability Score**: {analysis.get('sustainability_score', 'N/A')}/10\n\n"
        
        response += "🔍 **Key Factors**:\n"
        for factor in analysis.get("key_factors", []):
            response += f"• {factor}\n"
        
        response += "\n💡 **Recommendations**:\n"
        for rec in analysis.get("recommendations", []):
            response += f"• {rec}\n"
        
        return response
    
    async def _format_sustainability_suggestions_response(self, suggestions: List[Dict[str, Any]]) -> str:
        """Format sustainability suggestions response."""
        response = "🌱 **Sustainability Suggestions**\n\n"
        
        if not suggestions:
            return response + "I couldn't generate specific suggestions right now, but choosing eco-friendly options is always a great start!"

        for suggestion in suggestions:
            response += f"**{suggestion.get('category', 'General')}**: {suggestion.get('suggestion', 'N/A')}\n"
            response += f"• CO2 Reduction: {suggestion.get('co2_reduction', 'N/A')}\n"
            response += f"• Impact: {suggestion.get('impact', 'N/A')}\n\n"
        
        response += "💡 Implementing these suggestions can significantly reduce your carbon footprint!"
        
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
    
    async def _format_co2_calculation_response(self, co2_data: Dict[str, Any], calc_params: Dict[str, Any]) -> str:
        """Format CO2 calculation response with contextual analysis from Gemini AI."""
        ai_response = None
        try:
            prompt = f"""
            Generate a user-friendly, contextual analysis of this CO2 calculation:
            - Product: {calc_params.get('product_name', 'N/A')}
            - Total CO2: {co2_data['total_co2']:.1f} kg
            - Rating: {co2_data['rating']}
            - Breakdown: {json.dumps(co2_data['breakdown'])}
            
            Your response should be a markdown-formatted string that:
            - Provides a clear, engaging summary of the CO2 impact.
            - Explains the breakdown in simple terms.
            - Offers personalized, actionable sustainability tips.
            - Includes an interesting environmental fact or comparison.
            """
            
            ai_response = await self._llm_generate_text(self.instruction, prompt)
            
            if not ai_response:
                raise ValueError("AI response was empty")

            # Combine with hardcoded data for a complete response
            response = f"🌍 **CO2 Emission Analysis**\n\n"
            response += f"**Product**: {calc_params.get('product_name', 'N/A').title()}\n"
            response += f"**Total CO2 Emissions**: {co2_data['total_co2']:.1f} kg CO2 ({co2_data['rating']} Impact)\n\n"
            response += f"{ai_response}"
            
            return response

        except Exception as e:
            logger.error(
                "AI-powered response formatting failed", 
                error=str(e), 
                ai_response=ai_response
            )
            return "I'm sorry, but I encountered an error while processing your request. Please try again."
    
    async def _execute_environmental_analysis_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute environmental analysis task."""
        params = task.get("parameters", {})
        analysis = await self._perform_environmental_analysis(params)
        
        return {
            "analysis": analysis,
            "parameters": params
        }
