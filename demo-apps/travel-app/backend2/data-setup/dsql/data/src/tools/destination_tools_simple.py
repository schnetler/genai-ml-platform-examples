"""
Simple destination recommendation tools without nested agent calls
"""

from typing import Dict, Any, List, Optional
from strands import tool
from ..vector_store.destination_store import DestinationVectorStore


@tool
def recommend_destinations(
    query: str,
    budget: Optional[float] = None,
    travelers: int = 1
) -> Dict[str, Any]:
    """
    Recommend travel destinations based on user preferences and constraints.
    
    Args:
        query: Natural language description of desired trip (e.g., "romantic getaway", "adventure trip")
        budget: Optional total budget for the trip
        travelers: Number of travelers
        
    Returns:
        Dictionary containing recommendations
    """
    # Simple implementation without nested agent calls
    recommendations = []
    
    # Basic recommendations based on query keywords
    query_lower = query.lower()
    
    if "romantic" in query_lower or "couple" in query_lower:
        recommendations.extend([
            {"destination": "Paris", "reason": "City of Love with romantic atmosphere"},
            {"destination": "Venice", "reason": "Romantic canals and intimate dining"},
            {"destination": "Santorini", "reason": "Beautiful sunsets and luxury resorts"}
        ])
    elif "adventure" in query_lower or "outdoor" in query_lower:
        recommendations.extend([
            {"destination": "Queenstown", "reason": "Adventure capital with bungee jumping and skiing"},
            {"destination": "Costa Rica", "reason": "Zip-lining, hiking, and wildlife"},
            {"destination": "Iceland", "reason": "Glaciers, volcanoes, and northern lights"}
        ])
    elif "beach" in query_lower or "relax" in query_lower:
        recommendations.extend([
            {"destination": "Maldives", "reason": "Pristine beaches and overwater bungalows"},
            {"destination": "Bali", "reason": "Beautiful beaches with cultural experiences"},
            {"destination": "Hawaii", "reason": "Diverse islands with beaches and activities"}
        ])
    else:
        # Default recommendations
        recommendations.extend([
            {"destination": "Rome", "reason": "History, culture, and amazing food"},
            {"destination": "Tokyo", "reason": "Modern city with unique culture"},
            {"destination": "Barcelona", "reason": "Architecture, beaches, and nightlife"}
        ])
    
    # Filter by budget if provided
    if budget and budget < 1000:
        # Focus on budget-friendly destinations
        budget_friendly = [r for r in recommendations if r["destination"] not in ["Maldives", "Santorini"]]
        recommendations = budget_friendly if budget_friendly else recommendations[:2]
    
    return {
        "recommendations": recommendations[:3],  # Return top 3
        "search_criteria": {
            "query": query,
            "budget": budget,
            "travelers": travelers
        }
    }


@tool
def get_destination_info(destination: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific destination.
    
    Args:
        destination: Name of the destination
        
    Returns:
        Dictionary containing destination information
    """
    # Use vector store if available, otherwise return basic info
    try:
        store = DestinationVectorStore()
        # Search for destination info
        results = store.search(f"information about {destination}", k=1)
        if results:
            return {
                "destination": destination,
                "description": results[0].get("text", f"{destination} is a popular travel destination"),
                "source": "vector_store"
            }
    except:
        pass
    
    # Fallback to basic information
    destination_info = {
        "Paris": {
            "description": "The City of Light, known for art, fashion, gastronomy, and culture",
            "activities": ["Eiffel Tower", "Louvre Museum", "Seine River Cruise", "Notre-Dame Cathedral"],
            "best_time": "April-May and September-October",
            "currency": "Euro (EUR)",
            "language": "French"
        },
        "Rome": {
            "description": "The Eternal City, rich in history, art, and culinary delights",
            "activities": ["Colosseum", "Vatican City", "Trevi Fountain", "Roman Forum"],
            "best_time": "April-May and September-October",
            "currency": "Euro (EUR)",
            "language": "Italian"
        },
        "Tokyo": {
            "description": "A vibrant metropolis blending modern technology with traditional culture",
            "activities": ["Senso-ji Temple", "Shibuya Crossing", "Mount Fuji day trip", "Tsukiji Market"],
            "best_time": "March-May and October-November",
            "currency": "Japanese Yen (JPY)",
            "language": "Japanese"
        },
        "default": {
            "description": f"{destination} is a wonderful travel destination with unique attractions",
            "activities": ["Explore local culture", "Visit historic sites", "Try local cuisine", "Shopping"],
            "best_time": "Varies by season",
            "currency": "Local currency",
            "language": "Local language"
        }
    }
    
    info = destination_info.get(destination, destination_info["default"])
    info["destination"] = destination
    
    return info


@tool
def compare_destinations(
    destinations: List[str],
    comparison_criteria: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compare multiple destinations side by side.
    
    Args:
        destinations: List of destination names to compare
        comparison_criteria: Optional list of criteria to compare
        
    Returns:
        Dictionary containing destination comparisons
    """
    if not comparison_criteria:
        comparison_criteria = ["cost", "activities", "weather", "culture"]
    
    comparisons = {}
    
    for dest in destinations:
        info = get_destination_info(dest)
        comparisons[dest] = {
            "summary": info.get("description", ""),
            "best_for": _get_best_for(dest),
            "relative_cost": _get_relative_cost(dest),
            "highlights": info.get("activities", [])[:3]
        }
    
    return {
        "destinations": comparisons,
        "criteria_used": comparison_criteria,
        "recommendation": _get_recommendation(destinations)
    }


def _get_best_for(destination: str) -> str:
    """Get what a destination is best for."""
    best_for_map = {
        "Paris": "Romance, art, and culture",
        "Rome": "History, architecture, and food",
        "Tokyo": "Technology, culture contrast, and unique experiences",
        "Maldives": "Beach relaxation and water activities",
        "Iceland": "Natural wonders and adventure",
        "Barcelona": "Beach, culture, and nightlife mix"
    }
    return best_for_map.get(destination, "General tourism and exploration")


def _get_relative_cost(destination: str) -> str:
    """Get relative cost rating."""
    cost_map = {
        "Paris": "High",
        "Rome": "Medium-High",
        "Tokyo": "High",
        "Maldives": "Very High",
        "Iceland": "High",
        "Barcelona": "Medium",
        "Prague": "Low-Medium",
        "Budapest": "Low-Medium"
    }
    return cost_map.get(destination, "Medium")


def _get_recommendation(destinations: List[str]) -> str:
    """Get a recommendation based on destinations being compared."""
    if len(destinations) == 1:
        return f"{destinations[0]} is a great choice for your trip!"
    
    # Simple logic to recommend based on common comparisons
    if "Paris" in destinations and "Rome" in destinations:
        return "Both are excellent for culture and history. Choose Paris for romance and art, Rome for ancient history and food."
    elif "Maldives" in destinations:
        return "Choose Maldives for ultimate beach relaxation, other destinations for more varied activities."
    else:
        return f"All destinations offer unique experiences. Consider your budget and interests when choosing."