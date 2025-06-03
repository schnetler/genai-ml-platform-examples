// Export the simulation service
import simulationService from './SimulationService';
export { default as simulationService } from './SimulationService';

// Export types
export type { SimulationData, SimulationResponseHandler } from './types';

// Export simulations
export { baliTripSimulation } from './simulations/baliTrip';

// Export the service as default
export default simulationService;