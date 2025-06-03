"""Hotel-related tools for the travel planner."""

import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from strands.tools import tool
from ..models.travel_plan import Hotel
from ..services.mock.hotel_service import LocalDBHotelService

logger = logging.getLogger(__name__)

# Initialize the hotel service
hotel_service = LocalDBHotelService()


@tool
def search_hotels(
    location: str,
    check_in_date: str,
    check_out_date: str,
    guests: int = 2,
    rooms: int = 1,
    star_rating: Optional[List[int]] = None,
    amenities: Optional[List[str]] = None,
    max_price: Optional[float] = None,
    hotel_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for available hotels in a location using real hotel data.
    
    Args:
        location: City code (e.g., NYC, CDG, NRT) or city name
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        guests: Number of guests
        rooms: Number of rooms needed
        star_rating: List of acceptable star ratings (1-5)
        amenities: Required amenities (e.g., ['spa', 'pool', 'gym'])
        max_price: Maximum price per night
        hotel_type: Type of hotel (luxury, boutique, business, budget)
    
    Returns:
        List of available hotels matching criteria
    """
    try:
        # Call the database service
        results = asyncio.run(hotel_service.search_hotels(
            location=location,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            guests=guests,
            rooms=rooms,
            star_rating=star_rating,
            hotel_type=hotel_type,
            amenities=amenities,
            max_price=max_price
        ))
        
        if results['status'] == 'success':
            # Convert to Hotel model format for consistency
            hotels = []
            for h in results['results']:
                # Get the best available room option
                room_option = h['room_options'][0] if h['room_options'] else None
                
                if room_option:
                    hotel = Hotel(
                        hotel_id=str(h['hotel_id']),
                        name=h['name'],
                        location=h['location']['city'],
                        address=h['location']['address'],
                        star_rating=float(h['star_rating']),
                        price_per_night=room_option['price_per_night'],
                        amenities=h['amenities'],
                        room_type=room_option['room_type'],
                        availability=room_option['available'],
                        review_score=h.get('review_score', 8.0)
                    )
                    hotels.append(hotel.model_dump())
                    
            return {
                "success": True,
                "hotels": hotels,
                "search_parameters": results['search_params'],
                "total_results": results['total_results']
            }
        else:
            return {
                "success": False,
                "error": results.get('error', 'Failed to search hotels'),
                "hotels": [],
                "total_results": 0
            }
            
    except Exception as e:
        logger.error(f"Error searching hotels: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "hotels": [],
            "total_results": 0
        }


@tool
def get_hotel_details(hotel_id: int, check_in_date: str, check_out_date: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific hotel.
    
    Args:
        hotel_id: Unique hotel identifier from search results
        check_in_date: Check-in date for pricing
        check_out_date: Check-out date for pricing
    
    Returns:
        Detailed hotel information including room types and policies
    """
    try:
        results = asyncio.run(hotel_service.get_hotel_details(
            hotel_id=hotel_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date
        ))
        
        if results['status'] == 'success':
            hotel_data = results['hotel']
            
            # Find the best room type for simplified display
            best_room = hotel_data['room_types'][0] if hotel_data['room_types'] else None
            
            if best_room:
                hotel = Hotel(
                    hotel_id=str(hotel_data['hotel_id']),
                    name=hotel_data['name'],
                    location=hotel_data['location']['city'],
                    address=hotel_data['location']['address'],
                    star_rating=float(hotel_data['star_rating']),
                    price_per_night=best_room['average_price'],
                    amenities=hotel_data['amenities']['property'],
                    room_type=best_room['type'],
                    availability=best_room['available_rooms'] > 0,
                    review_score=hotel_data['review_summary']['overall_score']
                )
                
                return {
                    "success": True,
                    "hotel": hotel.model_dump(),
                    "additional_info": {
                        "description": hotel_data['description'],
                        "neighborhood": hotel_data['location']['neighborhood'],
                        "check_in_time": hotel_data['policies']['check_in_time'],
                        "check_out_time": hotel_data['policies']['check_out_time'],
                        "cancellation_policy": hotel_data['policies']['cancellation'],
                        "nearby_attractions": hotel_data['nearby_attractions'],
                        "room_types": hotel_data['room_types'],
                        "review_details": hotel_data['review_summary']
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No rooms available for selected dates"
                }
        else:
            return {
                "success": False,
                "error": results.get('error', 'Hotel not found')
            }
            
    except Exception as e:
        logger.error(f"Error getting hotel details: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@tool
def book_hotel(
    hotel_id: int,
    check_in_date: str,
    check_out_date: str,
    room_type: str,
    rooms: int,
    guests: List[Dict[str, str]],
    contact_email: str = "",
    contact_phone: str = ""
) -> Dict[str, Any]:
    """
    Book a hotel room for the specified guests.
    
    Args:
        hotel_id: Hotel ID from search results
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        room_type: Type of room to book (standard, deluxe, suite)
        rooms: Number of rooms to book
        guests: List of guest details [{"first_name": "John", "last_name": "Doe"}]
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
        results = asyncio.run(hotel_service.book_hotel(
            hotel_id=hotel_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            room_type=room_type.lower(),
            rooms=rooms,
            guests=guests,
            contact_info=contact_info
        ))
        
        if results['status'] == 'success':
            booking = results['booking']
            return {
                "success": True,
                "booking_reference": booking['booking_reference'],
                "status": booking['status'],
                "hotel": booking['hotel'],
                "reservation": booking['reservation'],
                "pricing": booking['pricing'],
                "policies": booking['policies'],
                "booking_date": booking['booking_date']
            }
        else:
            return {
                "success": False,
                "error": results.get('error', 'Failed to book hotel')
            }
            
    except Exception as e:
        logger.error(f"Error booking hotel: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@tool
def check_hotel_availability(
    hotel_id: int,
    check_in_date: str,
    check_out_date: str,
    room_type: str = "standard",
    rooms: int = 1
) -> Dict[str, Any]:
    """
    Check real-time availability for a specific hotel.
    
    Args:
        hotel_id: Hotel identifier from search results
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        room_type: Type of room (standard, deluxe, suite)
        rooms: Number of rooms needed
    
    Returns:
        Real-time availability status and pricing
    """
    try:
        results = asyncio.run(hotel_service.check_room_availability(
            hotel_id=hotel_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            room_type=room_type.lower(),
            rooms=rooms
        ))
        
        if results['status'] == 'success':
            availability = results['availability']
            return {
                "success": True,
                "hotel_id": hotel_id,
                "is_available": availability['available'],
                "available_rooms": availability['rooms_remaining'],
                "requested_rooms": rooms,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "nights": availability['nights'],
                "room_type": availability['room_type'],
                "price_per_night": availability['price_per_night'],
                "total_price": availability['total_price'],
                "includes": availability.get('includes', []),
                "urgency": availability.get('urgency')
            }
        else:
            return {
                "success": False,
                "error": results.get('error', 'Failed to check availability')
            }
            
    except Exception as e:
        logger.error(f"Error checking hotel availability: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }