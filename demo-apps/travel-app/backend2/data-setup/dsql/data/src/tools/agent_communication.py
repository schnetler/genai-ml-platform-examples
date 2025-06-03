"""Inter-agent communication tools for the multi-agent travel planning system."""

from typing import Dict, Any, Optional
import json
import asyncio
import threading
from strands.tools import tool
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Global registry to store agent instances
_agent_registry: Dict[str, Any] = {}

# Import WebSocket manager and rate limiter
try:
    from ..websocket.manager import ws_manager, EventType
    from ..utils.rate_limiter import rate_limiter
except ImportError:
    # Fallback for testing
    ws_manager = None
    rate_limiter = None
    EventType = None

# Global plan context for WebSocket broadcasting
_current_plan_id: Optional[str] = None


def register_agent(agent_name: str, agent_instance: Any) -> None:
    """Register an agent instance in the global registry."""
    _agent_registry[agent_name] = agent_instance
    logger.info(f"Registered agent: {agent_name}")


def get_agent_instance(agent_name: str) -> Optional[Any]:
    """Get an agent instance from the registry."""
    return _agent_registry.get(agent_name)


def set_current_plan_id(plan_id: str) -> None:
    """Set the current plan ID for WebSocket broadcasting."""
    global _current_plan_id
    _current_plan_id = plan_id


def _schedule_async_broadcast(event_type: EventType, data: Dict[str, Any]) -> None:
    """Schedule an async broadcast from a sync context."""
    if not ws_manager or not _current_plan_id or not EventType:
        return
        
    try:
        # Get the current event loop if it exists
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, can't broadcast
            return
            
        # Schedule the coroutine to run on the event loop
        asyncio.run_coroutine_threadsafe(
            _broadcast_agent_event(event_type, data),
            loop
        )
    except Exception as e:
        logger.debug(f"Could not schedule broadcast: {str(e)}")


async def _broadcast_agent_event(event_type: EventType, data: Dict[str, Any]) -> None:
    """Broadcast agent event to WebSocket if available."""
    if ws_manager and _current_plan_id and EventType:
        try:
            await ws_manager.broadcast_to_plan(_current_plan_id, event_type, data)
        except Exception as e:
            logger.error(f"Failed to broadcast agent event: {str(e)}")


async def _execute_with_monitoring(
    agent_name: str, 
    func, 
    *args, 
    **kwargs
) -> Any:
    """Execute agent function with monitoring and WebSocket updates."""
    # Broadcast that agent is starting
    await _broadcast_agent_event(
        EventType.AGENT_THINKING,
        {
            "agent": agent_name,
            "message": f"{agent_name.replace('_', ' ').title()} is working on your request..."
        }
    )
    
    try:
        # Execute with rate limiting if available
        if rate_limiter:
            result = await rate_limiter.execute_with_rate_limit(func, *args, **kwargs)
        else:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
        
        # Broadcast successful completion
        await _broadcast_agent_event(
            EventType.AGENT_RESPONSE,
            {
                "agent": agent_name,
                "success": True,
                "timestamp": asyncio.get_event_loop().time()
            }
        )
        
        return result
        
    except Exception as e:
        # Broadcast error
        await _broadcast_agent_event(
            EventType.PLANNING_ERROR,
            {
                "agent": agent_name,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
        )
        raise e



@tool
def consult_flight_specialist(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the flight specialist agent for flight-related queries.
    
    Args:
        request: The flight-related request or question
        context: Additional context information
    """
    # Broadcast agent activation
    if ws_manager and _current_plan_id and EventType:
        try:
            _schedule_async_broadcast(
                EventType.AGENT_THINKING,
                {
                    "agent": "flight_specialist",
                    "message": "Flight Specialist is analyzing flight options..."
                }
            )
        except Exception:
            pass  # Don't fail if broadcast fails
    
    try:
        logger.info(f"Consulting flight specialist with request: {request[:100]}...")
        flight_agent = get_agent_instance("flight_specialist")
        if not flight_agent:
            logger.warning("Flight specialist agent not available")
            return {
                "success": False,
                "error": "Flight specialist agent not available",
                "agent": "flight_specialist"
            }
        
        # Use synchronous method to avoid nested agent issues
        response = flight_agent.process_request_sync(request, context)
        logger.info(f"Flight specialist response received: success={response.get('success', False)}")
        
        # Broadcast completion
        if ws_manager and _current_plan_id and EventType:
            try:
                _schedule_async_broadcast(
                    EventType.AGENT_RESPONSE,
                    {
                        "agent": "flight_specialist",
                        "success": response.get('success', False),
                        "response_preview": response.get('response', '')[:100] + "..." if response.get('response') else ""
                    }
                )
            except Exception:
                pass
        
        return response
        
    except Exception as e:
        logger.error(f"Error consulting flight specialist: {str(e)}")
        
        # Broadcast error
        if ws_manager and _current_plan_id and EventType:
            try:
                _schedule_async_broadcast(
                    EventType.PLANNING_ERROR,
                    {
                        "agent": "flight_specialist",
                        "error": str(e)
                    }
                )
            except Exception:
                pass
        
        return {
            "success": False,
            "error": f"Failed to consult flight specialist: {str(e)}",
            "agent": "flight_specialist"
        }


@tool
def consult_hotel_specialist(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the hotel specialist agent for accommodation-related queries.
    
    Args:
        request: The hotel-related request or question
        context: Additional context information
    """
    try:
        logger.info(f"Consulting hotel specialist with request: {request[:100]}...")
        hotel_agent = get_agent_instance("hotel_specialist")
        if not hotel_agent:
            logger.warning("Hotel specialist agent not available")
            return {
                "success": False,
                "error": "Hotel specialist agent not available",
                "agent": "hotel_specialist"
            }
        
        # Use synchronous method to avoid nested agent issues
        response = hotel_agent.process_request_sync(request, context)
        logger.info(f"Hotel specialist response received: success={response.get('success', False)}")
        return response
        
    except Exception as e:
        logger.error(f"Error consulting hotel specialist: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to consult hotel specialist: {str(e)}",
            "agent": "hotel_specialist"
        }


@tool
def consult_destination_expert(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the destination expert agent for destination-related queries.
    
    Args:
        request: The destination-related request or question
        context: Additional context information
    """
    try:
        logger.info(f"Consulting destination expert with request: {request[:100]}...")
        destination_agent = get_agent_instance("destination_expert")
        if not destination_agent:
            logger.warning("Destination expert agent not available")
            return {
                "success": False,
                "error": "Destination expert agent not available",
                "agent": "destination_expert"
            }
        
        # Use synchronous method to avoid nested agent issues
        response = destination_agent.process_request_sync(request, context)
        logger.info(f"Destination expert response received: success={response.get('success', False)}")
        return response
        
    except Exception as e:
        logger.error(f"Error consulting destination expert: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to consult destination expert: {str(e)}",
            "agent": "destination_expert"
        }


@tool
def consult_activity_curator(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the activity curator agent for activity and itinerary-related queries.
    
    Args:
        request: The activity-related request or question
        context: Additional context information
    """
    try:
        logger.info(f"Consulting activity curator with request: {request[:100]}...")
        activity_agent = get_agent_instance("activity_curator")
        if not activity_agent:
            logger.warning("Activity curator agent not available")
            return {
                "success": False,
                "error": "Activity curator agent not available",
                "agent": "activity_curator"
            }
        
        # Use synchronous method to avoid nested agent issues
        response = activity_agent.process_request_sync(request, context)
        logger.info(f"Activity curator response received: success={response.get('success', False)}")
        return response
        
    except Exception as e:
        logger.error(f"Error consulting activity curator: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to consult activity curator: {str(e)}",
            "agent": "activity_curator"
        }


@tool
def consult_budget_analyst(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the budget analyst agent for budget and cost-related queries.
    
    Args:
        request: The budget-related request or question
        context: Additional context information
    """
    try:
        logger.info(f"Consulting budget analyst with request: {request[:100]}...")
        budget_agent = get_agent_instance("budget_analyst")
        if not budget_agent:
            logger.warning("Budget analyst agent not available")
            return {
                "success": False,
                "error": "Budget analyst agent not available",
                "agent": "budget_analyst"
            }
        
        # Use synchronous method to avoid nested agent issues
        response = budget_agent.process_request_sync(request, context)
        logger.info(f"Budget analyst response received: success={response.get('success', False)}")
        return response
        
    except Exception as e:
        logger.error(f"Error consulting budget analyst: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to consult budget analyst: {str(e)}",
            "agent": "budget_analyst"
        }


@tool
def coordinate_multi_agent_task(
    task_description: str,
    required_agents: list,
    task_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Coordinate a task that requires input from multiple specialist agents.
    
    Args:
        task_description: Description of the task that needs coordination
        required_agents: List of agent names needed for this task
        task_context: Context information for the task
    """
    try:
        results = {}
        errors = []
        
        # Map agent names to consultation functions
        consultation_map = {
            "flight_specialist": consult_flight_specialist,
            "hotel_specialist": consult_hotel_specialist,
            "destination_expert": consult_destination_expert,
            "activity_curator": consult_activity_curator,
            "budget_analyst": consult_budget_analyst
        }
        
        # Consult each required agent
        for agent_name in required_agents:
            if agent_name in consultation_map:
                try:
                    # Create agent-specific request
                    agent_request = f"Task: {task_description}\n\nPlease provide your {agent_name.replace('_', ' ')} perspective on this task."
                    
                    # Consult the agent using the sync tool functions
                    result = consultation_map[agent_name](agent_request, task_context)
                    results[agent_name] = result
                    
                except Exception as e:
                    errors.append(f"Failed to consult {agent_name}: {str(e)}")
            else:
                errors.append(f"Unknown agent: {agent_name}")
        
        return {
            "success": len(errors) == 0,
            "task": task_description,
            "agent_responses": results,
            "errors": errors if errors else None,
            "coordination_summary": f"Coordinated task with {len(results)} agents"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Multi-agent coordination failed: {str(e)}",
            "task": task_description
        }


@tool
def get_agent_capabilities() -> Dict[str, Any]:
    """
    Get the capabilities of all available specialist agents.
    """
    try:
        capabilities = {}
        
        for agent_name, agent_instance in _agent_registry.items():
            if hasattr(agent_instance, 'get_capabilities'):
                capabilities[agent_name] = agent_instance.get_capabilities()
            else:
                capabilities[agent_name] = {
                    "agent_name": agent_name,
                    "status": "available",
                    "capabilities": "Unknown - no capabilities method"
                }
        
        logger.info(f"Retrieved capabilities for {len(_agent_registry)} agents")
        return {
            "success": True,
            "available_agents": len(_agent_registry),
            "agent_capabilities": capabilities
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent capabilities: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to get agent capabilities: {str(e)}"
        }


@tool 
def delegate_specialized_task(
    agent_name: str,
    task: str,
    task_parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Delegate a specific task to a specialist agent with parameters.
    
    Args:
        agent_name: Name of the specialist agent
        task: Task description
        task_parameters: Specific parameters for the task
    """
    try:
        # Map to consultation functions
        consultation_map = {
            "flight_specialist": consult_flight_specialist,
            "hotel_specialist": consult_hotel_specialist, 
            "destination_expert": consult_destination_expert,
            "activity_curator": consult_activity_curator,
            "budget_analyst": consult_budget_analyst
        }
        
        if agent_name not in consultation_map:
            return {
                "success": False,
                "error": f"Unknown specialist agent: {agent_name}",
                "available_agents": list(consultation_map.keys())
            }
        
        # Format task with parameters
        if task_parameters:
            formatted_task = f"{task}\n\nTask Parameters:\n{json.dumps(task_parameters, indent=2)}"
        else:
            formatted_task = task
        
        # Delegate to the specialist using sync tool functions
        result = consultation_map[agent_name](formatted_task, task_parameters)
        
        return {
            "success": True,
            "delegated_to": agent_name,
            "task": task,
            "result": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Task delegation failed: {str(e)}",
            "agent": agent_name,
            "task": task
        }