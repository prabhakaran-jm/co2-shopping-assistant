"""
Host Agent - Central Orchestrator for CO2-Aware Shopping Assistant

This agent acts as the central router and orchestrator, processing user queries
and delegating tasks to specialized agents using the A2A protocol.
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from .base_agent import BaseAgent
from ..a2a.protocol import A2AProtocol

logger = structlog.get_logger(__name__)


class HostAgent(BaseAgent):
    """
    Host Agent that orchestrates all other agents in the system.
    
    This agent:
    - Processes natural language user queries
    - Routes requests to appropriate specialized agents
    - Coordinates multi-agent workflows
    - Manages session state and context
    """
    
    def __init__(self, sub_agents: List[BaseAgent]):
        """
        Initialize the Host Agent.
        
        Args:
            sub_agents: List of specialized agents to orchestrate
        """
        super().__init__(
            name="HostAgent",
            description="Central orchestrator for the CO2-Aware Shopping Assistant system",
            instruction=self._get_host_instruction(sub_agents)
        )
        
        self.sub_agents = {agent.name: agent for agent in sub_agents}
        self.a2a_protocol = A2AProtocol()
        self.session_contexts = {}
        
        logger.info(
            "Host Agent initialized",
            sub_agents=list(self.sub_agents.keys())
        )
    
    def _get_host_instruction(self, sub_agents: List[BaseAgent]) -> str:
        """Generate instruction for the host agent based on available sub-agents."""
        agent_descriptions = []
        for agent in sub_agents:
            agent_descriptions.append(f"- {agent.name}: {agent.description}")
        
        return f"""You are the Host Agent, the central orchestrator for the CO2-Aware Shopping Assistant.

Available specialized agents:
{chr(10).join(agent_descriptions)}

Your responsibilities:
1. Analyze user queries to understand their intent
2. Route requests to the most appropriate specialized agent(s)
3. Coordinate multi-step workflows when needed
4. Provide comprehensive responses by combining results from multiple agents
5. Maintain conversation context and session state

Routing Guidelines:
- Product searches, recommendations, and catalog queries → ProductDiscoveryAgent
- CO2 calculations, environmental impact, sustainability → CO2CalculatorAgent  
- Cart operations, adding/removing items, cart totals → CartManagementAgent
- Checkout, payment, order processing → CheckoutAgent
- Complex queries involving multiple aspects → Coordinate multiple agents

Always provide helpful, environmentally conscious responses that guide users toward sustainable shopping choices."""
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process user message and route to appropriate agents.
        
        Args:
            message: User's message/query
            session_id: Session identifier
            
        Returns:
            Dictionary containing the response
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("Processing user message", message=message, session_id=session_id)
            
            # Initialize session context if needed
            if session_id not in self.session_contexts:
                self.session_contexts[session_id] = {
                    "conversation_history": [],
                    "user_preferences": {},
                    "current_cart": {},
                    "last_activity": datetime.now()
                }
            
            # Update session context
            context = self.session_contexts[session_id]
            context["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "type": "user"
            })
            
            # Analyze user intent and determine routing
            intent = await self._analyze_intent(message, context)
            logger.info("Intent analyzed", intent=intent, session_id=session_id)
            
            # Route to appropriate agent(s)
            response = await self._route_request(message, intent, context, session_id)
            
            # Update conversation history
            context["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "agent_response": response,
                "type": "agent"
            })
            context["last_activity"] = datetime.now()
            
            # Update metrics
            response_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(success=True, response_time=response_time)
            
            return {
                "response": response,
                "session_id": session_id,
                "intent": intent,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Message processing failed", error=str(e), session_id=session_id)
            response_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(success=False, response_time=response_time)
            
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_intent(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user intent to determine routing strategy.
        
        Args:
            message: User's message
            context: Session context
            
        Returns:
            Dictionary containing intent analysis
        """
        message_lower = message.lower()
        
        # Intent classification based on keywords and patterns
        intent = {
            "primary_agent": None,
            "secondary_agents": [],
            "confidence": 0.0,
            "intent_type": "unknown",
            "parameters": {}
        }
        
        # Product discovery patterns
        product_keywords = [
            "find", "search", "look for", "show me", "recommend", "suggest",
            "product", "item", "buy", "purchase", "catalog", "browse"
        ]
        
        # CO2/environmental patterns
        co2_keywords = [
            "co2", "carbon", "emission", "environmental", "eco", "green",
            "sustainable", "climate", "footprint", "impact", "greenhouse"
        ]
        
        # Cart management patterns
        cart_keywords = [
            "cart", "add to cart", "remove from cart", "cart total", "quantity",
            "checkout", "proceed", "order", "buy now"
        ]
        
        # Checkout patterns
        checkout_keywords = [
            "checkout", "payment", "pay", "order", "purchase", "buy",
            "shipping", "delivery", "address", "billing"
        ]
        
        # Calculate confidence scores
        product_score = sum(1 for keyword in product_keywords if keyword in message_lower)
        co2_score = sum(1 for keyword in co2_keywords if keyword in message_lower)
        cart_score = sum(1 for keyword in cart_keywords if keyword in message_lower)
        checkout_score = sum(1 for keyword in checkout_keywords if keyword in message_lower)
        
        # Determine primary agent based on highest score
        scores = {
            "ProductDiscoveryAgent": product_score,
            "CO2CalculatorAgent": co2_score,
            "CartManagementAgent": cart_score,
            "CheckoutAgent": checkout_score
        }
        
        primary_agent = max(scores, key=scores.get)
        max_score = scores[primary_agent]
        
        if max_score > 0:
            intent["primary_agent"] = primary_agent
            intent["confidence"] = min(max_score / len(message.split()), 1.0)
            
            # Determine intent type
            if primary_agent == "ProductDiscoveryAgent":
                intent["intent_type"] = "product_search"
            elif primary_agent == "CO2CalculatorAgent":
                intent["intent_type"] = "environmental_analysis"
            elif primary_agent == "CartManagementAgent":
                intent["intent_type"] = "cart_operation"
            elif primary_agent == "CheckoutAgent":
                intent["intent_type"] = "checkout_process"
        
        # Extract parameters
        intent["parameters"] = await self._extract_parameters(message, intent["intent_type"])
        
        return intent
    
    async def _extract_parameters(self, message: str, intent_type: str) -> Dict[str, Any]:
        """
        Extract relevant parameters from user message.
        
        Args:
            message: User's message
            intent_type: Type of intent
            
        Returns:
            Dictionary containing extracted parameters
        """
        parameters = {}
        
        if intent_type == "product_search":
            # Extract product-related parameters
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', message)
            if price_match:
                parameters["max_price"] = float(price_match.group(1))
            
            category_match = re.search(r'(electronics|clothing|books|home|sports)', message.lower())
            if category_match:
                parameters["category"] = category_match.group(1)
        
        elif intent_type == "environmental_analysis":
            # Extract environmental parameters
            if "shipping" in message.lower():
                parameters["include_shipping"] = True
            
            if "compare" in message.lower():
                parameters["comparison_mode"] = True
        
        elif intent_type == "cart_operation":
            # Extract cart operation parameters
            if "add" in message.lower():
                parameters["operation"] = "add"
            elif "remove" in message.lower():
                parameters["operation"] = "remove"
            elif "clear" in message.lower():
                parameters["operation"] = "clear"
        
        return parameters
    
    async def _route_request(
        self, 
        message: str, 
        intent: Dict[str, Any], 
        context: Dict[str, Any],
        session_id: str
    ) -> str:
        """
        Route request to appropriate agent(s) and combine responses.
        
        Args:
            message: User's message
            intent: Intent analysis result
            context: Session context
            session_id: Session identifier
            
        Returns:
            Combined response from agents
        """
        primary_agent_name = intent.get("primary_agent")
        
        if not primary_agent_name or primary_agent_name not in self.sub_agents:
            # Fallback to general response
            return await self._generate_fallback_response(message, context)
        
        try:
            # Route to primary agent
            primary_agent = self.sub_agents[primary_agent_name]
            
            # Prepare task for the agent
            task = {
                "message": message,
                "intent": intent,
                "context": context,
                "session_id": session_id,
                "parameters": intent.get("parameters", {})
            }
            
            # Execute task using A2A protocol
            response = await self.a2a_protocol.send_request(
                agent_name=primary_agent_name,
                task=task
            )
            
            # Process response
            if isinstance(response, dict) and "response" in response:
                return response["response"]
            else:
                return str(response)
                
        except Exception as e:
            logger.error(
                "Agent routing failed",
                agent_name=primary_agent_name,
                error=str(e),
                session_id=session_id
            )
            return await self._generate_fallback_response(message, context)
    
    async def _generate_fallback_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate a fallback response when routing fails.
        
        Args:
            message: User's message
            context: Session context
            
        Returns:
            Fallback response
        """
        return f"""I understand you're looking for help with shopping. I'm your CO2-Aware Shopping Assistant, designed to help you make environmentally conscious purchasing decisions.

I can help you with:
- Finding eco-friendly products
- Calculating CO2 emissions for your purchases
- Managing your shopping cart
- Processing orders with sustainable shipping options

Could you please rephrase your request? For example:
- "Find me eco-friendly electronics under $200"
- "What's the carbon footprint of this product?"
- "Add this item to my cart"
- "Show me sustainable shipping options"

I'm here to help you shop more sustainably! 🌱"""
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task assigned to the host agent.
        
        Args:
            task: Task definition
            
        Returns:
            Task execution result
        """
        task_type = task.get("type", "unknown")
        
        if task_type == "coordinate_workflow":
            return await self._coordinate_workflow(task)
        elif task_type == "session_management":
            return await self._manage_session(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _coordinate_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate a multi-agent workflow."""
        workflow_steps = task.get("steps", [])
        results = []
        
        for step in workflow_steps:
            agent_name = step.get("agent")
            step_task = step.get("task", {})
            
            if agent_name in self.sub_agents:
                agent = self.sub_agents[agent_name]
                result = await agent.execute_task(step_task)
                results.append({
                    "step": step,
                    "result": result
                })
        
        return {
            "workflow_results": results,
            "status": "completed"
        }
    
    async def _manage_session(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Manage session state and context."""
        session_id = task.get("session_id")
        action = task.get("action", "get")
        
        if action == "get":
            return self.session_contexts.get(session_id, {})
        elif action == "clear":
            if session_id in self.session_contexts:
                del self.session_contexts[session_id]
            return {"status": "cleared"}
        else:
            return {"error": f"Unknown session action: {action}"}
    
    async def _internal_health_check(self) -> Dict[str, Any]:
        """Internal health check for the host agent."""
        # Check sub-agents health
        sub_agent_health = {}
        for name, agent in self.sub_agents.items():
            try:
                health = await agent.health_check()
                sub_agent_health[name] = health["status"]
            except Exception as e:
                sub_agent_health[name] = f"error: {str(e)}"
        
        # Check A2A protocol
        a2a_status = await self.a2a_protocol.health_check()
        
        return {
            "internal_status": "ok",
            "sub_agents_health": sub_agent_health,
            "a2a_protocol_status": a2a_status,
            "active_sessions": len(self.session_contexts)
        }
