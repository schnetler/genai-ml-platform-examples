import { TravelPlan, BookingStatus } from '../../models/TravelPlan';
import { sampleTravelPlans } from '../travel/SampleTravelData';

/**
 * Generates simulated results for the demo mode
 */
export function generateSimulatedResults(agentType: string): any[] {
  // Get a sample travel plan to use for data
  const samplePlan = sampleTravelPlans[0]; // Use Japan travel plan by default
  
  switch (agentType) {
    case 'flight':
      return samplePlan.flights?.map((flight, index) => ({
        id: `flight-${index}`,
        type: 'flight',
        title: `${flight.airline} ${flight.flightNumber}`,
        description: `${flight.departure.airport} to ${flight.arrival.airport}`,
        data: flight,
        status: flight.status,
        timestamp: new Date().toISOString()
      })) || [];
      
    case 'hotel':
      return samplePlan.accommodations?.map((accommodation, index) => ({
        id: `accommodation-${index}`,
        type: 'accommodation',
        title: accommodation.name,
        description: `${accommodation.type} in ${accommodation.address}`,
        data: accommodation,
        status: accommodation.status,
        timestamp: new Date().toISOString()
      })) || [];
      
    case 'attraction':
    case 'dining':
      // Filter activities based on dining vs attractions
      const activities = samplePlan.activities?.filter(activity => {
        if (agentType === 'dining') {
          return activity.name.toLowerCase().includes('dining') || 
                activity.name.toLowerCase().includes('restaurant') ||
                activity.name.toLowerCase().includes('food') ||
                activity.name.toLowerCase().includes('meal');
        } else {
          return !activity.name.toLowerCase().includes('dining') && 
                !activity.name.toLowerCase().includes('restaurant') &&
                !activity.name.toLowerCase().includes('food');
        }
      });
      
      return (activities || []).map((activity, index) => ({
        id: `activity-${index}`,
        type: 'activity',
        title: activity.name,
        description: activity.description || activity.location || '',
        data: activity,
        status: activity.status || BookingStatus.PENDING,
        timestamp: new Date().toISOString()
      }));
      
    case 'scheduling':
      // Return the full itinerary
      return [{
        id: 'itinerary-1',
        type: 'itinerary',
        title: samplePlan.title,
        description: samplePlan.description || `${samplePlan.destination.name} travel plan`,
        data: samplePlan,
        status: BookingStatus.CONFIRMED,
        timestamp: new Date().toISOString()
      }];
      
    default:
      return [];
  }
}