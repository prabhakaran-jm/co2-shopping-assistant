"""
Agent-to-Agent (A2A) Protocol Implementation

This module implements the A2A protocol for inter-agent communication
in the CO2-Aware Shopping Assistant system.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import structlog
import httpx

logger = structlog.get_logger(__name__)


class A2AMessage:
    """A2A message structure."""
    
    def __init__(
        self,
        message_id: str,
        sender: str,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.message_id = message_id
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.payload = payload
        self.timestamp = timestamp or datetime.now()
        self.status = "pending"
        self.response = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """Create message from dictionary."""
        message = cls(
            message_id=data["message_id"],
            sender=data["sender"],
            recipient=data["recipient"],
            message_type=data["message_type"],
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
        message.status = data.get("status", "pending")
        return message


class A2AProtocol:
    """
    Agent-to-Agent communication protocol implementation.
    
    This class handles:
    - Message routing between agents
    - Request/response patterns
    - Message queuing and delivery
    - Error handling and retries
    - Protocol discovery and negotiation
    """
    
    def __init__(self):
        """Initialize the A2A protocol."""
        self.agents = {}  # Registered agents
        self.message_queue = asyncio.Queue()
        self.pending_messages = {}  # message_id -> A2AMessage
        self.message_handlers = {}  # message_type -> handler function
        self.running = False
        
        # Protocol configuration
        self.max_retries = 3
        self.timeout_seconds = 30
        self.retry_delay = 1.0
        
        logger.info("A2A Protocol initialized")
    
    async def initialize(self):
        """Initialize the A2A protocol."""
        self.running = True
        
        # Start message processing loop
        asyncio.create_task(self._message_processing_loop())
        
        logger.info("A2A Protocol started")
    
    async def register_agent(self, agent_name: str, agent_instance: Any, endpoint: Optional[str] = None):
        """
        Register an agent with the A2A protocol.
        
        Args:
            agent_name: Unique name for the agent
            agent_instance: Agent instance
            endpoint: Optional HTTP endpoint for the agent
        """
        self.agents[agent_name] = {
            "instance": agent_instance,
            "endpoint": endpoint,
            "registered_at": datetime.now(),
            "status": "active"
        }
        
        logger.info("Agent registered", agent_name=agent_name, endpoint=endpoint)
    
    async def unregister_agent(self, agent_name: str):
        """Unregister an agent from the A2A protocol."""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info("Agent unregistered", agent_name=agent_name)
    
    async def send_request(
        self,
        agent_name: str,
        task: Dict[str, Any],
        message_type: str = "task_request",
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Send a request to a specific agent.
        
        Args:
            agent_name: Target agent name
            task: Task to execute
            message_type: Type of message
            timeout: Request timeout in seconds
            
        Returns:
            Response from the target agent
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not registered")
        
        # Create message
        message_id = f"MSG_{uuid.uuid4().hex[:8].upper()}"
        message = A2AMessage(
            message_id=message_id,
            sender="A2AProtocol",
            recipient=agent_name,
            message_type=message_type,
            payload=task
        )
        
        # Store pending message
        self.pending_messages[message_id] = message
        
        try:
            # Send message
            response = await self._send_message(message, timeout or self.timeout_seconds)
            
            # Update message status
            message.status = "completed"
            message.response = response
            
            return response
            
        except Exception as e:
            # Update message status
            message.status = "failed"
            message.response = {"error": str(e)}
            
            logger.error("A2A request failed", agent_name=agent_name, error=str(e))
            raise
        
        finally:
            # Clean up pending message
            if message_id in self.pending_messages:
                del self.pending_messages[message_id]
    
    async def send_broadcast(
        self,
        message_type: str,
        payload: Dict[str, Any],
        exclude_agents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send a broadcast message to all registered agents.
        
        Args:
            message_type: Type of message
            payload: Message payload
            exclude_agents: List of agents to exclude from broadcast
            
        Returns:
            Dictionary of responses from agents
        """
        exclude_agents = exclude_agents or []
        responses = {}
        
        for agent_name in self.agents:
            if agent_name not in exclude_agents:
                try:
                    response = await self.send_request(
                        agent_name=agent_name,
                        task=payload,
                        message_type=message_type
                    )
                    responses[agent_name] = response
                except Exception as e:
                    responses[agent_name] = {"error": str(e)}
        
        return responses
    
    async def register_message_handler(self, message_type: str, handler: Callable):
        """
        Register a message handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        self.message_handlers[message_type] = handler
        logger.info("Message handler registered", message_type=message_type)
    
    async def _send_message(self, message: A2AMessage, timeout: float) -> Dict[str, Any]:
        """Send a message to the target agent."""
        agent_info = self.agents[message.recipient]
        
        if agent_info["endpoint"]:
            # Send via HTTP endpoint
            return await self._send_http_message(message, agent_info["endpoint"], timeout)
        else:
            # Send directly to agent instance
            return await self._send_direct_message(message, agent_info["instance"], timeout)
    
    async def _send_http_message(self, message: A2AMessage, endpoint: str, timeout: float) -> Dict[str, Any]:
        """Send message via HTTP endpoint."""
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(
                    f"{endpoint}/a2a/message",
                    json=message.to_dict()
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"HTTP request failed: {str(e)}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
    
    async def _send_direct_message(self, message: A2AMessage, agent_instance: Any, timeout: float) -> Dict[str, Any]:
        """Send message directly to agent instance."""
        try:
            # Try to call the agent's process_message method
            if hasattr(agent_instance, 'process_message'):
                response = await asyncio.wait_for(
                    agent_instance.process_message(
                        message.payload.get("message", ""),
                        message.payload.get("session_id", "default")
                    ),
                    timeout=timeout
                )
                return response
            
            # Try to call the agent's execute_task method
            elif hasattr(agent_instance, 'execute_task'):
                response = await asyncio.wait_for(
                    agent_instance.execute_task(message.payload),
                    timeout=timeout
                )
                return response
            
            else:
                raise Exception(f"Agent {message.recipient} does not support A2A communication")
                
        except asyncio.TimeoutError:
            raise Exception(f"Request to {message.recipient} timed out after {timeout} seconds")
        except Exception as e:
            raise Exception(f"Direct message failed: {str(e)}")
    
    async def _message_processing_loop(self):
        """Main message processing loop."""
        while self.running:
            try:
                # Process queued messages
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self._process_message(message)
                
                # Clean up old pending messages
                await self._cleanup_pending_messages()
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error("Message processing loop error", error=str(e))
                await asyncio.sleep(1.0)
    
    async def _process_message(self, message: A2AMessage):
        """Process a queued message."""
        try:
            # Check if we have a handler for this message type
            if message.message_type in self.message_handlers:
                handler = self.message_handlers[message.message_type]
                response = await handler(message)
                
                # Update message status
                message.status = "processed"
                message.response = response
                
                logger.info("Message processed", message_id=message.message_id)
            else:
                logger.warning("No handler for message type", message_type=message.message_type)
                
        except Exception as e:
            logger.error("Message processing failed", message_id=message.message_id, error=str(e))
            message.status = "failed"
            message.response = {"error": str(e)}
    
    async def _cleanup_pending_messages(self):
        """Clean up old pending messages."""
        current_time = datetime.now()
        timeout_threshold = current_time.timestamp() - (self.timeout_seconds * 2)
        
        expired_messages = []
        for message_id, message in self.pending_messages.items():
            if message.timestamp.timestamp() < timeout_threshold:
                expired_messages.append(message_id)
        
        for message_id in expired_messages:
            message = self.pending_messages[message_id]
            message.status = "timeout"
            del self.pending_messages[message_id]
            logger.warning("Message timed out", message_id=message_id)
    
    async def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of a specific agent."""
        if agent_name not in self.agents:
            return {"status": "not_registered"}
        
        agent_info = self.agents[agent_name]
        
        # Try to get health status from agent
        try:
            if hasattr(agent_info["instance"], 'health_check'):
                health_status = await agent_info["instance"].health_check()
            else:
                health_status = {"status": "unknown"}
        except Exception as e:
            health_status = {"status": "error", "error": str(e)}
        
        return {
            "status": agent_info["status"],
            "registered_at": agent_info["registered_at"].isoformat(),
            "endpoint": agent_info["endpoint"],
            "health": health_status
        }
    
    async def get_protocol_status(self) -> Dict[str, Any]:
        """Get overall protocol status."""
        return {
            "running": self.running,
            "registered_agents": list(self.agents.keys()),
            "pending_messages": len(self.pending_messages),
            "message_handlers": list(self.message_handlers.keys()),
            "configuration": {
                "max_retries": self.max_retries,
                "timeout_seconds": self.timeout_seconds,
                "retry_delay": self.retry_delay
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the A2A protocol."""
        try:
            # Check if protocol is running
            if not self.running:
                return {"status": "unhealthy", "error": "Protocol not running"}
            
            # Check registered agents
            agent_statuses = {}
            for agent_name in self.agents:
                agent_statuses[agent_name] = await self.get_agent_status(agent_name)
            
            # Check for any unhealthy agents
            unhealthy_agents = [
                name for name, status in agent_statuses.items()
                if status.get("health", {}).get("status") not in ["healthy", "unknown"]
            ]
            
            if unhealthy_agents:
                return {
                    "status": "degraded",
                    "unhealthy_agents": unhealthy_agents,
                    "agent_statuses": agent_statuses
                }
            
            return {
                "status": "healthy",
                "registered_agents": len(self.agents),
                "pending_messages": len(self.pending_messages),
                "agent_statuses": agent_statuses
            }
            
        except Exception as e:
            logger.error("A2A health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}
    
    async def shutdown(self):
        """Shutdown the A2A protocol."""
        self.running = False
        
        # Wait for pending messages to complete
        while self.pending_messages:
            await asyncio.sleep(0.1)
        
        logger.info("A2A Protocol shutdown complete")
    
    def __str__(self) -> str:
        """String representation of the A2A protocol."""
        return f"A2AProtocol(agents={len(self.agents)}, running={self.running})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the A2A protocol."""
        return (
            f"A2AProtocol("
            f"agents={list(self.agents.keys())}, "
            f"running={self.running}, "
            f"pending_messages={len(self.pending_messages)}"
            f")"
        )
