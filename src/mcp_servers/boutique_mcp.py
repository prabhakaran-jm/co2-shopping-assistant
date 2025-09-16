"""
Boutique MCP Server for CO2-Aware Shopping Assistant

This MCP server provides standardized access to Online Boutique APIs
for product catalog, cart operations, and order management.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import httpx
from grpc import aio
import sys
import os

# Add protos directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'protos'))

# Import generated gRPC stubs
import demo_pb2 as pb2
import demo_pb2_grpc as pb2_grpc

logger = structlog.get_logger(__name__)


class BoutiqueMCPServer:
    """
    MCP Server for Online Boutique integration.
    
    This server implements the MCP (Model Context Protocol),
    providing standardized access to Online Boutique APIs without requiring custom integrations.
    
    This server provides:
    - Product catalog access
    - Cart operations
    - Order management
    - Inventory checking
    
    Key MCP Features:
    - Standardized tool discovery
    - JSON-RPC communication
    - Resource management
    - Prompt templates
    """
    
    def __init__(self, boutique_base_url: str = "http://online-boutique.online-boutique.svc.cluster.local"):
        """
        Initialize the Boutique MCP Server.
        
        Args:
            boutique_base_url: Base URL for Online Boutique services
        """
        self.boutique_base_url = boutique_base_url
        self.running = False

        # Allow endpoint configuration via environment variables. If an HTTP proxy base is
        # provided (e.g., ob-proxy), callers can point HTTP services there.
        product_catalog_addr = os.getenv(
            "PRODUCT_CATALOG_ADDR",
            "productcatalogservice.online-boutique.svc.cluster.local:3550",
        )
        cartservice_addr = os.getenv(
            "CARTSERVICE_ADDR",
            "http://cartservice.online-boutique.svc.cluster.local:7070",
        )
        checkoutservice_addr = os.getenv(
            "CHECKOUTSERVICE_ADDR",
            "http://checkoutservice.online-boutique.svc.cluster.local:5050",
        )
        recommendation_addr = os.getenv(
            "RECOMMENDATION_SERVICE_ADDR",
            "http://recommendationservice.online-boutique.svc.cluster.local:8080",
        )
        currency_addr = os.getenv(
            "CURRENCYSERVICE_ADDR",
            "http://currencyservice.online-boutique.svc.cluster.local:7000",
        )

        # Optional proxy base (e.g., http://ob-proxy.<ns>.svc.cluster.local)
        proxy_base = os.getenv("OB_PROXY_BASE_URL") or os.getenv("BOUTIQUE_BASE_URL")
        if proxy_base:
            # If a proxy is provided, prefer routing HTTP services through it when not
            # explicitly overridden above. We keep product_catalog gRPC as-is.
            cartservice_addr = os.getenv("CARTSERVICE_ADDR", f"{proxy_base}/cartservice")
            checkoutservice_addr = os.getenv("CHECKOUTSERVICE_ADDR", f"{proxy_base}/checkoutservice")
            recommendation_addr = os.getenv("RECOMMENDATION_SERVICE_ADDR", f"{proxy_base}/recommendationservice")
            currency_addr = os.getenv("CURRENCYSERVICE_ADDR", f"{proxy_base}/currencyservice")

        # Service endpoints (may be gRPC host:port or HTTP URLs)
        self.endpoints = {
            "product_catalog": product_catalog_addr,  # gRPC
            "cart_service": cartservice_addr,        # HTTP or proxy HTTP
            "checkout_service": checkoutservice_addr,  # HTTP or proxy HTTP
            "recommendation_service": recommendation_addr,  # HTTP or proxy HTTP
            "currency_service": currency_addr,       # HTTP or proxy HTTP
        }
        
        # HTTP client with shorter default timeout for snappier startup
        self.client = httpx.AsyncClient(timeout=5.0)
        
        logger.info("Boutique MCP Server initialized", base_url=boutique_base_url)
    
    async def start(self):
        """Start the MCP server."""
        self.running = True
        
        # Optionally skip startup checks
        skip_checks = os.getenv("SKIP_MCP_STARTUP_CHECKS", "").lower() in ("1", "true", "yes")
        
        if skip_checks:
            logger.info("Skipping MCP startup connectivity checks per env")
        else:
            # Run connectivity tests in background (non-blocking) for faster startup
            asyncio.create_task(self._test_connectivity_background())
        
        logger.info("Boutique MCP Server started")
    
    async def stop(self):
        """Stop the MCP server."""
        self.running = False
        await self.client.aclose()
        logger.info("Boutique MCP Server stopped")
    
    async def _test_connectivity(self):
        """Test connectivity to boutique services (parallel, short timeouts)."""
        async def probe(service_name: str, endpoint: str):
            try:
                is_http = isinstance(endpoint, str) and endpoint.startswith("http")
                if service_name == "product_catalog" and not is_http:
                    try:
                        async with aio.insecure_channel(endpoint) as ch:
                            stub = pb2_grpc.ProductCatalogServiceStub(ch)
                            await stub.ListProducts(pb2.Empty())
                        logger.info("gRPC service connectivity test passed", service=service_name)
                    except Exception as grpc_error:
                        logger.warning(
                            "gRPC service connectivity test failed",
                            service=service_name,
                            error=str(grpc_error),
                        )
                elif is_http:
                    health_url = f"{endpoint.rstrip('/')}/health"
                    try:
                        response = await self.client.get(health_url, timeout=3.0)
                        if response.status_code == 200:
                            logger.info("HTTP service connectivity test passed", service=service_name)
                        else:
                            logger.warning(
                                "HTTP service connectivity test failed",
                                service=service_name,
                                status=response.status_code,
                            )
                    except Exception as http_err:
                        logger.warning(
                            "HTTP service connectivity test failed",
                            service=service_name,
                            error=str(http_err),
                        )
                else:
                    logger.info(
                        "Skipping connectivity probe for endpoint with unknown scheme",
                        service=service_name,
                        endpoint=endpoint,
                    )
            except Exception as e:
                logger.warning("Service connectivity test failed", service=service_name, error=str(e))
        
        tasks = [probe(name, ep) for name, ep in self.endpoints.items()]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _test_connectivity_background(self):
        """Run connectivity tests in background after a brief delay to allow app to come up."""
        try:
            # Small delay so the server can finish starting
            await asyncio.sleep(1.0)
            await self._test_connectivity()
        except Exception:
            # Best-effort only; do not crash the app
            pass
    
    # Product Catalog Operations
    
    async def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for products in the catalog.
        
        Args:
            query: Search query
            category: Product category filter
            max_price: Maximum price filter
            min_price: Minimum price filter
            limit: Maximum number of results
            
        Returns:
            List of products matching the search criteria
        """
        try:
            print(f"BoutiqueMCP: Starting search_products with query: '{query}'")
            logger.info(f"Fetching products from {self.endpoints['product_catalog']} via gRPC")
            
            # gRPC call to ProductCatalogService
            print(f"BoutiqueMCP: Creating gRPC channel to {self.endpoints['product_catalog']}")
            async with aio.insecure_channel(self.endpoints['product_catalog']) as ch:
                stub = pb2_grpc.ProductCatalogServiceStub(ch)
                resp = await stub.ListProducts(pb2.Empty())
                
                logger.info(f"Received {len(resp.products)} products from gRPC")
                
                # Convert gRPC response to our format
                products = []
                for p in resp.products:
                    # Calculate price in units
                    price_units = p.price_usd.units + (p.price_usd.nanos / 1e9)
                    
                    # Apply filters
                    if query and query.strip():
                        query_lower = query.lower().strip()
                        # Skip filtering for "show all" or "all products" queries
                        if not any(phrase in query_lower for phrase in ["show all", "all products", "show me all", "list all", "show products", "products"]):
                            # For specific product searches, filter out stop words and check if all remaining words match
                            stop_words = {"show", "find", "search", "me", "for", "a", "the", "is", "are", "of"}
                            all_query_words = [word for word in query_lower.split() if word]
                            query_words = [word for word in all_query_words if word not in stop_words]

                            if query_words:
                                product_name_lower = p.name.lower()
                                # Normalize product name to handle compound words and variations
                                product_name_condensed = product_name_lower.replace(' ', '').replace('-', '')
                                
                                all_words_found = True
                                for word in query_words:
                                    # Normalize each query word by removing hyphens
                                    normalized_word = word.replace('-', '')
                                    
                                    # Check for the query word in both the original and condensed product names
                                    if normalized_word not in product_name_lower and \
                                       normalized_word not in product_name_condensed:
                                        all_words_found = False
                                        break
                                
                                if not all_words_found:
                                    continue
                    
                    if category:
                        cats = [c.lower() for c in p.categories]
                        if category.lower() not in cats:
                            continue
                    
                    if max_price and price_units > max_price:
                        continue
                    
                    if min_price and price_units < min_price:
                        continue
                    
                    product = {
                        "id": p.id,
                        "name": p.name,
                        "description": p.description,
                        "picture": p.picture,
                        "price_usd": {
                            "units": int(price_units),
                            "nanos": int((price_units % 1) * 1e9),
                            "currency_code": p.price_usd.currency_code
                        },
                        "categories": list(p.categories),
                        "weight_kg": 0.5,  # Default weight for CO2 calculation
                        "dimensions_cm": [20, 15, 10]  # Default dimensions
                    }
                    products.append(product)
                    
                    # Apply limit
                    if len(products) >= limit:
                        break
                
                logger.info("Product search completed", query=query, results_count=len(products))
                return products
            
        except Exception as e:
            print(f"BoutiqueMCP: Exception in search_products: {str(e)}")
            logger.error("Product search failed", query=query, error=str(e))
            return []
    
    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific product.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product details or None if not found
        """
        try:
            logger.info(f"Fetching product details from {self.endpoints['product_catalog']} via gRPC")
            
            # gRPC call to ProductCatalogService
            async with aio.insecure_channel(self.endpoints['product_catalog']) as ch:
                stub = pb2_grpc.ProductCatalogServiceStub(ch)
                req = pb2.GetProductRequest(id=product_id)
                resp = await stub.GetProduct(req)
                
                # Convert gRPC response to our format
                price_units = resp.price_usd.units + (resp.price_usd.nanos / 1e9)
                
                product = {
                    "id": resp.id,
                    "name": resp.name,
                    "description": resp.description,
                    "picture": resp.picture,
                    "price_usd": {
                        "units": int(price_units),
                        "nanos": int((price_units % 1) * 1e9),
                        "currency_code": resp.price_usd.currency_code
                    },
                    "categories": list(resp.categories),
                    "weight_kg": 0.5,  # Default weight for CO2 calculation
                    "dimensions_cm": [20, 15, 10]  # Default dimensions
                }
                
                logger.info("Product details retrieved", product_id=product_id)
                return product
            
        except Exception as e:
            logger.error("Product details retrieval failed", product_id=product_id, error=str(e))
            return None
    
    async def get_product_categories(self) -> List[str]:
        """
        Get list of available product categories by aggregating from ListProducts (gRPC).
        
        Returns:
            List of category names
        """
        try:
            endpoint = self.endpoints["product_catalog"]
            async with aio.insecure_channel(endpoint) as ch:
                stub = pb2_grpc.ProductCatalogServiceStub(ch)
                resp = await stub.ListProducts(pb2.Empty())
                categories_set = set()
                for p in resp.products:
                    for c in p.categories:
                        categories_set.add(c)
                categories = sorted(categories_set)
                logger.info("Product categories aggregated", count=len(categories))
                return categories
        except Exception as e:
            logger.error("Product categories retrieval failed", error=str(e))
            return []
    
    # Cart Operations
    
    async def add_to_cart(
        self,
        user_id: str,
        product_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Add a product to the user's cart.
        
        Args:
            user_id: User identifier
            product_id: Product identifier
            quantity: Quantity to add
            
        Returns:
            Cart operation result
        """
        try:
            cart_item = {
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity
            }
            
            response = await self.client.post(
                f"{self.endpoints['cart_service']}/cart/add",
                json=cart_item
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("Item added to cart", user_id=user_id, product_id=product_id, quantity=quantity)
            return result
            
        except Exception as e:
            logger.error("Add to cart failed", user_id=user_id, product_id=product_id, error=str(e))
            return {"success": False, "error": str(e)}
    
    async def remove_from_cart(
        self,
        user_id: str,
        product_id: str
    ) -> Dict[str, Any]:
        """
        Remove a product from the user's cart.
        
        Args:
            user_id: User identifier
            product_id: Product identifier
            
        Returns:
            Cart operation result
        """
        try:
            response = await self.client.delete(
                f"{self.endpoints['cart_service']}/cart/{user_id}/items/{product_id}"
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("Item removed from cart", user_id=user_id, product_id=product_id)
            return result
            
        except Exception as e:
            logger.error("Remove from cart failed", user_id=user_id, product_id=product_id, error=str(e))
            return {"success": False, "error": str(e)}
    
    async def get_cart_contents(self, user_id: str) -> Dict[str, Any]:
        """
        Get the contents of the user's cart.
        
        Args:
            user_id: User identifier
            
        Returns:
            Cart contents
        """
        try:
            response = await self.client.get(
                f"{self.endpoints['cart_service']}/cart/{user_id}"
            )
            response.raise_for_status()
            
            cart = response.json()
            
            logger.info("Cart contents retrieved", user_id=user_id, items_count=len(cart.get("items", [])))
            return cart
            
        except Exception as e:
            logger.error("Cart contents retrieval failed", user_id=user_id, error=str(e))
            return {"items": [], "total": 0.0}
    
    async def update_cart_item_quantity(
        self,
        user_id: str,
        product_id: str,
        quantity: int
    ) -> Dict[str, Any]:
        """
        Update the quantity of a cart item.
        
        Args:
            user_id: User identifier
            product_id: Product identifier
            quantity: New quantity
            
        Returns:
            Cart operation result
        """
        try:
            update_data = {
                "quantity": quantity
            }
            
            response = await self.client.put(
                f"{self.endpoints['cart_service']}/cart/{user_id}/items/{product_id}",
                json=update_data
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("Cart item quantity updated", user_id=user_id, product_id=product_id, quantity=quantity)
            return result
            
        except Exception as e:
            logger.error("Cart item quantity update failed", user_id=user_id, product_id=product_id, error=str(e))
            return {"success": False, "error": str(e)}
    
    async def clear_cart(self, user_id: str) -> Dict[str, Any]:
        """
        Clear all items from the user's cart.
        
        Args:
            user_id: User identifier
            
        Returns:
            Cart operation result
        """
        try:
            response = await self.client.delete(
                f"{self.endpoints['cart_service']}/cart/{user_id}"
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("Cart cleared", user_id=user_id)
            return result
            
        except Exception as e:
            logger.error("Cart clear failed", user_id=user_id, error=str(e))
            return {"success": False, "error": str(e)}
    
    # Recommendation Operations
    
    async def get_recommendations(
        self,
        user_id: str,
        product_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get product recommendations for a user.
        
        Args:
            user_id: User identifier
            product_ids: List of product IDs to base recommendations on
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended products
        """
        try:
            params = {
                "user_id": user_id,
                "limit": limit
            }
            
            if product_ids:
                params["product_ids"] = ",".join(product_ids)
            
            response = await self.client.get(
                f"{self.endpoints['recommendation_service']}/recommendations",
                params=params
            )
            response.raise_for_status()
            
            recommendations = response.json().get("recommendations", [])
            
            logger.info("Recommendations retrieved", user_id=user_id, count=len(recommendations))
            return recommendations
            
        except Exception as e:
            logger.error("Recommendations retrieval failed", user_id=user_id, error=str(e))
            return []
    
    # Checkout Operations
    
    async def process_checkout(
        self,
        user_id: str,
        shipping_address: Dict[str, Any],
        payment_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a checkout for the user's cart.
        
        Args:
            user_id: User identifier
            shipping_address: Shipping address information
            payment_info: Payment information
            
        Returns:
            Checkout result
        """
        try:
            checkout_data = {
                "user_id": user_id,
                "shipping_address": shipping_address,
                "payment_info": payment_info
            }
            
            response = await self.client.post(
                f"{self.endpoints['checkout_service']}/checkout",
                json=checkout_data
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("Checkout processed", user_id=user_id, order_id=result.get("order_id"))
            return result
            
        except Exception as e:
            logger.error("Checkout processing failed", user_id=user_id, error=str(e))
            return {"success": False, "error": str(e)}
    
    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order status information or None if not found
        """
        try:
            response = await self.client.get(
                f"{self.endpoints['checkout_service']}/orders/{order_id}"
            )
            response.raise_for_status()
            
            order_status = response.json()
            
            logger.info("Order status retrieved", order_id=order_id)
            return order_status
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Order not found", order_id=order_id)
                return None
            else:
                logger.error("Order status retrieval failed", order_id=order_id, error=str(e))
                return None
        except Exception as e:
            logger.error("Order status retrieval failed", order_id=order_id, error=str(e))
            return None
    
    # Currency Operations
    
    async def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Dict[str, Any]:
        """
        Convert currency amount.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Currency conversion result
        """
        try:
            params = {
                "amount": amount,
                "from": from_currency,
                "to": to_currency
            }
            
            response = await self.client.get(
                f"{self.endpoints['currency_service']}/convert",
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("Currency converted", amount=amount, from_currency=from_currency, to_currency=to_currency)
            return result
            
        except Exception as e:
            logger.error("Currency conversion failed", amount=amount, from_currency=from_currency, to_currency=to_currency, error=str(e))
            return {"success": False, "error": str(e)}
    
    async def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currencies.
        
        Returns:
            List of supported currency codes
        """
        try:
            response = await self.client.get(
                f"{self.endpoints['currency_service']}/currencies"
            )
            response.raise_for_status()
            
            currencies = response.json().get("currencies", [])
            
            logger.info("Supported currencies retrieved", count=len(currencies))
            return currencies
            
        except Exception as e:
            logger.error("Supported currencies retrieval failed", error=str(e))
            return []
    
    # Health and Status
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the MCP server."""
        try:
            health_status = {
                "status": "healthy",
                "services": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check each service endpoint
            for service_name, endpoint in self.endpoints.items():
                try:
                    is_http = isinstance(endpoint, str) and endpoint.startswith("http")
                    if service_name == "product_catalog" and not is_http:
                        # gRPC health via ListProducts
                        try:
                            async with aio.insecure_channel(endpoint) as ch:
                                stub = pb2_grpc.ProductCatalogServiceStub(ch)
                                await stub.ListProducts(pb2.Empty())
                            health_status["services"][service_name] = {"status": "healthy"}
                        except Exception as grpc_error:
                            health_status["services"][service_name] = {
                                "status": "unhealthy",
                                "error": str(grpc_error),
                            }
                    elif is_http:
                        # HTTP health when routed via proxy
                        try:
                            health_url = f"{endpoint.rstrip('/')}/health"
                            response = await self.client.get(health_url, timeout=5.0)
                            health_status["services"][service_name] = {
                                "status": "healthy" if response.status_code == 200 else "unhealthy",
                                "status_code": response.status_code,
                            }
                        except Exception as http_err:
                            health_status["services"][service_name] = {
                                "status": "unhealthy",
                                "error": str(http_err),
                            }
                    else:
                        health_status["services"][service_name] = {
                            "status": "unknown",
                            "note": "no probe for non-HTTP endpoint",
                        }
                except Exception as e:
                    health_status["services"][service_name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            
            # Determine overall status
            unhealthy_services = [
                name for name, status in health_status["services"].items()
                if status["status"] != "healthy"
            ]
            
            if unhealthy_services:
                health_status["status"] = "degraded"
                health_status["unhealthy_services"] = unhealthy_services
            
            return health_status
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get server metrics."""
        return {
            "running": self.running,
            "endpoints": self.endpoints,
            "timestamp": datetime.now().isoformat()
        }
    
    def __str__(self) -> str:
        """String representation of the MCP server."""
        return f"BoutiqueMCPServer(base_url={self.boutique_base_url}, running={self.running})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the MCP server."""
        return (
            f"BoutiqueMCPServer("
            f"base_url={self.boutique_base_url}, "
            f"running={self.running}, "
            f"endpoints={len(self.endpoints)}"
            f")"
        )
