"""
SmartCart Backend API - FastAPI Application
Main entry point for all API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="SmartCart API",
    description="AI-powered smart shopping system backend",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= DATA MODELS =============

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image_url: str
    stock: int

class CartItem(BaseModel):
    id: str
    user_id: str
    product_id: str
    quantity: int
    added_at: str

class AddToCartRequest(BaseModel):
    user_id: str
    product_id: str
    quantity: int = 1

class RecommendationRequest(BaseModel):
    product_id: str
    user_id: Optional[str] = None

class Analytics(BaseModel):
    user_id: str
    total_spent: float
    total_saved: float
    items_purchased: int
    frequently_bought: List[str]

# ============= MOCK DATA (Replace with Supabase in production) =============

MOCK_PRODUCTS = [
    {
        "id": "p1",
        "name": "Organic Apples",
        "description": "Fresh organic apples from local farms",
        "price": 4.99,
        "category": "Fruits",
        "image_url": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400",
        "stock": 50
    },
    {
        "id": "p2",
        "name": "Whole Wheat Bread",
        "description": "Freshly baked whole wheat bread",
        "price": 3.49,
        "category": "Bakery",
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400",
        "stock": 30
    },
    {
        "id": "p3",
        "name": "Almond Milk",
        "description": "Unsweetened almond milk, dairy-free",
        "price": 5.99,
        "category": "Dairy",
        "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400",
        "stock": 40
    },
    {
        "id": "p4",
        "name": "Greek Yogurt",
        "description": "Low-fat Greek yogurt with probiotics",
        "price": 6.49,
        "category": "Dairy",
        "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400",
        "stock": 25
    },
    {
        "id": "p5",
        "name": "Quinoa",
        "description": "Organic quinoa, high in protein",
        "price": 8.99,
        "category": "Grains",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400",
        "stock": 35
    },
    {
        "id": "p6",
        "name": "Avocados",
        "description": "Ripe avocados, perfect for guacamole",
        "price": 7.99,
        "category": "Fruits",
        "image_url": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400",
        "stock": 45
    },
    {
        "id": "p7",
        "name": "Salmon Fillet",
        "description": "Fresh Atlantic salmon, rich in Omega-3",
        "price": 15.99,
        "category": "Seafood",
        "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400",
        "stock": 20
    },
    {
        "id": "p8",
        "name": "Spinach",
        "description": "Fresh organic spinach leaves",
        "price": 3.99,
        "category": "Vegetables",
        "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400",
        "stock": 60
    }
]

MOCK_CART = {}  # Format: {user_id: [cart_items]}

# ============= API ENDPOINTS =============

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "SmartCart API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/products", response_model=List[Product])
async def get_products(search: Optional[str] = None, category: Optional[str] = None):
    """
    Get all products with optional search and category filters
    """
    products = MOCK_PRODUCTS.copy()
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        products = [
            p for p in products 
            if search_lower in p["name"].lower() or search_lower in p["description"].lower()
        ]
    
    # Apply category filter
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    
    return products

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """
    Get a specific product by ID
    """
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@app.post("/cart/add")
async def add_to_cart(request: AddToCartRequest):
    """
    Add a product to user's cart
    """
    # Verify product exists
    product = next((p for p in MOCK_PRODUCTS if p["id"] == request.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check stock availability
    if product["stock"] < request.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Initialize user cart if not exists
    if request.user_id not in MOCK_CART:
        MOCK_CART[request.user_id] = []
    
    # Check if product already in cart
    existing_item = next(
        (item for item in MOCK_CART[request.user_id] if item["product_id"] == request.product_id),
        None
    )
    
    if existing_item:
        existing_item["quantity"] += request.quantity
    else:
        cart_item = {
            "id": f"cart_{len(MOCK_CART[request.user_id]) + 1}",
            "user_id": request.user_id,
            "product_id": request.product_id,
            "quantity": request.quantity,
            "added_at": datetime.now().isoformat()
        }
        MOCK_CART[request.user_id].append(cart_item)
    
    return {
        "message": "Product added to cart successfully",
        "cart_items": len(MOCK_CART[request.user_id])
    }

@app.get("/cart/{user_id}")
async def get_cart(user_id: str):
    """
    Get user's cart with product details and total
    """
    if user_id not in MOCK_CART:
        return {"items": [], "total": 0, "savings": 0}
    
    cart_items = []
    total = 0
    
    for item in MOCK_CART[user_id]:
        product = next((p for p in MOCK_PRODUCTS if p["id"] == item["product_id"]), None)
        if product:
            item_total = product["price"] * item["quantity"]
            cart_items.append({
                **item,
                "product": product,
                "item_total": round(item_total, 2)
            })
            total += item_total
    
    # Calculate mock savings (10% discount simulation)
    savings = round(total * 0.1, 2)
    
    return {
        "items": cart_items,
        "total": round(total, 2),
        "savings": savings,
        "final_total": round(total - savings, 2)
    }

@app.delete("/cart/remove/{user_id}/{product_id}")
async def remove_from_cart(user_id: str, product_id: str):
    """
    Remove a product from user's cart
    """
    if user_id not in MOCK_CART:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    MOCK_CART[user_id] = [
        item for item in MOCK_CART[user_id] 
        if item["product_id"] != product_id
    ]
    
    return {"message": "Product removed from cart successfully"}

@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """
    Get AI-powered product recommendations
    This is a simplified version - in production, this calls Flowise API
    """
    # Find the requested product
    product = next((p for p in MOCK_PRODUCTS if p["id"] == request.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Mock recommendation logic (in production, use Flowise + OpenAI)
    # Recommend products from same category or complementary items
    recommendations = [
        p for p in MOCK_PRODUCTS 
        if p["id"] != request.product_id and 
        (p["category"] == product["category"] or p["price"] < product["price"] * 1.2)
    ][:3]
    
    return {
        "product_id": request.product_id,
        "recommendations": recommendations,
        "reason": f"Customers who bought {product['name']} also liked these items"
    }

@app.get("/analytics/{user_id}")
async def get_analytics(user_id: str):
    """
    Get user shopping analytics and insights
    """
    # Mock analytics data
    cart = MOCK_CART.get(user_id, [])
    
    total_items = sum(item["quantity"] for item in cart)
    
    # Calculate totals from cart
    total_spent = 0
    categories = {}
    
    for item in cart:
        product = next((p for p in MOCK_PRODUCTS if p["id"] == item["product_id"]), None)
        if product:
            total_spent += product["price"] * item["quantity"]
            categories[product["category"]] = categories.get(product["category"], 0) + 1
    
    frequently_bought = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        "user_id": user_id,
        "total_spent": round(total_spent, 2),
        "total_saved": round(total_spent * 0.1, 2),
        "items_purchased": total_items,
        "frequently_bought": [cat[0] for cat in frequently_bought],
        "savings_percentage": 10
    }

@app.get("/categories")
async def get_categories():
    """
    Get all available product categories
    """
    categories = list(set(p["category"] for p in MOCK_PRODUCTS))
    return {"categories": sorted(categories)}

# ============= RUN SERVER =============

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)