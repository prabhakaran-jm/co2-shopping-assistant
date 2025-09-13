"""
Pytest configuration and shared fixtures for CO2-Aware Shopping Assistant tests
"""
import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, patch
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_data():
    """Load sample test data from fixtures"""
    fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_data.json')
    with open(fixtures_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing"""
    mock_llm = Mock()
    mock_llm.run.return_value = "Mock LLM response"
    return mock_llm


@pytest.fixture
def mock_boutique_mcp():
    """Create a mock Boutique MCP server"""
    mock_mcp = Mock()
    mock_mcp.list_products.return_value = {
        "products": [
            {"id": "1", "name": "Eco Laptop", "price": 999.99},
            {"id": "2", "name": "Green Phone", "price": 599.99}
        ]
    }
    mock_mcp.get_product.return_value = {
        "id": "1",
        "name": "Eco Laptop",
        "price": 999.99,
        "description": "Environmentally friendly laptop"
    }
    mock_mcp.add_to_cart.return_value = {
        "success": True,
        "cart_id": "cart_123"
    }
    mock_mcp.view_cart.return_value = {
        "items": [{"product_id": "1", "quantity": 1, "price": 999.99}],
        "total": 999.99
    }
    mock_mcp.checkout.return_value = {
        "success": True,
        "order_id": "order_123",
        "total": 999.99
    }
    return mock_mcp


@pytest.fixture
def mock_co2_mcp():
    """Create a mock CO2 MCP server"""
    mock_mcp = Mock()
    mock_mcp.calculate_product_co2.return_value = {
        "co2_emissions": 2.5,
        "unit": "kg",
        "category": "electronics"
    }
    mock_mcp.calculate_shipping_co2.return_value = {
        "co2_emissions": 0.8,
        "unit": "kg",
        "method": "standard"
    }
    mock_mcp.get_eco_friendly_shipping.return_value = {
        "recommendations": [
            {"method": "electric_delivery", "co2_emissions": 0.2},
            {"method": "bike_delivery", "co2_emissions": 0.1}
        ]
    }
    return mock_mcp


@pytest.fixture
def mock_host_agent():
    """Create a mock host agent"""
    mock_agent = Mock()
    mock_agent.run.return_value = "Mock host agent response"
    return mock_agent


@pytest.fixture
def mock_specialized_agents():
    """Create mock specialized agents"""
    return {
        'product_discovery': Mock(),
        'co2_calculator': Mock(),
        'cart_management': Mock(),
        'checkout': Mock()
    }


@pytest.fixture
def test_session_id():
    """Generate a test session ID"""
    return "test_session_12345"


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'GOOGLE_AI_API_KEY': 'test_api_key',
        'PROJECT_ID': 'test_project',
        'LOCATION': 'us-central1',
        'ONLINE_BOUTIQUE_URL': 'http://test-boutique:80',
        'CO2_API_URL': 'https://test-co2-api.com'
    }):
        yield


@pytest.fixture
def mock_requests():
    """Mock requests library for API calls"""
    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        # Configure mock responses
        mock_get.return_value.json.return_value = {"success": True}
        mock_post.return_value.json.return_value = {"success": True}
        
        yield {
            'get': mock_get,
            'post': mock_post
        }


@pytest.fixture
def mock_a2a_message():
    """Create a sample A2A message for testing"""
    from a2a.protocol import A2AMessage
    
    return A2AMessage(
        sender="host_agent",
        recipient="product_discovery_agent",
        action="search_products",
        payload={"query": "eco-friendly laptops", "filters": {"price_max": 1000}},
        session_id="test_session_123"
    )


@pytest.fixture
def mock_user_query():
    """Sample user query for testing"""
    return "Find me eco-friendly laptops under $1500"


@pytest.fixture
def mock_eco_response():
    """Sample eco-friendly response for testing"""
    return """
    I found several eco-friendly laptops for you:
    1. EcoLaptop Air - $1299 (1.8 kg CO2 emissions)
    2. GreenBook Pro - $999 (2.1 kg CO2 emissions)
    3. SustainableBook - $799 (2.5 kg CO2 emissions)
    
    The EcoLaptop Air has the lowest carbon footprint!
    """


@pytest.fixture
def mock_co2_calculation():
    """Sample CO2 calculation response"""
    return {
        "co2_emissions": 1.8,
        "unit": "kg",
        "category": "electronics",
        "comparison": "30% lower than average",
        "savings": "0.7 kg CO2 saved"
    }


@pytest.fixture
def mock_cart_operation():
    """Sample cart operation response"""
    return {
        "success": True,
        "message": "EcoLaptop Air added to cart! Total CO2 impact: 1.8 kg",
        "cart_id": "cart_123",
        "total_co2": 1.8
    }


@pytest.fixture
def mock_checkout_result():
    """Sample checkout result"""
    return {
        "success": True,
        "order_id": "order_123",
        "message": "Order completed with eco-friendly shipping! 🌱",
        "total_co2": 2.0,
        "co2_savings": 0.7
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location"""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Mark slow tests
        if "performance" in str(item.fspath) or "concurrent" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
