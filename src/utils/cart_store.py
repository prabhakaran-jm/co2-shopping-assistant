"""Shared in-memory cart store across agents.

This module provides a simple process-local store for carts keyed by session_id,
so CartManagementAgent and CheckoutAgent see the same cart state.
"""

from datetime import datetime
from typing import Dict, Any

_carts: Dict[str, Dict[str, Any]] = {}


def get_or_create_cart(session_id: str) -> Dict[str, Any]:
    if session_id not in _carts:
        _carts[session_id] = {
            "items": [],
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "total_value": 0.0,
            "total_co2": 0.0,
        }
    return _carts[session_id]


def set_cart(session_id: str, cart: Dict[str, Any]) -> None:
    _carts[session_id] = cart


def clear_cart(session_id: str) -> None:
    cart = get_or_create_cart(session_id)
    cart["items"] = []
    cart["last_updated"] = datetime.now()


def get_items(session_id: str) -> list:
    return list(get_or_create_cart(session_id).get("items", []))


