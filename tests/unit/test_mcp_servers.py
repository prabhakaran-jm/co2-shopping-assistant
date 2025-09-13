"""
Unit tests for MCP servers in CO2-Aware Shopping Assistant
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_servers.boutique_mcp import BoutiqueMCP
from mcp_servers.co2_mcp import CO2MCP


class TestBoutiqueMCP:
    """Test the Boutique MCP server functionality"""
    
    @pytest.fixture
    def boutique_mcp(self):
        """Create BoutiqueMCP instance with mocked dependencies"""
        with patch('mcp_servers.boutique_mcp.requests') as mock_requests:
            mock_requests.get.return_value.json.return_value = {"products": []}
            mock_requests.post.return_value.json.return_value = {"success": True}
            return BoutiqueMCP()
    
    def test_boutique_mcp_initialization(self, boutique_mcp):
        """Test BoutiqueMCP initializes correctly"""
        assert boutique_mcp.base_url == "http://frontend.default.svc.cluster.local"
        assert boutique_mcp.session_id is not None
    
    @pytest.mark.asyncio
    async def test_list_products(self, boutique_mcp):
        """Test listing products functionality"""
        with patch('mcp_servers.boutique_mcp.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "products": [
                    {"id": "1", "name": "Eco Laptop", "price": 999.99},
                    {"id": "2", "name": "Green Phone", "price": 599.99}
                ]
            }
            mock_get.return_value = mock_response
            
            result = await boutique_mcp.list_products()
            
            assert result is not None
            assert "products" in result
            assert len(result["products"]) == 2
            assert result["products"][0]["name"] == "Eco Laptop"
    
    @pytest.mark.asyncio
    async def test_get_product(self, boutique_mcp):
        """Test getting a specific product"""
        with patch('mcp_servers.boutique_mcp.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "1",
                "name": "Eco Laptop",
                "price": 999.99,
                "description": "Environmentally friendly laptop"
            }
            mock_get.return_value = mock_response
            
            result = await boutique_mcp.get_product("1")
            
            assert result is not None
            assert result["id"] == "1"
            assert result["name"] == "Eco Laptop"
            assert result["price"] == 999.99
    
    @pytest.mark.asyncio
    async def test_add_to_cart(self, boutique_mcp):
        """Test adding item to cart"""
        with patch('mcp_servers.boutique_mcp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"success": True, "cart_id": "cart_123"}
            mock_post.return_value = mock_response
            
            result = await boutique_mcp.add_to_cart("1", 2)
            
            assert result is not None
            assert result["success"] is True
            assert "cart_id" in result
    
    @pytest.mark.asyncio
    async def test_view_cart(self, boutique_mcp):
        """Test viewing cart contents"""
        with patch('mcp_servers.boutique_mcp.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "items": [
                    {"product_id": "1", "quantity": 2, "price": 999.99}
                ],
                "total": 1999.98
            }
            mock_get.return_value = mock_response
            
            result = await boutique_mcp.view_cart()
            
            assert result is not None
            assert "items" in result
            assert "total" in result
            assert result["total"] == 1999.98
    
    @pytest.mark.asyncio
    async def test_checkout(self, boutique_mcp):
        """Test checkout process"""
        with patch('mcp_servers.boutique_mcp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "success": True,
                "order_id": "order_123",
                "total": 1999.98
            }
            mock_post.return_value = mock_response
            
            result = await boutique_mcp.checkout()
            
            assert result is not None
            assert result["success"] is True
            assert "order_id" in result
    
    @pytest.mark.asyncio
    async def test_error_handling(self, boutique_mcp):
        """Test error handling in API calls"""
        with patch('mcp_servers.boutique_mcp.requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            result = await boutique_mcp.list_products()
            
            # Should return error response instead of raising exception
            assert result is not None
            assert "error" in result


class TestCO2MCP:
    """Test the CO2 MCP server functionality"""
    
    @pytest.fixture
    def co2_mcp(self):
        """Create CO2MCP instance with mocked dependencies"""
        with patch('mcp_servers.co2_mcp.requests') as mock_requests:
            mock_requests.post.return_value.json.return_value = {"co2_emissions": 2.5}
            return CO2MCP()
    
    def test_co2_mcp_initialization(self, co2_mcp):
        """Test CO2MCP initializes correctly"""
        assert co2_mcp.api_url == "https://api.co2data.org"
    
    @pytest.mark.asyncio
    async def test_calculate_product_co2(self, co2_mcp):
        """Test product CO2 calculation"""
        with patch('mcp_servers.co2_mcp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "co2_emissions": 2.5,
                "unit": "kg",
                "category": "electronics"
            }
            mock_post.return_value = mock_response
            
            result = await co2_mcp.calculate_product_co2("laptop", "electronics")
            
            assert result is not None
            assert result["co2_emissions"] == 2.5
            assert result["unit"] == "kg"
            assert result["category"] == "electronics"
    
    @pytest.mark.asyncio
    async def test_calculate_shipping_co2(self, co2_mcp):
        """Test shipping CO2 calculation"""
        with patch('mcp_servers.co2_mcp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "co2_emissions": 0.8,
                "unit": "kg",
                "method": "standard",
                "distance_km": 500
            }
            mock_post.return_value = mock_response
            
            result = await co2_mcp.calculate_shipping_co2("standard", 500)
            
            assert result is not None
            assert result["co2_emissions"] == 0.8
            assert result["method"] == "standard"
            assert result["distance_km"] == 500
    
    @pytest.mark.asyncio
    async def test_eco_friendly_recommendations(self, co2_mcp):
        """Test eco-friendly shipping recommendations"""
        with patch('mcp_servers.co2_mcp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "recommendations": [
                    {"method": "electric_delivery", "co2_emissions": 0.2},
                    {"method": "bike_delivery", "co2_emissions": 0.1}
                ]
            }
            mock_post.return_value = mock_response
            
            result = await co2_mcp.get_eco_friendly_shipping(500)
            
            assert result is not None
            assert "recommendations" in result
            assert len(result["recommendations"]) == 2
            assert result["recommendations"][0]["method"] == "electric_delivery"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, co2_mcp):
        """Test error handling in CO2 API calls"""
        with patch('mcp_servers.co2_mcp.requests.post') as mock_post:
            mock_post.side_effect = Exception("CO2 API Error")
            
            result = await co2_mcp.calculate_product_co2("laptop", "electronics")
            
            # Should return error response instead of raising exception
            assert result is not None
            assert "error" in result


class TestMCPIntegration:
    """Test MCP server integration"""
    
    @pytest.mark.asyncio
    async def test_boutique_and_co2_integration(self):
        """Test that Boutique and CO2 MCP servers work together"""
        with patch('mcp_servers.boutique_mcp.requests.get') as mock_boutique_get, \
             patch('mcp_servers.co2_mcp.requests.post') as mock_co2_post:
            
            # Mock boutique response
            boutique_response = Mock()
            boutique_response.json.return_value = {
                "products": [{"id": "1", "name": "Eco Laptop", "price": 999.99}]
            }
            mock_boutique_get.return_value = boutique_response
            
            # Mock CO2 response
            co2_response = Mock()
            co2_response.json.return_value = {"co2_emissions": 2.5}
            mock_co2_post.return_value = co2_response
            
            # Test workflow
            boutique_mcp = BoutiqueMCP()
            co2_mcp = CO2MCP()
            
            # Get product
            products = await boutique_mcp.list_products()
            assert len(products["products"]) == 1
            
            # Calculate CO2
            co2_result = await co2_mcp.calculate_product_co2("laptop", "electronics")
            assert co2_result["co2_emissions"] == 2.5


if __name__ == "__main__":
    pytest.main([__file__])
