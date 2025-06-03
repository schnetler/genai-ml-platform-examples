import { WebSocketMessage } from '../common/apiClient';

/**
 * Type for simulation response handler
 */
export type SimulationResponseHandler = (message: WebSocketMessage) => void;

/**
 * Type for a simulation data object
 */
export interface SimulationData {
  // Simulation metadata
  name: string;
  description: string;
  prompt: string;
  
  // Initial message to display when starting the simulation
  initialMessage: WebSocketMessage;
  
  // Response handlers for different message types
  handleStartTravel: (planRequest: any, onResponse: SimulationResponseHandler) => void;
  handleUserMessage: (message: string, onResponse: SimulationResponseHandler) => void;
  
  // Optional custom handlers for specific scenarios
  [key: string]: any;
}