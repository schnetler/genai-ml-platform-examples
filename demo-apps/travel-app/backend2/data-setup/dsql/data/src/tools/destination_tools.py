"""
Destination recommendation tools for travel planning
"""

from typing import Dict, Any, List, Optional
import asyncio
from strands import tool
from ..agents.destination_agent import DestinationAgent

# Initialize the destination agent
destination_agent = DestinationAgent()


@tool
def recommend_destinations(
    query: str,
    origin: str,
    departure_date: str,
    return_date: Optional[str] = None,
    budget: Optional[float] = None,
    travelers: int = 1
) -> Dict[str, Any]:
    """
    Recommend travel destinations based on user preferences and constraints.
    
    Args:
        query: Natural language description of desired trip (e.g., "romantic getaway", "adventure trip")
        origin: Origin city or airport code
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Optional return date in YYYY-MM-DD format
        budget: Optional total budget for the trip
        travelers: Number of travelers
        
    Returns:
        Dictionary containing:
        - recommendations: List of recommended destinations with details
        - search_criteria: The criteria used for the search
    """
    travel_dates = {
        "departure": departure_date,
        "return": return_date
    }
    
    recommendations = asyncio.run(destination_agent.recommend_destinations(
        query=query,
        origin=origin,
        travel_dates=travel_dates,
        budget=budget,
        travelers=travelers
    ))
    
    return {
        "recommendations": recommendations,
        "search_criteria": {
            "query": query,
            "origin": origin,
            "dates": travel_dates,
            "budget": budget,
            "travelers": travelers
        }
    }


@tool
def get_destination_info(destination: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific destination.
    
    Args:
        destination: Name or airport code of the destination
        
    Returns:
        Dictionary containing detailed destination information including:
        - description
        - activities
        - climate
        - attractions
        - practical info (currency, language, visa)
    """
    return asyncio.run(destination_agent.get_destination_details(destination))


@tool
def compare_destinations(
    destinations: List[str],
    origin: str,
    departure_date: str,
    return_date: Optional[str] = None,
    comparison_criteria: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compare multiple destinations side by side.
    
    Args:
        destinations: List of destination names or codes to compare
        origin: Origin city or airport code
        departure_date: Departure date for cost comparison
        return_date: Optional return date
        comparison_criteria: Optional list of criteria to compare (e.g., ["cost", "activities", "weather"])
        
    Returns:
        Dictionary with side-by-side comparison of destinations
    """
    if not comparison_criteria:
        comparison_criteria = ["cost", "activities", "weather", "travel_time"]
    
    comparisons = {}
    
    for dest in destinations:
        # Get destination details
        details = asyncio.run(destination_agent.get_destination_details(dest))
        
        if "error" not in details:
            # Get flight info for cost and travel time
            try:
                from ..services.mock.flight_service import LocalDBFlightService
                flight_service = LocalDBFlightService()
                
                flight_results = asyncio.run(flight_service.search_flights(
                    origin=origin.upper(),
                    destination=details["airport_code"],
                    departure_date=departure_date,
                    return_date=return_date,
                    passengers=1
                ))
                
                if flight_results["flights"]:
                    cheapest = min(flight_results["flights"], key=lambda f: f["price"])
                    flight_info = {
                        "price": cheapest["price"],
                        "duration": cheapest.get("duration", "Unknown")
                    }
                else:
                    flight_info = {"price": None, "duration": None}
                    
            except Exception:
                flight_info = {"price": None, "duration": None}
            
            comparisons[dest] = {
                "name": details["name"],
                "country": details["country"],
                "flight_cost": flight_info["price"],
                "flight_duration": flight_info["duration"],
                "activities": details.get("activities", [])[:5],
                "current_weather": details["climate"]["current_season"],
                "temperature": details["climate"]["temperature_range"],
                "cuisine": details.get("cuisine", [])[:3],
                "top_attractions": details.get("attractions", [])[:3],
                "visa_required": details.get("visa_required", False)
            }
    
    return {
        "destinations": comparisons,
        "comparison_criteria": comparison_criteria,
        "origin": origin,
        "travel_dates": {
            "departure": departure_date,
            "return": return_date
        }
    }