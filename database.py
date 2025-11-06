"""
Supabase Database Connection and Query Functions
Replace mock data in main.py with these functions in production
"""

from supabase import create_client, Client
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ============= PRODUCT QUERIES =============

async def get_all_products(search: Optional[str] = None, category: Optional[str] = None):
    """Fetch all products from Supabase with optional filters"""
    if not supabase:
        raise Exception("Supabase client not initialized")
    
    query = supabase.table("products").select("*")
    
    if search:
        query = query.ilike("name", f"%{search}%")
    
    if category:
        query = query.eq("category", category)
    
    response = query.execute()
    return response.data

async def get_product_by_id(product_id: str):
    """Fetch a single product by ID"""
    if not supabase:
        raise Exception("Supabase client not initialized")
    
    response = supabase.table("products").select("*").eq("id", product_id).execute()
    return response.data[0] if response.data else None

# ============= CART QUERIES =============

async def add_to_cart_db(user_id: str, product_id: str, quantity: int):
    """Add item to cart in Supabase"""
    if not supabase:
        raise Exception("Supabase client not initialized")
    
    # Check if item already exists in cart
    existing = supabase.table("cart_items").select("*").eq("user_id", user_id).eq("product_id", product_id).execute()
    
    if existing.data:
        # Update quantity
        new_quantity = existing.data[0]["quantity"] + quantity
        response = supabase.table("cart_items").update({"quantity": new_quantity}).eq("id", existing.data[0]["id"]).execute()
    else:
        # Insert new item
        response = supabase.table("cart_items").insert({
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity
        }).execute()
    
    return response.data

async def get_user_cart(user_id: str):
    """Get user's cart with product details"""
    if not supabase:
        raise Exception("Supabase client not initialized")
    
    response = supabase.table("cart_items").select("*, products(*)").eq("user_id", user_id).execute()
    return response.data

async def remove_from_cart_db(user_id: str, product_id: str):
    """Remove item from cart"""
    if not supabase:
        raise Exception("Supabase client not initialized")
    
    response = supabase.table("cart_items").delete().eq("user_id", user_id).eq("product_id", product_id).execute()
    return response.data

# ============= ANALYTICS QUERIES =============

async def get_user_analytics(user_id: str):
    """Get user shopping analytics"""
    if not supabase:
        raise Exception("Supabase client not initialized")
    
    # Get purchase history
    purchases = supabase.table("purchase_history").select("*").eq("user_id", user_id).execute()
    
    # Get analytics summary
    analytics = supabase.table("analytics").select("*").eq("user_id", user_id).execute()
    
    return {
        "purchases": purchases.data,
        "analytics": analytics.data[0] if analytics.data else None
    }

# ============= USER QUERIES =============

async def create_user(email: str, name: str):
    """Create a new user"""
    if not supabase:
        raise Exception("Supabase client not initialized")
    
    response = supabase.table("users").insert({
        "email": email,
        "name": name
    }).execute()
    
    return response.data

async def get_user_by_id(user_id: str):
    """Get user by ID"""
    if not supabase:
        raise Exception("Supabase client not initialized")
    
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None