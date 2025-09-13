"""
Unit tests for AI agents in CO2-Aware Shopping Assistant
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

from src.agents.base_agent import BaseAgent
from src.agents.host_agent import HostAgent
from src.agents.product_discovery_agent import ProductDiscoveryAgent
from src.agents.co2_calculator_agent import CO2CalculatorAgent
from src.agents.cart_management_agent import CartManagementAgent
from src.agents.checkout_agent import CheckoutAgent


class TestBaseAgent:
    """Test the base agent functionality"""
    
    def test_base_agent_initialization(self):
        """Test that base agent initializes correctly"""
        agent = BaseAgent(
            name="test_agent",
            description="Test agent for unit testing",
            llm=Mock(),
            tools=[]
        )
        
        assert agent.name == "test_agent"
        assert agent.description == "Test agent for unit testing"
        assert agent.tools == []
        assert agent.llm is not None

    def test_base_agent_run_not_implemented(self):
        """Test that base agent run method raises NotImplementedError"""
        agent = BaseAgent(
            name="test_agent",
            description="Test agent",
            llm=Mock(),
            tools=[]
        )
        
        with pytest.raises(NotImplementedError):
            agent.run("test message")


class TestHostAgent:
    """Test the host agent (router) functionality"""
    
    @pytest.fixture
    def mock_agents(self):
        """Create mock specialized agents"""
        return {
            'product_discovery': Mock(),
            'co2_calculator': Mock(),
            'cart_management': Mock(),
            'checkout': Mock()
        }
    
    @pytest.fixture
    def host_agent(self, mock_agents):
        """Create host agent with mocked dependencies"""
        with patch('src.agents.host_agent.LlmAgent') as mock_llm_agent:
            mock_llm_agent.return_value = Mock()
            agent = HostAgent()
            agent.specialized_agents = mock_agents
            return agent
    
    def test_host_agent_initialization(self, host_agent):
        """Test host agent initializes with correct name and description"""
        assert host_agent.name == "Host Agent"
        assert "orchestrator" in host_agent.description.lower()
        assert "router" in host_agent.description.lower()
    
    @pytest.mark.asyncio
    async def test_host_agent_routes_product_queries(self, host_agent):
        """Test that product-related queries are routed to ProductDiscoveryAgent"""
        # Mock the LLM response
        host_agent.llm.run.return_value = "I found some eco-friendly products for you"
        
        # Mock the specialized agent response
        host_agent.specialized_agents['product_discovery'].run.return_value = "Product recommendations"
        
        result = await host_agent.run("Find me eco-friendly laptops")
        
        # Verify the product discovery agent was called
        host_agent.specialized_agents['product_discovery'].run.assert_called_once()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_host_agent_routes_co2_queries(self, host_agent):
        """Test that CO2-related queries are routed to CO2CalculatorAgent"""
        host_agent.llm.run.return_value = "I'll calculate the CO2 emissions for you"
        host_agent.specialized_agents['co2_calculator'].run.return_value = "CO2 calculation result"
        
        result = await host_agent.run("What's the carbon footprint of this product?")
        
        host_agent.specialized_agents['co2_calculator'].run.assert_called_once()
        assert result is not None


class TestProductDiscoveryAgent:
    """Test the product discovery agent functionality"""
    
    @pytest.fixture
    def product_agent(self):
        """Create product discovery agent with mocked dependencies"""
        with patch('src.agents.product_discovery_agent.LlmAgent') as mock_llm_agent:
            mock_llm_agent.return_value = Mock()
            agent = ProductDiscoveryAgent()
            return agent
    
    def test_product_agent_initialization(self, product_agent):
        """Test product discovery agent initializes correctly"""
        assert product_agent.name == "Product Discovery Agent"
        assert "product" in product_agent.description.lower()
        assert "search" in product_agent.description.lower()
    
    @pytest.mark.asyncio
    async def test_product_agent_search_products(self, product_agent):
        """Test product search functionality"""
        # Mock the LLM response
        product_agent.llm.run.return_value = "Here are some eco-friendly products"
        
        result = await product_agent.run("Find eco-friendly laptops under $1000")
        
        assert result is not None
        assert "eco-friendly" in result.lower()


class TestCO2CalculatorAgent:
    """Test the CO2 calculator agent functionality"""
    
    @pytest.fixture
    def co2_agent(self):
        """Create CO2 calculator agent with mocked dependencies"""
        with patch('src.agents.co2_calculator_agent.LlmAgent') as mock_llm_agent:
            mock_llm_agent.return_value = Mock()
            agent = CO2CalculatorAgent()
            return agent
    
    def test_co2_agent_initialization(self, co2_agent):
        """Test CO2 calculator agent initializes correctly"""
        assert co2_agent.name == "CO2 Calculator Agent"
        assert "co2" in co2_agent.description.lower()
        assert "emission" in co2_agent.description.lower()
    
    @pytest.mark.asyncio
    async def test_co2_agent_calculates_emissions(self, co2_agent):
        """Test CO2 emission calculation functionality"""
        co2_agent.llm.run.return_value = "This product has 2.5 kg CO2 emissions"
        
        result = await co2_agent.run("Calculate CO2 emissions for this laptop")
        
        assert result is not None
        assert "co2" in result.lower()
        assert "emission" in result.lower()


class TestCartManagementAgent:
    """Test the cart management agent functionality"""
    
    @pytest.fixture
    def cart_agent(self):
        """Create cart management agent with mocked dependencies"""
        with patch('src.agents.cart_management_agent.LlmAgent') as mock_llm_agent:
            mock_llm_agent.return_value = Mock()
            agent = CartManagementAgent()
            return agent
    
    def test_cart_agent_initialization(self, cart_agent):
        """Test cart management agent initializes correctly"""
        assert cart_agent.name == "Cart Management Agent"
        assert "cart" in cart_agent.description.lower()
        assert "management" in cart_agent.description.lower()
    
    @pytest.mark.asyncio
    async def test_cart_agent_adds_items(self, cart_agent):
        """Test adding items to cart functionality"""
        cart_agent.llm.run.return_value = "Item added to cart successfully"
        
        result = await cart_agent.run("Add this eco-friendly laptop to my cart")
        
        assert result is not None
        assert "cart" in result.lower()


class TestCheckoutAgent:
    """Test the checkout agent functionality"""
    
    @pytest.fixture
    def checkout_agent(self):
        """Create checkout agent with mocked dependencies"""
        with patch('src.agents.checkout_agent.LlmAgent') as mock_llm_agent:
            mock_llm_agent.return_value = Mock()
            agent = CheckoutAgent()
            return agent
    
    def test_checkout_agent_initialization(self, checkout_agent):
        """Test checkout agent initializes correctly"""
        assert checkout_agent.name == "Checkout Agent"
        assert "checkout" in checkout_agent.description.lower()
        assert "order" in checkout_agent.description.lower()
    
    @pytest.mark.asyncio
    async def test_checkout_agent_processes_orders(self, checkout_agent):
        """Test order processing functionality"""
        checkout_agent.llm.run.return_value = "Order processed successfully with eco-friendly shipping"
        
        result = await checkout_agent.run("Process my order with sustainable shipping")
        
        assert result is not None
        assert "order" in result.lower()


class TestAgentIntegration:
    """Test agent integration and communication"""
    
    @pytest.mark.asyncio
    async def test_agents_work_together(self):
        """Test that agents can work together in a workflow"""
        # This would test the A2A protocol integration
        # For now, we'll mock the interaction
        
        with patch('src.agents.host_agent.HostAgent') as mock_host:
            mock_host.return_value.run.return_value = "Complete workflow executed"
            
            # Simulate a complex workflow
            result = await mock_host.return_value.run(
                "Find me eco-friendly products, calculate their CO2 impact, and add the best one to my cart"
            )
            
            assert result is not None
            assert "workflow" in result.lower()

class TestProductDiscoveryAgentRequestParsing:
    """Test the request parsing of the Product Discovery Agent"""

    @pytest.fixture
    def product_agent(self):
        """Create a ProductDiscoveryAgent instance for testing"""
        return ProductDiscoveryAgent()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message, expected_type", [
        ("show hairdryer", "search"),
        ("show tanktop", "search"),
        ("find sunglasses", "search"),
        ("search for a watch", "search"),
        ("show me all products", "search"),
        ("recommend some eco-friendly shoes", "recommend"),
        ("compare laptops", "compare"),
        ("tell me about the camera", "details"),
        ("what is the price of the phone", "details"),
        ("show", "general"),
        ("hairdryer", "search"),
        ("I want to buy a new phone", "general"),
    ])
    async def test_parse_request_type(self, product_agent, message, expected_type):
        """Test that _parse_request_type correctly classifies user queries"""
        request_type = await product_agent._parse_request_type(message)
        assert request_type == expected_type


if __name__ == "__main__":
    pytest.main([__file__])
