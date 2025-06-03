"""Flight-related tools for the travel planner."""

import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from strands.tools import tool
from ..models.travel_plan import Flight
from ..services.mock.flight_service import LocalDBFlightService

logger = logging.getLogger(__name__)

# Initialize the flight service
flight_service = LocalDBFlightService()


@tool
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    cabin_class: str = "economy",
    max_price: Optional[float] = None,
    nonstop_only: bool = False
) -> Dict[str, Any]:
    """
    Search for available flights between two locations using real flight data.
    
    Args:
        origin: Airport code (e.g., NYC, CDG, NRT)
        destination: Airport code
        departure_date: Date in YYYY-MM-DD format
        return_date: Optional return date in YYYY-MM-DD format
        passengers: Number of passengers
        cabin_class: Class of service (economy, business, first)
        max_price: Maximum price per ticket
        nonstop_only: Only show nonstop flights
    
    Returns:
        Dictionary containing flight search results
    """
    try:
        # Call the database service
        results = asyncio.run(flight_service.search_flights(
            origin=origin.upper(),
            destination=destination.upper(),
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            cabin_class=cabin_class.lower(),
            max_price=max_price,
            nonstop_only=nonstop_only
        ))
        
        if results['status'] == 'success':
            # Convert to Flight model format for consistency
            outbound_flights = []
            for f in results['results']['outbound_flights']:
                flight = Flight(
                    flight_number=f['flight_number'],
                    airline=f['airline'],
                    origin=f['origin']['code'],
                    destination=f['destination']['code'],
                    departure_time=datetime.fromisoformat(f['departure']['datetime']),
                    arrival_time=datetime.fromisoformat(f['arrival']['datetime']),
                    price=f['price'],
                    cabin_class=f['cabin_class'],
                    duration_minutes=f['duration_minutes'],
                    stops=0,  # Direct flights for now
                    available_seats=f['seats_available']
                )
                outbound_flights.append(flight.model_dump())
                
            return_flights = []
            if results['results']['return_flights']:
                for f in results['results']['return_flights']:
                    flight = Flight(
                        flight_number=f['flight_number'],
                        airline=f['airline'],
                        origin=f['origin']['code'],
                        destination=f['destination']['code'],
                        departure_time=datetime.fromisoformat(f['departure']['datetime']),
                        arrival_time=datetime.fromisoformat(f['arrival']['datetime']),
                        price=f['price'],
                        cabin_class=f['cabin_class'],
                        duration_minutes=f['duration_minutes'],
                        stops=0,
                        available_seats=f['seats_available']
                    )
                    return_flights.append(flight.model_dump())
                    
            return {
                "success": True,
                "outbound_flights": outbound_flights,
                "return_flights": return_flights if return_flights else None,
                "search_parameters": results['search_params'],
                "total_results": results['results']['total_results']
            }
        else:
            return {
                "success": False,
                "error": results.get('error', 'Failed to search flights'),
                "outbound_flights": [],
                "return_flights": None
            }
            
    except Exception as e:
        logger.error(f"Error searching flights: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "outbound_flights": [],
            "return_flights": None
        }


@tool
def get_flight_details(flight_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific flight.
    
    Args:
        flight_id: Unique flight ID from search results
    
    Returns:
        Detailed flight information including aircraft, amenities, etc.
    """
    try:
        results = asyncio.run(flight_service.get_flight_details(flight_id))
        
        if results['status'] == 'success':
            flight_data = results['flight']
            
            # Convert to Flight model format
            flight = Flight(
                flight_number=flight_data['flight_number'],
                airline=flight_data['airline']['name'],
                origin=flight_data['route']['origin']['code'],
                destination=flight_data['route']['destination']['code'],
                departure_time=datetime.fromisoformat(flight_data['schedule']['departure']['datetime']),
                arrival_time=datetime.fromisoformat(flight_data['schedule']['arrival']['datetime']),
                price=flight_data['availability']['economy']['price'],
                cabin_class="economy",
                duration_minutes=flight_data['schedule']['duration_minutes'],
                stops=0,
                available_seats=flight_data['availability']['economy']['available']
            )
            
            return {
                "success": True,
                "flight": flight.model_dump(),
                "additional_info": {
                    "aircraft": flight_data['aircraft']['type'],
                    "aircraft_config": flight_data['aircraft']['configuration'],
                    "route_details": flight_data['route'],
                    "availability_by_class": flight_data['availability'],
                    "status": flight_data['status']
                }
            }
        else:
            return {
                "success": False,
                "error": results.get('error', 'Flight not found')
            }
            
    except Exception as e:
        logger.error(f"Error getting flight details: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@tool
def check_flight_availability(
    flight_id: int,
    cabin_class: str = "economy",
    passengers: int = 1
) -> Dict[str, Any]:
    """
    Check real-time availability for a specific flight.
    
    Args:
        flight_id: Unique flight ID from search results
        cabin_class: Class to check (economy, business, first)
        passengers: Number of passengers
    
    Returns:
        Real-time availability status and pricing
    """
    try:
        results = asyncio.run(flight_service.check_flight_availability(
            flight_id=flight_id,
            cabin_class=cabin_class.lower(),
            passengers=passengers
        ))
        
        if results['status'] == 'success':
            availability = results['availability']
            return {
                "success": True,
                "flight_id": flight_id,
                "is_available": availability['available'],
                "available_seats": availability['seats_remaining'],
                "requested_seats": passengers,
                "cabin_class": cabin_class,
                "pricing": {
                    "price_per_passenger": availability['price_per_passenger'],
                    "total_price": availability['total_price'],
                    "currency": availability['currency']
                },
                "fare_rules": availability.get('fare_rules', {})
            }
        else:
            return {
                "success": False,
                "error": results.get('error', 'Failed to check availability')
            }
            
    except Exception as e:
        logger.error(f"Error checking flight availability: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@tool
def book_flight(
    flight_id: int,
    passengers: List[Dict[str, str]],
    cabin_class: str = "economy",
    contact_email: str = "",
    contact_phone: str = ""
) -> Dict[str, Any]:
    """
    Book a flight for the specified passengers.
    
    Args:
        flight_id: Unique flight ID from search results
        passengers: List of passenger details [{"first_name": "John", "last_name": "Doe", "date_of_birth": "1990-01-01"}]
        cabin_class: Class to book (economy, business, first)
        contact_email: Contact email for booking confirmation
        contact_phone: Contact phone number
    
    Returns:
        Booking confirmation with reference number
    """
    try:
        # Prepare contact info
        contact_info = {
            "email": contact_email,
            "phone": contact_phone
        }
        
        # Call booking service
        results = asyncio.run(flight_service.book_flight(
            flight_id=flight_id,
            passengers=passengers,
            cabin_class=cabin_class.lower(),
            contact_info=contact_info
        ))
        
        if results['status'] == 'success':
            booking = results['booking']
            return {
                "success": True,
                "booking_reference": booking['booking_reference'],
                "status": booking['status'],
                "flight_details": booking['flight'],
                "passengers": booking['passengers'],
                "total_price": booking['total_price'],
                "tickets": booking['tickets'],
                "booking_date": booking['booking_date']
            }
        else:
            return {
                "success": False,
                "error": results.get('error', 'Failed to book flight')
            }
            
    except Exception as e:
        logger.error(f"Error booking flight: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }