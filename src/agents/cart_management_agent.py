"""
Cart Management Agent for CO2-Aware Shopping Assistant

This agent specializes in intelligent cart operations, CO2-aware suggestions,
and cart state management with environmental consciousness.
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..utils import cart_store
import structlog

from .base_agent import BaseAgent

logger = structlog.get_logger(__name__)


class CartManagementAgent(BaseAgent):
    """
    Cart Management Agent that handles shopping cart operations with environmental awareness.
    
    This agent:
    - Manages cart operations (add, remove, update quantities)
    - Provides CO2-aware cart suggestions
    - Calculates cart totals including environmental impact
    - Manages session persistence and state
    """
    
    def __init__(self):
        """Initialize the Cart Management Agent."""
        super().__init__(
            name="CartManagementAgent",
            description="Intelligent cart management with environmental consciousness",
            instruction=self._get_cart_management_instruction()
        )
        
        # Cart state management
        self.cart_sessions = {}
        
        logger.info("Cart Management Agent initialized")
        
        # Simple alias map for product name variants
        self.alias_map = {
            "tanktop": "Tank Top",
            "tank top": "Tank Top",
            "candleholder": "Candle Holder",
            "candle holder": "Candle Holder",
            "bamboo jar": "Bamboo Glass Jar",
            "glass jar": "Bamboo Glass Jar",
            "jar": "Bamboo Glass Jar",
        }
    
    def _get_cart_management_instruction(self) -> str:
        """Get instruction for the cart management agent."""
        return """You are the Cart Management Agent, specialized in managing shopping carts with environmental consciousness.

Your capabilities:
1. Add, remove, and update items in the shopping cart
2. Provide CO2-aware cart suggestions and optimizations
3. Calculate cart totals including environmental impact
4. Manage cart persistence and session state
5. Suggest eco-friendly alternatives for cart items

Key principles:
- Always consider environmental impact when managing cart items
- Provide clear CO2 calculations for cart contents
- Suggest sustainable alternatives when appropriate
- Help users optimize their cart for both value and sustainability
- Maintain cart state across sessions

When managing cart operations:
- Include CO2 emission information for all items
- Suggest eco-friendly alternatives for high-impact items
- Provide clear cart totals with environmental breakdown
- Offer optimization suggestions to reduce carbon footprint
- Explain the environmental benefits of cart changes

Always help users make environmentally conscious cart decisions while meeting their shopping needs."""
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process cart management requests.
        
        Args:
            message: User's message/query
            session_id: Session identifier
            
        Returns:
            Dictionary containing the response
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("Processing cart management request", message=message, session_id=session_id)
            
            # Initialize cart session if needed
            # Ensure shared cart exists
            cart_store.get_or_create_cart(session_id)
            
            # Parse the request type
            request_type = await self._parse_cart_request_type(message)
            
            if request_type == "add":
                response = await self._handle_add_to_cart(message, session_id)
            elif request_type == "remove":
                response = await self._handle_remove_from_cart(message, session_id)
            elif request_type == "update":
                response = await self._handle_update_cart(message, session_id)
            elif request_type == "view":
                response = await self._handle_view_cart(message, session_id)
            elif request_type == "clear":
                response = await self._handle_clear_cart(message, session_id)
            elif request_type == "suggest":
                response = await self._handle_cart_suggestions(message, session_id)
            else:
                response = await self._handle_general_cart_inquiry(message, session_id)
            
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
            logger.error("Cart management processing failed", error=str(e), session_id=session_id)
            response_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(success=False, response_time=response_time)
            
            return {
                "response": "I apologize, but I encountered an error while managing your cart. Please try again.",
                "error": str(e),
                "agent": self.name
            }
    
    async def _parse_cart_request_type(self, message: str) -> str:
        """Parse the type of cart management request."""
        message_lower = message.lower()

        # Check for clear/empty first (before view patterns that contain "cart")
        if any(word in message_lower for word in ["clear", "empty", "remove all"]):
            return "clear"
        elif any(word in message_lower for word in ["add", "put", "include"]):
            return "add"
        elif any(word in message_lower for word in ["remove", "delete", "take out"]):
            return "remove"
        elif any(word in message_lower for word in ["update", "change", "modify", "quantity"]):
            return "update"
        elif any(word in message_lower for word in ["view", "show", "see", "cart", "items", "show my cart"]):
            return "view"
        elif any(word in message_lower for word in ["suggest", "recommend", "optimize", "improve"]):
            return "suggest"
        else:
            return "general"
    
    async def _handle_add_to_cart(self, message: str, session_id: str) -> str:
        """Handle add to cart requests."""
        try:
            product_info = await self._extract_product_info(message)
            if not product_info:
                return "I need more information to add an item to your cart. Please specify the product name."

            product_details = await self._get_product_details(product_info)
            if not product_details:
                return f"I couldn't find the product '{product_info}'. Please try another name."

            cart_item = await self._add_item_to_cart(product_details, session_id)
            cart_totals = await self._calculate_cart_totals(session_id)
            return await self._format_add_to_cart_response(cart_item, cart_totals)

        except Exception as e:
            logger.error("Add to cart failed", error=str(e), exc_info=True)
            return f"I encountered an error while adding the item to your cart: {str(e)}"

    async def _handle_remove_from_cart(self, message: str, session_id: str) -> str:
        """Handle remove from cart requests."""
        try:
            item_identifier = await self._extract_item_identifier(message)
            if not item_identifier:
                return "I need to know which item to remove. Please specify the product name."

            removed_item = await self._remove_item_from_cart(item_identifier, session_id)
            if not removed_item:
                return f"I couldn't find '{item_identifier}' in your cart."

            cart_totals = await self._calculate_cart_totals(session_id)
            return await self._format_remove_from_cart_response(removed_item, cart_totals)

        except Exception as e:
            logger.error("Remove from cart failed", error=str(e), exc_info=True)
            return "I encountered an error while removing the item from your cart."

    async def _handle_update_cart(self, message: str, session_id: str) -> str:
        """Handle cart update requests."""
        try:
            update_params = await self._extract_update_parameters(message)
            if not update_params:
                return "I need more information to update your cart. Please specify the item and quantity."

            updated_item = await self._update_cart_item(update_params, session_id)
            if not updated_item:
                return f"I couldn't find the item to update."

            cart_totals = await self._calculate_cart_totals(session_id)
            return await self._format_update_cart_response(updated_item, cart_totals)

        except Exception as e:
            logger.error("Cart update failed", error=str(e), exc_info=True)
            return "I encountered an error while updating your cart."

    async def _handle_view_cart(self, message: str, session_id: str) -> str:
        """Handle view cart requests."""
        try:
            logger.info(f"Handling view cart for session_id: {session_id}")
            cart_contents = await self._get_cart_contents(session_id)
            logger.info(f"Retrieved cart contents for session_id: {session_id}", cart_contents=cart_contents)

            if not cart_contents["items"]:
                return "Your cart is empty. Would you like to browse some eco-friendly products?"

            cart_totals = await self._calculate_cart_totals(session_id)
            return await self._format_view_cart_response(cart_contents, cart_totals)

        except Exception as e:
            logger.error("View cart failed", error=str(e), exc_info=True)
            return "I encountered an error while retrieving your cart."

    async def _handle_clear_cart(self, message: str, session_id: str) -> str:
        """Handle clear cart requests."""
        try:
            cart_totals = await self._calculate_cart_totals(session_id)
            await self._clear_cart(session_id)
            return await self._format_clear_cart_response(cart_totals)

        except Exception as e:
            logger.error("Clear cart failed", error=str(e), exc_info=True)
            return "I encountered an error while clearing your cart."
    
    async def _handle_cart_suggestions(self, message: str, session_id: str) -> str:
        """Handle cart suggestion requests."""
        try:
            # Get cart contents
            cart_contents = await self._get_cart_contents(session_id)
            
            if not cart_contents["items"]:
                return "Your cart is empty. I can suggest some eco-friendly products to get you started!"
            
            # Generate suggestions
            suggestions = await self._generate_cart_suggestions(cart_contents)
            
            # Format response
            response = self._format_cart_suggestions_response(suggestions)
            
            return response
            
        except Exception as e:
            logger.error("Cart suggestions failed", error=str(e))
            return "I encountered an error while generating cart suggestions. Please try again."
    
    async def _handle_general_cart_inquiry(self, message: str, session_id: str) -> str:
        """Handle general cart-related inquiries."""
        return """🛒 I'm your Cart Management Agent, here to help you manage your shopping cart with environmental consciousness!

I can help you with:
- **Add Items**: "Add this eco-friendly laptop to my cart"
- **Remove Items**: "Remove the smartphone from my cart"
- **Update Quantities**: "Change the quantity of this item to 2"
- **View Cart**: "Show me what's in my cart"
- **Cart Suggestions**: "Suggest ways to make my cart more eco-friendly"
- **Clear Cart**: "Empty my cart"

**Environmental Features**:
- CO2 emission calculations for all cart items
- Eco-friendly alternative suggestions
- Sustainability optimization recommendations
- Environmental impact breakdown

What would you like to do with your cart? I'll make sure to highlight the environmental impact of your choices! 🌱"""
    
    async def _extract_product_info(self, message: str) -> Optional[str]:
        """Extract product information from message."""
        import re
        
        # Look for product IDs (alphanumeric patterns)
        id_match = re.search(r'[A-Z0-9]{6,}', message)
        if id_match:
            return id_match.group(0)
        
        # Look for product names (after add/put/include and before 'to cart')
        msg = message.lower()
        if "to my cart" in msg:
            msg = msg.replace("to my cart", "to cart")
        if "add" in msg and "to cart" in msg:
            between = msg.split("add", 1)[1].split("to cart", 1)[0].strip()
            if between:
                return between
        # Multi-item support: split by 'and' and try first token
        if " and " in msg and "to cart" in msg:
            first = msg.split("add", 1)[1].split("to cart", 1)[0].strip().split(" and ", 1)[0].strip()
            if first:
                return first
        # Fallback: next words after add/put/include
        words = msg.split()
        add_indicators = ["add", "put", "include"]
        for i, word in enumerate(words):
            if word in add_indicators and i + 1 < len(words):
                product_words = []
                for w in words[i + 1:i + 5]:
                    if w in ["to", "cart", "my", "in", "and", ","]:
                        break
                    product_words.append(w)
                if product_words:
                    return " ".join(product_words)
        
        return None
    
    async def _extract_item_identifier(self, message: str) -> Optional[str]:
        """Extract item identifier for removal."""
        import re
        
        # Look for product IDs
        id_match = re.search(r'[A-Z0-9]{6,}', message)
        if id_match:
            return id_match.group(0)
        
        # Look for product names before 'from cart'
        msg = message.lower()
        if "from my cart" in msg:
            msg = msg.replace("from my cart", "from cart")
        if "remove" in msg and "from cart" in msg:
            between = msg.split("remove", 1)[1].split("from cart", 1)[0].strip()
            if between:
                return between
        # Fallback: next words after remove/delete/take out
        words = msg.split()
        remove_indicators = ["remove", "delete", "take out"]
        for i, word in enumerate(words):
            if word in remove_indicators and i + 1 < len(words):
                product_words = []
                for w in words[i + 1:i + 5]:
                    if w in ["from", "cart", "my", "in"]:
                        break
                    product_words.append(w)
                if product_words:
                    return " ".join(product_words)
        
        return None
    
    async def _extract_update_parameters(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract update parameters from message."""
        import re
        
        params = {
            "item_identifier": None,
            "quantity": None,
            "operation": "update"
        }
        
        # Extract quantity
        quantity_match = re.search(r'(\d+)', message)
        if quantity_match:
            params["quantity"] = int(quantity_match.group(1))
        
        # Extract item identifier
        words = message.lower().split()
        update_indicators = ["update", "change", "modify", "quantity"]
        
        for i, word in enumerate(words):
            if word in update_indicators and i + 1 < len(words):
                product_words = words[i + 1:i + 4]
                params["item_identifier"] = " ".join(product_words)
                break
        
        return params if params["item_identifier"] else None
    
    async def _get_product_details(self, product_info: str) -> Optional[Dict[str, Any]]:
        """Get product details (mock implementation)."""
        # Mock product database (Online Boutique items)
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
        
        # Normalize aliases
        info_key = (product_info or "").strip().lower()
        if info_key in self.alias_map:
            info_key = self.alias_map[info_key].lower()
        
        # Find matching product
        for product in mock_products:
            if (info_key in product["name"].lower() or 
                info_key in product["id"].lower()):
                return product
        
        return None
    
    async def _add_item_to_cart(self, product_details: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Add item to cart."""
        cart = cart_store.get_or_create_cart(session_id)
        
        # Check if item already exists in cart
        for item in cart["items"]:
            if item["product_id"] == product_details["id"]:
                item["quantity"] += 1
                item["last_updated"] = datetime.now()
                return item
        
        # Add new item
        cart_item = {
            "product_id": product_details["id"],
            "name": product_details["name"],
            "price": product_details["price"],
            "quantity": 1,
            "co2_emissions": product_details["co2_emissions"],
            "eco_score": product_details["eco_score"],
            "added_at": datetime.now(),
            "last_updated": datetime.now()
        }
        
        cart["items"].append(cart_item)
        cart["last_updated"] = datetime.now()
        
        return cart_item
    
    async def _remove_item_from_cart(self, item_identifier: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Remove item from cart."""
        cart = cart_store.get_or_create_cart(session_id)
        
        for i, item in enumerate(cart["items"]):
            if (item_identifier.lower() in item["name"].lower() or 
                item_identifier.lower() in item["product_id"].lower()):
                removed_item = cart["items"].pop(i)
                cart["last_updated"] = datetime.now()
                return removed_item
        
        return None
    
    async def _update_cart_item(self, update_params: Dict[str, Any], session_id: str) -> Optional[Dict[str, Any]]:
        """Update cart item."""
        cart = cart_store.get_or_create_cart(session_id)
        
        for item in cart["items"]:
            if (update_params["item_identifier"].lower() in item["name"].lower() or 
                update_params["item_identifier"].lower() in item["product_id"].lower()):
                
                if update_params["quantity"] is not None:
                    item["quantity"] = update_params["quantity"]
                    item["last_updated"] = datetime.now()
                    cart["last_updated"] = datetime.now()
                    return item
        
        return None
    
    async def _get_cart_contents(self, session_id: str) -> Dict[str, Any]:
        """Get cart contents with improved error handling."""
        try:
            cart = cart_store.get_or_create_cart(session_id)
            # Collapse items by product id to ensure accurate counts
            collapsed = {}
            for item in cart["items"]:
                key = item["product_id"]
                if key in collapsed:
                    collapsed[key]["quantity"] += item.get("quantity", 1)
                else:
                    collapsed[key] = item.copy()
                    if "quantity" not in collapsed[key]:
                        collapsed[key]["quantity"] = 1
            return {
                "items": list(collapsed.values()),
                "created_at": cart["created_at"],
                "last_updated": cart["last_updated"]
            }
        except Exception as e:
            logger.error("Failed to get or process cart contents", error=str(e), session_id=session_id, exc_info=True)
            # Return an empty cart structure on failure to prevent downstream errors
            return {
                "items": [],
                "created_at": datetime.now(),
                "last_updated": datetime.now()
            }
    
    async def _clear_cart(self, session_id: str):
        """Clear cart contents."""
        cart = cart_store.get_or_create_cart(session_id)
        cart["items"] = []
        cart["last_updated"] = datetime.now()
    
    async def _calculate_cart_totals(self, session_id: str) -> Dict[str, Any]:
        """Calculate cart totals including CO2 emissions."""
        cart = cart_store.get_or_create_cart(session_id)
        
        total_value = 0.0
        total_co2 = 0.0
        item_count = 0
        
        for item in cart["items"]:
            total_value += item["price"] * item["quantity"]
            total_co2 += item["co2_emissions"] * item["quantity"]
            item_count += item["quantity"]
        
        # Determine environmental rating
        if total_co2 < 50:
            eco_rating = "Very Low"
        elif total_co2 < 100:
            eco_rating = "Low"
        elif total_co2 < 200:
            eco_rating = "Medium"
        elif total_co2 < 400:
            eco_rating = "High"
        else:
            eco_rating = "Very High"
        
        return {
            "total_value": total_value,
            "total_co2": total_co2,
            "item_count": item_count,
            "eco_rating": eco_rating,
            "average_co2_per_item": total_co2 / item_count if item_count > 0 else 0
        }
    
    async def _generate_cart_suggestions(self, cart_contents: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate cart optimization suggestions."""
        suggestions = []
        
        # Analyze cart for high CO2 items
        high_co2_items = []
        for item in cart_contents["items"]:
            if item["co2_emissions"] > 30:  # High CO2 threshold
                high_co2_items.append(item)
        
        if high_co2_items:
            suggestions.append({
                "type": "eco_alternative",
                "title": "Consider Eco-Friendly Alternatives",
                "description": f"Found {len(high_co2_items)} high-impact items. Consider eco-friendly alternatives.",
                "impact": "High",
                "co2_reduction": "30-50%"
            })
        
        # Check for quantity optimization
        large_quantity_items = [item for item in cart_contents["items"] if item["quantity"] > 3]
        if large_quantity_items:
            suggestions.append({
                "type": "quantity_optimization",
                "title": "Optimize Quantities",
                "description": "Consider if you need all these quantities. Bulk buying can reduce packaging impact.",
                "impact": "Medium",
                "co2_reduction": "10-20%"
            })
        
        # General eco suggestions
        suggestions.append({
            "type": "general",
            "title": "Choose Eco-Friendly Shipping",
            "description": "Select ground shipping over air freight to reduce CO2 emissions.",
            "impact": "High",
            "co2_reduction": "60-80%"
        })
        
        return suggestions
    
    async def _format_add_to_cart_response(self, cart_item: Dict[str, Any], cart_totals: Dict[str, Any]) -> str:
        """Generate an AI-powered response for adding an item to the cart."""
        prompt = f"""
        The user just added "{cart_item['name']}" to their cart.
        The item's CO2 impact is {cart_item['co2_emissions']:.1f} kg.
        The cart now has {cart_totals['item_count']} items with a total CO2 impact of {cart_totals['total_co2']:.1f} kg.

        Generate a friendly, conversational response that:
        1. Confirms the item was added.
        2. Briefly mentions the item's environmental impact.
        3. Provides a relevant sustainability tip.
        4. Includes the cart summary (total items, total CO2).
        5. Uses emojis to be more engaging.
        """
        return await self._llm_generate_text(self.instruction, prompt) or "Item added to cart."

    async def _format_remove_from_cart_response(self, removed_item: Dict[str, Any], cart_totals: Dict[str, Any]) -> str:
        """Generate an AI-powered response for removing an item from the cart."""
        prompt = f"""
        The user just removed "{removed_item['name']}" from their cart.
        The cart now has {cart_totals['item_count']} items with a total CO2 impact of {cart_totals['total_co2']:.1f} kg.

        Generate a friendly, conversational response that:
        1. Confirms the item was removed.
        2. If the cart is not empty, provides the updated cart summary.
        3. If the cart is empty, encourages the user to find some eco-friendly products.
        4. Suggests a more sustainable alternative to the removed item.
        """
        return await self._llm_generate_text(self.instruction, prompt) or "Item removed from cart."

    async def _format_update_cart_response(self, updated_item: Dict[str, Any], cart_totals: Dict[str, Any]) -> str:
        """Generate an AI-powered response for updating a cart item."""
        prompt = f"""
        The user just updated the quantity of "{updated_item['name']}" to {updated_item['quantity']}.
        The cart now has {cart_totals['item_count']} items with a total CO2 impact of {cart_totals['total_co2']:.1f} kg.

        Generate a friendly, conversational response that:
        1. Confirms the quantity was updated.
        2. Provides the updated cart summary.
        3. Briefly analyzes the impact of the quantity change on the cart's total CO2.
        """
        return await self._llm_generate_text(self.instruction, prompt) or "Cart updated."

    def _serialize_cart_items(self, items: List[Dict[str, Any]]) -> str:
        """Serialize cart items to JSON, handling datetime objects."""
        def default_serializer(o):
            if isinstance(o, datetime):
                return o.isoformat()
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

        return json.dumps(items, default=default_serializer)

    async def _format_view_cart_response(self, cart_contents: Dict[str, Any], cart_totals: Dict[str, Any]) -> str:
        """Generate an AI-powered analysis of the user's cart."""
        prompt = f"""
        The user is viewing their cart. Here are the details:
        - Items: {self._serialize_cart_items(cart_contents['items'])}
        - Totals: {json.dumps(cart_totals)}

        Generate a comprehensive and personalized analysis of the cart that includes:
        1. A friendly and engaging opening.
        2. A summary of the cart's contents (number of items, total value).
        3. A detailed analysis of the cart's total CO2 emissions in kilograms (kg), with a relatable analogy (e.g., equivalent to driving X miles). Always use "kg" as the unit for CO2 emissions.
        4. A sustainability score for the cart.
        5. Actionable recommendations for reducing the cart's carbon footprint (e.g., suggesting alternatives for high-impact items).
        6. A concluding, encouraging message.
        
        IMPORTANT: Always express CO2 emissions in kilograms (kg), never in grams or gCO2e.
        """
        return await self._llm_generate_text(self.instruction, prompt) or "Here are the items in your cart."

    async def _format_clear_cart_response(self, cleared_cart_totals: Dict[str, Any]) -> str:
        """Generate an AI-powered response for clearing the cart."""
        prompt = f"""
        The user has cleared their cart.
        The cleared cart had a total CO2 impact of {cleared_cart_totals['total_co2']:.1f} kg.

        Generate a friendly and encouraging response that:
        1. Confirms the cart was cleared.
        2. Briefly mentions the environmental impact of the items that were in the cart.
        3. Encourages the user to start fresh with some eco-friendly product suggestions.
        """
        return await self._llm_generate_text(self.instruction, prompt) or "Your cart has been cleared."

    async def _format_cart_suggestions_response(self, suggestions: List[Dict[str, Any]]) -> str:
        """Generate an AI-powered response for cart suggestions."""
        prompt = f"""
        Here are some suggestions to make the user's cart more sustainable:
        {json.dumps(suggestions)}

        Format these suggestions into a friendly, conversational, and easy-to-read response.
        For each suggestion, explain the environmental benefit.
        """
        return await self._llm_generate_text(self.instruction, prompt) or "Here are some suggestions for your cart."
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task assigned to this agent."""
        task_type = task.get("type", "unknown")
        
        if task_type == "add_to_cart":
            return await self._execute_add_to_cart_task(task)
        elif task_type == "remove_from_cart":
            return await self._execute_remove_from_cart_task(task)
        elif task_type == "get_cart_contents":
            return await self._execute_get_cart_contents_task(task)
        elif task_type == "calculate_cart_totals":
            return await self._execute_calculate_cart_totals_task(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _execute_add_to_cart_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute add to cart task."""
        product_info = task.get("product_info")
        session_id = task.get("session_id", "default")
        
        product_details = await self._get_product_details(product_info)
        if not product_details:
            return {"error": "Product not found"}
        
        cart_item = await self._add_item_to_cart(product_details, session_id)
        cart_totals = await self._calculate_cart_totals(session_id)
        
        return {
            "cart_item": cart_item,
            "cart_totals": cart_totals
        }
    
    async def _execute_remove_from_cart_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute remove from cart task."""
        item_identifier = task.get("item_identifier")
        session_id = task.get("session_id", "default")
        
        removed_item = await self._remove_item_from_cart(item_identifier, session_id)
        if not removed_item:
            return {"error": "Item not found in cart"}
        
        cart_totals = await self._calculate_cart_totals(session_id)
        
        return {
            "removed_item": removed_item,
            "cart_totals": cart_totals
        }
    
    async def _execute_get_cart_contents_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get cart contents task."""
        session_id = task.get("session_id", "default")
        cart_contents = await self._get_cart_contents(session_id)
        
        return {
            "cart_contents": cart_contents
        }
    
    async def _execute_calculate_cart_totals_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calculate cart totals task."""
        session_id = task.get("session_id", "default")
        cart_totals = await self._calculate_cart_totals(session_id)
        
        return {
            "cart_totals": cart_totals
        }
