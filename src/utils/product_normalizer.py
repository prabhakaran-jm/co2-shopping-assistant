"""
Utility functions to normalize product data across agents.

Provides consistent parsing of price fields, mocked CO2 emissions,
eco score computation, and rating labels so all agents display
aligned values.
"""

from typing import Dict, Any, List


def parse_price_usd(product: Dict[str, Any]) -> float:
    """Extract numeric price from Online Boutique style product objects."""
    price_value = 0.0
    if "price_usd" in product:
        price_usd = product["price_usd"]
        if isinstance(price_usd, dict):
            units = price_usd.get("units", 0)
            nanos = price_usd.get("nanos", 0)
            price_value = float(units)
            price_value += (float(nanos) / 1e9)
        else:
            try:
                price_value = float(price_usd) if price_usd else 0.0
            except (ValueError, TypeError):
                price_value = 0.0
    elif "price" in product:
        price_raw = product.get("price", 0.0)
        if isinstance(price_raw, (int, float)):
            price_value = float(price_raw)
        elif isinstance(price_raw, str):
            try:
                price_value = float(price_raw.replace("$", "").replace(",", ""))
            except (ValueError, TypeError):
                price_value = 0.0
    return price_value


def compute_mock_co2(price_value: float) -> float:
    """Mock CO2 emissions based on price, consistent with agents' assumptions."""
    base_co2 = 50.0
    eco_factor = max(0.1, min(1.0, (1000 - price_value) / 1000))
    return base_co2 * eco_factor


def compute_eco_score(price_value: float) -> int:
    """Mock eco score based on price, 1..10 inclusive."""
    return max(1, min(10, int(10 - (price_value / 20))))


def co2_rating_label(co2_emissions: float) -> str:
    """Convert CO2 value to qualitative label."""
    if co2_emissions < 30:
        return "Low"
    if co2_emissions < 60:
        return "Medium"
    return "High"


def image_url_from_picture(picture: str) -> str:
    if not picture:
        return ""
    if picture.startswith("/"):
        return f"/ob-images{picture}"
    return f"/ob-images/{picture}"


def normalize_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized product dict with consistent fields used by UI/agents."""
    price_value = parse_price_usd(product)
    co2_emissions = float(product.get("co2_emissions", compute_mock_co2(price_value)))
    eco_score = int(product.get("eco_score", compute_eco_score(price_value)))
    co2_rating = product.get("co2_rating") or co2_rating_label(co2_emissions)
    picture = product.get("picture", "")
    normalized = {
        "name": product.get("name", "N/A"),
        "price": price_value,
        "co2_emissions": co2_emissions,
        "eco_score": eco_score,
        "co2_rating": co2_rating,
        "description": product.get("description", "No description available"),
        "image_url": image_url_from_picture(picture),
        "id": product.get("id", product.get("item_id", "")),
        "categories": product.get("categories", []),
        "original": product,
    }
    return normalized


def normalize_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [normalize_product(p) for p in products]


