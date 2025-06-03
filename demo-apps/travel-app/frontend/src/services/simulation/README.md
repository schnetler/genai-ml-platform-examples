# Travel Planner Simulation System

This directory contains the simulation system for the travel planning application. It allows the frontend to function without connecting to the backend, making it useful for development, testing, and demonstrations.

## How It Works

The simulation system intercepts WebSocket messages in the frontend and generates mock responses that mimic the behavior of the backend. This allows developers to test the UI without requiring a working backend connection.

## Configuration

The simulation system is controlled by two environment variables in `.env.local`:

```
REACT_APP_USE_SIMULATION=true
REACT_APP_SIMULATION_TYPE=bali_trip
```

- `REACT_APP_USE_SIMULATION`: Set to `true` to enable simulation mode, `false` to use the real backend.
- `REACT_APP_SIMULATION_TYPE`: Specifies which simulation data to use. Options:
  - `bali_trip`: A 3-night trip to Bali for 2 people with a $3000 budget.
  - (Add other simulation types as they're implemented)

## Available Simulations

### Bali Trip

**Prompt**: "Plan a trip to Bali, Indonesia for 2 people for 3 nights with a budget of $3000 on 24-25 June"

This simulation demonstrates a complete travel planning flow for a short vacation to Bali. The simulation includes:

- Flight options from Sydney to Denpasar
- Hotel options in different areas of Bali
- Activity recommendations
- Budget breakdown
- Complete day-by-day itinerary

## Adding New Simulations

To add a new simulation:

1. Create a new file in the `simulations` directory (e.g., `newTrip.ts`)
2. Implement the required `SimulationData` interface
3. Register the simulation in `SimulationService.ts` by adding it to the `loadSimulations` method
4. Update this README to document the new simulation type

## How to Test

1. Set the environment variables in `.env.local`
2. Start the frontend
3. Use the travel planner as normal - the system will display the simulated responses