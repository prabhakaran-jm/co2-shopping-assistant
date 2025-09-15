"""
Checkout Agent for CO2-Aware Shopping Assistant

This agent specializes in order processing, payment coordination,
and eco-friendly shipping selection with environmental consciousness.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from .base_agent import BaseAgent

logger = structlog.get_logger(__name__)


class CheckoutAgent(BaseAgent):
    """
    Checkout Agent that handles order processing with environmental consciousness.
    
    This agent:
    - Processes orders with eco-friendly shipping selection
    - Coordinates payment and confirmation
    - Validates transactions and handles errors
    - Provides order tracking and status updates
    """
    
    def __init__(self):
        """Initialize the Checkout Agent."""
        super().__init__(
            name="CheckoutAgent",
            description="Order processing and payment coordination with environmental consciousness",
            instruction=self._get_checkout_instruction()
        )
        
        # Order management
        self.orders = {}
        self.shipping_options = {
            "ground": {
                "name": "Ground Shipping",
                "cost": 5.99,
                "co2_per_mile": 0.5,
                "eco_rating": "Low",
                "delivery_days": "3-5"
            },
            "express": {
                "name": "Express Shipping",
                "cost": 12.99,
                "co2_per_mile": 2.0,
                "eco_rating": "High",
                "delivery_days": "1-2"
            },
            "eco": {
                "name": "Eco-Friendly Shipping",
                "cost": 7.99,
                "co2_per_mile": 0.3,
                "eco_rating": "Very Low",
                "delivery_days": "4-6"
            }
        }
        
        logger.info("Checkout Agent initialized")
    
    def _get_checkout_instruction(self) -> str:
        """Get instruction for the checkout agent."""
        return """You are the Checkout Agent, specialized in processing orders with environmental consciousness.

Your capabilities:
1. Process orders with eco-friendly shipping selection
2. Coordinate payment and confirmation processes
3. Validate transactions and handle errors gracefully
4. Provide order tracking and status updates
5. Suggest sustainable shipping and packaging options

Key principles:
- Always prioritize eco-friendly shipping options
- Provide clear CO2 calculations for shipping choices
- Explain environmental benefits of sustainable options
- Ensure secure and reliable payment processing
- Maintain order accuracy and customer satisfaction

When processing orders:
- Calculate total CO2 emissions including shipping
- Suggest the most eco-friendly shipping option
- Provide clear breakdown of costs and environmental impact
- Handle payment securely and efficiently
- Generate order confirmations with tracking information

Always help users complete their purchases while minimizing environmental impact."""
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process checkout requests.
        
        Args:
            message: User's message/query
            session_id: Session identifier
            
        Returns:
            Dictionary containing the response
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("Processing checkout request", message=message, session_id=session_id)
            
            # Parse the request type
            request_type = await self._parse_checkout_request_type(message)
            
            if request_type == "checkout":
                response = await self._handle_checkout_process(message, session_id)
            elif request_type == "shipping":
                response = await self._handle_shipping_selection(message, session_id)
            elif request_type == "payment":
                response = await self._handle_payment_process(message, session_id)
            elif request_type == "order_status":
                response = await self._handle_order_status(message, session_id)
            elif request_type == "tracking":
                response = await self._handle_order_tracking(message, session_id)
            else:
                response = await self._handle_general_checkout_inquiry(message, session_id)
            
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
            logger.error("Checkout processing failed", error=str(e), session_id=session_id)
            response_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(success=False, response_time=response_time)
            
            return {
                "response": "I apologize, but I encountered an error while processing your checkout. Please try again.",
                "error": str(e),
                "agent": self.name
            }
    
    async def _parse_checkout_request_type(self, message: str) -> str:
        """Parse the type of checkout request."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["checkout", "buy", "purchase", "order", "proceed"]):
            return "checkout"
        elif any(word in message_lower for word in ["shipping", "delivery", "ship", "express", "ground"]):
            return "shipping"
        elif any(word in message_lower for word in ["payment", "pay", "card", "billing", "charge"]):
            return "payment"
        elif any(word in message_lower for word in ["status", "order status", "where is my order"]):
            return "order_status"
        elif any(word in message_lower for word in ["track", "tracking", "track my order"]):
            return "tracking"
        else:
            return "general"
    
    async def _handle_checkout_process(self, message: str, session_id: str) -> str:
        """Handle checkout process requests."""
        try:
            # Get cart contents from CartManagementAgent via Host session context, fallback to mock
            cart_contents = await self._get_cart_contents(session_id)
            
            if not cart_contents.get("items"):
                return "Your cart is empty. Please add some items before proceeding to checkout."
            
            # Calculate order totals
            order_totals = await self._calculate_order_totals(cart_contents)
            
            # Get shipping options
            shipping_options = await self._get_shipping_options(cart_contents)

            # Auto-select shipping if user said 'checkout with X'
            msg = message.lower()
            auto_pref = None
            if "checkout with" in msg:
                if "eco" in msg:
                    auto_pref = "eco"
                elif "express" in msg:
                    auto_pref = "express"
                elif "ground" in msg:
                    auto_pref = "ground"
            if auto_pref:
                try:
                    from ..utils import cart_store
                    cart_store.set_shipping(session_id, auto_pref)
                except Exception:
                    pass

            # Persist a checkout snapshot for resilience across session hops
            try:
                from ..utils import cart_store
                cart_store.set_checkout_snapshot(session_id, {
                    "items": cart_contents.get("items", []),
                    "order_totals": order_totals
                })
            except Exception:
                pass

            # Format checkout response
            response = self._format_checkout_response(order_totals, shipping_options)
            
            return response
            
        except Exception as e:
            logger.error("Checkout process failed", error=str(e))
            return "I encountered an error while processing your checkout. Please try again."
    
    async def _handle_shipping_selection(self, message: str, session_id: str) -> str:
        """Handle shipping selection requests."""
        try:
            # Extract shipping preference
            shipping_preference = await self._extract_shipping_preference(message)
            
            # Get shipping options
            shipping_options = await self._get_shipping_options({})
            
            # Filter based on preference
            if shipping_preference:
                filtered_options = [opt for opt in shipping_options if shipping_preference in opt["type"]]
                if filtered_options:
                    shipping_options = filtered_options
            
            # Persist selection if provided
            if shipping_preference in [opt["type"] for opt in shipping_options]:
                try:
                    from ..utils import cart_store
                    cart_store.set_shipping(session_id, shipping_preference)
                except Exception:
                    pass
            # Format shipping response
            response = self._format_shipping_response(shipping_options)
            
            return response
            
        except Exception as e:
            logger.error("Shipping selection failed", error=str(e))
            return "I encountered an error while processing shipping options. Please try again."
    
    async def _handle_payment_process(self, message: str, session_id: str) -> str:
        """Handle payment process requests."""
        try:
            # Extract payment information
            payment_info = await self._extract_payment_info(message)
            
            if not payment_info:
                return "I need payment information to process your order. Please provide your payment details."
            
            # Calculate current totals from shared cart for amount
            cart_contents = await self._get_cart_contents(session_id)
            order_totals = await self._calculate_order_totals(cart_contents)
            amount = order_totals.get("total", 0.0)
            # Fallback to checkout snapshot if live cart appears empty
            if amount <= 0 or order_totals.get("item_count", 0) <= 0:
                try:
                    from ..utils import cart_store
                    snapshot = cart_store.get_checkout_snapshot(session_id)
                    if snapshot:
                        cart_contents = {"items": snapshot.get("items", [])}
                        order_totals = snapshot.get("order_totals", order_totals)
                        amount = order_totals.get("total", 0.0)
                except Exception:
                    pass
            if amount <= 0 or order_totals.get("item_count", 0) <= 0:
                return "Your cart is empty. Please add some items before proceeding to payment."
            
            # Process payment
            payment_result = await self._process_payment(payment_info, session_id)
            payment_result["amount"] = amount
            
            if payment_result["success"]:
                # Create order
                order = await self._create_order(session_id, payment_result)
                # Clear cart after success
                try:
                    from ..utils import cart_store
                    cart_store.clear_cart(session_id)
                    cart_store.clear_checkout_snapshot(session_id)
                except Exception:
                    pass
                
                # Format success response
                response = self._format_payment_success_response(order)
            else:
                # Format error response
                response = self._format_payment_error_response(payment_result)
            
            return response
            
        except Exception as e:
            logger.error("Payment process failed", error=str(e))
            return "I encountered an error while processing your payment. Please try again."
    
    async def _handle_order_status(self, message: str, session_id: str) -> str:
        """Handle order status requests."""
        try:
            # Extract order identifier
            order_id = await self._extract_order_identifier(message)
            
            if not order_id:
                return "I need an order ID to check the status. Please provide your order number."
            
            # Get order status
            order_status = await self._get_order_status(order_id)
            
            if not order_status:
                return f"I couldn't find order {order_id}. Please check your order number."
            
            # Format status response
            response = self._format_order_status_response(order_status)
            
            return response
            
        except Exception as e:
            logger.error("Order status check failed", error=str(e))
            return "I encountered an error while checking your order status. Please try again."
    
    async def _handle_order_tracking(self, message: str, session_id: str) -> str:
        """Handle order tracking requests."""
        try:
            # Extract order identifier
            order_id = await self._extract_order_identifier(message)
            
            if not order_id:
                return "I need an order ID to track your order. Please provide your order number."
            
            # Get tracking information
            tracking_info = await self._get_tracking_info(order_id)
            
            if not tracking_info:
                return f"I couldn't find tracking information for order {order_id}. Please check your order number."
            
            # Format tracking response
            response = self._format_tracking_response(tracking_info)
            
            return response
            
        except Exception as e:
            logger.error("Order tracking failed", error=str(e))
            return "I encountered an error while tracking your order. Please try again."
    
    async def _handle_general_checkout_inquiry(self, message: str, session_id: str) -> str:
        """Handle general checkout-related inquiries."""
        return """💳 I'm your Checkout Agent, here to help you complete your purchase with environmental consciousness!

I can help you with:
- **Checkout Process**: "Proceed to checkout" or "Complete my order"
- **Shipping Options**: "Show me shipping options" or "What's the most eco-friendly shipping?"
- **Payment Processing**: "Process payment" or "Pay with my card"
- **Order Status**: "What's the status of my order?" or "Check order status"
- **Order Tracking**: "Track my order" or "Where is my package?"

**Environmental Features**:
- Eco-friendly shipping options with CO2 calculations
- Sustainable packaging recommendations
- Environmental impact breakdown for your order
- Carbon offset suggestions

**Shipping Options**:
- 🌱 **Eco-Friendly**: Low CO2, 4-6 days
- 🚚 **Ground**: Standard shipping, 3-5 days  
- ✈️ **Express**: Fast delivery, 1-2 days

Ready to complete your environmentally conscious purchase? Let me know how I can help! 🌍"""
    
    async def _get_cart_contents(self, session_id: str) -> Dict[str, Any]:
        """Get cart contents from shared cart store."""
        try:
            from ..utils import cart_store
            cart = cart_store.get_or_create_cart(session_id)
            return {"items": cart.get("items", []), "session_id": session_id}
        except Exception:
            return {"items": [], "session_id": session_id}
    
    async def _calculate_order_totals(self, cart_contents: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate order totals."""
        items = cart_contents.get("items", [])
        
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        total_co2 = sum(item["co2_emissions"] * item["quantity"] for item in items)
        item_count = sum(item["quantity"] for item in items)
        
        return {
            "subtotal": subtotal,
            "total_co2": total_co2,
            "item_count": item_count,
            "tax": subtotal * 0.08,  # 8% tax
            "shipping_cost": 0.0,  # Will be calculated based on shipping option
            "total": subtotal + (subtotal * 0.08)
        }
    
    async def _get_shipping_options(self, cart_contents: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get available shipping options."""
        options = []
        
        for key, option in self.shipping_options.items():
            # Calculate CO2 for shipping (mock distance of 500 miles)
            shipping_co2 = 500 * option["co2_per_mile"]
            
            options.append({
                "type": key,
                "name": option["name"],
                "cost": option["cost"],
                "co2_emissions": shipping_co2,
                "eco_rating": option["eco_rating"],
                "delivery_days": option["delivery_days"],
                "description": self._get_shipping_description(key, option)
            })
        
        # Sort by eco-friendliness (lowest CO2 first)
        options.sort(key=lambda x: x["co2_emissions"])
        
        return options
    
    def _get_shipping_description(self, shipping_type: str, option: Dict[str, Any]) -> str:
        """Get shipping option description."""
        descriptions = {
            "eco": "Most environmentally friendly option with minimal CO2 emissions",
            "ground": "Standard ground shipping with moderate environmental impact",
            "express": "Fast delivery but higher CO2 emissions due to air transport"
        }
        
        return descriptions.get(shipping_type, "Standard shipping option")
    
    async def _extract_shipping_preference(self, message: str) -> Optional[str]:
        """Extract shipping preference from message."""
        message_lower = message.lower()
        
        if "eco" in message_lower or "green" in message_lower or "environmental" in message_lower:
            return "eco"
        elif "express" in message_lower or "fast" in message_lower or "quick" in message_lower:
            return "express"
        elif "ground" in message_lower or "standard" in message_lower:
            return "ground"
        
        return None
    
    async def _extract_payment_info(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract payment information from message."""
        import re
        
        # Mock payment info extraction
        payment_info = {
            "card_number": None,
            "expiry_date": None,
            "cvv": None,
            "cardholder_name": None
        }
        
        # Look for card number pattern (simplified)
        card_match = re.search(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}', message)
        if card_match:
            payment_info["card_number"] = card_match.group(0).replace(" ", "").replace("-", "")
        
        # Look for expiry date
        expiry_match = re.search(r'(\d{2})/(\d{2})', message)
        if expiry_match:
            payment_info["expiry_date"] = f"{expiry_match.group(1)}/{expiry_match.group(2)}"
        
        # Look for CVV
        cvv_match = re.search(r'\b\d{3,4}\b', message)
        if cvv_match:
            payment_info["cvv"] = cvv_match.group(0)
        
        # Check if we have enough payment info
        if payment_info["card_number"] and payment_info["expiry_date"]:
            return payment_info
        
        return None
    
    async def _process_payment(self, payment_info: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Process payment (mock implementation)."""
        # Mock payment processing
        payment_result = {
            "success": True,
            "transaction_id": f"TXN_{uuid.uuid4().hex[:8].upper()}",
            "amount": 0.0,  # Will be set based on order
            "payment_method": "credit_card",
            "timestamp": datetime.now(),
            "status": "completed"
        }
        
        # Simulate payment processing delay
        await asyncio.sleep(0.1)
        
        return payment_result
    
    async def _create_order(self, session_id: str, payment_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create order after successful payment."""
        order_id = f"ORD_{uuid.uuid4().hex[:8].upper()}"
        
        # Get cart contents
        cart_contents = await self._get_cart_contents(session_id)
        order_totals = await self._calculate_order_totals(cart_contents)
        
        # Create order
        order = {
            "order_id": order_id,
            "session_id": session_id,
            "items": cart_contents["items"],
            "totals": order_totals,
            "payment": payment_result,
            "shipping": {
                "method": "eco",  # Default to eco-friendly
                "address": "Default Address",  # Mock address
                "tracking_number": f"TRK_{uuid.uuid4().hex[:8].upper()}"
            },
            "status": "confirmed",
            "created_at": datetime.now(),
            "estimated_delivery": datetime.now().replace(day=datetime.now().day + 5)
        }
        
        # Store order
        self.orders[order_id] = order
        
        return order
    
    async def _extract_order_identifier(self, message: str) -> Optional[str]:
        """Extract order identifier from message."""
        import re
        
        # Look for order ID pattern
        order_match = re.search(r'ORD_[A-Z0-9]{8}', message.upper())
        if order_match:
            return order_match.group(0)
        
        # Look for any alphanumeric pattern that could be an order ID
        id_match = re.search(r'[A-Z0-9]{8,}', message.upper())
        if id_match:
            return id_match.group(0)
        
        return None
    
    async def _get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order status."""
        return self.orders.get(order_id)
    
    async def _get_tracking_info(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get tracking information."""
        order = self.orders.get(order_id)
        if not order:
            return None
        
        # Mock tracking information
        tracking_info = {
            "order_id": order_id,
            "tracking_number": order["shipping"]["tracking_number"],
            "status": order["status"],
            "current_location": "Distribution Center",
            "estimated_delivery": order["estimated_delivery"],
            "tracking_history": [
                {
                    "timestamp": order["created_at"],
                    "location": "Warehouse",
                    "status": "Order confirmed"
                },
                {
                    "timestamp": datetime.now(),
                    "location": "Distribution Center",
                    "status": "In transit"
                }
            ]
        }
        
        return tracking_info
    
    def _format_checkout_response(self, order_totals: Dict[str, Any], shipping_options: List[Dict[str, Any]]) -> str:
        """Format checkout response."""
        response = f"🛒 **Ready to Checkout**\n\n"
        response += f"📦 **Order Summary**:\n"
        response += f"• Items: {order_totals['item_count']}\n"
        response += f"• Subtotal: ${order_totals['subtotal']:.2f}\n"
        response += f"• Tax: ${order_totals['tax']:.2f}\n"
        response += f"• CO2 Impact: {order_totals['total_co2']:.1f} kg\n\n"
        
        response += f"🚚 **Shipping Options** (Choose one):\n"
        for i, option in enumerate(shipping_options, 1):
            response += f"{i}. **{option['name']}** - ${option['cost']:.2f}\n"
            response += f"   • CO2: {option['co2_emissions']:.1f} kg ({option['eco_rating']} Impact)\n"
            response += f"   • Delivery: {option['delivery_days']} days\n"
            response += f"   • {option['description']}\n\n"
        
        response += f"💡 **Recommendation**: Choose Eco-Friendly shipping for the lowest environmental impact!\n\n"
        response += f"Ready to proceed? Just say 'proceed to checkout' or specify your shipping preference!"
        
        return response
    
    def _format_shipping_response(self, shipping_options: List[Dict[str, Any]]) -> str:
        """Format shipping options response."""
        response = f"🚚 **Available Shipping Options**\n\n"
        
        for i, option in enumerate(shipping_options, 1):
            response += f"{i}. **{option['name']}** - ${option['cost']:.2f}\n"
            response += f"   • CO2 Emissions: {option['co2_emissions']:.1f} kg\n"
            response += f"   • Environmental Impact: {option['eco_rating']}\n"
            response += f"   • Delivery Time: {option['delivery_days']} days\n"
            response += f"   • {option['description']}\n\n"
        
        response += f"🌱 **Eco-Friendly Choice**: Option 1 (Eco-Friendly Shipping) has the lowest CO2 emissions!\n\n"
        response += f"Which shipping option would you prefer?"
        
        return response
    
    def _format_payment_success_response(self, order: Dict[str, Any]) -> str:
        """Format payment success response."""
        response = f"✅ **Payment Successful!**\n\n"
        response += f"🎉 **Order Confirmed**: {order['order_id']}\n"
        response += f"💰 **Total Paid**: ${order['totals']['total']:.2f}\n"
        response += f"🌍 **Total CO2**: {order['totals']['total_co2']:.1f} kg\n"
        response += f"📦 **Items**: {order['totals']['item_count']}\n\n"
        
        response += f"🚚 **Shipping Details**:\n"
        response += f"• Method: {order['shipping']['method'].title()}\n"
        response += f"• Tracking: {order['shipping']['tracking_number']}\n"
        response += f"• Estimated Delivery: {order['estimated_delivery'].strftime('%Y-%m-%d')}\n\n"
        
        response += f"📧 **Next Steps**:\n"
        response += f"• You'll receive an email confirmation shortly\n"
        response += f"• Track your order with: '{order['order_id']}'\n"
        response += f"• Estimated delivery: {order['estimated_delivery'].strftime('%B %d, %Y')}\n\n"
        
        response += f"🌱 **Thank you for choosing environmentally conscious shopping!**"
        
        return response
    
    def _format_payment_error_response(self, payment_result: Dict[str, Any]) -> str:
        """Format payment error response."""
        response = f"❌ **Payment Failed**\n\n"
        response += f"Unfortunately, we couldn't process your payment. Please try again with different payment information.\n\n"
        response += f"💡 **Tips**:\n"
        response += f"• Check your card number and expiry date\n"
        response += f"• Ensure sufficient funds are available\n"
        response += f"• Try a different payment method\n\n"
        response += f"Would you like to try again?"
        
        return response
    
    def _format_order_status_response(self, order: Dict[str, Any]) -> str:
        """Format order status response."""
        response = f"📋 **Order Status**: {order['order_id']}\n\n"
        response += f"📦 **Status**: {order['status'].title()}\n"
        response += f"📅 **Order Date**: {order['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
        response += f"🚚 **Shipping**: {order['shipping']['method'].title()}\n"
        response += f"📦 **Tracking**: {order['shipping']['tracking_number']}\n"
        response += f"📅 **Estimated Delivery**: {order['estimated_delivery'].strftime('%Y-%m-%d')}\n\n"
        
        response += f"💰 **Order Total**: ${order['totals']['total']:.2f}\n"
        response += f"🌍 **CO2 Impact**: {order['totals']['total_co2']:.1f} kg\n\n"
        
        response += f"📧 **Need Help?** Contact support with your order number: {order['order_id']}"
        
        return response
    
    def _format_tracking_response(self, tracking_info: Dict[str, Any]) -> str:
        """Format tracking response."""
        response = f"📦 **Order Tracking**: {tracking_info['order_id']}\n\n"
        response += f"🔍 **Tracking Number**: {tracking_info['tracking_number']}\n"
        response += f"📍 **Current Location**: {tracking_info['current_location']}\n"
        response += f"📅 **Estimated Delivery**: {tracking_info['estimated_delivery'].strftime('%Y-%m-%d')}\n\n"
        
        response += f"📋 **Tracking History**:\n"
        for event in tracking_info['tracking_history']:
            response += f"• {event['timestamp'].strftime('%Y-%m-%d %H:%M')} - {event['location']}: {event['status']}\n"
        
        response += f"\n🌱 **Environmental Impact**: Your order was shipped using eco-friendly methods!"
        
        return response
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task assigned to this agent."""
        task_type = task.get("type", "unknown")
        
        if task_type == "process_checkout":
            return await self._execute_checkout_task(task)
        elif task_type == "process_payment":
            return await self._execute_payment_task(task)
        elif task_type == "get_order_status":
            return await self._execute_order_status_task(task)
        elif task_type == "get_tracking_info":
            return await self._execute_tracking_task(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _execute_checkout_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute checkout task."""
        session_id = task.get("session_id", "default")
        cart_contents = await self._get_cart_contents(session_id)
        order_totals = await self._calculate_order_totals(cart_contents)
        shipping_options = await self._get_shipping_options(cart_contents)
        
        return {
            "order_totals": order_totals,
            "shipping_options": shipping_options,
            "cart_contents": cart_contents
        }
    
    async def _execute_payment_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute payment task."""
        payment_info = task.get("payment_info", {})
        session_id = task.get("session_id", "default")
        
        payment_result = await self._process_payment(payment_info, session_id)
        
        if payment_result["success"]:
            order = await self._create_order(session_id, payment_result)
            return {
                "success": True,
                "order": order,
                "payment_result": payment_result
            }
        else:
            return {
                "success": False,
                "payment_result": payment_result
            }
    
    async def _execute_order_status_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute order status task."""
        order_id = task.get("order_id")
        order_status = await self._get_order_status(order_id)
        
        return {
            "order_status": order_status
        }
    
    async def _execute_tracking_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tracking task."""
        order_id = task.get("order_id")
        tracking_info = await self._get_tracking_info(order_id)
        
        return {
            "tracking_info": tracking_info
        }
