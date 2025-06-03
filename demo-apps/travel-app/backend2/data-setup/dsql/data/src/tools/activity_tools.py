"""Activity search and booking tools for travel planning."""

from typing import Dict, Any, List, Optional
import asyncio
from strands import tool
from ..services.mock.activity_service import LocalDBActivityService

# Initialize the activity service
activity_service = LocalDBActivityService()


@tool
def search_activities(
    location: str,
    activity_date: Optional[str] = None,
    category: Optional[str] = None,
    duration_max: Optional[float] = None,
    price_max: Optional[float] = None,
    tags: Optional[List[str]] = None,
    participants: int = 2
) -> Dict[str, Any]:
    """
    Search for activities and experiences in a destination.
    
    Args:
        location: City name or airport code
        activity_date: Date for the activity in YYYY-MM-DD format
        category: Activity category - one of: sightseeing, cultural, dining, romantic, adventure
        duration_max: Maximum duration in hours
        price_max: Maximum price per person in USD
        tags: List of tags to filter by (e.g., ["guided", "skip-the-line", "outdoor"])
        participants: Number of participants (default: 2)
        
    Returns:
        Dictionary containing:
        - results: List of activities with details
        - search_params: The parameters used for search
        - total_results: Number of activities found
        
    Example:
        Search for romantic activities in Paris under $150:
        >>> await search_activities("Paris", category="romantic", price_max=150)
        
        Search for half-day sightseeing tours:
        >>> await search_activities("Rome", category="sightseeing", duration_max=4)
    """
    return asyncio.run(activity_service.search_activities(
        location=location,
        activity_date=activity_date,
        category=category,
        duration_max=duration_max,
        price_max=price_max,
        tags=tags,
        participants=participants
    ))


@tool
def get_activity_details(activity_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific activity.
    
    Args:
        activity_id: The unique identifier for the activity
        
    Returns:
        Dictionary containing comprehensive activity details including:
        - Full description and what's included
        - Schedule and availability
        - Pricing breakdown
        - Meeting point and location details
        - Booking policies
        - Reviews and ratings
    """
    return asyncio.run(activity_service.get_activity_details(activity_id))


@tool
def check_activity_availability(
    activity_id: int,
    date: str,
    time_slot: str,
    participants: int = 2
) -> Dict[str, Any]:
    """
    Check if an activity is available for a specific date and time.
    
    Args:
        activity_id: The unique identifier for the activity
        date: Date to check in YYYY-MM-DD format
        time_slot: Time slot to check (e.g., "09:00", "14:00")
        participants: Number of participants
        
    Returns:
        Dictionary containing:
        - available: Boolean indicating if spots are available
        - spots_remaining: Number of spots left
        - date: The requested date
        - time_slot: The requested time
    """
    return asyncio.run(activity_service.check_availability(
        activity_id=activity_id,
        date=date,
        time_slot=time_slot,
        participants=participants
    ))


@tool
def filter_activities_by_interests(
    activities: List[Dict[str, Any]],
    interests: List[str],
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Filter and rank activities based on traveler interests.
    
    Args:
        activities: List of activity dictionaries from search results
        interests: List of traveler interests (e.g., ["art", "food", "history", "adventure"])
        max_results: Maximum number of activities to return
        
    Returns:
        Filtered and ranked list of activities matching interests
    """
    scored_activities = []
    
    for activity in activities:
        score = 0
        activity_tags = [tag.lower() for tag in activity.get('tags', [])]
        activity_name_lower = activity.get('name', '').lower()
        activity_desc_lower = activity.get('description', '').lower()
        
        # Score based on interest matches
        for interest in interests:
            interest_lower = interest.lower()
            
            # Direct tag match
            if interest_lower in activity_tags:
                score += 3
                
            # Category match
            if interest_lower in activity.get('category', '').lower():
                score += 2
                
            # Name or description match
            if interest_lower in activity_name_lower or interest_lower in activity_desc_lower:
                score += 1
                
        if score > 0:
            scored_activities.append({
                'activity': activity,
                'interest_score': score
            })
    
    # Sort by score and return top results
    scored_activities.sort(key=lambda x: x['interest_score'], reverse=True)
    
    return [item['activity'] for item in scored_activities[:max_results]]


@tool
def create_daily_itinerary(
    location: str,
    date: str,
    interests: List[str],
    budget_per_person: Optional[float] = None,
    start_time: str = "09:00",
    end_time: str = "18:00"
) -> Dict[str, Any]:
    """
    Create a suggested daily itinerary with activities.
    
    Args:
        location: City for the itinerary
        date: Date for the itinerary in YYYY-MM-DD format
        interests: List of interests to consider
        budget_per_person: Maximum budget per person for the day
        start_time: Preferred start time (default: "09:00")
        end_time: Preferred end time (default: "18:00")
        
    Returns:
        Dictionary containing:
        - itinerary: List of suggested activities with times
        - total_cost: Estimated total cost per person
        - total_duration: Total time for all activities
    """
    # Search for activities
    all_activities = asyncio.run(activity_service.search_activities(
        location=location,
        activity_date=date,
        price_max=budget_per_person
    ))
    
    if all_activities['status'] != 'success':
        return {
            'status': 'error',
            'error': 'Could not find activities for the location'
        }
    
    # Filter by interests
    activities = filter_activities_by_interests(
        all_activities['results'],
        interests,
        max_results=20
    )
    
    # Build itinerary
    itinerary = []
    current_time = datetime.strptime(start_time, "%H:%M")
    end_datetime = datetime.strptime(end_time, "%H:%M")
    total_cost = 0
    total_duration = 0
    
    # Add morning activity (sightseeing/cultural)
    morning_activities = [a for a in activities if a['category'] in ['sightseeing', 'cultural'] 
                         and a['duration']['hours'] <= 4]
    
    if morning_activities:
        activity = morning_activities[0]
        itinerary.append({
            'time': current_time.strftime("%H:%M"),
            'activity': activity,
            'duration': activity['duration']['formatted']
        })
        total_cost += activity['pricing']['adult']
        total_duration += activity['duration']['hours']
        current_time += timedelta(hours=activity['duration']['hours'])
    
    # Add lunch break
    if current_time.hour <= 12:
        current_time = datetime.strptime("12:30", "%H:%M")
        itinerary.append({
            'time': "12:30",
            'activity': {
                'name': 'Lunch Break',
                'category': 'dining',
                'description': 'Time for lunch at a local restaurant'
            },
            'duration': '1h 30min'
        })
        current_time += timedelta(hours=1.5)
    
    # Add afternoon activity
    afternoon_activities = [a for a in activities 
                          if a not in [i['activity'] for i in itinerary if 'pricing' in i.get('activity', {})]
                          and a['duration']['hours'] <= 3
                          and current_time.hour + a['duration']['hours'] <= end_datetime.hour]
    
    if afternoon_activities:
        activity = afternoon_activities[0]
        itinerary.append({
            'time': current_time.strftime("%H:%M"),
            'activity': activity,
            'duration': activity['duration']['formatted']
        })
        total_cost += activity['pricing']['adult']
        total_duration += activity['duration']['hours']
    
    return {
        'status': 'success',
        'location': location,
        'date': date,
        'itinerary': itinerary,
        'total_cost_per_person': total_cost,
        'total_duration_hours': total_duration,
        'recommendations': f"This itinerary focuses on {', '.join(interests[:3])} based on your interests"
    }


# Import datetime for itinerary creation
from datetime import datetime, timedelta