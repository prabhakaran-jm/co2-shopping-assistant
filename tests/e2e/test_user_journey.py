"""
End-to-end tests for complete user journeys in CO2-Aware Shopping Assistant
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
from unittest.mock import patch
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from main import app


class TestEcoFriendlyShoppingJourney:
    """Test complete eco-friendly shopping journey"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_eco_friendly_laptop_purchase(self, client):
        """Test complete journey: search -> compare -> add to cart -> checkout"""
        session_id = "eco_laptop_journey"
        
        with patch('main.host_agent') as mock_host_agent:
            # Mock responses for different stages
            def mock_eco_journey(message, session_id):
                if "eco-friendly laptop" in message.lower():
                    return """
                    I found several eco-friendly laptops for you:
                    1. GreenBook Pro - $999 (2.1 kg CO2 emissions)
                    2. EcoLaptop Air - $1299 (1.8 kg CO2 emissions)
                    3. SustainableBook - $799 (2.5 kg CO2 emissions)
                    
                    The EcoLaptop Air has the lowest carbon footprint!
                    """
                elif "co2" in message.lower() or "carbon" in message.lower():
                    return "EcoLaptop Air: 1.8 kg CO2 emissions (manufacturing + shipping)"
                elif "cart" in message.lower() or "add" in message.lower():
                    return "EcoLaptop Air added to your cart! Total CO2 impact: 1.8 kg"
                elif "checkout" in message.lower() or "order" in message.lower():
                    return """
                    Order completed! 🌱
                    - Product: EcoLaptop Air
                    - Shipping: Eco-friendly delivery (0.2 kg CO2)
                    - Total CO2: 2.0 kg
                    - You saved 0.7 kg CO2 compared to standard options!
                    """
                else:
                    return "I can help you find eco-friendly products!"
            
            mock_host_agent.run.side_effect = mock_eco_journey
            
            # Step 1: Search for eco-friendly laptops
            search_response = client.post(
                "/chat",
                json={
                    "message": "I need an eco-friendly laptop for work",
                    "session_id": session_id
                }
            )
            assert search_response.status_code == 200
            search_data = search_response.json()
            assert "eco-friendly" in search_data["response"].lower()
            assert "laptop" in search_data["response"].lower()
            
            # Step 2: Ask about CO2 impact
            co2_response = client.post(
                "/chat",
                json={
                    "message": "What's the carbon footprint of the EcoLaptop Air?",
                    "session_id": session_id
                }
            )
            assert co2_response.status_code == 200
            co2_data = co2_response.json()
            assert "co2" in co2_data["response"].lower()
            
            # Step 3: Add to cart
            cart_response = client.post(
                "/cart/add",
                json={
                    "product_id": "ecolaptop_air",
                    "quantity": 1,
                    "session_id": session_id
                }
            )
            assert cart_response.status_code == 200
            
            # Step 4: Checkout with eco-friendly shipping
            checkout_response = client.post(
                "/checkout",
                json={
                    "session_id": session_id,
                    "shipping_method": "eco_friendly"
                }
            )
            assert checkout_response.status_code == 200
            checkout_data = checkout_response.json()
            assert "order completed" in checkout_data["response"].lower()
            assert "co2" in checkout_data["response"].lower()
    
    def test_sustainable_phone_purchase(self, client):
        """Test sustainable phone purchase journey"""
        session_id = "sustainable_phone_journey"
        
        with patch('main.host_agent') as mock_host_agent:
            def mock_phone_journey(message, session_id):
                if "sustainable phone" in message.lower():
                    return """
                    Here are sustainable phone options:
                    1. FairPhone 4 - $579 (1.2 kg CO2, modular design)
                    2. Shiftphone - $699 (1.0 kg CO2, repairable)
                    3. Teracube 2e - $399 (1.5 kg CO2, 10-year warranty)
                    
                    Shiftphone has the lowest environmental impact!
                    """
                elif "co2" in message.lower():
                    return "Shiftphone: 1.0 kg CO2 emissions (very low impact!)"
                elif "cart" in message.lower():
                    return "Shiftphone added to cart! Great eco choice!"
                elif "checkout" in message.lower():
                    return "Order completed! You chose the most sustainable option! 🌱"
                else:
                    return "I can help you find sustainable products!"
            
            mock_host_agent.run.side_effect = mock_phone_journey
            
            # Complete journey
            search_response = client.post(
                "/chat",
                json={
                    "message": "I want a sustainable smartphone",
                    "session_id": session_id
                }
            )
            assert search_response.status_code == 200
            
            # Add to cart
            cart_response = client.post(
                "/cart/add",
                json={
                    "product_id": "shiftphone",
                    "quantity": 1,
                    "session_id": session_id
                }
            )
            assert cart_response.status_code == 200
            
            # Checkout
            checkout_response = client.post(
                "/checkout",
                json={
                    "session_id": session_id,
                    "shipping_method": "eco_friendly"
                }
            )
            assert checkout_response.status_code == 200


class TestCO2AwarenessJourney:
    """Test CO2 awareness and education journey"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_co2_education_journey(self, client):
        """Test user learning about CO2 impact"""
        session_id = "co2_education_journey"
        
        with patch('main.host_agent') as mock_host_agent:
            def mock_education_journey(message, session_id):
                if "what is co2" in message.lower():
                    return """
                    CO2 (carbon dioxide) emissions contribute to climate change. 
                    When shopping, every product has a carbon footprint from:
                    - Manufacturing processes
                    - Transportation and shipping
                    - Packaging materials
                    
                    I help you choose products with lower CO2 impact! 🌱
                    """
                elif "how to reduce" in message.lower():
                    return """
                    Here's how to reduce your shopping CO2 footprint:
                    1. Choose eco-friendly products
                    2. Select sustainable shipping options
                    3. Buy from local suppliers when possible
                    4. Consider product lifespan and repairability
                    
                    I can help you find low-impact alternatives!
                    """
                elif "compare" in message.lower():
                    return """
                    CO2 Comparison:
                    - Standard laptop: 3.5 kg CO2
                    - Eco-friendly laptop: 2.0 kg CO2
                    - You save: 1.5 kg CO2 (43% reduction!)
                    """
                else:
                    return "I can help you understand environmental impact!"
            
            mock_host_agent.run.side_effect = mock_education_journey
            
            # Learn about CO2
            learn_response = client.post(
                "/chat",
                json={
                    "message": "What is CO2 and why should I care?",
                    "session_id": session_id
                }
            )
            assert learn_response.status_code == 200
            assert "co2" in learn_response.json()["response"].lower()
            
            # Learn about reduction strategies
            reduce_response = client.post(
                "/chat",
                json={
                    "message": "How can I reduce my shopping CO2 footprint?",
                    "session_id": session_id
                }
            )
            assert reduce_response.status_code == 200
            assert "reduce" in reduce_response.json()["response"].lower()
            
            # Compare CO2 impact
            compare_response = client.post(
                "/chat",
                json={
                    "message": "Compare CO2 impact of different laptops",
                    "session_id": session_id
                }
            )
            assert compare_response.status_code == 200
            assert "comparison" in compare_response.json()["response"].lower()


class TestErrorRecoveryJourney:
    """Test error recovery and resilience"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_api_error_recovery(self, client):
        """Test recovery from API errors"""
        session_id = "error_recovery_journey"
        
        with patch('main.host_agent') as mock_host_agent:
            # First call fails, second succeeds
            call_count = 0
            def mock_error_recovery(message, session_id):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("Temporary API error")
                else:
                    return "I found eco-friendly products for you!"
            
            mock_host_agent.run.side_effect = mock_error_recovery
            
            # First request should handle error gracefully
            response1 = client.post(
                "/chat",
                json={
                    "message": "Find me eco products",
                    "session_id": session_id
                }
            )
            # Should return error response, not crash
            assert response1.status_code in [500, 200]
            
            # Second request should succeed
            response2 = client.post(
                "/chat",
                json={
                    "message": "Find me eco products",
                    "session_id": session_id
                }
            )
            assert response2.status_code == 200
            assert "eco-friendly" in response2.json()["response"].lower()
    
    def test_invalid_input_handling(self, client):
        """Test handling of invalid user input"""
        session_id = "invalid_input_test"
        
        with patch('main.host_agent') as mock_host_agent:
            mock_host_agent.run.return_value = "I didn't understand that. Can you rephrase?"
            
            # Test with empty message
            response1 = client.post(
                "/chat",
                json={
                    "message": "",
                    "session_id": session_id
                }
            )
            assert response1.status_code == 422  # Validation error
            
            # Test with very long message
            long_message = "a" * 10000
            response2 = client.post(
                "/chat",
                json={
                    "message": long_message,
                    "session_id": session_id
                }
            )
            # Should either handle gracefully or return validation error
            assert response2.status_code in [200, 422]


class TestPerformanceJourney:
    """Test performance under load"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_concurrent_user_sessions(self, client):
        """Test multiple concurrent user sessions"""
        import threading
        import time
        
        results = []
        
        def simulate_user_session(user_id):
            session_id = f"user_{user_id}_session"
            
            with patch('main.host_agent') as mock_host_agent:
                mock_host_agent.run.return_value = f"Response for user {user_id}"
                
                # Simulate user journey
                search_response = client.post(
                    "/chat",
                    json={
                        "message": f"Find eco products for user {user_id}",
                        "session_id": session_id
                    }
                )
                
                cart_response = client.post(
                    "/cart/add",
                    json={
                        "product_id": f"product_{user_id}",
                        "quantity": 1,
                        "session_id": session_id
                    }
                )
                
                results.append({
                    "user_id": user_id,
                    "search_status": search_response.status_code,
                    "cart_status": cart_response.status_code
                })
        
        # Create multiple user sessions
        threads = []
        for i in range(10):
            thread = threading.Thread(target=simulate_user_session, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All sessions should succeed
        assert len(results) == 10
        assert all(r["search_status"] == 200 for r in results)
        assert all(r["cart_status"] == 200 for r in results)


if __name__ == "__main__":
    pytest.main([__file__])
