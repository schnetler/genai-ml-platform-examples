"""Booking tools for flights, hotels, and activities."""

from typing import Dict, Any, List, Optional
from strands import tool
from ..services.mock.booking_service import LocalBookingService
from ..services.mock.flight_service import LocalDBFlightService
from ..services.mock.hotel_service import LocalDBHotelService

# Initialize services
booking_service = LocalBookingService()
flight_service = LocalDBFlightService()
hotel_service = LocalDBHotelService()


@tool
async def book_flight(
    flight_id: int,
    passengers: List[Dict[str, Any]],
    cabin_class: str = "economy",
    plan_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Book a flight for one or more passengers.
    
    Args:
        flight_id: The ID of the flight to book
        passengers: List of passenger dictionaries, each containing:
            - first_name: Passenger's first name
            - last_name: Passenger's last name
            - date_of_birth: Date of birth (YYYY-MM-DD)
            - passport_number: Passport number (optional)
            - email: Contact email
        cabin_class: Cabin class (economy, business, first)
        plan_id: Optional travel plan ID to link the booking
        
    Returns:
        Dictionary containing:
        - booking reference
        - flight details
        - total price
        - confirmation status
        
    Example:
        >>> passengers = [
        ...     {"first_name": "John", "last_name": "Doe", "date_of_birth": "1990-01-15", "email": "john@example.com"},
        ...     {"first_name": "Jane", "last_name": "Doe", "date_of_birth": "1992-03-20", "email": "jane@example.com"}
        ... ]
        >>> await book_flight(flight_id=12345, passengers=passengers, cabin_class="economy")
    """
    # Add cabin class to passenger info
    for passenger in passengers:
        passenger['cabin_class'] = cabin_class
    
    return await booking_service.book_flight(
        flight_id=flight_id,
        passengers=passengers,
        plan_id=plan_id
    )


@tool
async def book_hotel(
    hotel_id: int,
    check_in_date: str,
    check_out_date: str,
    room_type: str = "standard",
    rooms: int = 1,
    guest_names: List[str] = None,
    special_requests: Optional[str] = None,
    plan_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Book hotel room(s) for specified dates.
    
    Args:
        hotel_id: The ID of the hotel to book
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        room_type: Type of room (standard, deluxe, suite)
        rooms: Number of rooms to book
        guest_names: List of primary guest names (one per room)
        special_requests: Optional special requests (e.g., "High floor", "Near elevator")
        plan_id: Optional travel plan ID to link the booking
        
    Returns:
        Dictionary containing:
        - booking reference
        - hotel details
        - total price for all nights
        - confirmation status
        
    Example:
        >>> await book_hotel(
        ...     hotel_id=456,
        ...     check_in_date="2025-06-27",
        ...     check_out_date="2025-06-30",
        ...     room_type="deluxe",
        ...     rooms=1,
        ...     guest_names=["John Doe"]
        ... )
    """
    # Prepare guest details
    guests = []
    if guest_names:
        for i, name in enumerate(guest_names[:rooms]):
            guests.append({
                'name': name,
                'room_number': i + 1
            })
    else:
        # Default guest if no names provided
        for i in range(rooms):
            guests.append({
                'name': f'Guest {i + 1}',
                'room_number': i + 1
            })
    
    return await booking_service.book_hotel(
        hotel_id=hotel_id,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        room_type=room_type,
        rooms=rooms,
        guests=guests,
        plan_id=plan_id,
        special_requests=special_requests
    )


@tool
async def get_booking_details(booking_reference: str) -> Dict[str, Any]:
    """
    Retrieve details of an existing booking.
    
    Args:
        booking_reference: The booking reference number
        
    Returns:
        Dictionary containing full booking details including:
        - Booking status
        - Booked item details (flight/hotel/activity)
        - Guest information
        - Price breakdown
        - Cancellation policy
    """
    return await booking_service.get_booking(booking_reference)


@tool
async def cancel_booking(booking_reference: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Cancel an existing booking.
    
    Args:
        booking_reference: The booking reference to cancel
        reason: Optional reason for cancellation
        
    Returns:
        Dictionary containing:
        - Cancellation confirmation
        - Refund amount
        - Refund status
    """
    return await booking_service.cancel_booking(booking_reference, reason)


@tool
async def book_complete_trip(
    flights: List[Dict[str, Any]],
    hotels: List[Dict[str, Any]],
    passengers: List[Dict[str, Any]],
    plan_id: str
) -> Dict[str, Any]:
    """
    Book a complete trip including flights and hotels.
    
    Args:
        flights: List of flight bookings, each containing:
            - flight_id: ID of the flight
            - cabin_class: Cabin class preference
        hotels: List of hotel bookings, each containing:
            - hotel_id: ID of the hotel
            - check_in_date: Check-in date
            - check_out_date: Check-out date
            - room_type: Room type
            - rooms: Number of rooms
        passengers: List of passenger/guest details
        plan_id: Travel plan ID to link all bookings
        
    Returns:
        Dictionary containing:
        - List of all booking references
        - Total trip cost
        - Summary of booked items
    """
    bookings = []
    total_cost = 0
    errors = []
    
    # Book flights
    for flight_info in flights:
        try:
            result = await book_flight(
                flight_id=flight_info['flight_id'],
                passengers=passengers,
                cabin_class=flight_info.get('cabin_class', 'economy'),
                plan_id=plan_id
            )
            
            if result['status'] == 'success':
                bookings.append({
                    'type': 'flight',
                    'reference': result['booking']['reference'],
                    'details': result['booking']['flight'],
                    'price': result['booking']['total_price']
                })
                total_cost += result['booking']['total_price']
            else:
                errors.append(f"Flight booking failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            errors.append(f"Flight booking error: {str(e)}")
    
    # Book hotels
    guest_names = [p.get('first_name', '') + ' ' + p.get('last_name', '') for p in passengers]
    
    for hotel_info in hotels:
        try:
            result = await book_hotel(
                hotel_id=hotel_info['hotel_id'],
                check_in_date=hotel_info['check_in_date'],
                check_out_date=hotel_info['check_out_date'],
                room_type=hotel_info.get('room_type', 'standard'),
                rooms=hotel_info.get('rooms', 1),
                guest_names=guest_names[:hotel_info.get('rooms', 1)],
                plan_id=plan_id
            )
            
            if result['status'] == 'success':
                bookings.append({
                    'type': 'hotel',
                    'reference': result['booking']['reference'],
                    'details': result['booking']['hotel'],
                    'check_in': result['booking']['check_in'],
                    'check_out': result['booking']['check_out'],
                    'price': result['booking']['total_price']
                })
                total_cost += result['booking']['total_price']
            else:
                errors.append(f"Hotel booking failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            errors.append(f"Hotel booking error: {str(e)}")
    
    return {
        'status': 'success' if not errors else 'partial_success',
        'bookings': bookings,
        'total_cost': total_cost,
        'currency': 'USD',
        'errors': errors if errors else None,
        'summary': {
            'flights_booked': len([b for b in bookings if b['type'] == 'flight']),
            'hotels_booked': len([b for b in bookings if b['type'] == 'hotel']),
            'total_bookings': len(bookings)
        }
    }


@tool
async def check_and_book_flight(
    flight_id: int,
    passengers: List[Dict[str, Any]],
    cabin_class: str = "economy",
    plan_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check flight availability and price before booking.
    
    Args:
        flight_id: The ID of the flight to check and book
        passengers: List of passenger details
        cabin_class: Cabin class preference
        plan_id: Optional travel plan ID
        
    Returns:
        Dictionary with availability check and booking result
    """
    # First check flight details and availability
    flight_details = await flight_service.get_flight_details(flight_id)
    
    if flight_details['status'] != 'success':
        return {
            'status': 'error',
            'error': 'Flight not found'
        }
    
    flight = flight_details['flight']
    seats_available = flight['availability'][cabin_class]['seats_available']
    
    if seats_available < len(passengers):
        return {
            'status': 'error',
            'error': f'Only {seats_available} seats available in {cabin_class} class',
            'availability': flight['availability']
        }
    
    # Proceed with booking
    return await book_flight(
        flight_id=flight_id,
        passengers=passengers,
        cabin_class=cabin_class,
        plan_id=plan_id
    )