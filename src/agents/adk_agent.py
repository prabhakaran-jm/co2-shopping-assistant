"""
ADK-based Agent for CO2-Aware Shopping Assistant

This module demonstrates minimal integration with Google's Agent Development Kit (ADK).
It creates a simple ADK agent that can handle eco-friendly product recommendations.
"""

from typing import Dict, Any, Optional 
import structlog
import importlib.metadata 
 
# ADK imports 
try: 
    from google.adk import Agent, Runner 
    from google.adk.tools import BaseTool 
    from google.adk.models import Gemini 
    from google.adk.sessions import InMemorySessionService 
    from google.genai import types 
    ADK_AVAILABLE = True 
except ImportError as e: 
    logger = structlog.get_logger(__name__) 
    logger.warning(f"ADK not available: {e}") 
    ADK_AVAILABLE = False 
    Agent = None 
    Runner = None 
    BaseTool = None 
    Gemini = None 
    InMemorySessionService = None 
    types = None 
 
logger = structlog.get_logger(__name__) 
 
# Define tool class only if ADK is available 
if ADK_AVAILABLE and BaseTool is not None: 
    class EcoRecommendationTool(BaseTool): 
        """ADK Tool for eco-friendly product recommendations.""" 
         
        def __init__(self, boutique_mcp_server=None): 
            super().__init__( 
                name="eco_recommendation", 
                description="Get eco-friendly product recommendations based on user preferences" 
            ) 
            self.boutique_mcp_server = boutique_mcp_server 
         
        async def execute(self, query: str, max_price: Optional[float] = None,  
                         eco_score_min: Optional[float] = None) -> Dict[str, Any]: 
            """ 
            Execute eco-friendly product recommendation. 
             
            Args: 
                query: Product search query 
                max_price: Maximum price filter 
                eco_score_min: Minimum eco-score filter 
                 
            Returns: 
                Dictionary with recommended products 
            """ 
            try: 
                logger.info("ADK Tool: Executing eco recommendation",  
                           query=query, max_price=max_price, eco_score_min=eco_score_min) 
                 
                if not self.boutique_mcp_server: 
                    return { 
                        "success": False, 
                        "error": "Boutique MCP server not available", 
                        "products": [] 
                    } 
                 
                # Search for products 
                products = await self.boutique_mcp_server.search_products(query) 
                 
                if not products: 
                    return { 
                        "success": False, 
                        "error": "No products found", 
                        "products": [] 
                    } 
                 
                # Process products: parse price and eco_score once
                processed_products = []
                for product in products:
                    try:
                        # Parse price
                        price_str = product.get("price", "$0")
                        parsed_price = float(price_str.replace("$", "").replace(",", ""))
                        
                        # Parse eco_score
                        eco_score_str = product.get("eco_score", "0/10")
                        parsed_eco_score = float(eco_score_str.split("/")[0])
                        
                        # Store parsed values
                        product['parsed_price'] = parsed_price
                        product['parsed_eco_score'] = parsed_eco_score
                        
                        processed_products.append(product)
                    except (ValueError, TypeError, IndexError):
                        # Skip products with malformed data
                        continue
                
                # Apply filters using parsed values
                filtered_products = []
                for product in processed_products:
                    # Price filter
                    if max_price and product['parsed_price'] > max_price:
                        continue
                    
                    # Eco-score filter
                    if eco_score_min and product['parsed_eco_score'] < eco_score_min:
                        continue
                    
                    filtered_products.append(product)
                
                # Sort by eco-score (descending) using parsed values
                filtered_products.sort(key=lambda p: p['parsed_eco_score'], reverse=True)
                 
                return { 
                    "success": True, 
                    "products": filtered_products[:10],  # Limit to top 10 
                    "total_found": len(filtered_products), 
                    "filters_applied": { 
                        "max_price": max_price, 
                        "eco_score_min": eco_score_min 
                    } 
                } 
                 
            except Exception as e: 
                logger.error("ADK Tool: Error in eco recommendation", error=str(e)) 
                return { 
                    "success": False, 
                    "error": str(e), 
                    "products": [] 
                } 
else: 
    # Fallback class when ADK is not available 
    class EcoRecommendationTool: 
        """Fallback tool when ADK is not available.""" 
         
        def __init__(self, boutique_mcp_server=None): 
            self.boutique_mcp_server = boutique_mcp_server 
         
        async def execute(self, *args, **kwargs): 
            return { 
                "success": False, 
                "error": "ADK not available", 
                "products": [] 
            } 
 
class ADKEcoAgent: 
    """ADK-based Agent for eco-friendly shopping assistance.""" 
     
    def __init__(self, boutique_mcp_server=None): 
        """Initialize the ADK agent.""" 
        self.name = "ADKEcoAgent" 
        self.description = "ADK-powered eco-friendly shopping assistant" 
        self.boutique_mcp_server = boutique_mcp_server 
        self.agent = None 
        self.runner = None 
        self.tool = None 
         
        if not ADK_AVAILABLE: 
            logger.warning("ADK not available, ADK agent will not be functional") 
            return 
         
        try: 
            # Create the eco recommendation tool 
            self.tool = EcoRecommendationTool(boutique_mcp_server) 
             
            # Create ADK agent with Gemini model
            self.agent = Agent(
                name="ADKEcoAgent",
                model=Gemini(model_name="gemini-2.0-flash"),
                tools=[self.tool]
            )
             
            # CORRECTED: Create runner with proper InMemorySessionService
            # This provides the session management functionality that was missing
            session_service = InMemorySessionService()
            self.runner = Runner(
                app_name="co2-assistant",
                agent=self.agent,
                session_service=session_service
            )
             
            logger.info("ADK Eco Agent initialized successfully") 
             
        except Exception as e: 
            logger.error("Failed to initialize ADK agent", error=str(e)) 
            self.agent = None 
            self.runner = None
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process a user message using the ADK agent.
        
        Args:
            message: User message
            session_id: Session identifier (used as user_id for ADK runner)
            
        Returns:
            Response from ADK agent
        """
        if not self.agent or not self.runner:
            return {
                "success": False,
                "error": "ADK agent not available",
                "response": "I'm sorry, the ADK-powered eco assistant is not available right now."
            }
        
        try:
            logger.info("ADK Agent: Processing message", message=message, session_id=session_id)
            
            # THE FINAL SOLUTION: A single call to run_async with all required
            # keyword arguments, as revealed by the clean environment's error message.
            # run_async returns an async generator, so we need to iterate through it
            
            # First, ensure the session exists by creating it if needed
            try:
                session = await self.runner.session_service.get_session(session_id)
            except Exception:
                # Session doesn't exist, create it with proper parameters
                session = await self.runner.session_service.create_session(
                    app_name="co2-assistant",
                    user_id=session_id,
                    session_id=session_id
                )
            
            # Create proper Content object for the message
            content = types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )
            
            # Try using the synchronous run method instead of run_async
            generator = self.runner.run(
                user_id=session_id,      # Using session_id as the user identifier
                session_id=session_id,
                new_message=content
            )
            
            # Get the final result from the generator
            result = None
            for item in generator:
                result = item
            
            # Extract response content properly
            if result and hasattr(result, 'content'):
                response_text = result.content
            elif result and hasattr(result, 'text'):
                response_text = result.text
            elif result:
                response_text = str(result)
            else:
                response_text = "I couldn't process your request."
            
            return {
                "success": True,
                "response": response_text,
                "agent_type": "ADK",
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error("ADK Agent: Error processing message", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while processing your request."
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the ADK agent."""
        try:
            # Get dynamic ADK version
            adk_version = "unknown"
            if ADK_AVAILABLE:
                try:
                    adk_version = importlib.metadata.version("google-adk")
                except importlib.metadata.PackageNotFoundError:
                    adk_version = "installed but version not found"
            
            if not ADK_AVAILABLE:
                return {
                    "agent_name": "ADKEcoAgent",
                    "status": "unavailable",
                    "error": "ADK package not available",
                    "adk_version": adk_version
                }
            
            if not self.agent:
                return {
                    "agent_name": "ADKEcoAgent", 
                    "status": "unhealthy",
                    "error": "ADK agent not initialized",
                    "adk_version": adk_version
                }
            
            # Get dynamic model name from agent
            model_name = "unknown"
            if hasattr(self.agent, 'model') and hasattr(self.agent.model, 'model_name'):
                model_name = self.agent.model.model_name
            
            return {
                "agent_name": "ADKEcoAgent",
                "status": "healthy",
                "adk_version": adk_version,
                "tools_count": len(self.agent.tools) if self.agent.tools else 0,
                "model": model_name
            }
            
        except Exception as e:
            logger.error("ADK Agent health check failed", error=str(e))
            return {
                "agent_name": "ADKEcoAgent",
                "status": "unhealthy", 
                "error": str(e),
                "adk_version": "unknown"
            }
    
    async def stop(self):
        """Stop the ADK agent."""
        logger.info("ADK Eco Agent stopped")