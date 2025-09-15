"""Shared in-memory cart store across agents.

This module provides a simple process-local store for carts keyed by session_id,
so CartManagementAgent and CheckoutAgent see the same cart state.
"""

from datetime import datetime
from typing import Dict, Any

_carts: Dict[str, Dict[str, Any]] = {}


def _normalize(session_id: str) -> str:
    # Demo stabilization: force a single cart namespace to avoid UI session drift
    try:
        sid = (session_id or "").strip()
        if not sid or len(sid) < 4:
            return "demo"
        return sid
    except Exception:
        return "demo"


def get_or_create_cart(session_id: str) -> Dict[str, Any]:
    key = _normalize(session_id)
    if key not in _carts:
        _carts[key] = {
            "items": [],
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "total_value": 0.0,
            "total_co2": 0.0,
        }
    return _carts[key]


def set_cart(session_id: str, cart: Dict[str, Any]) -> None:
    _carts[_normalize(session_id)] = cart


def clear_cart(session_id: str) -> None:
    cart = get_or_create_cart(_normalize(session_id))
    cart["items"] = []
    cart["last_updated"] = datetime.now()


def get_items(session_id: str) -> list:
    return list(get_or_create_cart(_normalize(session_id)).get("items", []))


def set_shipping(session_id: str, shipping_type: str) -> None:
    cart = get_or_create_cart(_normalize(session_id))
    cart["selected_shipping"] = shipping_type
    cart["last_updated"] = datetime.now()


def get_shipping(session_id: str) -> str:
    return get_or_create_cart(_normalize(session_id)).get("selected_shipping", "")


# ---------- Checkout snapshot helpers ----------

def set_checkout_snapshot(session_id: str, snapshot: Dict[str, Any]) -> None:
    cart = get_or_create_cart(_normalize(session_id))
    cart["checkout_snapshot"] = snapshot
    cart["last_updated"] = datetime.now()


def get_checkout_snapshot(session_id: str) -> Dict[str, Any]:
    return get_or_create_cart(_normalize(session_id)).get("checkout_snapshot", {})


def clear_checkout_snapshot(session_id: str) -> None:
    cart = get_or_create_cart(_normalize(session_id))
    if "checkout_snapshot" in cart:
        del cart["checkout_snapshot"]
    cart["last_updated"] = datetime.now()


