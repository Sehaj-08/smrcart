"""
Supabase Database Connection and Query Functions (REST API Version)
This version uses direct HTTP requests instead of the Supabase SDK.
Fully Render-compatible (no build issues).
"""

import os
import requests
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials not found in .env file")

# Standard headers for Supabase REST API
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Helper to build URLs
def build_url(table: str, query: str = ""):
    return f"{SUPABASE_URL}/rest/v1/{table}{query}"

# ==========================================================
# ============= PRODUCT QUERIES =============================
# ==========================================================

async def get_all_products(search: Optional[str] = None, category: Optional[str] = None):
    """Fetch all products with optional filters"""
    params = []
    if search:
        params.append(f"name=ilike.*{search}*")
    if category:
        params.append(f"category=eq.{category}")

    query = f"?select=*" + ("&" + "&".join(params) if params else "")
    res = requests.get(build_url("products", query), headers=HEADERS)
    res.raise_for_status()
    return res.json()

async def get_product_by_id(product_id: str):
    """Fetch single product by ID"""
    query = f"?select=*&id=eq.{product_id}"
    res = requests.get(build_url("products", query), headers=HEADERS)
    res.raise_for_status()
    data = res.json()
    return data[0] if data else None

# ==========================================================
# ============= CART QUERIES ===============================
# ==========================================================

async def add_to_cart_db(user_id: str, product_id: str, quantity: int):
    """Add item to cart, or update if exists"""
    # Check if item already exists
    query = f"?user_id=eq.{user_id}&product_id=eq.{product_id}&select=*"
    existing = requests.get(build_url("cart_items", query), headers=HEADERS).json()

    if existing:
        # Update quantity
        new_quantity = existing[0]["quantity"] + quantity
        update_data = {"quantity": new_quantity}
        url = build_url("cart_items", f"?id=eq.{existing[0]['id']}")
        res = requests.patch(url, headers=HEADERS, json=update_data)
    else:
        # Insert new item
        data = {"user_id": user_id, "product_id": product_id, "quantity": quantity}
        res = requests.post(build_url("cart_items"), headers=HEADERS, json=data)

    res.raise_for_status()
    return res.json()

async def get_user_cart(user_id: str):
    """Get user's cart with product details"""
    query = f"?user_id=eq.{user_id}&select=*,products(*)"
    res = requests.get(build_url("cart_items", query), headers=HEADERS)
    res.raise_for_status()
    return res.json()

async def remove_from_cart_db(user_id: str, product_id: str):
    """Remove item from cart"""
    query = f"?user_id=eq.{user_id}&product_id=eq.{product_id}"
    res = requests.delete(build_url("cart_items", query), headers=HEADERS)
    res.raise_for_status()
    return {"deleted": True}

# ==========================================================
# ============= ANALYTICS QUERIES ==========================
# ==========================================================

async def get_user_analytics(user_id: str):
    """Get user shopping analytics"""
    purchases_query = f"?user_id=eq.{user_id}&select=*"
    analytics_query = f"?user_id=eq.{user_id}&select=*"

    purchases = requests.get(build_url("purchase_history", purchases_query), headers=HEADERS).json()
    analytics = requests.get(build_url("analytics", analytics_query), headers=HEADERS).json()

    return {
        "purchases": purchases,
        "analytics": analytics[0] if analytics else None
    }

# ==========================================================
# ============= USER QUERIES ===============================
# ==========================================================

async def create_user(email: str, name: str):
    """Create a new user"""
    data = {"email": email, "name": name}
    res = requests.post(build_url("users"), headers=HEADERS, json=data)
    res.raise_for_status()
    return res.json()

async def get_user_by_id(user_id: str):
    """Fetch a user by ID"""
    query = f"?id=eq.{user_id}&select=*"
    res = requests.get(build_url("users", query), headers=HEADERS)
    res.raise_for_status()
    data = res.json()
    return data[0] if data else None
