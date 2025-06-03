"""
AWS-native destination recommendation tools for Lambda environment
"""

import json
import boto3
from typing import Dict, Any, List, Optional
from strands import tool

# Initialize AWS clients
s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime')


# Hardcoded destination data for now - in production, this would come from S3 or DynamoDB
DESTINATION_DATA = {
    "paris": {
        "name": "Paris",
        "country": "France",
        "description": "The City of Light, known for art, fashion, gastronomy, and culture",
        "activities": ["Eiffel Tower", "Louvre Museum", "Seine River Cruise", "Notre-Dame Cathedral"],
        "best_time": "April-May and September-October",
        "currency": "Euro (EUR)",
        "language": "French",
        "tags": ["romantic", "cultural", "art", "fashion", "gastronomy", "historic"],
        "cost_level": "high",
        "climate": "temperate"
    },
    "rome": {
        "name": "Rome",
        "country": "Italy",
        "description": "The Eternal City, rich in history, art, and culinary delights",
        "activities": ["Colosseum", "Vatican City", "Trevi Fountain", "Roman Forum"],
        "best_time": "April-May and September-October",
        "currency": "Euro (EUR)",
        "language": "Italian",
        "tags": ["historic", "cultural", "art", "food", "architecture"],
        "cost_level": "medium-high",
        "climate": "mediterranean"
    },
    "tokyo": {
        "name": "Tokyo",
        "country": "Japan",
        "description": "A vibrant metropolis blending modern technology with traditional culture",
        "activities": ["Senso-ji Temple", "Shibuya Crossing", "Mount Fuji day trip", "Tsukiji Market"],
        "best_time": "March-May and October-November",
        "currency": "Japanese Yen (JPY)",
        "language": "Japanese",
        "tags": ["modern", "cultural", "technology", "food", "shopping"],
        "cost_level": "high",
        "climate": "temperate"
    },
    "bali": {
        "name": "Bali",
        "country": "Indonesia",
        "description": "Tropical paradise with beautiful beaches, temples, and rich culture",
        "activities": ["Beach hopping", "Temple visits", "Rice terrace tours", "Surfing"],
        "best_time": "April-October",
        "currency": "Indonesian Rupiah (IDR)",
        "language": "Indonesian",
        "tags": ["beach", "tropical", "cultural", "relaxation", "adventure"],
        "cost_level": "low-medium",
        "climate": "tropical"
    },
    "santorini": {
        "name": "Santorini",
        "country": "Greece",
        "description": "Stunning island with white-washed buildings and spectacular sunsets",
        "activities": ["Sunset in Oia", "Wine tasting", "Beach exploration", "Boat tours"],
        "best_time": "April-May and September-October",
        "currency": "Euro (EUR)",
        "language": "Greek",
        "tags": ["romantic", "beach", "scenic", "luxury", "wine"],
        "cost_level": "high",
        "climate": "mediterranean"
    },
    "iceland": {
        "name": "Iceland",
        "country": "Iceland",
        "description": "Land of fire and ice with dramatic landscapes and natural wonders",
        "activities": ["Northern Lights", "Blue Lagoon", "Glacier hiking", "Waterfall tours"],
        "best_time": "June-August for weather, September-March for Northern Lights",
        "currency": "Icelandic Króna (ISK)",
        "language": "Icelandic",
        "tags": ["adventure", "nature", "scenic", "unique", "outdoor"],
        "cost_level": "high",
        "climate": "subarctic"
    },
    "barcelona": {
        "name": "Barcelona",
        "country": "Spain",
        "description": "Vibrant city with stunning architecture, beaches, and nightlife",
        "activities": ["Sagrada Familia", "Park Güell", "Las Ramblas", "Beach time"],
        "best_time": "May-June and September-October",
        "currency": "Euro (EUR)",
        "language": "Spanish/Catalan",
        "tags": ["cultural", "beach", "architecture", "nightlife", "food"],
        "cost_level": "medium",
        "climate": "mediterranean"
    },
    "new_york": {
        "name": "New York City",
        "country": "USA",
        "description": "The city that never sleeps - a global hub of culture, finance, and entertainment",
        "activities": ["Times Square", "Central Park", "Broadway shows", "Museums"],
        "best_time": "April-June and September-November",
        "currency": "US Dollar (USD)",
        "language": "English",
        "tags": ["urban", "cultural", "shopping", "entertainment", "food"],
        "cost_level": "high",
        "climate": "temperate"
    }
}


def _match_destinations_by_tags(query: str, budget: Optional[float] = None) -> List[Dict[str, Any]]:
    """Match destinations based on query keywords and budget"""
    query_lower = query.lower()
    matches = []
    
    for key, dest in DESTINATION_DATA.items():
        score = 0
        reasons = []
        
        # Check tag matches
        for tag in dest['tags']:
            if tag in query_lower:
                score += 2
                reasons.append(f"matches {tag}")
        
        # Check description and name matches
        if dest['name'].lower() in query_lower:
            score += 3
            reasons.append("exact destination match")
        elif any(word in dest['description'].lower() for word in query_lower.split()):
            score += 1
            reasons.append("description match")
        
        # Budget filtering
        if budget:
            if budget < 1500 and dest['cost_level'] in ['low-medium', 'medium']:
                score += 1
                reasons.append("budget-friendly")
            elif budget >= 1500 and budget < 3000 and dest['cost_level'] in ['medium', 'medium-high']:
                score += 1
                reasons.append("within budget range")
            elif budget >= 3000:
                score += 0  # No penalty for any destination
        
        if score > 0:
            matches.append({
                "destination": dest['name'],
                "country": dest['country'],
                "score": score,
                "reason": ', '.join(reasons) if reasons else "general match",
                "description": dest['description'],
                "cost_level": dest['cost_level']
            })
    
    # Sort by score and return top matches
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches[:5]


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
    # Get matches from our data
    matches = _match_destinations_by_tags(query, budget)
    
    # If no matches, provide default recommendations
    if not matches:
        query_lower = query.lower()
        if "romantic" in query_lower:
            matches = [
                {"destination": "Paris", "reason": "Classic romantic destination"},
                {"destination": "Santorini", "reason": "Beautiful sunsets and luxury"},
                {"destination": "Venice", "reason": "Romantic canals and ambiance"}
            ]
        elif "adventure" in query_lower:
            matches = [
                {"destination": "Iceland", "reason": "Dramatic landscapes and outdoor activities"},
                {"destination": "New Zealand", "reason": "Adventure capital"},
                {"destination": "Costa Rica", "reason": "Diverse ecosystems and activities"}
            ]
        elif "beach" in query_lower:
            matches = [
                {"destination": "Bali", "reason": "Tropical beaches and culture"},
                {"destination": "Maldives", "reason": "Pristine beaches and luxury"},
                {"destination": "Hawaii", "reason": "Diverse islands and activities"}
            ]
        else:
            matches = [
                {"destination": "Rome", "reason": "History and culture"},
                {"destination": "Tokyo", "reason": "Modern meets traditional"},
                {"destination": "Barcelona", "reason": "Beach, culture, and nightlife"}
            ]
    
    # Format recommendations
    recommendations = []
    for match in matches[:3]:
        rec = {
            "destination": match['destination'],
            "reason": match.get('reason', 'Great destination for your trip')
        }
        if 'country' in match:
            rec['country'] = match['country']
        if 'description' in match:
            rec['description'] = match['description']
        if 'cost_level' in match:
            rec['cost_level'] = match['cost_level']
        recommendations.append(rec)
    
    return {
        "recommendations": recommendations,
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
    # Normalize destination name
    dest_key = destination.lower().replace(" ", "_").replace("-", "_")
    
    # Look for exact match first
    if dest_key in DESTINATION_DATA:
        info = DESTINATION_DATA[dest_key].copy()
        info['destination'] = info.pop('name')
        return info
    
    # Try partial match
    for key, data in DESTINATION_DATA.items():
        if destination.lower() in data['name'].lower():
            info = data.copy()
            info['destination'] = info.pop('name')
            return info
    
    # Return default info if not found
    return {
        "destination": destination,
        "description": f"{destination} is a wonderful travel destination with unique attractions",
        "activities": ["Explore local culture", "Visit historic sites", "Try local cuisine", "Shopping"],
        "best_time": "Varies by season",
        "currency": "Local currency",
        "language": "Local language",
        "tags": ["general", "tourism"],
        "cost_level": "medium"
    }


@tool
def compare_destinations(
    destinations: List[str],
    comparison_criteria: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compare multiple destinations side by side.
    
    Args:
        destinations: List of destination names to compare
        comparison_criteria: Optional list of criteria to compare (cost, activities, weather, culture)
        
    Returns:
        Dictionary containing destination comparisons
    """
    if not comparison_criteria:
        comparison_criteria = ["cost", "activities", "weather", "culture"]
    
    comparisons = {}
    
    for dest_name in destinations:
        info = get_destination_info(dest_name)
        
        # Build comparison data
        comparison = {
            "summary": info.get("description", ""),
            "best_for": _get_best_for_tags(info.get("tags", [])),
            "relative_cost": info.get("cost_level", "medium"),
            "highlights": info.get("activities", [])[:3],
            "best_time": info.get("best_time", "Year-round"),
            "climate": info.get("climate", "varies")
        }
        
        # Add specific criteria if requested
        if "cost" in comparison_criteria:
            comparison["budget_estimate"] = _estimate_daily_cost(info.get("cost_level", "medium"))
        
        if "weather" in comparison_criteria:
            comparison["weather_notes"] = f"Climate: {info.get('climate', 'temperate')}, Best time: {info.get('best_time', 'varies')}"
        
        comparisons[dest_name] = comparison
    
    return {
        "destinations": comparisons,
        "criteria_used": comparison_criteria,
        "recommendation": _get_comparison_recommendation(destinations, comparisons)
    }


def _get_best_for_tags(tags: List[str]) -> str:
    """Convert tags to 'best for' description"""
    if not tags:
        return "General tourism"
    
    tag_descriptions = {
        "romantic": "couples and romance",
        "adventure": "outdoor enthusiasts",
        "beach": "beach lovers",
        "cultural": "culture seekers",
        "historic": "history buffs",
        "modern": "urban explorers",
        "nature": "nature lovers",
        "luxury": "luxury travelers"
    }
    
    descriptions = [tag_descriptions.get(tag, tag) for tag in tags[:3]]
    return ", ".join(descriptions)


def _estimate_daily_cost(cost_level: str) -> str:
    """Estimate daily cost range based on cost level"""
    cost_estimates = {
        "low": "$50-100 per day",
        "low-medium": "$75-150 per day",
        "medium": "$100-200 per day",
        "medium-high": "$150-300 per day",
        "high": "$200-500+ per day",
        "very high": "$300-1000+ per day"
    }
    return cost_estimates.get(cost_level, "$100-300 per day")


def _get_comparison_recommendation(destinations: List[str], comparisons: Dict[str, Any]) -> str:
    """Generate recommendation based on destination comparison"""
    if len(destinations) == 1:
        return f"{destinations[0]} is an excellent choice for your trip!"
    
    # Analyze cost levels
    cost_levels = [comp.get("relative_cost", "medium") for comp in comparisons.values()]
    
    if len(set(cost_levels)) > 1:
        # Different cost levels
        budget_friendly = [dest for dest, comp in comparisons.items() if "low" in comp.get("relative_cost", "")]
        luxury = [dest for dest, comp in comparisons.items() if "high" in comp.get("relative_cost", "")]
        
        if budget_friendly and luxury:
            return f"Consider {', '.join(budget_friendly)} for budget-friendly options, or {', '.join(luxury)} for a more luxurious experience."
    
    # Generic recommendation
    return f"All destinations offer unique experiences. Consider your priorities: {destinations[0]} for {comparisons[destinations[0]]['best_for']}, " \
           f"or {destinations[-1]} for {comparisons[destinations[-1]]['best_for']}."