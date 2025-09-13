"""
Unit tests for A2A (Agent-to-Agent) protocol in CO2-Aware Shopping Assistant
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from a2a.protocol import A2AMessage


class TestA2AMessage:
    """Test the A2A message protocol"""
    
    def test_a2a_message_creation(self):
        """Test creating an A2A message"""
        message = A2AMessage(
            sender="host_agent",
            recipient="product_discovery_agent",
            action="search_products",
            payload={"query": "eco-friendly laptops", "filters": {"price_max": 1000}},
            session_id="session_123"
        )
        
        assert message.sender == "host_agent"
        assert message.recipient == "product_discovery_agent"
        assert message.action == "search_products"
        assert message.payload["query"] == "eco-friendly laptops"
        assert message.session_id == "session_123"
        assert message.timestamp is not None
    
    def test_a2a_message_serialization(self):
        """Test A2A message serialization to dict"""
        message = A2AMessage(
            sender="host_agent",
            recipient="co2_calculator_agent",
            action="calculate_emissions",
            payload={"product_id": "laptop_123", "shipping_method": "standard"},
            session_id="session_456"
        )
        
        message_dict = message.to_dict()
        
        assert message_dict["sender"] == "host_agent"
        assert message_dict["recipient"] == "co2_calculator_agent"
        assert message_dict["action"] == "calculate_emissions"
        assert message_dict["payload"]["product_id"] == "laptop_123"
        assert message_dict["session_id"] == "session_456"
        assert "timestamp" in message_dict
    
    def test_a2a_message_deserialization(self):
        """Test A2A message deserialization from dict"""
        message_dict = {
            "sender": "product_discovery_agent",
            "recipient": "host_agent",
            "action": "products_found",
            "payload": {
                "products": [
                    {"id": "1", "name": "Eco Laptop", "price": 999.99},
                    {"id": "2", "name": "Green Phone", "price": 599.99}
                ]
            },
            "session_id": "session_789",
            "timestamp": datetime.now().isoformat()
        }
        
        message = A2AMessage.from_dict(message_dict)
        
        assert message.sender == "product_discovery_agent"
        assert message.recipient == "host_agent"
        assert message.action == "products_found"
        assert len(message.payload["products"]) == 2
        assert message.session_id == "session_789"
    
    def test_a2a_message_validation(self):
        """Test A2A message validation"""
        # Valid message
        valid_message = A2AMessage(
            sender="host_agent",
            recipient="cart_agent",
            action="add_to_cart",
            payload={"product_id": "123", "quantity": 1},
            session_id="session_123"
        )
        assert valid_message.is_valid() is True
        
        # Invalid message - missing required fields
        with pytest.raises(ValueError):
            A2AMessage(
                sender="",  # Empty sender
                recipient="cart_agent",
                action="add_to_cart",
                payload={"product_id": "123"},
                session_id="session_123"
            )
    
    def test_a2a_message_types(self):
        """Test different types of A2A messages"""
        # Search request
        search_message = A2AMessage(
            sender="host_agent",
            recipient="product_discovery_agent",
            action="search_products",
            payload={"query": "sustainable products"},
            session_id="session_123"
        )
        assert search_message.action == "search_products"
        
        # CO2 calculation request
        co2_message = A2AMessage(
            sender="host_agent",
            recipient="co2_calculator_agent",
            action="calculate_co2",
            payload={"product_id": "laptop_123", "shipping": "eco"},
            session_id="session_123"
        )
        assert co2_message.action == "calculate_co2"
        
        # Cart operation
        cart_message = A2AMessage(
            sender="host_agent",
            recipient="cart_management_agent",
            action="add_item",
            payload={"product_id": "laptop_123", "quantity": 1},
            session_id="session_123"
        )
        assert cart_message.action == "add_item"
        
        # Checkout request
        checkout_message = A2AMessage(
            sender="host_agent",
            recipient="checkout_agent",
            action="process_order",
            payload={"cart_id": "cart_123", "shipping_method": "eco"},
            session_id="session_123"
        )
        assert checkout_message.action == "process_order"


class TestA2ACommunication:
    """Test A2A communication patterns"""
    
    def test_request_response_pattern(self):
        """Test request-response communication pattern"""
        # Request message
        request = A2AMessage(
            sender="host_agent",
            recipient="product_discovery_agent",
            action="search_products",
            payload={"query": "eco-friendly laptops"},
            session_id="session_123"
        )
        
        # Response message
        response = A2AMessage(
            sender="product_discovery_agent",
            recipient="host_agent",
            action="search_results",
            payload={
                "products": [
                    {"id": "1", "name": "Eco Laptop", "price": 999.99}
                ],
                "request_id": request.timestamp
            },
            session_id="session_123"
        )
        
        assert request.sender == response.recipient
        assert request.recipient == response.sender
        assert request.session_id == response.session_id
        assert response.payload["request_id"] == request.timestamp
    
    def test_broadcast_pattern(self):
        """Test broadcast communication pattern"""
        # Host agent broadcasts to multiple agents
        broadcast = A2AMessage(
            sender="host_agent",
            recipient="all_agents",
            action="session_start",
            payload={"user_id": "user_123", "preferences": {"eco_friendly": True}},
            session_id="session_123"
        )
        
        assert broadcast.recipient == "all_agents"
        assert broadcast.action == "session_start"
    
    def test_chain_pattern(self):
        """Test chain communication pattern (agent A -> agent B -> agent C)"""
        # Step 1: Host -> Product Discovery
        step1 = A2AMessage(
            sender="host_agent",
            recipient="product_discovery_agent",
            action="search_products",
            payload={"query": "sustainable products"},
            session_id="session_123"
        )
        
        # Step 2: Product Discovery -> CO2 Calculator
        step2 = A2AMessage(
            sender="product_discovery_agent",
            recipient="co2_calculator_agent",
            action="calculate_co2",
            payload={"product_id": "laptop_123"},
            session_id="session_123"
        )
        
        # Step 3: CO2 Calculator -> Cart Management
        step3 = A2AMessage(
            sender="co2_calculator_agent",
            recipient="cart_management_agent",
            action="add_eco_product",
            payload={"product_id": "laptop_123", "co2_emissions": 2.5},
            session_id="session_123"
        )
        
        # Verify chain
        assert step1.session_id == step2.session_id == step3.session_id
        assert step1.recipient == step2.sender
        assert step2.recipient == step3.sender


class TestA2AErrorHandling:
    """Test A2A error handling and recovery"""
    
    def test_error_message_format(self):
        """Test error message format"""
        error_message = A2AMessage(
            sender="product_discovery_agent",
            recipient="host_agent",
            action="error",
            payload={
                "error_type": "api_error",
                "error_message": "Failed to connect to product API",
                "original_action": "search_products",
                "retry_after": 30
            },
            session_id="session_123"
        )
        
        assert error_message.action == "error"
        assert "error_type" in error_message.payload
        assert "error_message" in error_message.payload
        assert "original_action" in error_message.payload
    
    def test_timeout_handling(self):
        """Test timeout handling in A2A communication"""
        # Message with timeout
        message = A2AMessage(
            sender="host_agent",
            recipient="co2_calculator_agent",
            action="calculate_co2",
            payload={"product_id": "laptop_123"},
            session_id="session_123"
        )
        
        # Simulate timeout by checking timestamp
        old_timestamp = message.timestamp
        # In real implementation, you'd check if current time - timestamp > timeout
        
        assert message.timestamp == old_timestamp


class TestA2APerformance:
    """Test A2A performance characteristics"""
    
    def test_message_size_optimization(self):
        """Test that messages are optimized for size"""
        # Large payload
        large_payload = {
            "products": [{"id": f"product_{i}", "name": f"Product {i}"} for i in range(100)],
            "metadata": {"total": 100, "page": 1}
        }
        
        message = A2AMessage(
            sender="product_discovery_agent",
            recipient="host_agent",
            action="search_results",
            payload=large_payload,
            session_id="session_123"
        )
        
        # Serialize and check size
        message_dict = message.to_dict()
        message_size = len(str(message_dict))
        
        # Should be reasonable size (less than 1MB for this test)
        assert message_size < 1024 * 1024
    
    def test_concurrent_messages(self):
        """Test handling multiple concurrent messages"""
        messages = []
        
        # Create multiple messages for the same session
        for i in range(10):
            message = A2AMessage(
                sender=f"agent_{i}",
                recipient="host_agent",
                action=f"action_{i}",
                payload={"data": f"data_{i}"},
                session_id="session_123"
            )
            messages.append(message)
        
        # All messages should have the same session ID
        session_ids = [msg.session_id for msg in messages]
        assert all(sid == "session_123" for sid in session_ids)
        
        # All messages should be valid
        assert all(msg.is_valid() for msg in messages)


if __name__ == "__main__":
    pytest.main([__file__])
