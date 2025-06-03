import { WebSocketMessage } from '../../common/apiClient';
import { SimulationData, SimulationResponseHandler } from '../types';
import { v4 as uuidv4 } from 'uuid';

/**
 * Helper function to generate a timestamp for messages
 */
const getTimestamp = (): string => new Date().toISOString();

/**
 * Helper function to create a unique ID
 */
const generateId = (): string => uuidv4();

/**
 * Helper function to wait for a specified time
 */
const delay = (ms: number): Promise<void> => 
  new Promise(resolve => setTimeout(resolve, ms));

/**
 * Bali trip simulation data
 */
export const baliTripSimulation: SimulationData = {
  name: 'Bali Trip',
  description: 'A 3-night trip to Bali, Indonesia for 2 people with a budget of $3000',
  prompt: 'Plan a trip to Bali, Indonesia for 2 people for 3 nights with a budget of $3000 on 24-25 June',
  
  // Initial message to display when starting the simulation
  initialMessage: {
    type: 'connection_ack',
    payload: {
      message: 'Connected to travel planning service (Simulation Mode)',
      status: 'CONNECTED',
      simulationMode: true,
      simulationType: 'bali_trip',
      timestamp: getTimestamp()
    }
  },
  
  /**
   * Handle the initial travel planning request
   */
  handleStartTravel: async (planRequest: any, onResponse: SimulationResponseHandler) => {
    console.log('🌴 BALI TRIP SIMULATION: Starting travel planning sequence', planRequest);
    
    // Acknowledge the request
    onResponse({
      type: "plan_update",
      payload: {
        message: 'Starting travel planning process...',
        planId: generateId(),
        status: 'PLANNING',
        timestamp: getTimestamp()
      }
    });
    
    // Wait a moment to simulate processing
    await delay(1500);
    
    // First notification - planning started
    onResponse({
      type: "notification",
      payload: {
        message: 'Planning your trip to Bali, Indonesia',
        timestamp: getTimestamp(),
        data: {
          type: 'PLANNING_STARTED',
          currentStage: 'PLANNING',
          details: {
            userGoal: 'Plan a trip to Bali, Indonesia for 2 people for 3 nights with a budget of $3000 on 24-25 June',
            activeAgents: ['DestinationAgent']
          }
        }
      }
    });
    
    // Wait a moment before showing destination information
    await delay(3000);
    
    // Destination information
    onResponse({
      type: "results_updated",
      payload: {
        timestamp: getTimestamp(),
        results: {
          destination: {
            name: 'Bali',
            country: 'Indonesia',
            description: 'Bali is an Indonesian island known for its forested volcanic mountains, iconic rice paddies, beaches and coral reefs. The island is home to religious sites such as cliffside Uluwatu Temple. To the south, the beachside city of Kuta has lively bars, while Seminyak, Sanur and Nusa Dua are popular resort towns.',
            imageUrl: 'https://source.unsplash.com/random/800x600/?bali',
            climate: 'Tropical',
            currency: 'Indonesian Rupiah (IDR)',
            language: 'Indonesian (Bahasa Indonesia)',
            timeZone: 'WITA (UTC+8)',
            bestTimeToVisit: 'April to October (dry season)',
            visaRequirements: 'Visa-free for many countries for up to 30 days'
          }
        }
      }
    });
    
    // Notify that we're now searching for flights
    await delay(2000);
    
    // First send a STAGE_CHANGE message
    onResponse({
      type: "STAGE_CHANGE",
      payload: {
        currentStage: 'executing',
        previousStage: 'planning'
      },
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation'
    });
    
    // Then activate the flight agent
    onResponse({
      type: "AGENT_ACTIVATED",
      payload: {
        agentType: 'flight',
        agentName: 'Flight Expert'
      },
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation'
    });
    
    // Also send the original notification for backward compatibility
    onResponse({
      type: "notification",
      payload: {
        message: 'Searching for flights to Bali',
        timestamp: getTimestamp(),
        data: {
          type: 'STAGE_CHANGE',
          currentStage: 'SEARCHING_FLIGHTS',
          previousStage: 'PLANNING',
          details: {
            activeAgents: ['FlightAgent']
          }
        }
      }
    });
    
    // Wait a bit longer for flight results
    await delay(4000);
    
    // Flight search results
    onResponse({
      type: "RESULTS_UPDATED",
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation',
      payload: {
        results: [
          {
            type: 'flight',
            title: 'Round-trip to Bali',
            description: 'Departing Sydney on June 24, 2023, returning June 27. Economy class, 2 adults.',
            details: {
              flights: [
                {
                  id: 'F-' + generateId().substring(0, 8),
              airline: 'Jetstar Airways',
              flightNumber: 'JQ43',
              departureAirport: 'SYD',
              departureCity: 'Sydney',
              arrivalAirport: 'DPS',
              arrivalCity: 'Denpasar, Bali',
              departureDate: '2023-06-24',
              departureTime: '10:15',
              arrivalDate: '2023-06-24',
              arrivalTime: '15:45',
              duration: '6h 30m',
              stops: 0,
              price: 849.99,
              currency: 'USD',
              cabinClass: 'Economy',
              seatsAvailable: 8,
              returnFlight: {
                airline: 'Jetstar Airways',
                flightNumber: 'JQ44',
                departureAirport: 'DPS',
                departureCity: 'Denpasar, Bali',
                arrivalAirport: 'SYD',
                arrivalCity: 'Sydney',
                departureDate: '2023-06-27',
                departureTime: '16:30',
                arrivalDate: '2023-06-27',
                arrivalTime: '23:55',
                duration: '7h 25m',
                stops: 0
              }
            },
            {
              id: 'F-' + generateId().substring(0, 8),
              airline: 'Garuda Indonesia',
              flightNumber: 'GA715',
              departureAirport: 'SYD',
              departureCity: 'Sydney',
              arrivalAirport: 'DPS',
              arrivalCity: 'Denpasar, Bali',
              departureDate: '2023-06-24',
              departureTime: '12:30',
              arrivalDate: '2023-06-24',
              arrivalTime: '18:15',
              duration: '6h 45m',
              stops: 0,
              price: 1099.99,
              currency: 'USD',
              cabinClass: 'Economy',
              seatsAvailable: 12,
              returnFlight: {
                airline: 'Garuda Indonesia',
                flightNumber: 'GA714',
                departureAirport: 'DPS',
                departureCity: 'Denpasar, Bali',
                arrivalAirport: 'SYD',
                arrivalCity: 'Sydney',
                departureDate: '2023-06-27',
                departureTime: '19:45',
                arrivalDate: '2023-06-28',
                arrivalTime: '03:20',
                duration: '7h 35m',
                stops: 0
              }
            },
            {
              id: 'F-' + generateId().substring(0, 8),
              airline: 'Qantas',
              flightNumber: 'QF43',
              departureAirport: 'SYD',
              departureCity: 'Sydney',
              arrivalAirport: 'DPS',
              arrivalCity: 'Denpasar, Bali',
              departureDate: '2023-06-24',
              departureTime: '09:45',
              arrivalDate: '2023-06-24',
              arrivalTime: '14:55',
              duration: '6h 10m',
              stops: 0,
              price: 1249.99,
              currency: 'USD',
              cabinClass: 'Economy',
              seatsAvailable: 5,
              returnFlight: {
                airline: 'Qantas',
                flightNumber: 'QF44',
                departureAirport: 'DPS',
                departureCity: 'Denpasar, Bali',
                arrivalAirport: 'SYD',
                arrivalCity: 'Sydney',
                departureDate: '2023-06-27',
                departureTime: '15:45',
                arrivalDate: '2023-06-27',
                arrivalTime: '22:15',
                duration: '6h 30m',
                stops: 0
              }
            }
              ]
            }
          }
        ]
      }
    });
    
    // Flight recommendation
    await delay(2500);
    onResponse({
      type: "notification",
      payload: {
        message: 'Flight expert analyzing options',
        timestamp: getTimestamp(),
        data: {
          type: 'AGENT_ACTIVATED',
          agentType: 'FlightExpertAgent',
          details: {
            activeAgents: ['FlightExpertAgent']
          }
        }
      }
    });
    
    // Flight recommendation result
    await delay(3000);
    onResponse({
      type: "RESULTS_UPDATED",
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation',
      payload: {
        results: [
          {
            type: 'flight',
            title: 'Recommended Flight to Bali',
            description: 'Best value flight option based on price and convenience',
            details: {
              recommendedFlights: [
                {
                  id: 'F-' + generateId().substring(0, 8),
              airline: 'Jetstar Airways',
              flightNumber: 'JQ43',
              departureAirport: 'SYD',
              departureCity: 'Sydney',
              arrivalAirport: 'DPS',
              arrivalCity: 'Denpasar, Bali',
              departureDate: '2023-06-24',
              departureTime: '10:15',
              arrivalDate: '2023-06-24',
              arrivalTime: '15:45',
              duration: '6h 30m',
              stops: 0,
              price: 849.99,
              currency: 'USD',
              cabinClass: 'Economy',
              seatsAvailable: 8,
              returnFlight: {
                airline: 'Jetstar Airways',
                flightNumber: 'JQ44',
                departureAirport: 'DPS',
                departureCity: 'Denpasar, Bali',
                arrivalAirport: 'SYD',
                arrivalCity: 'Sydney',
                departureDate: '2023-06-27',
                departureTime: '16:30',
                arrivalDate: '2023-06-27',
                arrivalTime: '23:55',
                duration: '7h 25m',
                stops: 0
              },
              reasonForRecommendation: 'Best value for money with direct flights at convenient times.'
            }
              ]
            }
          }
        ]
      }
    });
    
    // Hotel search notification
    await delay(2000);
    onResponse({
      type: "notification",
      payload: {
        message: 'Searching for hotels in Bali',
        timestamp: getTimestamp(),
        data: {
          type: 'STAGE_CHANGE',
          currentStage: 'SEARCHING_HOTELS',
          previousStage: 'SEARCHING_FLIGHTS',
          details: {
            activeAgents: ['HotelAgent']
          }
        }
      }
    });
    
    // Hotel search results
    await delay(4000);
    onResponse({
      type: "RESULTS_UPDATED",
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation',
      payload: {
        results: [
          {
            type: 'accommodation',
            title: 'Hotels in Bali',
            description: 'Accommodation options for your stay',
            details: {
              hotels: [
                {
                  id: 'H-' + generateId().substring(0, 8),
              name: 'Alila Seminyak',
              address: 'Jl. Taman Ganesha No.9, Seminyak, Bali',
              location: {
                latitude: -8.6747,
                longitude: 115.1563,
                address: 'Seminyak, Bali, Indonesia'
              },
              starRating: 5,
              price: 320,
              currency: 'USD',
              pricePerNight: true,
              totalPrice: 960,
              amenities: ['Beach Access', 'Swimming Pool', 'Spa', 'Restaurant', 'Free Wi-Fi', 'Airport Shuttle'],
              images: ['https://source.unsplash.com/random/800x600/?hotel,bali,luxury'],
              roomType: 'Deluxe Ocean View',
              checkIn: '2023-06-24',
              checkOut: '2023-06-27',
              guestCapacity: 2,
              description: 'Located on Bali\'s southwest coast, Alila Seminyak is a stunning beachfront resort with modern amenities and spacious rooms.'
            },
            {
              id: 'H-' + generateId().substring(0, 8),
              name: 'Ubud Hanging Gardens',
              address: 'Desa Buahan, Payangan, Gianyar, Bali',
              location: {
                latitude: -8.4207,
                longitude: 115.2522,
                address: 'Ubud, Bali, Indonesia'
              },
              starRating: 4,
              price: 280,
              currency: 'USD',
              pricePerNight: true,
              totalPrice: 840,
              amenities: ['Infinity Pool', 'Spa', 'Restaurant', 'Free Wi-Fi', 'Room Service', 'Jungle Views'],
              images: ['https://source.unsplash.com/random/800x600/?hotel,bali,ubud'],
              roomType: 'Deluxe Valley View',
              checkIn: '2023-06-24',
              checkOut: '2023-06-27',
              guestCapacity: 2,
              description: 'Set in the heart of Bali, Ubud Hanging Gardens offers breathtaking views of the jungle and spacious villas with private pools.'
            },
            {
              id: 'H-' + generateId().substring(0, 8),
              name: 'Kuta Beach Resort',
              address: 'Jl. Pantai Kuta, Kuta, Bali',
              location: {
                latitude: -8.7214,
                longitude: 115.1686,
                address: 'Kuta, Bali, Indonesia'
              },
              starRating: 3,
              price: 180,
              currency: 'USD',
              pricePerNight: true,
              totalPrice: 540,
              amenities: ['Swimming Pool', 'Restaurant', 'Free Wi-Fi', 'Beach Access', 'Air Conditioning'],
              images: ['https://source.unsplash.com/random/800x600/?hotel,bali,kuta'],
              roomType: 'Standard Room',
              checkIn: '2023-06-24',
              checkOut: '2023-06-27',
              guestCapacity: 2,
              description: 'Located in lively Kuta, this resort offers comfortable accommodation with easy access to the beach, shopping, and nightlife.'
            }
              ]
            }
          }
        ]
      }
    });
    
    // Hotel recommendation
    await delay(2500);
    onResponse({
      type: "notification",
      payload: {
        message: 'Hotel expert analyzing options',
        timestamp: getTimestamp(),
        data: {
          type: 'AGENT_ACTIVATED',
          agentType: 'HotelExpertAgent',
          details: {
            activeAgents: ['HotelExpertAgent']
          }
        }
      }
    });
    
    // Hotel recommendation result
    await delay(3000);
    onResponse({
      type: "RESULTS_UPDATED",
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation',
      payload: {
        results: [
          {
            type: 'accommodation',
            title: 'Recommended Bali Hotel',
            description: 'Best hotel option for your stay',
            details: {
              recommendedHotels: [
                {
                  id: 'H-' + generateId().substring(0, 8),
              name: 'Ubud Hanging Gardens',
              address: 'Desa Buahan, Payangan, Gianyar, Bali',
              location: {
                latitude: -8.4207,
                longitude: 115.2522,
                address: 'Ubud, Bali, Indonesia'
              },
              starRating: 4,
              price: 280,
              currency: 'USD',
              pricePerNight: true,
              totalPrice: 840,
              amenities: ['Infinity Pool', 'Spa', 'Restaurant', 'Free Wi-Fi', 'Room Service', 'Jungle Views'],
              images: ['https://source.unsplash.com/random/800x600/?hotel,bali,ubud'],
              roomType: 'Deluxe Valley View',
              checkIn: '2023-06-24',
              checkOut: '2023-06-27',
              guestCapacity: 2,
              description: 'Set in the heart of Bali, Ubud Hanging Gardens offers breathtaking views of the jungle and spacious villas with private pools.',
              reasonForRecommendation: 'Great value with authentic Balinese experience in Ubud, providing a perfect balance of luxury and cultural immersion.'
            }
              ]
            }
          }
        ]
      }
    });
    
    // Activity search notification
    await delay(2000);
    onResponse({
      type: "notification",
      payload: {
        message: 'Searching for activities in Bali',
        timestamp: getTimestamp(),
        data: {
          type: 'STAGE_CHANGE',
          currentStage: 'SEARCHING_ACTIVITIES',
          previousStage: 'SEARCHING_HOTELS',
          details: {
            activeAgents: ['ActivitiesAgent']
          }
        }
      }
    });
    
    // Activity search results
    await delay(4000);
    onResponse({
      type: "RESULTS_UPDATED",
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation',
      payload: {
        results: [
          {
            type: 'activity',
            title: 'Bali Activities',
            description: 'Exciting experiences and attractions in Bali',
            details: {
              activities: [
                {
                  id: 'A-' + generateId().substring(0, 8),
              name: 'Ubud Sacred Monkey Forest',
              location: 'Ubud, Bali',
              category: 'Nature',
              price: 20,
              currency: 'USD',
              duration: '2 hours',
              description: 'Explore this sacred nature reserve and temple complex with over 700 monkeys roaming freely.',
              images: ['https://source.unsplash.com/random/800x600/?monkey,forest,bali'],
              bookingRequired: true,
              availableDates: ['2023-06-25', '2023-06-26']
            },
            {
              id: 'A-' + generateId().substring(0, 8),
              name: 'Tegallalang Rice Terraces',
              location: 'Tegallalang, Bali',
              category: 'Sightseeing',
              price: 15,
              currency: 'USD',
              duration: '3 hours',
              description: 'Visit the stunning stepped rice paddies, famous for their beautiful paths and traditional Balinese subak irrigation system.',
              images: ['https://source.unsplash.com/random/800x600/?rice,terraces,bali'],
              bookingRequired: false,
              availableDates: ['2023-06-25', '2023-06-26', '2023-06-27']
            },
            {
              id: 'A-' + generateId().substring(0, 8),
              name: 'Uluwatu Temple Sunset & Kecak Dance',
              location: 'Uluwatu, Bali',
              category: 'Cultural',
              price: 25,
              currency: 'USD',
              duration: '4 hours',
              description: 'Experience the breathtaking clifftop temple at sunset followed by a traditional Kecak fire dance performance.',
              images: ['https://source.unsplash.com/random/800x600/?uluwatu,temple,bali'],
              bookingRequired: true,
              availableDates: ['2023-06-25', '2023-06-26']
            },
            {
              id: 'A-' + generateId().substring(0, 8),
              name: 'Mount Batur Sunrise Trek',
              location: 'Kintamani, Bali',
              category: 'Adventure',
              price: 65,
              currency: 'USD',
              duration: '7 hours',
              description: 'Early morning hike up Mount Batur to watch the sunrise over the stunning volcanic landscape.',
              images: ['https://source.unsplash.com/random/800x600/?mount,batur,bali'],
              bookingRequired: true,
              availableDates: ['2023-06-25', '2023-06-26']
            },
            {
              id: 'A-' + generateId().substring(0, 8),
              name: 'Balinese Cooking Class',
              location: 'Ubud, Bali',
              category: 'Food & Drink',
              price: 45,
              currency: 'USD',
              duration: '4 hours',
              description: 'Learn to prepare authentic Balinese dishes with local chefs, including a market visit to select fresh ingredients.',
              images: ['https://source.unsplash.com/random/800x600/?cooking,class,bali'],
              bookingRequired: true,
              availableDates: ['2023-06-25', '2023-06-26']
            }
              ]
            }
          }
        ]
      }
    });
    
    // Activity recommendations
    await delay(3000);
    onResponse({
      type: "RESULTS_UPDATED",
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation',
      payload: {
        results: [
          {
            type: 'activity',
            title: 'Recommended Bali Activities',
            description: 'Carefully selected activities for your trip',
            details: {
              recommendedActivities: [
                {
                  id: 'A-' + generateId().substring(0, 8),
              name: 'Tegallalang Rice Terraces',
              location: 'Tegallalang, Bali',
              category: 'Sightseeing',
              price: 15,
              currency: 'USD',
              duration: '3 hours',
              description: 'Visit the stunning stepped rice paddies, famous for their beautiful paths and traditional Balinese subak irrigation system.',
              images: ['https://source.unsplash.com/random/800x600/?rice,terraces,bali'],
              bookingRequired: false,
              availableDates: ['2023-06-25'],
              reasonForRecommendation: 'Must-see cultural attraction near your hotel in Ubud.',
              recommendedDate: '2023-06-25',
              recommendedTime: '10:00'
            },
            {
              id: 'A-' + generateId().substring(0, 8),
              name: 'Balinese Cooking Class',
              location: 'Ubud, Bali',
              category: 'Food & Drink',
              price: 45,
              currency: 'USD',
              duration: '4 hours',
              description: 'Learn to prepare authentic Balinese dishes with local chefs, including a market visit to select fresh ingredients.',
              images: ['https://source.unsplash.com/random/800x600/?cooking,class,bali'],
              bookingRequired: true,
              availableDates: ['2023-06-26'],
              reasonForRecommendation: 'Highly-rated cultural experience that lets you bring Balinese cuisine skills home.',
              recommendedDate: '2023-06-26',
              recommendedTime: '09:00'
            },
            {
              id: 'A-' + generateId().substring(0, 8),
              name: 'Uluwatu Temple Sunset & Kecak Dance',
              location: 'Uluwatu, Bali',
              category: 'Cultural',
              price: 25,
              currency: 'USD',
              duration: '4 hours',
              description: 'Experience the breathtaking clifftop temple at sunset followed by a traditional Kecak fire dance performance.',
              images: ['https://source.unsplash.com/random/800x600/?uluwatu,temple,bali'],
              bookingRequired: true,
              availableDates: ['2023-06-26'],
              reasonForRecommendation: 'Perfect evening activity with spectacular views and cultural performance.',
              recommendedDate: '2023-06-26',
              recommendedTime: '16:00'
            }
              ]
            }
          }
        ]
      }
    });
    
    // Budget check
    await delay(2000);
    onResponse({
      type: "notification",
      payload: {
        message: 'Checking budget constraints',
        timestamp: getTimestamp(),
        data: {
          type: 'AGENT_ACTIVATED',
          agentType: 'BudgetAgent',
          details: {
            activeAgents: ['BudgetAgent']
          }
        }
      }
    });
    
    // Budget breakdown
    await delay(2500);
    onResponse({
      type: "RESULTS_UPDATED",
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation',
      payload: {
        results: [
          {
            type: 'budget',
            title: 'Trip Budget',
            description: 'Financial breakdown for your Bali trip',
            details: {
              budget: {
                totalBudget: 3000,
                currency: 'USD',
                allocatedBudget: 2824.99,
                remainingBudget: 175.01,
                breakdown: {
                  flights: 1699.98, // 849.99 x 2 persons
                  accommodation: 840, // 280 x 3 nights
                  activities: 255, // 15 + 45 + 25 + 85 (food) + 85 (transportation)
                  food: 170, // Estimated for 3 days
                  transportation: 35, // Local transportation
                  extras: 0
                },
                status: 'WITHIN_BUDGET'
              }
            }
          }
        ]
      }
    });
    
    // Create itinerary
    await delay(2000);
    onResponse({
      type: "notification",
      payload: {
        message: 'Creating your Bali itinerary',
        timestamp: getTimestamp(),
        data: {
          type: 'STAGE_CHANGE',
          currentStage: 'CREATING_ITINERARY',
          previousStage: 'SEARCHING_ACTIVITIES',
          details: {
            activeAgents: ['ItineraryAgent']
          }
        }
      }
    });
    
    // Final itinerary
    await delay(4000);
    onResponse({
      type: "RESULTS_UPDATED",
      timestamp: getTimestamp(),
      sessionId: 'bali-simulation',
      payload: {
        results: [
          {
            type: 'itinerary',
            title: '3-Night Bali Itinerary',
            description: 'Your day-by-day plan for an amazing Bali trip',
            details: {
              itinerary: {
                id: 'I-' + generateId(),
                title: '3-Night Bali Adventure',
                description: 'A perfect blend of culture, nature, and relaxation in beautiful Bali.',
                startDate: '2023-06-24',
                endDate: '2023-06-27',
                destination: 'Bali, Indonesia',
                totalCost: 2824.99,
                currency: 'USD',
                days: [
                  {
                    date: '2023-06-24',
                    title: 'Arrival Day',
                    description: 'Arrive in Bali and settle into your accommodation.',
                    items: [
                      {
                        time: '10:15 - 15:45',
                        title: 'Flight from Sydney to Denpasar',
                        description: 'Jetstar Airways JQ43',
                        type: 'transportation',
                        duration: '6h 30m'
                  },
                  {
                    time: '16:30 - 18:00',
                    title: 'Transfer to Ubud',
                    description: 'Private transfer from airport to hotel (included)',
                    type: 'transportation',
                    duration: '1h 30m'
                  },
                  {
                    time: '18:00',
                    title: 'Check-in at Ubud Hanging Gardens',
                    description: 'Deluxe Valley View room',
                    type: 'accommodation'
                  },
                  {
                    time: '19:30',
                    title: 'Dinner at hotel restaurant',
                    description: 'Welcome dinner with traditional Balinese cuisine',
                    type: 'food',
                    price: 30,
                    currency: 'USD'
                  }
                ]
              },
              {
                date: '2023-06-25',
                title: 'Ubud Exploration',
                description: 'Discover the cultural heart of Bali.',
                items: [
                  {
                    time: '07:00 - 09:00',
                    title: 'Breakfast at hotel',
                    description: 'Included with accommodation',
                    type: 'food'
                  },
                  {
                    time: '10:00 - 13:00',
                    title: 'Tegallalang Rice Terraces',
                    description: 'Visit the stunning stepped rice paddies',
                    type: 'activity',
                    price: 15,
                    currency: 'USD',
                    duration: '3h'
                  },
                  {
                    time: '13:30 - 15:00',
                    title: 'Lunch in Ubud',
                    description: 'Traditional Balinese lunch at a local warung',
                    type: 'food',
                    price: 15,
                    currency: 'USD'
                  },
                  {
                    time: '15:30 - 17:30',
                    title: 'Ubud Sacred Monkey Forest',
                    description: 'Explore the nature reserve and temple complex',
                    type: 'activity',
                    price: 20,
                    currency: 'USD',
                    duration: '2h'
                  },
                  {
                    time: '19:00',
                    title: 'Dinner in Ubud',
                    description: 'Dinner at a local restaurant with traditional dance performance',
                    type: 'food',
                    price: 25,
                    currency: 'USD'
                  }
                ]
              },
              {
                date: '2023-06-26',
                title: 'Cultural Immersion',
                description: 'Immerse yourself in Balinese culture and traditions.',
                items: [
                  {
                    time: '07:00 - 08:30',
                    title: 'Breakfast at hotel',
                    description: 'Included with accommodation',
                    type: 'food'
                  },
                  {
                    time: '09:00 - 13:00',
                    title: 'Balinese Cooking Class',
                    description: 'Learn to prepare authentic Balinese dishes',
                    type: 'activity',
                    price: 45,
                    currency: 'USD',
                    duration: '4h'
                  },
                  {
                    time: '13:30 - 15:00',
                    title: 'Free time / Relax at hotel',
                    description: 'Enjoy the hotel facilities or explore Ubud town',
                    type: 'free time',
                    duration: '1h 30m'
                  },
                  {
                    time: '16:00 - 20:00',
                    title: 'Uluwatu Temple Sunset & Kecak Dance',
                    description: 'Visit the clifftop temple and watch traditional fire dance',
                    type: 'activity',
                    price: 25,
                    currency: 'USD',
                    duration: '4h'
                  },
                  {
                    time: '20:30',
                    title: 'Seafood dinner at Jimbaran Bay',
                    description: 'Fresh seafood dinner on the beach',
                    type: 'food',
                    price: 35,
                    currency: 'USD'
                  }
                ]
              },
              {
                date: '2023-06-27',
                title: 'Departure Day',
                description: 'Final day in paradise before returning home.',
                items: [
                  {
                    time: '07:00 - 09:00',
                    title: 'Breakfast at hotel',
                    description: 'Included with accommodation',
                    type: 'food'
                  },
                  {
                    time: '09:00 - 12:00',
                    title: 'Free time / Spa treatment',
                    description: 'Optional spa treatment or last-minute shopping',
                    type: 'free time',
                    duration: '3h'
                  },
                  {
                    time: '12:00',
                    title: 'Check-out from Ubud Hanging Gardens',
                    description: 'Check-out and prepare for departure',
                    type: 'accommodation'
                  },
                  {
                    time: '12:30 - 14:00',
                    title: 'Transfer to airport',
                    description: 'Private transfer from hotel to airport',
                    type: 'transportation',
                    duration: '1h 30m'
                  },
                  {
                    time: '16:30 - 23:55',
                    title: 'Flight from Denpasar to Sydney',
                    description: 'Jetstar Airways JQ44',
                    type: 'transportation',
                    duration: '7h 25m'
                      }
                    ]
                  }
                ]
              }
            }
          }
        ]
      }
    });
    
    // Final plan status
    await delay(2000);
    onResponse({
      type: "plan_update",
      payload: {
        message: 'Travel plan completed',
        planId: generateId(),
        status: 'COMPLETED',
        timestamp: getTimestamp()
      }
    });
  },
  
  /**
   * Handle user messages during the simulation
   */
  handleUserMessage: async (message: string, onResponse: SimulationResponseHandler) => {
    // Acknowledge the message
    onResponse({
      type: "notification",
      payload: {
        message: 'Message received',
        timestamp: getTimestamp(),
        data: {
          type: 'MESSAGE_RECEIVED',
          content: message
        }
      }
    });
    
    // Wait a moment to simulate processing
    await delay(2000);
    
    // Simple responses based on message content
    if (message.toLowerCase().includes('budget')) {
      onResponse({
        type: "notification",
        payload: {
          message: 'Your budget of $3000 covers flights, accommodation, and activities for 2 people.',
          timestamp: getTimestamp(),
          data: {
            type: 'INFORMATION',
            source: 'BudgetAgent'
          }
        }
      });
    } else if (message.toLowerCase().includes('flight')) {
      onResponse({
        type: "notification",
        payload: {
          message: 'We recommend the Jetstar Airways direct flight for the best value.',
          timestamp: getTimestamp(),
          data: {
            type: 'INFORMATION',
            source: 'FlightExpertAgent'
          }
        }
      });
    } else if (message.toLowerCase().includes('hotel') || message.toLowerCase().includes('accommodation')) {
      onResponse({
        type: "notification",
        payload: {
          message: 'The Ubud Hanging Gardens offers the best balance of luxury and value within your budget.',
          timestamp: getTimestamp(),
          data: {
            type: 'INFORMATION',
            source: 'HotelExpertAgent'
          }
        }
      });
    } else if (message.toLowerCase().includes('activity') || message.toLowerCase().includes('activities')) {
      onResponse({
        type: "notification",
        payload: {
          message: 'We\'ve selected activities that showcase Bali\'s culture, nature, and cuisine.',
          timestamp: getTimestamp(),
          data: {
            type: 'INFORMATION',
            source: 'ActivitiesAgent'
          }
        }
      });
    } else {
      // Generic response
      onResponse({
        type: "notification",
        payload: {
          message: 'Thank you for your message. Your 3-night trip to Bali has been planned within your $3000 budget.',
          timestamp: getTimestamp(),
          data: {
            type: 'INFORMATION',
            source: 'TravelPlanAgent'
          }
        }
      });
    }
  }
};