"""
Flowise AI Integration for Product Recommendations
Connects to Flowise API with Chroma vector store and OpenAI
"""

import httpx
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

FLOWISE_API_URL = os.getenv("FLOWISE_API_URL")
FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY")

async def get_ai_recommendations(product_name: str, product_category: str, user_preferences: List[str] = None) -> Dict:
    """
    Get AI-powered product recommendations from Flowise
    
    Args:
        product_name: Name of the current product
        product_category: Category of the product
        user_preferences: Optional list of user preferences
    
    Returns:
        Dictionary with recommendations and reasoning
    """
    
    if not FLOWISE_API_URL:
        # Return mock recommendations if Flowise not configured
        return {
            "recommendations": [],
            "reasoning": "AI service not configured. Using fallback recommendations.",
            "confidence": 0.5
        }
    
    # Prepare the prompt for Flowise
    prompt = f"""
    A customer is viewing: {product_name} (Category: {product_category})
    
    Based on this product, suggest 3-5 similar or complementary products that would be good alternatives or additions.
    Consider:
    - Products in the same category
    - Complementary products that go well together
    - Better value alternatives
    - Healthier options if applicable
    
    User preferences: {', '.join(user_preferences) if user_preferences else 'None specified'}
    
    Provide recommendations with brief reasons why each product is suggested.
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                FLOWISE_API_URL,
                json={
                    "question": prompt,
                    "overrideConfig": {
                        "temperature": 0.7,
                        "maxTokens": 500
                    }
                },
                headers={
                    "Authorization": f"Bearer {FLOWISE_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "recommendations": parse_ai_response(result),
                    "reasoning": result.get("text", ""),
                    "confidence": 0.85
                }
            else:
                return {
                    "recommendations": [],
                    "reasoning": f"AI service error: {response.status_code}",
                    "confidence": 0.0
                }
    
    except Exception as e:
        return {
            "recommendations": [],
            "reasoning": f"Error connecting to AI service: {str(e)}",
            "confidence": 0.0
        }

def parse_ai_response(ai_result: Dict) -> List[Dict]:
    """
    Parse Flowise AI response into structured recommendations
    
    Args:
        ai_result: Raw response from Flowise API
    
    Returns:
        List of recommendation dictionaries
    """
    # This is a simplified parser
    # In production, you'd parse the AI response more carefully
    
    recommendations = []
    text = ai_result.get("text", "")
    
    # Simple parsing logic (customize based on your Flowise output format)
    lines = text.split("\n")
    
    for line in lines:
        if line.strip() and not line.startswith("#"):
            recommendations.append({
                "suggestion": line.strip(),
                "source": "AI"
            })
    
    return recommendations[:5]  # Limit to 5 recommendations

async def get_semantic_search(query: str, top_k: int = 5) -> List[Dict]:
    """
    Perform semantic search using Chroma vector store through Flowise
    
    Args:
        query: Search query
        top_k: Number of results to return
    
    Returns:
        List of matching products
    """
    
    if not FLOWISE_API_URL:
        return []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FLOWISE_API_URL}/search",
                json={
                    "query": query,
                    "top_k": top_k
                },
                headers={
                    "Authorization": f"Bearer {FLOWISE_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                return []
    
    except Exception as e:
        print(f"Semantic search error: {str(e)}")
        return []

# ============= HELPER FUNCTIONS =============

def calculate_similarity_score(product1: Dict, product2: Dict) -> float:
    """
    Calculate similarity score between two products
    Used as fallback when AI service is unavailable
    """
    score = 0.0
    
    # Same category = high similarity
    if product1.get("category") == product2.get("category"):
        score += 0.5
    
    # Similar price range
    price1 = product1.get("price", 0)
    price2 = product2.get("price", 0)
    price_diff = abs(price1 - price2) / max(price1, price2, 1)
    
    if price_diff < 0.2:
        score += 0.3
    elif price_diff < 0.5:
        score += 0.1
    
    return score