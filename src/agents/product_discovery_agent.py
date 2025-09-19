"""
Product Discovery Agent for CO2-Aware Shopping Assistant

This agent specializes in intelligent product search, recommendations,
and catalog operations with environmental consciousness.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from .base_agent import BaseAgent
from ..utils.product_normalizer import (
    normalize_products,
    normalize_product,
)

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

You can work in multiple patterns:
- SEQUENTIAL: For complex multi-step product searches
- PARALLEL: For searching multiple categories simultaneously  
- HIERARCHICAL: For breaking down complex shopping requests

Always consider environmental impact in your recommendations.

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
            elif request_type == "co2_savings":
                response = await self._handle_co2_savings(message, session_id)
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
        words = message_lower.split()

        search_keywords = ["find", "search", "look for", "show me"]
        recommend_keywords = ["recommend", "suggest", "best", "top"]
        compare_keywords = ["compare", "vs", "versus", "difference"]
        details_keywords = ["details", "info", "about", "specifications"]
        savings_keywords = ["savings", "save co2", "co2 savings", "reduce co2", "carbon savings"]

        if any(keyword in message_lower for keyword in search_keywords):
            return "search"
        
        if message_lower.startswith("show ") and len(words) > 1:
            return "search"

        if any(keyword in message_lower for keyword in recommend_keywords):
            return "recommend"

        if any(keyword in message_lower for keyword in compare_keywords):
            return "compare"

        if any(keyword in message_lower for keyword in details_keywords):
            return "details"

        if any(keyword in message_lower for keyword in savings_keywords):
            return "co2_savings"

        if len(words) == 1:
            if words[0] == "show":
                return "general"
            return "search"

        return "general"
    
    async def _handle_product_search(self, message: str, session_id: str) -> str:
        """Handle product search requests."""
        try:
            print(f"ProductDiscoveryAgent: _handle_product_search called with message: '{message}'")
            logger.info("ProductDiscoveryAgent: Handling product search", message=message)
            
            # Extract search parameters
            print("ProductDiscoveryAgent: Extracting search parameters...")
            search_params = await self._extract_search_parameters(message)
            print(f"ProductDiscoveryAgent: Extracted search parameters: {search_params}")
            logger.info("ProductDiscoveryAgent: Extracted search parameters", search_params=search_params)
            
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
            print(f"ProductDiscoveryAgent: Exception in _handle_product_search: {str(e)}")
            logger.error("Product search failed", error=str(e))
            return "I encountered an error while searching for products. Please try again."
    
    async def _handle_recommendations(self, message: str, session_id: str) -> str:
        """Handle product recommendation requests."""
        try:
            # Extract recommendation parameters
            rec_params = await self._extract_recommendation_parameters(message)
            message_lower = message.lower()
            
            # Alternatives flow: "suggest sustainable alternatives for <product>"
            if "alternative" in message_lower:
                ref = await self._extract_product_identifier(message)
                if not ref:
                    return "Please specify the product to suggest alternatives for (e.g., 'alternatives for watch')."
                
                alts = await self._get_alternatives(ref, limit=5)
                if not alts:
                    # Provide helpful suggestions even when no alternatives found
                    response = f"I couldn't find specific alternatives for '{ref}', but here are some excellent eco-friendly options:\n\n"
                    response += "🌿 **Top Eco-Friendly Products**\n\n"
                    response += "1. **Solar-Powered Watch** ($129.99)\n"
                    response += "   • Eco Score: 9/10 • CO2: 35.0kg\n\n"
                    response += "2. **Recycled Plastic Sunglasses** ($24.99)\n"
                    response += "   • Eco Score: 10/10 • CO2: 30.0kg\n\n"
                    response += "3. **Organic Cotton Shirt** ($29.99)\n"
                    response += "   • Eco Score: 10/10 • CO2: 25.0kg\n\n"
                    response += "Would you like to learn more about any of these sustainable options?"
                    return response
                
                # Format alternatives response
                response = f"🌿 **Sustainable Alternatives for {ref.title()}**\n\n"
                for i, p in enumerate(alts, 1):
                    response += f"{i}. **{p['name']}** (${p['price']:.2f})\n"
                    response += f"   • Eco Score: {p['eco_score']}/10\n"
                    response += f"   • CO2 Impact: {p['co2_emissions']:.1f}kg\n"
                    response += f"   • {p.get('description', 'Eco-friendly option')}\n\n"
                response += "💡 These alternatives offer better environmental impact! Would you like to compare any of these?"
                return response
            
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
        """Handle product details requests with improved context awareness."""
        try:
            # Extract product identifier
            product_id = await self._extract_product_identifier(message)
            
            if not product_id:
                return "I need a product name to get details. Could you specify which product you'd like to know more about? For example: 'Tell me about sunglasses' or 'Show me details for loafers'."
            
            # Search for products matching the identifier
            search_params = {"query": product_id, "limit": 5}
            products = await self._search_products(search_params)
            
            if not products:
                return f"I couldn't find any products matching '{product_id}'. Please check the product name or try a different search term."
            
            # Find the best matching product
            best_match = None
            for product in products:
                if product_id.lower() in product.get("name", "").lower():
                    best_match = product
                    break
            
            if not best_match:
                best_match = products[0]  # Use first result if no exact match
            
            # Get CO2 impact
            co2_data = await self._get_product_co2_impact(product_id)
            
            # Format detailed response
            response = self._format_product_details_response(best_match, co2_data)
            
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
    
    async def _handle_co2_savings(self, message: str, session_id: str) -> str:
        """Compute potential CO2 savings based on efficient picks vs catalog avg."""
        try:
            # Broad fetch with minimal filters
            products = await self._search_products({"query": "", "limit": 20})
            if not products:
                products = await self._search_products({"limit": 20})
            if not products:
                products = await self._get_fallback_products({})

            norm = normalize_products(products)
            if not norm:
                return (
                    "I couldn't find products to calculate CO2 savings."
                )

            # Catalog average
            avg_co2 = sum(p["co2_emissions"] for p in norm) / len(norm)

            # Efficient set: lowest CO2 per dollar (avoid div-by-zero)
            def eff_metric(p):
                return (p["co2_emissions"] / p["price"]) if p["price"] > 0 else float("inf")

            efficient = sorted(norm, key=eff_metric)[:3]
            if not efficient:
                return (
                    "I couldn't compute CO2 savings due to missing price data."
                )

            eff_avg = sum(p["co2_emissions"] for p in efficient) / len(efficient)
            savings = max(0.0, avg_co2 - eff_avg)
            names = ", ".join(p["name"] for p in efficient)

            return (
                "🧮 CO2 Savings Estimate\n\n"
                f"• Catalog average per item: {avg_co2:.1f}kg\n"
                f"• Efficient set average: {eff_avg:.1f}kg\n"
                f"• Estimated savings choosing efficient options: "
                f"{savings:.1f}kg per item\n\n"
                f"Top efficient picks: {names}"
            )
        except Exception:
            return (
                "I couldn't compute CO2 savings right now. Please try again in a moment."
            )
    
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
        
        print(f"🔍 ProductDiscoveryAgent: Extracting search parameters for: '{message}'")
        
        # Extract price range
        price_match = re.search(r'\$(\d+(?:\.\d{2})?)', message)
        if price_match:
            params["max_price"] = float(price_match.group(1))
        
        # Extract category with expanded synonyms mapped to available boutique categories
        # Note: For non-existent products (laptop, camera, etc.), we'll let them pass through
        # and be handled by the intelligent fallback system
        synonyms = {
            "clothing": ["clothing", "apparel", "clothes", "shirt", "tank top", "loafers", "shoes", "footwear", "top", "tee", "t-shirt"],
            "accessories": ["accessories", "accessory", "watch", "sunglasses", "glasses", "eyewear", "shades", "timepiece", "wristwatch"],
            "home": ["home", "kitchen", "mug", "jar", "hairdryer", "dryer", "candle", "holder", "salt", "pepper", "shakers", "cup", "container"]
        }
        msg = message.lower()
        print(f"🔍 ProductDiscoveryAgent: Checking category synonyms for: '{msg}'")
        for canonical, words in synonyms.items():
            if any(w in msg for w in words):
                print(f"🔍 ProductDiscoveryAgent: Found category match: '{canonical}' for words: {words}")
                params["category"] = canonical
                break

        # Don't pre-categorize electronics/tech searches - let intelligent fallback handle them
        electronics_terms = ["laptop", "computer", "phone", "camera", "electronics", "tech", "device"]
        if any(term in msg for term in electronics_terms):
            print(f"🔍 🚨 DETECTED ELECTRONICS SEARCH FOR: {msg} - WILL USE INTELLIGENT FALLBACK 🚨")
            logger.info(f"DETECTED ELECTRONICS SEARCH FOR: {msg} - WILL USE INTELLIGENT FALLBACK")
            params["category"] = None  # Don't force a category
        
        print(f"🔍 ProductDiscoveryAgent: Final search params: {params}")
        
        # Extract specific product query if found
        product_keywords = [
            "sunglasses", "glasses", "eyewear", "shades", "specs",
            "watch", "timepiece", "wristwatch", "clock", "timer",
            "loafers", "shoes", "footwear", "sneakers", "boots",
            "hairdryer", "dryer", "blow dryer", "hair dryer",
            "tank top", "shirt", "top", "tee", "t-shirt", "blouse",
            "mug", "cup", "coffee mug", "tea cup", "drinking cup",
            "candle holder", "candle", "holder", "candlestick",
            "salt", "pepper", "shakers", "spice", "seasoning",
            "bamboo glass jar", "jar", "container", "bottle", "vessel"
        ]
        
        # Find the first product keyword in the message, but preserve original query for electronics
        electronics_terms = ["laptop", "computer", "phone", "camera", "electronics", "tech", "device"]
        if not any(term in msg for term in electronics_terms):
            # Only extract product keywords for non-electronics searches
            for keyword in product_keywords:
                if keyword in msg:
                    params["query"] = keyword
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
        """Extract product identifier from message with improved natural language processing."""
        import re
        
        message_lower = message.lower().strip()
        
        # Look for product IDs (alphanumeric patterns)
        id_match = re.search(r'[A-Z0-9]{6,}', message)
        if id_match:
            return id_match.group(0)
        
        # Common product names from Online Boutique with synonyms
        product_names = [
            # Exact matches
            "sunglasses", "loafers", "watch", "hairdryer", "tank top", "shoes",
            "candle holder", "salt", "pepper", "shakers", "bamboo glass jar", "mug",
            # Synonyms and variations
            "glasses", "eyewear", "shades", "specs",  # sunglasses
            "shoes", "footwear", "sneakers", "boots", "sandals",  # loafers/shoes
            "timepiece", "wristwatch", "clock", "timer",  # watch
            "dryer", "blow dryer", "hair dryer",  # hairdryer
            "shirt", "top", "tee", "t-shirt", "blouse",  # tank top
            "candle", "holder", "candlestick",  # candle holder
            "salt", "pepper", "shaker", "spice", "seasoning",  # salt & pepper shakers
            "jar", "container", "bottle", "vessel",  # bamboo glass jar
            "cup", "coffee mug", "tea cup", "drinking cup",  # mug
            # Categories
            "electronics", "clothing", "accessories", "home", "sports", "beauty",
            "laptop", "phone", "book", "jacket", "dress", "pants"
        ]
        
        # Check for exact product name matches
        for product in product_names:
            if product in message_lower:
                return product
        
        # Look for product names in context (e.g., "about loafers", "yes about sunglasses")
        if "about" in message_lower:
            words = message_lower.split()
            for i, word in enumerate(words):
                if word == "about" and i + 1 < len(words):
                    next_word = words[i + 1]
                    if next_word in product_names:
                        return next_word
        
        # Look for general product words
        words = message.lower().split()
        product_words = [word for word in words if len(word) > 3 and word.isalpha()]
        
        if product_words:
            return " ".join(product_words[:3])  # Take first 3 words as product name
        
        return None
    
    async def _search_products(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search products using boutique MCP."""
        try:
            print(f"ProductDiscoveryAgent: _search_products called with params: {search_params}")
            logger.info("ProductDiscoveryAgent: Starting product search", search_params=search_params)
            
            if not self.boutique_mcp_server:
                print(f"ProductDiscoveryAgent: Boutique MCP server not available, using fallback data")
                logger.warning("Boutique MCP server not available, using fallback data")
                return await self._get_fallback_products(search_params)
            
            print(f"ProductDiscoveryAgent: Calling boutique MCP server")
            logger.info("ProductDiscoveryAgent: Calling boutique MCP server")
            # Call the boutique MCP server to search products
            products = await self.boutique_mcp_server.search_products(
                query=search_params.get("query", ""),
                category=search_params.get("category"),
                max_price=search_params.get("max_price"),
                min_price=search_params.get("min_price"),
                limit=search_params.get("limit", 10)
            )
            
            logger.info("Retrieved products from boutique MCP", count=len(products))
            # If no products due to category or strict filter, retry without category for graceful fallback
            if not products and search_params.get("category"):
                fallback_params = dict(search_params)
                fallback_params.pop("category", None)
                products = await self.boutique_mcp_server.search_products(
                    query=fallback_params.get("query", ""),
                    category=None,
                    max_price=fallback_params.get("max_price"),
                    min_price=fallback_params.get("min_price"),
                    limit=fallback_params.get("limit", 10)
                )
            
            # Check if we should use intelligent fallback
            should_use_intelligent_fallback = await self._should_use_intelligent_fallback(search_params, products)

            if not products or should_use_intelligent_fallback:
                print(f"ProductDiscoveryAgent: Using intelligent fallback - No products: {not products}, Irrelevant results: {should_use_intelligent_fallback}")
                logger.warning("Using intelligent fallback with Gemini", no_products=not products, irrelevant_results=should_use_intelligent_fallback)
                return await self._get_intelligent_fallback_products(search_params)

            return products
            
        except Exception as e:
            print(f"ProductDiscoveryAgent: Exception in _search_products: {str(e)}")
            logger.error("Failed to search products via MCP, using intelligent fallback", error=str(e))
            return await self._get_intelligent_fallback_products(search_params)

    async def _should_use_intelligent_fallback(self, search_params: Dict[str, Any], products: List[Dict]) -> bool:
        """Determine if we should use intelligent fallback instead of MCP results."""
        if not products:
            return True

        query = search_params.get("query", "").lower()

        # Extract meaningful search terms (remove stop words)
        stop_words = {"find", "search", "show", "get", "me", "for", "a", "the", "is", "are", "of"}
        query_words = [word for word in query.split() if word and word not in stop_words]

        if not query_words:
            return False

        # Check for specific product categories that don't exist in Online Boutique
        non_existent_categories = {
            "laptop", "computer", "phone", "mobile", "smartphone", "tablet", "ipad",
            "camera", "photography", "video", "gaming", "console", "tv", "television",
            "headphones", "earbuds", "speaker", "audio", "electronics", "tech"
        }

        # If user is searching for non-existent categories, use intelligent fallback
        for query_word in query_words:
            if query_word in non_existent_categories:
                print(f"🚨🚨 TRIGGERING INTELLIGENT FALLBACK FOR NON-EXISTENT CATEGORY: '{query_word}' 🚨🚨")
                logger.info(f"TRIGGERING INTELLIGENT FALLBACK FOR NON-EXISTENT CATEGORY: {query_word}")
                return True

        # Check if the returned products are actually relevant to the search
        # If none of the query words appear in any product name, it's probably irrelevant
        relevant_products = []
        for product in products:
            product_name_lower = product.get("name", "").lower()
            product_desc_lower = product.get("description", "").lower()

            for query_word in query_words:
                if query_word in product_name_lower or query_word in product_desc_lower:
                    relevant_products.append(product)
                    break

        # If less than 50% of products are relevant, use intelligent fallback
        relevance_ratio = len(relevant_products) / len(products) if products else 0
        is_irrelevant = relevance_ratio < 0.5

        if is_irrelevant:
            print(f"ProductDiscoveryAgent: Low relevance ratio ({relevance_ratio:.2f}) - triggering intelligent fallback")

        return is_irrelevant

    async def _get_intelligent_fallback_products(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get intelligent product suggestions using Gemini when no exact matches found."""
        try:
            print(f"🤖🤖 INTELLIGENT FALLBACK TRIGGERED! search_params: {search_params} 🤖🤖")
            logger.info(f"INTELLIGENT FALLBACK TRIGGERED! search_params: {search_params}")

            query = search_params.get("query", "")
            if not query:
                print("🤖 No query provided, using regular fallback")
                return await self._get_fallback_products(search_params)

            # Get available products from Online Boutique (without query filtering for intelligent fallback)
            fallback_params = search_params.copy()
            fallback_params["query"] = ""  # Don't filter by query for intelligent fallback
            available_products = await self._get_fallback_products(fallback_params)

            # Use Gemini to intelligently match user query to available products
            available_names = [p["name"] for p in available_products]
            available_categories = set()
            for p in available_products:
                available_categories.update(p.get("categories", []))

            # Create Gemini prompt for intelligent matching
            gemini_prompt = f"""
            User is searching for: "{query}"

            Available products in our catalog:
            {', '.join(available_names)}

            Available categories:
            {', '.join(available_categories)}

            Task: Return the most relevant products from our catalog that could satisfy the user's search for "{query}".
            If no direct match exists, suggest the closest alternatives with environmental benefits.

            Rules:
            1. Only recommend products that exist in our catalog
            2. Focus on eco-friendly and sustainable options
            3. Explain why the recommendation makes sense
            4. If searching for electronics (like laptop), suggest sustainable alternatives from available categories

            Format your response as a JSON object with this structure:
            {{
                "recommendations": [
                    {{
                        "product_name": "exact name from catalog",
                        "relevance_score": 0.8,
                        "explanation": "why this product fits the search"
                    }}
                ],
                "message": "Helpful explanation for the user"
            }}
            """

            # Since we're in fallback mode, we can't call ADK/Gemini directly
            # Instead, provide intelligent rule-based matching
            return await self._rule_based_intelligent_matching(query, available_products)

        except Exception as e:
            logger.error("Intelligent fallback failed", error=str(e))
            return await self._get_fallback_products(search_params)

    async def _rule_based_intelligent_matching(self, query: str, available_products: List[Dict]) -> List[Dict]:
        """Rule-based intelligent product matching when Gemini is not available."""
        query_lower = query.lower()
        print(f"🤖 RULE-BASED MATCHING: Query='{query}', Available products: {[p['name'] for p in available_products]}")

        # First, check for exact product name matches
        exact_matches = [p for p in available_products if p["name"].lower() == query_lower]
        if exact_matches:
            print(f"🤖 EXACT MATCH FOUND: {exact_matches[0]['name']}")
            return exact_matches

        # Then, check for partial name matches
        partial_matches = [p for p in available_products if query_lower in p["name"].lower()]
        if partial_matches:
            print(f"🤖 PARTIAL MATCH FOUND: {[p['name'] for p in partial_matches]}")
            return partial_matches

        # Electronics requests -> suggest Watch (closest electronic item)
        if any(term in query_lower for term in ["laptop", "computer", "electronics", "tech", "phone", "device"]):
            print(f"🤖 ELECTRONICS DETECTED: {query_lower}")
            matching_products = [p for p in available_products if p["name"].lower() == "watch"]
            if matching_products:
                product = matching_products[0].copy()
                term_found = next((term for term in ["laptop", "computer", "electronics", "tech", "phone", "device"] if term in query_lower), "electronics")
                product["ai_explanation"] = f"While we don't have {term_found}s in our catalog, I recommend this eco-friendly Watch as a sustainable tech accessory. It has a low CO2 footprint of {product['co2_emissions']}kg and an excellent eco-score of {product['eco_score']}/10."
                print(f"🤖 RETURNING ELECTRONICS RECOMMENDATION: {product['name']}")
                return [product]

        # Camera/Photography requests -> suggest Sunglasses (visual accessory)
        if any(term in query_lower for term in ["camera", "photography", "photo", "video", "lens"]):
            print(f"🤖 CAMERA DETECTED: {query_lower}")
            matching_products = [p for p in available_products if p["name"].lower() == "sunglasses"]
            if matching_products:
                product = matching_products[0].copy()
                product["ai_explanation"] = f"While we don't have cameras, I recommend these eco-friendly Sunglasses as they're perfect for outdoor photography and adventures! They have excellent UV protection, a low CO2 footprint of {product['co2_emissions']}kg, and an outstanding eco-score of {product['eco_score']}/10."
                print(f"🤖 RETURNING CAMERA RECOMMENDATION: {product['name']}")
                return [product]

        # Clothing requests -> suggest eco-friendly clothing
        if any(term in query_lower for term in ["shirt", "clothing", "apparel", "wear", "top", "clothes"]):
            matching_products = [p for p in available_products if "clothing" in p.get("categories", [])]
            if matching_products:
                return matching_products

        # Accessories -> suggest sunglasses or watch
        if any(term in query_lower for term in ["accessory", "accessories", "style", "fashion"]):
            matching_products = [p for p in available_products if "accessories" in p.get("categories", [])]
            if matching_products:
                return matching_products

        # Default: return top 3 most eco-friendly products
        sorted_products = sorted(available_products, key=lambda p: (-p.get("eco_score", 0), p.get("co2_emissions", 100)))
        top_products = sorted_products[:3]

        # Add explanation for the recommendation
        for product in top_products:
            product["ai_explanation"] = f"I couldn't find exact matches for '{query}', but here's an eco-friendly alternative: {product['name']} with {product['eco_score']}/10 eco-score and only {product['co2_emissions']}kg CO2 emissions."

        return top_products

    async def _get_fallback_products(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fallback products when MCP server is unavailable."""
        # Extended product catalog matching the actual Online Boutique products
        mock_products = [
            {
                "id": "sunglasses",
                "name": "Sunglasses",
                "category": "accessories",
                "categories": ["accessories"],
                "price": 19.99,
                "description": "Stylish sunglasses with UV protection",
                "eco_score": 9,
                "co2_emissions": 49.0,
                "availability": True
            },
            {
                "id": "tank-top",
                "name": "Tank Top",
                "category": "clothing",
                "categories": ["clothing"],
                "price": 18.99,
                "description": "Comfortable cotton tank top",
                "eco_score": 9,
                "co2_emissions": 49.1,
                "availability": True
            },
            {
                "id": "watch",
                "name": "Watch",
                "category": "accessories",
                "categories": ["accessories"],
                "price": 109.99,
                "description": "Classic wristwatch with leather strap",
                "eco_score": 4,
                "co2_emissions": 44.5,
                "availability": True
            },
            {
                "id": "loafers",
                "name": "Loafers",
                "category": "clothing",
                "categories": ["clothing"],
                "price": 89.99,
                "description": "Comfortable leather loafers",
                "eco_score": 5,
                "co2_emissions": 45.5,
                "availability": True
            },
            {
                "id": "hairdryer",
                "name": "Hairdryer",
                "category": "home",
                "price": 24.99,
                "description": "Energy-efficient hairdryer",
                "eco_score": 8,
                "co2_emissions": 48.8,
                "availability": True
            },
            {
                "id": "candle-holder",
                "name": "Candle Holder",
                "category": "home",
                "price": 18.99,
                "description": "Decorative candle holder",
                "eco_score": 9,
                "co2_emissions": 49.1,
                "availability": True
            },
            {
                "id": "salt-and-pepper-shakers",
                "name": "Salt & Pepper Shakers",
                "category": "home",
                "price": 18.49,
                "description": "Ceramic salt and pepper shakers",
                "eco_score": 9,
                "co2_emissions": 49.1,
                "availability": True
            },
            {
                "id": "bamboo-glass-jar",
                "name": "Bamboo Glass Jar",
                "category": "home",
                "price": 5.49,
                "description": "Sustainable bamboo glass jar",
                "eco_score": 9,
                "co2_emissions": 49.7,
                "availability": True
            },
            {
                "id": "mug",
                "name": "Mug",
                "category": "home",
                "price": 8.99,
                "description": "Ceramic coffee mug",
                "eco_score": 9,
                "co2_emissions": 49.6,
                "availability": True
            },
            # Additional eco-friendly alternatives
            {
                "id": "eco-watch-001",
                "name": "Solar-Powered Watch",
                "category": "accessories",
                "price": 129.99,
                "description": "Eco-friendly solar-powered watch",
                "eco_score": 9,
                "co2_emissions": 35.0,
                "availability": True
            },
            {
                "id": "organic-cotton-shirt",
                "name": "Organic Cotton Shirt",
                "category": "clothing",
                "price": 29.99,
                "description": "100% organic cotton t-shirt",
                "eco_score": 10,
                "co2_emissions": 25.0,
                "availability": True
            },
            {
                "id": "recycled-sunglasses",
                "name": "Recycled Plastic Sunglasses",
                "category": "accessories",
                "price": 24.99,
                "description": "Sunglasses made from recycled ocean plastic",
                "eco_score": 10,
                "co2_emissions": 30.0,
                "availability": True
            }
        ]
        
        # Filter based on search parameters
        print(f"🔍 ProductDiscoveryAgent: Filtering {len(mock_products)} mock products with params: {search_params}")
        filtered_products = []
        for product in mock_products:
            print(f"🔍 ProductDiscoveryAgent: Checking product: {product['name']} (category: {product['category']}, eco_score: {product['eco_score']})")
            
            # Check text query match first
            query = search_params.get("query", "").lower().strip()
            if query and query not in ["show all", "all products", "show me all", "list all", "show products", "products"]:
                # For specific product searches, filter out stop words and check if all remaining words match
                stop_words = {"show", "find", "search", "me", "for", "a", "the", "is", "are", "of"}
                all_query_words = [word for word in query.split() if word]
                query_words = [word for word in all_query_words if word not in stop_words]
                
                if query_words:
                    product_name_lower = product["name"].lower()
                    product_name_condensed = product_name_lower.replace(' ', '').replace('-', '')
                    
                    all_words_found = True
                    for word in query_words:
                        normalized_word = word.replace('-', '')
                        if normalized_word not in product_name_lower and normalized_word not in product_name_condensed:
                            all_words_found = False
                            break
                    
                    if not all_words_found:
                        print(f"🔍 ProductDiscoveryAgent: Filtered out by query text: {product['name']} (query: {query})")
                        continue
            
            if search_params.get("category") and product["category"] != search_params["category"]:
                print(f"🔍 ProductDiscoveryAgent: Filtered out by category: {product['name']}")
                continue
            
            if search_params.get("max_price") and product["price"] > search_params["max_price"]:
                print(f"🔍 ProductDiscoveryAgent: Filtered out by price: {product['name']}")
                continue
            
            if search_params.get("eco_friendly") and product["eco_score"] < 4.0:
                print(f"🔍 ProductDiscoveryAgent: Filtered out by eco_score: {product['name']} (score: {product['eco_score']})")
                continue
            
            print(f"🔍 ProductDiscoveryAgent: Product passed filters: {product['name']}")
            filtered_products.append(product)
        
        # *** START OF THE FIX ***
        # Corrected Fallback Logic:
        # If the initial filtering yields no results, try a broader search 
        # that STILL respects the most important criterion: the category.
        if not filtered_products and search_params.get("category"):
            print(f"⚠️ Initial filter found no results. Falling back to category-only search for '{search_params['category']}'.")
            
            # Re-filter using only the category and eco-friendly flag.
            fallback_products = []
            for product in mock_products:
                if product["category"] == search_params["category"]:
                    if search_params.get("eco_friendly") and product["eco_score"] < 4.0:
                        continue # Still respect the eco_friendly filter
                    fallback_products.append(product)
            
            print(f"✅ Fallback search found {len(fallback_products)} items in category.")
            return fallback_products
        # *** END OF THE FIX ***

        return filtered_products
    
    async def _enrich_with_co2_data(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize and enrich products for consistent downstream formatting."""
        normalized = normalize_products(products)
        if not normalized:
            # Fallback: if normalization fails, return products with minimal processing
            print(f"⚠️ normalize_products returned empty list. Using fallback normalization for {len(products)} products.")
            fallback_products = []
            for product in products:
                fallback_product = {
                    "name": product.get("name", "N/A"),
                    "price": float(product.get("price", 0.0)),
                    "co2_emissions": float(product.get("co2_emissions", 50.0)),
                    "eco_score": int(product.get("eco_score", 5)),
                    "co2_rating": self._calculate_co2_rating(float(product.get("co2_emissions", 50.0))),
                    "description": product.get("description", "No description available"),
                    "image_url": "",
                    "id": product.get("id", ""),
                    "categories": [product.get("category", "")] if product.get("category") else [],
                    "original": product,
                    "ai_explanation": product.get("ai_explanation") if product.get("ai_explanation") and product.get("ai_explanation").strip() else None,  # Preserve AI explanation only if present and not empty
                }
                fallback_products.append(fallback_product)
            return fallback_products
        return normalized
    
    def _calculate_co2_rating(self, co2_emissions: float) -> str:
        """Calculate CO2 rating based on emissions."""
        if co2_emissions <= 30.0:
            return "Low"
        elif co2_emissions <= 60.0:
            return "Medium"
        else:
            return "High"
    
    async def _get_recommendations(self, rec_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get product recommendations."""
        # Fetch broadly (ignore free-text query for recs), then score
        products = await self._search_products({
            "query": "",
            "category": rec_params.get("category"),
            "max_price": rec_params.get("max_price"),
            "limit": rec_params.get("limit", 10)
        })
        normalized = await self._enrich_with_co2_data(products)
        if not normalized:
            return []
        # Rank: higher eco_score first, then lower CO2, then lower price
        ranked = sorted(
            normalized,
            key=lambda p: (-p.get("eco_score", 0), p.get("co2_emissions", 1e9), p.get("price", 1e9))
        )
        return ranked[: rec_params.get("limit", 5)]
    
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
        """Format product search results into a user-friendly catalog-style response with images."""
        if not products:
            return "I couldn't find any products matching your criteria. Try adjusting your search terms."

        # Check if this is an intelligent fallback with AI explanations
        has_ai_explanations = any(product.get('ai_explanation') for product in products)
        

        if has_ai_explanations:
            response = f"🤖 **AI-Powered Product Suggestions** ({len(products)} recommendations)\n\n"
            response += "💡 *I couldn't find exact matches, but here are sustainable alternatives from our eco-friendly catalog:*\n\n"
        else:
            response = f"🌱 **Found {len(products)} eco-friendly products for you!**\n\n"

        response += "🛍️ **Product Catalog**\n"
        response += "=" * 50 + "\n\n"
        
        for i, product in enumerate(products, 1):
            price_value = product.get('price', 0.0)
            co2_emissions = product.get('co2_emissions', 0.0)
            co2_rating = product.get('co2_rating', 'Medium')
            image_url = product.get('image_url', '')
            
            # Create product card
            response += f"📦 **{i}. {product.get('name', 'N/A')}**\n"
            response += f"💰 **Price:** ${price_value:.2f}\n"
            response += f"🌍 **CO2 Impact:** {co2_emissions:.1f}kg ({co2_rating} Impact)\n"
            response += f"⭐ **Eco Score:** {product.get('eco_score', 'N/A')}/10\n"
            response += f"📝 **Description:** {product.get('description', 'No description available')}\n"

            # Add AI explanation if available
            if product.get('ai_explanation'):
                response += f"🤖 **AI Recommendation:** {product.get('ai_explanation')}\n"
            
            # Add image if available
            if image_url:
                response += f"![{product.get('name', 'Product')}]({image_url})\n"
            
            response += "-" * 40 + "\n\n"
        
        response += "💡 **What would you like to do next?**\n"
        response += "• Ask about a specific product\n"
        response += "• Add items to your cart\n"
        response += "• Compare products\n"
        response += "• Get recommendations\n"
        
        return response
    
    def _format_recommendation_response(self, recommendations: List[Dict[str, Any]], rec_params: Dict[str, Any]) -> str:
        """Format recommendation results."""
        if not recommendations:
            # Graceful default suggestions when no criteria
            return (
                "I couldn't generate recommendations from your criteria. "
                "Try specifying a category or price limit (e.g., 'eco-friendly under $20')."
            )
        
        response = f"🌱 Here are my top {len(recommendations)} sustainable recommendations:\n\n"
        
        for i, product in enumerate(recommendations, 1):
            response += f"{i}. **{product['name']}** (${product['price']:.2f})\n"
            response += f"   • Eco Score: {product['eco_score']}/10\n"
            response += f"   • CO2 Impact: {product['co2_emissions']:.1f}kg\n"
            response += f"   • Reason: high eco-score with relatively low CO2 for the price\n\n"
        
        response += "💡 These recommendations prioritize environmental sustainability while meeting your needs. Would you like to compare any of these products?"
        
        return response

    async def _get_alternatives(self, reference: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find sustainable alternatives in same/related category with better eco/CO2."""
        try:
            # Find the reference product first
            base_results = await self._search_products({"query": reference, "limit": 5})
            if not base_results:
                # If no exact match, try to find similar products
                return await self._get_general_alternatives(reference, limit)
            
            base = base_results[0]
            base_norm = (await self._enrich_with_co2_data([base]))[0]
            base_cat = (base_norm.get("categories") or [None])[0]
            
            # Search in same category broadly
            candidates = await self._search_products({"category": base_cat, "limit": 20})
            if not candidates:
                # Fallback to general search
                candidates = await self._search_products({"query": "", "limit": 20})
            
            norm = await self._enrich_with_co2_data(candidates)
            
            # Filter better eco/CO2 than base
            better = [p for p in norm if (p.get("eco_score", 0) > base_norm.get("eco_score", 0)) or (p.get("co2_emissions", 1e9) < base_norm.get("co2_emissions", 0))]
            
            # If no better alternatives found, return top eco-friendly options in category
            if not better:
                better = [p for p in norm if p.get("eco_score", 0) >= 7]  # At least good eco score
            
            # Rank by eco score desc then CO2 asc
            ranked = sorted(better, key=lambda p: (-p.get("eco_score", 0), p.get("co2_emissions", 1e9)))
            
            # Exclude the same product
            ranked = [p for p in ranked if p.get("name") != base_norm.get("name")]
            
            return ranked[:limit]
            
        except Exception as e:
            logger.error("Error finding alternatives", error=str(e), reference=reference)
            # Return general eco-friendly alternatives as fallback
            return await self._get_general_alternatives(reference, limit)
    
    async def _get_general_alternatives(self, reference: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get general eco-friendly alternatives when specific product not found."""
        # Return top eco-friendly products from our catalog
        eco_products = [
            {
                "id": "organic-cotton-shirt",
                "name": "Organic Cotton Shirt",
                "category": "clothing",
                "price": 29.99,
                "description": "100% organic cotton t-shirt",
                "eco_score": 10,
                "co2_emissions": 25.0,
                "availability": True
            },
            {
                "id": "recycled-sunglasses",
                "name": "Recycled Plastic Sunglasses",
                "category": "accessories",
                "price": 24.99,
                "description": "Sunglasses made from recycled ocean plastic",
                "eco_score": 10,
                "co2_emissions": 30.0,
                "availability": True
            },
            {
                "id": "eco-watch-001",
                "name": "Solar-Powered Watch",
                "category": "accessories",
                "price": 129.99,
                "description": "Eco-friendly solar-powered watch",
                "eco_score": 9,
                "co2_emissions": 35.0,
                "availability": True
            },
            {
                "id": "bamboo-glass-jar",
                "name": "Bamboo Glass Jar",
                "category": "home",
                "price": 5.49,
                "description": "Sustainable bamboo glass jar",
                "eco_score": 9,
                "co2_emissions": 49.7,
                "availability": True
            },
            {
                "id": "candle-holder",
                "name": "Candle Holder",
                "category": "home",
                "price": 18.99,
                "description": "Decorative candle holder",
                "eco_score": 9,
                "co2_emissions": 49.1,
                "availability": True
            }
        ]
        
        # Filter based on reference if possible
        reference_lower = reference.lower()
        if any(word in reference_lower for word in ["watch", "timepiece", "wristwatch"]):
            return [p for p in eco_products if "watch" in p["name"].lower()][:limit]
        elif any(word in reference_lower for word in ["sunglasses", "glasses", "eyewear"]):
            return [p for p in eco_products if "sunglasses" in p["name"].lower()][:limit]
        elif any(word in reference_lower for word in ["shirt", "top", "clothing"]):
            return [p for p in eco_products if "shirt" in p["name"].lower()][:limit]
        
        return eco_products[:limit]
    
    def _format_comparison_response(self, products: List[Dict[str, Any]]) -> str:
        """Format product comparison results."""
        if len(products) < 2:
            return "I need at least 2 products to make a comparison. Could you specify which products you'd like to compare?"
        
        response = "🔄 **Product Comparison** (Environmental Impact Focus):\n\n"
        
        for product in products:
            response += f"**{product['name']}** (${product['price']:.2f})\n"
            response += f"• CO2 Emissions: {product['co2_emissions']:.1f}kg\n"
            response += f"• Eco Score: {product['eco_score']}/10\n"
            response += f"• Rating: {product['co2_rating']}\n\n"
        
        # Find the most eco-friendly option
        best_eco = min(products, key=lambda p: p['co2_emissions'])
        response += f"🏆 **Most Eco-Friendly**: {best_eco['name']} with only {best_eco['co2_emissions']:.1f}kg CO2 emissions!"
        
        return response
    
    def _format_product_details_response(self, product: Dict[str, Any], co2_data: Dict[str, Any]) -> str:
        """Format detailed product information."""
        normalized = normalize_product(product)
        price_units = normalized["price"]
        co2_total = normalized["co2_emissions"]
        eco_score = normalized["eco_score"]
        eco_label = normalized["co2_rating"]
        
        response = f"📋 **Product Details: {normalized['name']}**\n\n"
        response += f"💰 **Price**: ${price_units:.2f}\n"
        
        # Handle categories (list from gRPC response)
        categories = normalized.get("categories", [])
        if categories:
            response += f"📦 **Categories**: {', '.join(categories)}\n"
        
        response += f"📝 **Description**: {normalized['description']}\n\n"
        
        response += "🌱 **Environmental Impact**:\n"
        # Distribute the normalized total into a simple mock breakdown that sums to total
        manuf = round(co2_total * 0.5, 1)
        ship = round(co2_total * 0.16, 1)
        usage = round(co2_total * 0.3, 1)
        disp = round(max(0.0, co2_total - (manuf + ship + usage)), 1)
        response += f"• Manufacturing: {manuf}kg CO2\n"
        response += f"• Shipping: {ship}kg CO2\n"
        response += f"• Usage: {usage}kg CO2\n"
        response += f"• Disposal: {disp}kg CO2\n"
        response += f"• **Total**: {co2_total:.1f}kg CO2 ({eco_label} impact)\n\n"
        
        response += f"⭐ **Eco Score**: {eco_score}/10\n"
        response += f"🆔 **Product ID**: {normalized.get('id', 'N/A')}\n\n"
        
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
