"""
Integration tests for API endpoints in CO2-Aware Shopping Assistant
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from main import app


class TestAPIEndpoints:
    """Test the main API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_chat_endpoint(self, client):
        """Test chat endpoint with valid request"""
        with patch('main.host_agent') as mock_host_agent:
            mock_host_agent.run.return_value = "I found some eco-friendly products for you"
            
            response = client.post(
                "/chat",
                json={
                    "message": "Find me eco-friendly laptops",
                    "session_id": "test_session_123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "session_id" in data
            assert data["session_id"] == "test_session_123"
    
    def test_chat_endpoint_missing_message(self, client):
        """Test chat endpoint with missing message"""
        response = client.post(
            "/chat",
            json={"session_id": "test_session_123"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_endpoint_missing_session_id(self, client):
        """Test chat endpoint with missing session_id"""
        response = client.post(
            "/chat",
            json={"message": "Find me eco-friendly laptops"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_products_endpoint(self, client):
        """Test products listing endpoint"""
        with patch('main.host_agent') as mock_host_agent:
            mock_host_agent.run.return_value = "Here are the available products"
            
            response = client.get("/products")
            
            assert response.status_code == 200
            data = response.json()
            assert "products" in data
    
    def test_cart_endpoint(self, client):
        """Test cart operations endpoint"""
        with patch('main.host_agent') as mock_host_agent:
            mock_host_agent.run.return_value = "Item added to cart successfully"
            
            response = client.post(
                "/cart/add",
                json={
                    "product_id": "laptop_123",
                    "quantity": 1,
                    "session_id": "test_session_123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
    
    def test_co2_calculation_endpoint(self, client):
        """Test CO2 calculation endpoint"""
        with patch('main.host_agent') as mock_host_agent:
            mock_host_agent.run.return_value = "CO2 emissions calculated: 2.5 kg"
            
            response = client.post(
                "/co2/calculate",
                json={
                    "product_id": "laptop_123",
                    "shipping_method": "standard",
                    "session_id": "test_session_123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "co2_emissions" in data or "response" in data
    
    def test_checkout_endpoint(self, client):
        """Test checkout endpoint"""
        with patch('main.host_agent') as mock_host_agent:
            mock_host_agent.run.return_value = "Order processed successfully"
            
            response = client.post(
                "/checkout",
                json={
                    "session_id": "test_session_123",
                    "shipping_method": "eco_friendly"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data or "response" in data


class TestAPIIntegration:
    """Test API integration scenarios"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_complete_shopping_workflow(self, client):
        """Test complete shopping workflow through API"""
        session_id = "integration_test_session"
        
        with patch('main.host_agent') as mock_host_agent:
            # Mock different responses for different calls
            def mock_host_response(message, session_id):
                if "search" in message.lower():
                    return "Found eco-friendly products"
                elif "cart" in message.lower():
                    return "Added to cart successfully"
                elif "co2" in message.lower():
                    return "CO2 emissions: 2.5 kg"
                elif "checkout" in message.lower():
                    return "Order completed with eco-friendly shipping"
                else:
                    return "I can help you with that"
            
            mock_host_agent.run.side_effect = mock_host_response
            
            # Step 1: Search for products
            search_response = client.post(
                "/chat",
                json={
                    "message": "Find me eco-friendly laptops",
                    "session_id": session_id
                }
            )
            assert search_response.status_code == 200
            
            # Step 2: Add to cart
            cart_response = client.post(
                "/cart/add",
                json={
                    "product_id": "laptop_123",
                    "quantity": 1,
                    "session_id": session_id
                }
            )
            assert cart_response.status_code == 200
            
            # Step 3: Calculate CO2
            co2_response = client.post(
                "/co2/calculate",
                json={
                    "product_id": "laptop_123",
                    "shipping_method": "eco_friendly",
                    "session_id": session_id
                }
            )
            assert co2_response.status_code == 200
            
            # Step 4: Checkout
            checkout_response = client.post(
                "/checkout",
                json={
                    "session_id": session_id,
                    "shipping_method": "eco_friendly"
                }
            )
            assert checkout_response.status_code == 200
    
    def test_error_handling_in_workflow(self, client):
        """Test error handling in API workflow"""
        with patch('main.host_agent') as mock_host_agent:
            mock_host_agent.run.side_effect = Exception("Agent error")
            
            response = client.post(
                "/chat",
                json={
                    "message": "Find me products",
                    "session_id": "error_test_session"
                }
            )
            
            # Should handle error gracefully
            assert response.status_code == 500
            data = response.json()
            assert "error" in data


class TestAPIPerformance:
    """Test API performance characteristics"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_concurrent_requests(self, client):
        """Test handling concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request(session_id):
            with patch('main.host_agent') as mock_host_agent:
                mock_host_agent.run.return_value = f"Response for session {session_id}"
                
                response = client.post(
                    "/chat",
                    json={
                        "message": "Test message",
                        "session_id": session_id
                    }
                )
                results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(f"session_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    def test_large_payload_handling(self, client):
        """Test handling large payloads"""
        large_message = "Find me " + "eco-friendly " * 1000 + "products"
        
        with patch('main.host_agent') as mock_host_agent:
            mock_host_agent.run.return_value = "Processed large request"
            
            response = client.post(
                "/chat",
                json={
                    "message": large_message,
                    "session_id": "large_payload_test"
                }
            )
            
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])
