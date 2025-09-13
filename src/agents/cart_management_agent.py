"""
Cart Management Agent for CO2-Aware Shopping Assistant

This agent specializes in intelligent cart operations, CO2-aware suggestions,
and cart state management with environmental consciousness.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
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
            if session_id not in self.cart_sessions:
                self.cart_sessions[session_id] = {
                    "items": [],
                    "created_at": datetime.now(),
                    "last_updated": datetime.now(),
                    "total_value": 0.0,
                    "total_co2": 0.0
                }
            
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
        
        if any(word in message_lower for word in ["add", "put", "include"]):
            return "add"
        elif any(word in message_lower for word in ["remove", "delete", "take out"]):
            return "remove"
        elif any(word in message_lower for word in ["update", "change", "modify", "quantity"]):
            return "update"
        elif any(word in message_lower for word in ["view", "show", "see", "cart", "items"]):
            return "view"
        elif any(word in message_lower for word in ["clear", "empty", "remove all"]):
            return "clear"
        elif any(word in message_lower for word in ["suggest", "recommend", "optimize", "improve"]):
            return "suggest"
        else:
            return "general"
    
    async def _handle_add_to_cart(self, message: str, session_id: str) -> str:
        """Handle add to cart requests."""
        try:
            # Extract product information
            product_info = await self._extract_product_info(message)
            
            if not product_info:
                return "I need more information to add an item to your cart. Please specify the product name, ID, or description."
            
            # Get product details (mock implementation)
            product_details = await self._get_product_details(product_info)
            
            if not product_details:
                return f"I couldn't find the product '{product_info}'. Please check the product name or try a different search term."
            
            # Add to cart
            cart_item = await self._add_item_to_cart(product_details, session_id)
            
            # Calculate updated cart totals
            cart_totals = await self._calculate_cart_totals(session_id)
            
            # Format response
            response = self._format_add_to_cart_response(cart_item, cart_totals)
            
            return response
            
        except Exception as e:
            logger.error("Add to cart failed", error=str(e))
            return "I encountered an error while adding the item to your cart. Please try again."
    
    async def _handle_remove_from_cart(self, message: str, session_id: str) -> str:
        """Handle remove from cart requests."""
        try:
            # Extract item identifier
            item_identifier = await self._extract_item_identifier(message)
            
            if not item_identifier:
                return "I need to know which item to remove from your cart. Please specify the product name or ID."
            
            # Remove from cart
            removed_item = await self._remove_item_from_cart(item_identifier, session_id)
            
            if not removed_item:
                return f"I couldn't find '{item_identifier}' in your cart. Please check the item name or ID."
            
            # Calculate updated cart totals
            cart_totals = await self._calculate_cart_totals(session_id)
            
            # Format response
            response = self._format_remove_from_cart_response(removed_item, cart_totals)
            
            return response
            
        except Exception as e:
            logger.error("Remove from cart failed", error=str(e))
            return "I encountered an error while removing the item from your cart. Please try again."
    
    async def _handle_update_cart(self, message: str, session_id: str) -> str:
        """Handle cart update requests."""
        try:
            # Extract update parameters
            update_params = await self._extract_update_parameters(message)
            
            if not update_params:
                return "I need more information to update your cart. Please specify the item and the changes you'd like to make."
            
            # Update cart item
            updated_item = await self._update_cart_item(update_params, session_id)
            
            if not updated_item:
                return f"I couldn't find the item to update. Please check the item name or ID."
            
            # Calculate updated cart totals
            cart_totals = await self._calculate_cart_totals(session_id)
            
            # Format response
            response = self._format_update_cart_response(updated_item, cart_totals)
            
            return response
            
        except Exception as e:
            logger.error("Cart update failed", error=str(e))
            return "I encountered an error while updating your cart. Please try again."
    
    async def _handle_view_cart(self, message: str, session_id: str) -> str:
        """Handle view cart requests."""
        try:
            # Get cart contents
            cart_contents = await self._get_cart_contents(session_id)
            
            if not cart_contents["items"]:
                return "Your cart is empty. Would you like to browse some eco-friendly products?"
            
            # Calculate cart totals
            cart_totals = await self._calculate_cart_totals(session_id)
            
            # Format response
            response = self._format_view_cart_response(cart_contents, cart_totals)
            
            return response
            
        except Exception as e:
            logger.error("View cart failed", error=str(e))
            return "I encountered an error while retrieving your cart. Please try again."
    
    async def _handle_clear_cart(self, message: str, session_id: str) -> str:
        """Handle clear cart requests."""
        try:
            # Clear cart
            await self._clear_cart(session_id)
            
            return "🛒 Your cart has been cleared. You can start fresh with eco-friendly products!"
            
        except Exception as e:
            logger.error("Clear cart failed", error=str(e))
            return "I encountered an error while clearing your cart. Please try again."
    
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
        
        # Look for product names (words after "add" or similar)
        words = message.lower().split()
        add_indicators = ["add", "put", "include"]
        
        for i, word in enumerate(words):
            if word in add_indicators and i + 1 < len(words):
                # Take next few words as product name
                product_words = words[i + 1:i + 4]
                return " ".join(product_words)
        
        return None
    
    async def _extract_item_identifier(self, message: str) -> Optional[str]:
        """Extract item identifier for removal."""
        import re
        
        # Look for product IDs
        id_match = re.search(r'[A-Z0-9]{6,}', message)
        if id_match:
            return id_match.group(0)
        
        # Look for product names
        words = message.lower().split()
        remove_indicators = ["remove", "delete", "take out"]
        
        for i, word in enumerate(words):
            if word in remove_indicators and i + 1 < len(words):
                product_words = words[i + 1:i + 4]
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
        # Mock product database
        mock_products = [
            {
                "id": "ECO-LAPTOP-001",
                "name": "Eco-Friendly Laptop",
                "price": 899.99,
                "category": "electronics",
                "co2_emissions": 45.5,
                "eco_score": 8.5,
                "description": "Energy-efficient laptop made from recycled materials"
            },
            {
                "id": "GREEN-PHONE-002",
                "name": "Sustainable Smartphone",
                "price": 599.99,
                "category": "electronics",
                "co2_emissions": 32.1,
                "eco_score": 9.2,
                "description": "Phone with biodegradable components and solar charging"
            },
            {
                "id": "ORGANIC-SHIRT-003",
                "name": "Organic Cotton T-Shirt",
                "price": 29.99,
                "category": "clothing",
                "co2_emissions": 8.5,
                "eco_score": 9.5,
                "description": "100% organic cotton t-shirt with fair trade certification"
            }
        ]
        
        # Find matching product
        for product in mock_products:
            if (product_info.lower() in product["name"].lower() or 
                product_info.lower() in product["id"].lower()):
                return product
        
        return None
    
    async def _add_item_to_cart(self, product_details: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Add item to cart."""
        cart = self.cart_sessions[session_id]
        
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
        cart = self.cart_sessions[session_id]
        
        for i, item in enumerate(cart["items"]):
            if (item_identifier.lower() in item["name"].lower() or 
                item_identifier.lower() in item["product_id"].lower()):
                removed_item = cart["items"].pop(i)
                cart["last_updated"] = datetime.now()
                return removed_item
        
        return None
    
    async def _update_cart_item(self, update_params: Dict[str, Any], session_id: str) -> Optional[Dict[str, Any]]:
        """Update cart item."""
        cart = self.cart_sessions[session_id]
        
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
        """Get cart contents."""
        cart = self.cart_sessions[session_id]
        return {
            "items": cart["items"].copy(),
            "created_at": cart["created_at"],
            "last_updated": cart["last_updated"]
        }
    
    async def _clear_cart(self, session_id: str):
        """Clear cart contents."""
        cart = self.cart_sessions[session_id]
        cart["items"] = []
        cart["last_updated"] = datetime.now()
    
    async def _calculate_cart_totals(self, session_id: str) -> Dict[str, Any]:
        """Calculate cart totals including CO2 emissions."""
        cart = self.cart_sessions[session_id]
        
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
    
    def _format_add_to_cart_response(self, cart_item: Dict[str, Any], cart_totals: Dict[str, Any]) -> str:
        """Format add to cart response."""
        response = f"✅ **Added to Cart**: {cart_item['name']}\n\n"
        response += f"💰 **Price**: ${cart_item['price']:.2f}\n"
        response += f"🌍 **CO2 Impact**: {cart_item['co2_emissions']:.1f} kg CO2\n"
        response += f"⭐ **Eco Score**: {cart_item['eco_score']}/10\n"
        response += f"📦 **Quantity**: {cart_item['quantity']}\n\n"
        
        response += f"🛒 **Cart Summary**:\n"
        response += f"• Total Items: {cart_totals['item_count']}\n"
        response += f"• Total Value: ${cart_totals['total_value']:.2f}\n"
        response += f"• Total CO2: {cart_totals['total_co2']:.1f} kg ({cart_totals['eco_rating']} Impact)\n\n"
        
        if cart_totals['eco_rating'] in ['High', 'Very High']:
            response += "💡 **Tip**: Consider eco-friendly alternatives to reduce your environmental impact!"
        
        return response
    
    def _format_remove_from_cart_response(self, removed_item: Dict[str, Any], cart_totals: Dict[str, Any]) -> str:
        """Format remove from cart response."""
        response = f"🗑️ **Removed from Cart**: {removed_item['name']}\n\n"
        response += f"🛒 **Updated Cart Summary**:\n"
        response += f"• Total Items: {cart_totals['item_count']}\n"
        response += f"• Total Value: ${cart_totals['total_value']:.2f}\n"
        response += f"• Total CO2: {cart_totals['total_co2']:.1f} kg ({cart_totals['eco_rating']} Impact)\n\n"
        
        if cart_totals['item_count'] == 0:
            response += "Your cart is now empty. Would you like to browse some eco-friendly products?"
        
        return response
    
    def _format_update_cart_response(self, updated_item: Dict[str, Any], cart_totals: Dict[str, Any]) -> str:
        """Format update cart response."""
        response = f"📝 **Updated Cart Item**: {updated_item['name']}\n\n"
        response += f"📦 **New Quantity**: {updated_item['quantity']}\n"
        response += f"💰 **Item Value**: ${updated_item['price'] * updated_item['quantity']:.2f}\n"
        response += f"🌍 **CO2 Impact**: {updated_item['co2_emissions'] * updated_item['quantity']:.1f} kg CO2\n\n"
        
        response += f"🛒 **Cart Summary**:\n"
        response += f"• Total Items: {cart_totals['item_count']}\n"
        response += f"• Total Value: ${cart_totals['total_value']:.2f}\n"
        response += f"• Total CO2: {cart_totals['total_co2']:.1f} kg ({cart_totals['eco_rating']} Impact)\n"
        
        return response
    
    def _format_view_cart_response(self, cart_contents: Dict[str, Any], cart_totals: Dict[str, Any]) -> str:
        """Format view cart response."""
        response = f"🛒 **Your Shopping Cart** ({cart_totals['item_count']} items)\n\n"
        
        for i, item in enumerate(cart_contents["items"], 1):
            response += f"{i}. **{item['name']}**\n"
            response += f"   • Quantity: {item['quantity']}\n"
            response += f"   • Price: ${item['price']:.2f} each\n"
            response += f"   • CO2 Impact: {item['co2_emissions']:.1f} kg each\n"
            response += f"   • Eco Score: {item['eco_score']}/10\n\n"
        
        response += f"💰 **Cart Totals**:\n"
        response += f"• **Total Value**: ${cart_totals['total_value']:.2f}\n"
        response += f"• **Total CO2**: {cart_totals['total_co2']:.1f} kg ({cart_totals['eco_rating']} Impact)\n"
        response += f"• **Average CO2 per Item**: {cart_totals['average_co2_per_item']:.1f} kg\n\n"
        
        if cart_totals['eco_rating'] in ['High', 'Very High']:
            response += "💡 **Sustainability Tip**: Consider eco-friendly alternatives to reduce your environmental impact!"
        
        return response
    
    def _format_cart_suggestions_response(self, suggestions: List[Dict[str, Any]]) -> str:
        """Format cart suggestions response."""
        response = "🌱 **Cart Optimization Suggestions**\n\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. **{suggestion['title']}**\n"
            response += f"   • {suggestion['description']}\n"
            response += f"   • CO2 Reduction: {suggestion['co2_reduction']}\n"
            response += f"   • Impact: {suggestion['impact']}\n\n"
        
        response += "💡 These suggestions can help you reduce your environmental impact while shopping!"
        
        return response
    
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
