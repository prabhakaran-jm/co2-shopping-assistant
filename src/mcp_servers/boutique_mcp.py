"""
Boutique MCP Server for CO2-Aware Shopping Assistant

This MCP server provides standardized access to Online Boutique APIs
for product catalog, cart operations, and order management.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
import httpx
from grpc import aio
import sys
import os
import time
import functools

# Add protos directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'protos'))

# Import generated gRPC stubs
import demo_pb2 as pb2
import demo_pb2_grpc as pb2_grpc

logger = structlog.get_logger(__name__)

class CircuitBreaker:
    """A simple implementation of the circuit breaker pattern."""
    def __init__(self, fail_max: int, reset_timeout: int):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.fail_count = 0
        self.state = "closed"
        self.last_failure_time = None

    def record_failure(self):
        self.fail_count += 1
        self.last_failure_time = time.time()
        if self.fail_count >= self.fail_max:
            self.state = "open"
            logger.warning(f"Circuit breaker for service has been opened.")

    def record_success(self):
        self.fail_count = 0
        self.state = "closed"

    @property
    def is_open(self) -> bool:
        if self.state == "open":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "half-open"
                return False
            return True
        return False

class BoutiqueMCPServer:
    """
    MCP Server for Online Boutique integration.
    """
    
    def __init__(self, boutique_base_url: str = "http://online-boutique.online-boutique.svc.cluster.local"):
        self.boutique_base_url = boutique_base_url
        self.running = False

        product_catalog_addr = os.getenv("PRODUCT_CATALOG_ADDR", "productcatalogservice.online-boutique.svc.cluster.local:3550")
        cartservice_addr = os.getenv("CARTSERVICE_ADDR", "http://cartservice.online-boutique.svc.cluster.local:7070")
        checkoutservice_addr = os.getenv("CHECKOUTSERVICE_ADDR", "http://checkoutservice.online-boutique.svc.cluster.local:5050")
        recommendation_addr = os.getenv("RECOMMENDATION_SERVICE_ADDR", "http://recommendationservice.online-boutique.svc.cluster.local:8080")
        currency_addr = os.getenv("CURRENCYSERVICE_ADDR", "http://currencyservice.online-boutique.svc.cluster.local:7000")

        proxy_base = os.getenv("OB_PROXY_BASE_URL") or os.getenv("BOUTIQUE_BASE_URL")
        if proxy_base:
            cartservice_addr = os.getenv("CARTSERVICE_ADDR", f"{proxy_base}/cartservice")
            checkoutservice_addr = os.getenv("CHECKOUTSERVICE_ADDR", f"{proxy_base}/checkoutservice")
            recommendation_addr = os.getenv("RECOMMENDATION_SERVICE_ADDR", f"{proxy_base}/recommendationservice")
            currency_addr = os.getenv("CURRENCYSERVICE_ADDR", f"{proxy_base}/currencyservice")

        self.endpoints = {
            "product_catalog": product_catalog_addr,
            "cart_service": cartservice_addr,
            "checkout_service": checkoutservice_addr,
            "recommendation_service": recommendation_addr,
            "currency_service": currency_addr,
        }
        
        self.client = httpx.AsyncClient(timeout=5.0)
        self.circuit_breakers = {name: CircuitBreaker(fail_max=3, reset_timeout=60) for name in self.endpoints}
        self._product_cache = []
        self._cache_last_updated = None

        logger.info("Boutique MCP Server initialized", base_url=boutique_base_url)

    @staticmethod
    def retry_with_breaker(service_name: str, fallback_method: str):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(self, *args, **kwargs):
                breaker = self.circuit_breakers[service_name]
                if breaker.is_open:
                    logger.warning(f"Circuit breaker for {service_name} is open. Using fallback.")
                    return await getattr(self, fallback_method)(*args, **kwargs)

                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        result = await func(self, *args, **kwargs)
                        breaker.record_success()
                        return result
                    except Exception as e:
                        logger.error(f"Attempt {attempt + 1} for {service_name} failed.", error=str(e))
                        if attempt == max_retries - 1:
                            breaker.record_failure()
                            logger.error(f"All retries for {service_name} failed. Using fallback.")
                            return await getattr(self, fallback_method)(*args, **kwargs)
                        await asyncio.sleep(1 * (2 ** attempt)) # Exponential backoff
            return wrapper
        return decorator

    async def start(self):
        self.running = True
        skip_checks = os.getenv("SKIP_MCP_STARTUP_CHECKS", "").lower() in ("1", "true", "yes")
        if skip_checks:
            logger.info("Skipping MCP startup connectivity checks per env")
        else:
            asyncio.create_task(self._test_connectivity_background())
        logger.info("Boutique MCP Server started")

    async def stop(self):
        self.running = False
        await self.client.aclose()
        logger.info("Boutique MCP Server stopped")

    async def _test_connectivity(self):
        async def probe(service_name: str, endpoint: str):
            # ... (implementation from previous steps)
            pass
        tasks = [probe(name, ep) for name, ep in self.endpoints.items()]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _test_connectivity_background(self):
        try:
            await asyncio.sleep(1.0)
            await self._test_connectivity()
        except Exception:
            pass

    @retry_with_breaker("product_catalog", "_fallback_search_products")
    async def search_products(self, query: str, category: Optional[str] = None, max_price: Optional[float] = None, min_price: Optional[float] = None, limit: int = 20) -> List[Dict[str, Any]]:
        logger.info("Searching for products", query=query, category=category, max_price=max_price, min_price=min_price)
        try:
            async with aio.insecure_channel(self.endpoints["product_catalog"]) as channel:
                stub = pb2_grpc.ProductCatalogServiceStub(channel)
                request = pb2.Empty()
                response = await stub.ListProducts(request)
                
                products = []
                for product_pb in response.products:
                    products.append({
                        "id": product_pb.id,
                        "name": product_pb.name,
                        "description": product_pb.description,
                        "picture": product_pb.picture,
                        "price": product_pb.price_usd.units + product_pb.price_usd.nanos / 1e9,
                        "categories": list(product_pb.categories),
                    })

                # Client-side filtering with improved search
                query_lower = query.lower().strip()
                show_all_commands = ["show all", "all products", "show me all", "list all", "show products", "products", "show all products", ""]
                
                if query and query_lower not in show_all_commands:
                    # First try exact matches
                    exact_matches = [p for p in products if query_lower in p['name'].lower() or query_lower in p['description'].lower()]
                    
                    if exact_matches:
                        products = exact_matches
                    else:
                        # If no exact matches, try category-based and fuzzy matching
                        products = self._intelligent_product_search(query_lower, products)
                
                if category:
                    products = [p for p in products if category in p['categories']]

                if min_price is not None:
                    products = [p for p in products if p['price'] >= min_price]

                if max_price is not None:
                    products = [p for p in products if p['price'] <= max_price]

                self._product_cache = products[:limit]
                self._cache_last_updated = datetime.now()
                
                return self._product_cache
        except Exception as e:
            logger.error("Failed to search products via gRPC", error=str(e))
            logger.info("Falling back to cached/mock products")
            return await self._fallback_search_products(query, category, max_price, min_price, limit)
    
    def _intelligent_product_search(self, query: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Intelligent product search with category mapping and fuzzy matching."""
        
        # Category mapping for common search terms
        category_mappings = {
            # Electronics
            "laptop": ["electronics", "accessories"],
            "computer": ["electronics", "accessories"], 
            "phone": ["electronics", "accessories"],
            "smartphone": ["electronics", "accessories"],
            "tablet": ["electronics", "accessories"],
            "camera": ["electronics", "accessories"],
            "gaming": ["electronics", "accessories"],
            "tech": ["electronics", "accessories"],
            
            # Clothing
            "shirt": ["clothing", "tops"],
            "t-shirt": ["clothing", "tops"],
            "pants": ["clothing", "footwear"],
            "jeans": ["clothing", "footwear"],
            "dress": ["clothing", "tops"],
            "jacket": ["clothing", "tops"],
            "shoes": ["footwear"],
            "boots": ["footwear"],
            "sneakers": ["footwear"],
            
            # Home & Kitchen
            "kitchen": ["kitchen"],
            "cookware": ["kitchen"],
            "appliance": ["kitchen", "hair", "beauty"],
            "home": ["home", "decor"],
            "decor": ["decor", "home"],
            "furniture": ["home", "decor"],
            
            # Beauty & Personal Care
            "beauty": ["beauty", "hair"],
            "skincare": ["beauty", "hair"],
            "makeup": ["beauty", "hair"],
            "hair": ["hair", "beauty"],
            "shampoo": ["hair", "beauty"],
            "conditioner": ["hair", "beauty"],
            
            # Accessories
            "accessory": ["accessories"],
            "jewelry": ["accessories"],
            "bag": ["accessories"],
            "purse": ["accessories"],
            "wallet": ["accessories"],
            "belt": ["accessories"]
        }
        
        # Find matching categories
        matching_categories = set()
        query_words = query.split()
        
        for word in query_words:
            if word in category_mappings:
                matching_categories.update(category_mappings[word])
        
        # If we found matching categories, return products from those categories
        if matching_categories:
            category_products = []
            for product in products:
                if any(cat in product.get('categories', []) for cat in matching_categories):
                    category_products.append(product)
            
            if category_products:
                # Add explanation to each product
                for product in category_products:
                    product['search_explanation'] = f"I couldn't find '{query}' exactly, but here are similar products from the {', '.join(matching_categories)} category:"
                return category_products
        
        # If no category matches, return all products with explanation
        for product in products:
            product['search_explanation'] = f"I couldn't find '{query}' in our catalog, but here are all available products:"
        return products

    async def _fallback_search_products(self, *args, **kwargs) -> List[Dict[str, Any]]:
        logger.warning("Using cached product data as fallback for search_products.")
        if self._product_cache:
            return self._product_cache
        
        # Return mock products if cache is empty - matching UI products
        return [
            {"id": "mock-1", "name": "Sunglasses", "description": "Stylish black sunglasses with UV protection.", "price": 19.99, "categories": ["accessories"], "picture": "/ob-images/static/img/products/sunglasses.jpg"},
            {"id": "mock-2", "name": "Watch", "description": "Elegant watch with leather strap and gold casing.", "price": 109.99, "categories": ["accessories"], "picture": "/ob-images/static/img/products/watch.jpg"},
            {"id": "mock-3", "name": "Loafers", "description": "Comfortable beige loafers with tassels.", "price": 89.99, "categories": ["apparel"], "picture": "/ob-images/static/img/products/loafers.jpg"},
        ]

    @retry_with_breaker("product_catalog", "_fallback_get_product_details")
    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        logger.info("Getting product details", product_id=product_id)
        try:
            async with aio.insecure_channel(self.endpoints["product_catalog"]) as channel:
                stub = pb2_grpc.ProductCatalogServiceStub(channel)
                request = pb2.GetProductRequest(id=product_id)
                product_pb = await stub.GetProduct(request)

                if not product_pb or not product_pb.id:
                    return None

                return {
                    "id": product_pb.id,
                    "name": product_pb.name,
                    "description": product_pb.description,
                    "picture": product_pb.picture,
                    "price": product_pb.price_usd.units + product_pb.price_usd.nanos / 1e9,
                    "categories": list(product_pb.categories),
                }
        except Exception as e:
            logger.error("Failed to get product details via gRPC", product_id=product_id, error=str(e))
            logger.info("Falling back to cached/mock product details")
            return await self._fallback_get_product_details(product_id)

    async def _fallback_get_product_details(self, product_id: str, *args, **kwargs) -> Optional[Dict[str, Any]]:
        logger.warning(f"Using cached product data as fallback for get_product_details for product_id: {product_id}")
        for product in self._product_cache:
            if product.get("id") == product_id:
                return product
        
        mock_products = [
            {"id": "mock-1", "name": "Sunglasses", "description": "Stylish black sunglasses with UV protection.", "price": 19.99, "categories": ["accessories"], "picture": "/ob-images/static/img/products/sunglasses.jpg"},
            {"id": "mock-2", "name": "Watch", "description": "Elegant watch with leather strap and gold casing.", "price": 109.99, "categories": ["accessories"], "picture": "/ob-images/static/img/products/watch.jpg"},
            {"id": "mock-3", "name": "Loafers", "description": "Comfortable beige loafers with tassels.", "price": 89.99, "categories": ["apparel"], "picture": "/ob-images/static/img/products/loafers.jpg"},
        ]
        for product in mock_products:
            if product.get("id") == product_id:
                return product

        return None

    # ... (Apply decorator and add fallbacks for other service calls: get_product_categories, add_to_cart, etc.)

    async def health_check(self) -> Dict[str, Any]:
        health_status = {
            "status": "healthy",
            "services": {},
            "timestamp": datetime.now().isoformat()
        }
        for service_name, endpoint in self.endpoints.items():
            breaker = self.circuit_breakers[service_name]
            health_status["services"][service_name] = {
                "status": "healthy" if not breaker.is_open else "unhealthy",
                "circuit_breaker_state": breaker.state,
                "failure_count": breaker.fail_count
            }
        unhealthy_services = [name for name, status in health_status["services"].items() if status["status"] != "healthy"]
        if unhealthy_services:
            health_status["status"] = "degraded"
            health_status["unhealthy_services"] = unhealthy_services
        return health_status

    # ... (rest of the methods)