"""
Host Agent - Central Orchestrator for CO2-Aware Shopping Assistant

This agent acts as the central router and orchestrator, processing user queries
and delegating tasks to specialized agents using the A2A protocol.
"""

import asyncio
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

You implement the Coordinator-Dispatcher pattern from modern agentic AI architectures:
- COORDINATOR: Analyze user intent and determine optimal agent workflow
- DISPATCHER: Route tasks to specialized agents based on capabilities

Available specialized agents:
{chr(10).join(agent_descriptions)}

You can orchestrate workflows using these patterns:
1. SEQUENTIAL: Step-by-step workflows (e.g., search → calculate CO2 → add to cart)
2. PARALLEL: Simultaneous operations (e.g., search multiple categories at once)  
3. HIERARCHICAL: Break complex requests into sub-tasks

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
            print(f"HOST: Processing user message: {message}")
            
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
            print(f"HOST: Intent analyzed: {intent}")
            
            # Route to appropriate agent(s)
            response = await self._route_request(message, intent, context, session_id)
            print(f"HOST: Received response from routing: {type(response)}")
            
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
        Analyze user intent to determine routing strategy with context awareness.
        
        Args:
            message: User's message
            context: Session context
            
        Returns:
            Dictionary containing intent analysis
        """
        message_lower = message.lower().strip()
        
        # Intent classification based on keywords and patterns
        intent = {
            "primary_agent": None,
            "secondary_agents": [],
            "confidence": 0.0,
            "intent_type": "unknown",
            "parameters": {}
        }
        
        # Check for follow-up questions and context
        conversation_history = context.get("conversation_history", [])
        last_agent_response = None
        if len(conversation_history) >= 2:
            last_agent_response = conversation_history[-2].get("agent_response", "")
        
        # Handle follow-up questions
        if await self._is_follow_up_question(message, last_agent_response):
            return await self._handle_follow_up_intent(message, last_agent_response, context)
        
        # Product discovery patterns (expanded)
        product_keywords = [
            "find", "search", "look for", "show me", "show", "recommend", "suggest",
            "product", "item", "buy", "purchase", "catalog", "browse",
            "sunglasses", "loafers", "watch", "hairdryer", "tank top", "shoes",
            "electronics", "clothing", "accessories", "home", "sports"
        ]
        
        # CO2/environmental patterns
        co2_keywords = [
            "co2", "carbon", "emission", "environmental", "eco", "green",
            "sustainable", "climate", "footprint", "impact", "greenhouse",
            "environmental benefits", "carbon footprint"
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
        
        # Comparison patterns
        comparison_keywords = [
            "compare", "comparison", "vs", "versus", "better", "best", "rank",
            "ranking", "top", "which is", "difference", "analyze", "analysis",
            "eco-value", "co2 efficiency", "price optimization", "comprehensive"
        ]
        
        # Calculate confidence scores
        product_score = sum(1 for keyword in product_keywords if keyword in message_lower)
        co2_score = sum(1 for keyword in co2_keywords if keyword in message_lower)
        cart_score = sum(1 for keyword in cart_keywords if keyword in message_lower)
        checkout_score = sum(1 for keyword in checkout_keywords if keyword in message_lower)
        comparison_score = sum(1 for keyword in comparison_keywords if keyword in message_lower)
        
        # Determine primary agent based on highest score
        scores = {
            "ProductDiscoveryAgent": product_score,
            "CO2CalculatorAgent": co2_score,
            "CartManagementAgent": cart_score,
            "CheckoutAgent": checkout_score,
            "ComparisonAgent": comparison_score
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
            elif primary_agent == "ComparisonAgent":
                intent["intent_type"] = "product_comparison"
        
        # Extract parameters with context
        intent["parameters"] = await self._extract_parameters(message, intent["intent_type"], context)
        
        return intent
    
    async def _is_follow_up_question(self, message: str, last_response: str) -> bool:
        """Check if the message is a follow-up question."""
        if not last_response:
            return False
        
        message_lower = message.lower().strip()
        
        # Simple follow-up indicators
        follow_up_indicators = [
            "yes", "no", "about", "more", "details", "tell me more",
            "what about", "how about", "can you", "could you"
        ]
        
        # Check for follow-up patterns
        for indicator in follow_up_indicators:
            if indicator in message_lower:
                return True
        
        # Check if message contains product names from last response
        if last_response:
            # Extract product names from last response (simplified)
            product_names = ["sunglasses", "loafers", "watch", "hairdryer", "tank top", "shoes"]
            for product in product_names:
                if product in message_lower and product in last_response.lower():
                    return True
        
        return False
    
    async def _handle_follow_up_intent(self, message: str, last_response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle follow-up questions with context awareness."""
        message_lower = message.lower().strip()
        
        # Default intent for follow-ups
        intent = {
            "primary_agent": "ProductDiscoveryAgent",
            "secondary_agents": [],
            "confidence": 0.8,
            "intent_type": "product_details",
            "parameters": {}
        }
        
        # Extract product reference from message or context
        product_reference = await self._extract_product_from_context(message, last_response)
        if product_reference:
            intent["parameters"]["product_reference"] = product_reference
            intent["parameters"]["query"] = product_reference
        
        # Determine specific intent type
        if "details" in message_lower or "about" in message_lower:
            intent["intent_type"] = "product_details"
        elif "co2" in message_lower or "carbon" in message_lower or "environmental" in message_lower:
            intent["intent_type"] = "environmental_analysis"
            intent["primary_agent"] = "CO2CalculatorAgent"
        elif "add" in message_lower or "cart" in message_lower:
            intent["intent_type"] = "cart_operation"
            intent["primary_agent"] = "CartManagementAgent"
        
        return intent
    
    async def _extract_product_from_context(self, message: str, last_response: str) -> Optional[str]:
        """Extract product reference from message or context."""
        message_lower = message.lower()
        
        # Common product names
        product_names = ["sunglasses", "loafers", "watch", "hairdryer", "tank top", "shoes", "electronics", "clothing"]
        
        # Check if message contains a product name
        for product in product_names:
            if product in message_lower:
                return product
        
        # Check if last response contained products and message is asking about them
        if last_response:
            for product in product_names:
                if product in last_response.lower() and ("about" in message_lower or "yes" in message_lower):
                    return product
        
        return None
    
    async def _extract_parameters(self, message: str, intent_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract relevant parameters from user message with context awareness.
        
        Args:
            message: User's message
            intent_type: Type of intent
            context: Session context for additional information
            
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
            
            # Extract specific product names
            product_names = ["sunglasses", "loafers", "watch", "hairdryer", "tank top", "shoes"]
            for product in product_names:
                if product in message.lower():
                    parameters["query"] = product
                    break
        
        elif intent_type == "product_details":
            # Extract product reference
            product_reference = await self._extract_product_from_context(message, "")
            if product_reference:
                parameters["product_reference"] = product_reference
                parameters["query"] = product_reference
        
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
        print(f"HOST: Primary agent: {primary_agent_name}")
        print(f"HOST: Available agents: {list(self.sub_agents.keys())}")
        
        if not primary_agent_name or primary_agent_name not in self.sub_agents:
            print(f"HOST: Agent not found, using fallback response")
            # Fallback to general response
            return await self._generate_fallback_response(message, context)
        
        try:
            print(f"HOST: Attempting to route to {primary_agent_name}")
            # Route to primary agent
            primary_agent = self.sub_agents[primary_agent_name]
            print(f"HOST: Found agent: {type(primary_agent)}")
            
            # Prepare task for the agent
            task = {
                "message": message,
                "intent": intent,
                "context": context,
                "session_id": session_id,
                "parameters": intent.get("parameters", {})
            }
            print(f"HOST: Prepared task: {task}")
            
            # Execute task using A2A protocol
            logger.info("HostAgent: Routing request to agent", agent_name=primary_agent_name, task=task)
            print(f"HOST: Calling A2A protocol send_request")
            response = await self.a2a_protocol.send_request(
                agent_name=primary_agent_name,
                task=task
            )
            print(f"HOST: Received response from A2A: {type(response)}")
            logger.info("HostAgent: Received response from agent", agent_name=primary_agent_name, response_type=type(response).__name__)
            
            # Process response
            if isinstance(response, dict) and "products" in response:
                return response  # It's already the structured product response
            
            if isinstance(response, dict) and "response" in response:
                # The actual response is nested, extract it
                return response["response"]
            
            # Fallback for simple string responses
            return str(response)
                
        except Exception as e:
            print(f"HOST: Exception in routing: {str(e)}")
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
    
    async def _determine_workflow_pattern(self, query: str, intent: Dict[str, Any]) -> str:
        """
        Determine the optimal workflow pattern based on query complexity.
        
        This implements the patterns discussed in the webinar:
        - Sequential: Step-by-step workflows
        - Parallel: Simultaneous operations
        - Hierarchical: Complex task decomposition
        
        Args:
            query: User query
            intent: Analyzed intent
            
        Returns:
            Workflow pattern: 'sequential', 'parallel', 'hierarchical', or 'simple'
        """
        # Complex multi-step queries → Sequential
        if any(keyword in query.lower() for keyword in [
            "then", "after that", "next", "step by step", "process"
        ]):
            return "sequential"
        
        # Multiple simultaneous searches → Parallel
        if any(keyword in query.lower() for keyword in [
            "and also", "both", "multiple", "several", "all of these"
        ]):
            return "parallel"
        
        # Complex planning → Hierarchical
        if any(keyword in query.lower() for keyword in [
            "plan", "organize", "arrange", "coordinate", "manage"
        ]):
            return "hierarchical"
        
        return "simple"
    
    async def _execute_sequential_workflow(self, query: str, intent: Dict[str, Any], session_id: str) -> str:
        """
        Execute a sequential workflow (replaces Saga pattern from microservices).
        
        Example: Search product → Calculate CO2 → Add to cart → Checkout
        
        Args:
            query: User query
            intent: Analyzed intent
            session_id: Session identifier
            
        Returns:
            Combined response from sequential steps
        """
        logger.info("Executing sequential workflow", query=query, session_id=session_id)
        
        steps = []
        context = self.session_contexts.get(session_id, {})
        
        # Step 1: Product Discovery
        if intent.get("needs_product_search", False):
            product_agent = self.sub_agents.get("ProductDiscoveryAgent")
            if product_agent:
                step_result = await product_agent.process_message(query, session_id)
                steps.append({"step": "product_discovery", "result": step_result})
                context["discovered_products"] = step_result
        
        # Step 2: CO2 Calculation
        if intent.get("needs_co2_calculation", False):
            co2_agent = self.sub_agents.get("CO2CalculatorAgent")
            if co2_agent:
                step_result = await co2_agent.process_message(query, session_id)
                steps.append({"step": "co2_calculation", "result": step_result})
                context["co2_data"] = step_result
        
        # Step 3: Cart Management
        if intent.get("needs_cart_operation", False):
            cart_agent = self.sub_agents.get("CartManagementAgent")
            if cart_agent:
                step_result = await cart_agent.process_message(query, session_id)
                steps.append({"step": "cart_management", "result": step_result})
                context["cart_state"] = step_result
        
        # Combine results
        return f"I've completed your request through a sequential workflow: {len(steps)} steps executed successfully."
