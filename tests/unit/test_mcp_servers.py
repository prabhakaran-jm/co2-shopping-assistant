"""
Unit tests for MCP servers in CO2-Aware Shopping Assistant
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_servers.boutique_mcp import BoutiqueMCPServer
from mcp_servers.co2_mcp import CO2MCPServer


class TestBoutiqueMCPServer:
    """Test the Boutique MCP server functionality"""

    @pytest.fixture
    def boutique_mcpserver(self):
        """Create BoutiqueMCPServer instance with mocked dependencies"""
        with patch('mcp_servers.boutique_mcp.httpx.AsyncClient'):
            server = BoutiqueMCPServer()
            server.add_to_cart = AsyncMock(return_value={"success": True, "cart_id": "cart_123"})
            server.view_cart = AsyncMock(return_value={"items": [], "total": 0.0})
            server.checkout = AsyncMock(return_value={"success": True, "order_id": "order_123"})
            yield server

    def test_boutique_mcpserver_initialization(self, boutique_mcpserver):
        """Test BoutiqueMCPServer initializes correctly"""
        assert boutique_mcpserver.boutique_base_url == "http://online-boutique.online-boutique.svc.cluster.local"

    @pytest.mark.asyncio
    async def test_search_products(self, boutique_mcpserver):
        """Test listing products functionality"""
        mock_products = [
            {"id": "1", "name": "Eco Laptop", "price": 999.99},
            {"id": "2", "name": "Green Phone", "price": 599.99}
        ]
        boutique_mcpserver.search_products = AsyncMock(return_value=mock_products)
        result = await boutique_mcpserver.search_products(query='')

        assert result is not None
        assert len(result) == 2
        assert result[0]["name"] == "Eco Laptop"

    @pytest.mark.asyncio
    async def test_get_product_details(self, boutique_mcpserver):
        """Test getting a specific product"""
        mock_product = {
            "id": "1",
            "name": "Eco Laptop",
            "price": 999.99,
            "description": "Environmentally friendly laptop"
        }
        boutique_mcpserver.get_product_details = AsyncMock(return_value=mock_product)

        result = await boutique_mcpserver.get_product_details("1")

        assert result is not None
        assert result["id"] == "1"
        assert result["name"] == "Eco Laptop"
        assert result["price"] == 999.99

    @pytest.mark.asyncio
    async def test_add_to_cart(self, boutique_mcpserver):
        """Test adding item to cart"""
        result = await boutique_mcpserver.add_to_cart("1", 2)

        assert result is not None
        assert result["success"] is True
        assert "cart_id" in result

    @pytest.mark.asyncio
    async def test_view_cart(self, boutique_mcpserver):
        """Test viewing cart contents"""
        result = await boutique_mcpserver.view_cart()

        assert result is not None
        assert "items" in result
        assert "total" in result

    @pytest.mark.asyncio
    async def test_checkout(self, boutique_mcpserver):
        """Test checkout process"""
        result = await boutique_mcpserver.checkout()

        assert result is not None
        assert result["success"] is True
        assert "order_id" in result

    @pytest.mark.asyncio
    async def test_error_handling_breaker_open(self, boutique_mcpserver):
        """Test circuit breaker fallback when open"""
        boutique_mcpserver._fallback_search_products = AsyncMock(return_value=[{"id": "fallback"}])
        
        breaker = boutique_mcpserver.circuit_breakers["product_catalog"]
        breaker.state = "open"
        breaker.last_failure_time = time.time()

        result = await boutique_mcpserver.search_products(query="test")

        assert result is not None
        assert len(result) == 1
        assert result[0]["id"] == "fallback"
        boutique_mcpserver._fallback_search_products.assert_called_once()

class TestCO2MCPServer:
    """Test the CO2 MCP server functionality"""

    @pytest.fixture
    def co2_mcpserver(self):
        """Create CO2MCPServer instance with mocked dependencies"""
        with patch('mcp_servers.co2_mcp.httpx.AsyncClient'):
            return CO2MCPServer()

    def test_co2_mcpserver_initialization(self, co2_mcpserver):
        """Test CO2MCPServer initializes correctly"""
        assert co2_mcpserver.co2_data_api_url == "https://api.carbonintensity.org.uk"

    @pytest.mark.asyncio
    async def test_calculate_product_co2(self, co2_mcpserver):
        """Test product CO2 calculation"""
        product_data = {"id": "test", "name": "Test Product", "category": "electronics", "price": 100.0}
        
        co2_mcpserver.calculate_product_co2 = AsyncMock(return_value={"total_co2": 25.0})
        
        result = await co2_mcpserver.calculate_product_co2(product_data)

        assert result is not None
        assert "total_co2" in result
        assert result["total_co2"] == 25.0

    @pytest.mark.asyncio
    async def test_calculate_shipping_co2(self, co2_mcpserver):
        """Test shipping CO2 calculation"""
        shipping_data = {"method": "ground", "distance_miles": 100, "weight_kg": 2}
        
        co2_mcpserver.calculate_shipping_co2 = AsyncMock(return_value={"total_co2": 100.0})

        result = await co2_mcpserver.calculate_shipping_co2(shipping_data)

        assert result is not None
        assert "total_co2" in result
        assert result["total_co2"] == 100.0

    @pytest.mark.asyncio
    async def test_get_sustainability_recommendations(self, co2_mcpserver):
        """Test sustainability recommendations"""
        context_data = {"products": [{"name": "High-CO2 TV", "co2": 150}]}
        
        mock_recs = [{"category": "Products", "title": "Choose Eco-Friendly Alternatives"}]
        co2_mcpserver.get_sustainability_recommendations = AsyncMock(return_value=mock_recs)

        result = await co2_mcpserver.get_sustainability_recommendations(context_data)

        assert result is not None
        assert len(result) == 1
        assert result[0]["category"] == "Products"

    @pytest.mark.asyncio
    async def test_error_handling(self, co2_mcpserver):
        """Test error handling in CO2 API calls"""
        co2_mcpserver.calculate_product_co2 = AsyncMock(return_value={"error": "Calculation failed"})
        
        result = await co2_mcpserver.calculate_product_co2({})

        assert result is not None
        assert "error" in result


class TestMCPIntegration:
    """Test MCP server integration"""

    @pytest.mark.asyncio
    async def test_boutique_and_co2_integration(self):
        """Test that Boutique and CO2 MCP servers work together"""
        with patch('mcp_servers.boutique_mcp.httpx.AsyncClient'), \
             patch('mcp_servers.co2_mcp.httpx.AsyncClient'):

            # Mock boutique response
            boutique_mcpserver = BoutiqueMCPServer()
            mock_products = [{"id": "1", "name": "Eco Laptop", "price": 999.99, "category": "electronics"}]
            boutique_mcpserver.search_products = AsyncMock(return_value=mock_products)

            # Mock CO2 response
            co2_mcpserver = CO2MCPServer()
            co2_mcpserver.calculate_product_co2 = AsyncMock(return_value={"total_co2": 25.0})

            # Get product
            products = await boutique_mcpserver.search_products(query='')
            assert len(products) == 1
            product = products[0]

            # Calculate CO2
            co2_result = await co2_mcpserver.calculate_product_co2(product)
            assert co2_result["total_co2"] == 25.0


if __name__ == "__main__":
    pytest.main([__file__])