import { WebSocketMessage } from '../common/apiClient';

/**
 * Stub for SimulationService - simulation functionality has been removed
 * This file is kept to prevent import errors but all functionality is disabled
 */
class SimulationService {
  private enabled: boolean = false;
  
  constructor() {
    // Simulation is permanently disabled
    this.enabled = false;
  }
  
  /**
   * Always returns false - simulation is disabled
   */
  public isEnabled(): boolean {
    return false;
  }
  
  /**
   * No-op - simulation is disabled
   */
  public initialize(): void {
    // Do nothing
  }
  
  /**
   * No-op - simulation is disabled
   */
  public addResponseHandler(handler: (message: WebSocketMessage) => void): void {
    // Do nothing
  }
  
  /**
   * Always returns false - simulation is disabled
   */
  public handleMessage(type: string, payload: any): boolean {
    return false;
  }
  
  /**
   * No-op - simulation is disabled
   */
  public stop(): void {
    // Do nothing
  }
}

// Export singleton instance
const simulationService = new SimulationService();
export default simulationService;