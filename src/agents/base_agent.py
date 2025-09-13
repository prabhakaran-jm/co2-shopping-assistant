"""
Base Agent Class for CO2-Aware Shopping Assistant

This module provides the base agent class that all specialized agents inherit from.
It implements common functionality and interfaces required by the ADK framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the CO2-Aware Shopping Assistant system.
    
    This class provides common functionality and interfaces that all agents
    must implement, following the Google ADK patterns.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gemini-2.0-flash",
        instruction: Optional[str] = None,
        tools: Optional[List[Any]] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Unique identifier for the agent
            description: Human-readable description of the agent's purpose
            model: LLM model to use (default: gemini-2.0-flash)
            instruction: System instruction/prompt for the agent
            tools: List of tools available to the agent
        """
        self.name = name
        self.description = description
        self.model = model
        self.instruction = instruction or self._get_default_instruction()
        self.tools = tools or []
        
        # Agent state
        self.status = "initialized"
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.metrics = {
            "requests_processed": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0
        }
        
        # A2A Agent Card (as mentioned in webinar)
        self.agent_card = self._create_agent_card()
        
        logger.info(
            "Agent initialized",
            agent_name=self.name,
            model=self.model,
            tools_count=len(self.tools)
        )
    
    def _get_default_instruction(self) -> str:
        """Get default instruction for the agent."""
        return f"""You are {self.name}, a specialized AI agent for the CO2-Aware Shopping Assistant.

Description: {self.description}

Your role is to help users make environmentally conscious shopping decisions by providing:
- Intelligent product recommendations
- Real-time CO2 emission calculations
- Eco-friendly alternatives
- Sustainable shipping options

Always prioritize environmental impact in your recommendations while considering user preferences and needs.
Provide clear, helpful responses and explain the environmental benefits of your suggestions."""
    
    @abstractmethod
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            message: User's message/query
            session_id: Session identifier for context
            
        Returns:
            Dictionary containing the agent's response
        """
        pass
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task assigned to this agent.
        
        Args:
            task: Task definition with parameters
            
        Returns:
            Dictionary containing task results
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for this agent.
        
        Returns:
            Dictionary containing health status information
        """
        try:
            # Basic health checks
            uptime = (datetime.now() - self.created_at).total_seconds()
            
            health_status = {
                "status": "healthy",
                "agent_name": self.name,
                "uptime_seconds": uptime,
                "last_activity": self.last_activity.isoformat(),
                "metrics": self.metrics.copy()
            }
            
            # Check if agent is responsive
            test_response = await self._internal_health_check()
            health_status.update(test_response)
            
            return health_status
            
        except Exception as e:
            logger.error("Health check failed", agent_name=self.name, error=str(e))
            return {
                "status": "unhealthy",
                "agent_name": self.name,
                "error": str(e)
            }
    
    async def _internal_health_check(self) -> Dict[str, Any]:
        """
        Internal health check specific to each agent.
        Override in subclasses for agent-specific checks.
        
        Returns:
            Dictionary with additional health information
        """
        return {"internal_status": "ok"}
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the agent.
        
        Returns:
            Dictionary containing current agent status
        """
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "model": self.model,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "tools_count": len(self.tools),
            "metrics": self.metrics.copy()
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this agent.
        
        Returns:
            Dictionary containing agent metrics
        """
        return self.metrics.copy()
    
    def _update_metrics(self, success: bool, response_time: float):
        """
        Update agent metrics.
        
        Args:
            success: Whether the request was successful
            response_time: Time taken to process the request
        """
        self.metrics["requests_processed"] += 1
        self.metrics["total_response_time"] += response_time
        self.metrics["average_response_time"] = (
            self.metrics["total_response_time"] / self.metrics["requests_processed"]
        )
        
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
        
        self.last_activity = datetime.now()
    
    async def _call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Call a tool available to this agent.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        for tool in self.tools:
            if hasattr(tool, 'name') and tool.name == tool_name:
                try:
                    result = await tool.execute(parameters)
                    logger.info(
                        "Tool executed successfully",
                        agent_name=self.name,
                        tool_name=tool_name
                    )
                    return result
                except Exception as e:
                    logger.error(
                        "Tool execution failed",
                        agent_name=self.name,
                        tool_name=tool_name,
                        error=str(e)
                    )
                    raise
        
        raise ValueError(f"Tool '{tool_name}' not found")
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}', status='{self.status}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"model='{self.model}', "
            f"tools={len(self.tools)}, "
            f"status='{self.status}'"
            f")"
        )
    
    def _create_agent_card(self) -> Dict[str, Any]:
        """
        Create an A2A agent card for discovery and communication.
        
        This implements the agent card concept mentioned in the webinar,
        allowing agents to present their capabilities to other agents.
        
        Returns:
            Dictionary containing agent capabilities and metadata
        """
        return {
            "agent_id": self.name,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "capabilities": [
                "environmental_consciousness",
                "product_search",
                "recommendations",
                "a2a_communication"
            ],
            "tools": [tool.name for tool in self.tools] if self.tools else [],
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "examples": self._get_agent_examples(),
            "tags": self._get_agent_tags()
        }
    
    def _get_agent_examples(self) -> List[str]:
        """Get example queries this agent can handle."""
        return [
            "Find eco-friendly products in category X",
            "Recommend sustainable alternatives",
            "Calculate environmental impact"
        ]
    
    def _get_agent_tags(self) -> List[str]:
        """Get tags describing this agent's specialization."""
        return ["environmental", "shopping", "ai", "sustainability"]
