"""Process-based inter-agent communication tools for complete isolation."""

from typing import Dict, Any, Optional
import logging
from strands.tools import tool

# Import process client
from ..agents.process_agent_client import get_process_client

# Import WebSocket manager and rate limiter
try:
    from ..websocket.manager import ws_manager, EventType
    from ..utils.rate_limiter import rate_limiter
except ImportError:
    # Fallback for testing
    ws_manager = None
    rate_limiter = None
    EventType = None

# Set up logging
logger = logging.getLogger(__name__)

# Global plan context for WebSocket broadcasting
_current_plan_id: Optional[str] = None


def set_current_plan_id(plan_id: str) -> None:
    """Set the current plan ID for WebSocket broadcasting."""
    global _current_plan_id
    _current_plan_id = plan_id


def _schedule_async_broadcast(event_type, data: Dict[str, Any]) -> None:
    """Schedule an async broadcast from a sync context."""
    if not ws_manager or not _current_plan_id or not EventType:
        return
        
    try:
        # Get the current event loop if it exists
        try:
            import asyncio
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, can't broadcast
            return
            
        # Schedule the coroutine to run on the event loop
        async def _broadcast():
            await ws_manager.broadcast_to_plan(_current_plan_id, event_type, data)
        
        asyncio.run_coroutine_threadsafe(_broadcast(), loop)
    except Exception as e:
        logger.debug(f"Could not schedule broadcast: {str(e)}")


@tool
def consult_flight_specialist(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the flight specialist agent for flight-related queries using process isolation.
    
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
        logger.info(f"Consulting flight specialist (process-isolated) with request: {request[:100]}...")
        
        # Use process client for complete isolation
        client = get_process_client()
        response = client.consult_agent_sync("flight_specialist", request, context)
        
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
                pass  # Don't fail if broadcast fails
        
        return response
        
    except Exception as e:
        logger.error(f"Error consulting flight specialist: {str(e)}")
        error_response = {
            "success": False,
            "agent": "flight_specialist",
            "error": str(e),
            "timestamp": "error"
        }
        
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
        
        return error_response


@tool
def consult_hotel_specialist(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the hotel specialist agent for accommodation-related queries using process isolation.
    
    Args:
        request: The hotel-related request or question
        context: Additional context information
    """
    # Broadcast agent activation
    if ws_manager and _current_plan_id and EventType:
        try:
            _schedule_async_broadcast(
                EventType.AGENT_THINKING,
                {
                    "agent": "hotel_specialist",
                    "message": "Hotel Specialist is searching for accommodations..."
                }
            )
        except Exception:
            pass
    
    try:
        logger.info(f"Consulting hotel specialist (process-isolated) with request: {request[:100]}...")
        
        # Use process client for complete isolation
        client = get_process_client()
        response = client.consult_agent_sync("hotel_specialist", request, context)
        
        logger.info(f"Hotel specialist response received: success={response.get('success', False)}")
        
        # Broadcast completion
        if ws_manager and _current_plan_id and EventType:
            try:
                _schedule_async_broadcast(
                    EventType.AGENT_RESPONSE,
                    {
                        "agent": "hotel_specialist",
                        "success": response.get('success', False),
                        "response_preview": response.get('response', '')[:100] + "..." if response.get('response') else ""
                    }
                )
            except Exception:
                pass
        
        return response
        
    except Exception as e:
        logger.error(f"Error consulting hotel specialist: {str(e)}")
        return {
            "success": False,
            "agent": "hotel_specialist",
            "error": str(e),
            "timestamp": "error"
        }


@tool
def consult_budget_analyst(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the budget analyst agent for financial analysis using process isolation.
    
    Args:
        request: The budget-related request or question
        context: Additional context information
    """
    # Broadcast agent activation
    if ws_manager and _current_plan_id and EventType:
        try:
            _schedule_async_broadcast(
                EventType.AGENT_THINKING,
                {
                    "agent": "budget_analyst",
                    "message": "Budget Analyst is analyzing costs and budget optimization..."
                }
            )
        except Exception:
            pass
    
    try:
        logger.info(f"Consulting budget analyst (process-isolated) with request: {request[:100]}...")
        
        # Use process client for complete isolation
        client = get_process_client()
        response = client.consult_agent_sync("budget_analyst", request, context)
        
        logger.info(f"Budget analyst response received: success={response.get('success', False)}")
        
        # Broadcast completion
        if ws_manager and _current_plan_id and EventType:
            try:
                _schedule_async_broadcast(
                    EventType.AGENT_RESPONSE,
                    {
                        "agent": "budget_analyst",
                        "success": response.get('success', False),
                        "response_preview": response.get('response', '')[:100] + "..." if response.get('response') else ""
                    }
                )
            except Exception:
                pass
        
        return response
        
    except Exception as e:
        logger.error(f"Error consulting budget analyst: {str(e)}")
        return {
            "success": False,
            "agent": "budget_analyst",
            "error": str(e),
            "timestamp": "error"
        }


@tool
def consult_destination_expert(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the destination expert agent for location-specific information using process isolation.
    
    Args:
        request: The destination-related request or question
        context: Additional context information
    """
    # Broadcast agent activation
    if ws_manager and _current_plan_id and EventType:
        try:
            _schedule_async_broadcast(
                EventType.AGENT_THINKING,
                {
                    "agent": "destination_expert",
                    "message": "Destination Expert is gathering location insights..."
                }
            )
        except Exception:
            pass
    
    try:
        logger.info(f"Consulting destination expert (process-isolated) with request: {request[:100]}...")
        
        # Use process client for complete isolation
        client = get_process_client()
        response = client.consult_agent_sync("destination_expert", request, context)
        
        logger.info(f"Destination expert response received: success={response.get('success', False)}")
        
        # Broadcast completion
        if ws_manager and _current_plan_id and EventType:
            try:
                _schedule_async_broadcast(
                    EventType.AGENT_RESPONSE,
                    {
                        "agent": "destination_expert",
                        "success": response.get('success', False),
                        "response_preview": response.get('response', '')[:100] + "..." if response.get('response') else ""
                    }
                )
            except Exception:
                pass
        
        return response
        
    except Exception as e:
        logger.error(f"Error consulting destination expert: {str(e)}")
        return {
            "success": False,
            "agent": "destination_expert",
            "error": str(e),
            "timestamp": "error"
        }


@tool
def consult_activity_curator(
    request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consult the activity curator agent for activity and experience recommendations using process isolation.
    
    Args:
        request: The activity-related request or question
        context: Additional context information
    """
    # Broadcast agent activation
    if ws_manager and _current_plan_id and EventType:
        try:
            _schedule_async_broadcast(
                EventType.AGENT_THINKING,
                {
                    "agent": "activity_curator",
                    "message": "Activity Curator is planning experiences and activities..."
                }
            )
        except Exception:
            pass
    
    try:
        logger.info(f"Consulting activity curator (process-isolated) with request: {request[:100]}...")
        
        # Use process client for complete isolation
        client = get_process_client()
        response = client.consult_agent_sync("activity_curator", request, context)
        
        logger.info(f"Activity curator response received: success={response.get('success', False)}")
        
        # Broadcast completion
        if ws_manager and _current_plan_id and EventType:
            try:
                _schedule_async_broadcast(
                    EventType.AGENT_RESPONSE,
                    {
                        "agent": "activity_curator",
                        "success": response.get('success', False),
                        "response_preview": response.get('response', '')[:100] + "..." if response.get('response') else ""
                    }
                )
            except Exception:
                pass
        
        return response
        
    except Exception as e:
        logger.error(f"Error consulting activity curator: {str(e)}")
        return {
            "success": False,
            "agent": "activity_curator",
            "error": str(e),
            "timestamp": "error"
        }


@tool
def coordinate_multi_agent_task(
    task_description: str,
    required_agents: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Coordinate a task that requires input from multiple specialist agents using process isolation.
    
    Args:
        task_description: Description of the task requiring multiple agents
        required_agents: Comma-separated list of agent types (optional, will use all if not specified)
        context: Additional context information
    """
    try:
        logger.info(f"Coordinating multi-agent task (process-isolated): {task_description[:100]}...")
        
        # Determine which agents to consult
        if required_agents:
            agent_types = [agent.strip() for agent in required_agents.split(',')]
        else:
            agent_types = ["flight_specialist", "hotel_specialist", "budget_analyst", "destination_expert", "activity_curator"]
        
        client = get_process_client()
        responses = {}
        
        # Consult each agent in parallel (though synchronously from our perspective)
        for agent_type in agent_types:
            try:
                response = client.consult_agent_sync(agent_type, task_description, context)
                responses[agent_type] = response
            except Exception as e:
                logger.error(f"Error consulting {agent_type} in multi-agent task: {str(e)}")
                responses[agent_type] = {
                    "success": False,
                    "agent": agent_type,
                    "error": str(e)
                }
        
        # Compile results
        successful_responses = [resp for resp in responses.values() if resp.get('success', False)]
        failed_responses = [resp for resp in responses.values() if not resp.get('success', False)]
        
        result = {
            "success": len(successful_responses) > 0,
            "agent": "multi_agent_coordinator",
            "total_agents": len(agent_types),
            "successful_agents": len(successful_responses),
            "failed_agents": len(failed_responses),
            "responses": responses
        }
        
        if successful_responses:
            # Combine successful responses
            combined_response = "# Multi-Agent Coordination Results\\n\\n"
            for agent_type, response in responses.items():
                if response.get('success', False):
                    combined_response += f"## {agent_type.replace('_', ' ').title()}\\n"
                    combined_response += response.get('response', '') + "\\n\\n"
            
            result["response"] = combined_response
        
        return result
        
    except Exception as e:
        logger.error(f"Error in multi-agent coordination: {str(e)}")
        return {
            "success": False,
            "agent": "multi_agent_coordinator",
            "error": str(e)
        }


@tool
def get_agent_capabilities() -> Dict[str, Any]:
    """Get information about available agent capabilities using process isolation."""
    return {
        "success": True,
        "agent": "capabilities_reporter",
        "available_agents": {
            "flight_specialist": {
                "description": "Expert in flight search, booking, and travel logistics",
                "capabilities": ["flight search", "route optimization", "airline recommendations", "pricing analysis"]
            },
            "hotel_specialist": {
                "description": "Expert in accommodation search and booking",
                "capabilities": ["hotel search", "location recommendations", "amenity analysis", "value assessment"]
            },
            "budget_analyst": {
                "description": "Expert in travel budget analysis and optimization",
                "capabilities": ["budget breakdown", "cost optimization", "expense tracking", "value analysis"]
            },
            "destination_expert": {
                "description": "Expert in destination information and recommendations",
                "capabilities": ["destination insights", "local recommendations", "cultural information", "travel tips"]
            },
            "activity_curator": {
                "description": "Expert in activity planning and experience curation",
                "capabilities": ["activity search", "itinerary planning", "experience recommendations", "timing optimization"]
            }
        },
        "communication_methods": ["individual consultation", "multi-agent coordination"],
        "isolation": "process-based for complete context separation"
    }


@tool
def delegate_specialized_task(
    agent_type: str,
    task_description: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Delegate a specialized task to a specific agent with parameters using process isolation.
    
    Args:
        agent_type: The type of agent to delegate to
        task_description: Detailed description of the task
        parameters: Specific parameters for the task
    """
    valid_agents = ["flight_specialist", "hotel_specialist", "budget_analyst", "destination_expert", "activity_curator"]
    
    if agent_type not in valid_agents:
        return {
            "success": False,
            "agent": "task_delegator",
            "error": f"Invalid agent type: {agent_type}. Valid types: {', '.join(valid_agents)}"
        }
    
    try:
        logger.info(f"Delegating specialized task to {agent_type} (process-isolated): {task_description[:100]}...")
        
        # Combine task description with parameters
        full_context = {"task_description": task_description}
        if parameters:
            full_context.update(parameters)
        
        client = get_process_client()
        response = client.consult_agent_sync(agent_type, task_description, full_context)
        
        # Add delegation metadata
        response["delegated_to"] = agent_type
        response["task_type"] = "specialized_delegation"
        
        return response
        
    except Exception as e:
        logger.error(f"Error delegating task to {agent_type}: {str(e)}")
        return {
            "success": False,
            "agent": "task_delegator",
            "delegated_to": agent_type,
            "error": str(e)
        }