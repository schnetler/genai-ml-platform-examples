"""Enhanced flight tools with WebSocket event broadcasting."""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from strands.tools import tool
from ..models.travel_plan import Flight
from ..services.mock.flight_service import LocalDBFlightService
from ..websocket.events import track_tool_execution, track_search_operation

logger = logging.getLogger(__name__)

# Initialize the flight service
flight_service = LocalDBFlightService()


@tool
@track_tool_execution("search_flights")
@track_search_operation("flight")
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    cabin_class: str = "economy",
    max_price: Optional[float] = None,
    nonstop_only: bool = False,
    _plan_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for available flights between two locations with real-time updates.
    
    Args:
        origin: Departure airport code or city name
        destination: Arrival airport code or city name
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round trip (YYYY-MM-DD)
        passengers: Number of passengers
        cabin_class: Class of service (economy, business, first)
        max_price: Maximum price per ticket
        nonstop_only: Only show nonstop flights
        _plan_id: Internal plan ID for WebSocket events
        
    Returns:
        Dictionary containing flight search results with pricing
    """
    try:
        # Parse dates
        try:
            departure_dt = datetime.strptime(departure_date, "%Y-%m-%d")
            return_dt = datetime.strptime(return_date, "%Y-%m-%d") if return_date else None
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid date format: {e}. Use YYYY-MM-DD format."
            }
        
        # Search for flights
        result = await flight_service.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            cabin_class=cabin_class,
            max_price=max_price,
            nonstop_only=nonstop_only
        )
        
        # Format response
        if result.get("success") and result.get("results"):
            flight_results = result["results"]
            
            # Enhance with summary information
            summary = {
                "total_options": len(flight_results.get("outbound_flights", [])),
                "cheapest_price": min([f["price"] for f in flight_results.get("outbound_flights", [])], default=0),
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date
            }
            
            if return_date and "return_flights" in flight_results:
                summary["return_date"] = return_date
                summary["return_options"] = len(flight_results.get("return_flights", []))
                
            return {
                "success": True,
                "summary": summary,
                "results": flight_results
            }
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error searching flights: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@tool
@track_tool_execution("get_flight_details")
async def get_flight_details(
    flight_number: str,
    departure_date: str,
    _plan_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific flight with real-time updates.
    
    Args:
        flight_number: Flight number (e.g., "AA100")
        departure_date: Date of departure (YYYY-MM-DD)
        _plan_id: Internal plan ID for WebSocket events
        
    Returns:
        Detailed flight information including schedule and amenities
    """
    try:
        result = await flight_service.get_flight_details(flight_number, departure_date)
        return result
    except Exception as e:
        logger.error(f"Error getting flight details: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@tool
@track_tool_execution("check_flight_availability")
async def check_flight_availability(
    flight_number: str,
    departure_date: str,
    passengers: int = 1,
    cabin_class: str = "economy",
    _plan_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check real-time availability for a specific flight with WebSocket updates.
    
    Args:
        flight_number: Flight number to check
        departure_date: Date of departure (YYYY-MM-DD)
        passengers: Number of passengers
        cabin_class: Desired cabin class
        _plan_id: Internal plan ID for WebSocket events
        
    Returns:
        Availability status and pricing information
    """
    try:
        result = await flight_service.check_availability(
            flight_number=flight_number,
            departure_date=departure_date,
            passengers=passengers,
            cabin_class=cabin_class
        )
        return result
    except Exception as e:
        logger.error(f"Error checking flight availability: {e}")
        return {
            "success": False,
            "error": str(e)
        }