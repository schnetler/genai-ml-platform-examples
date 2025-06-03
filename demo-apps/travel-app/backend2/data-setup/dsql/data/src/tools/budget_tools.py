"""Budget analysis and optimization tools for travel planning."""

from typing import Dict, Any, List, Optional
import json
from strands.tools import tool


@tool
def analyze_travel_budget(
    total_budget: float,
    travel_components: List[Dict[str, Any]],
    destination: str,
    duration_days: int
) -> Dict[str, Any]:
    """
    Analyze and break down travel budget across different components.
    
    Args:
        total_budget: Total available budget
        travel_components: List of travel components with estimated costs
        destination: Travel destination for cost context
        duration_days: Length of trip in days
    """
    try:
        # Calculate budget allocation recommendations
        recommended_allocation = {
            "flights": 0.35,      # 35% for flights
            "accommodation": 0.30, # 30% for hotels
            "activities": 0.20,    # 20% for activities/experiences
            "food": 0.10,         # 10% for dining
            "miscellaneous": 0.05  # 5% for misc/emergency
        }
        
        # Calculate recommended amounts
        budget_breakdown = {}
        for category, percentage in recommended_allocation.items():
            budget_breakdown[category] = {
                "recommended_amount": total_budget * percentage,
                "percentage": percentage * 100
            }
        
        # Analyze provided components
        component_analysis = []
        total_estimated_cost = 0
        
        for component in travel_components:
            cost = component.get('estimated_cost', 0)
            total_estimated_cost += cost
            component_analysis.append({
                "category": component.get('category', 'unknown'),
                "description": component.get('description', ''),
                "estimated_cost": cost,
                "budget_fit": "within_budget" if cost <= budget_breakdown.get(component.get('category', {}), {}).get('recommended_amount', 0) else "over_budget"
            })
        
        # Budget summary
        remaining_budget = total_budget - total_estimated_cost
        budget_utilization = (total_estimated_cost / total_budget) * 100 if total_budget > 0 else 0
        
        return {
            "success": True,
            "budget_analysis": {
                "total_budget": total_budget,
                "estimated_total_cost": total_estimated_cost,
                "remaining_budget": remaining_budget,
                "budget_utilization_percent": round(budget_utilization, 2),
                "status": "under_budget" if remaining_budget > 0 else "over_budget",
                "recommended_allocation": budget_breakdown,
                "component_analysis": component_analysis,
                "daily_budget": total_budget / duration_days if duration_days > 0 else 0
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Budget analysis failed: {str(e)}"
        }


@tool
def optimize_budget_allocation(
    current_plan: Dict[str, Any],
    budget_constraints: Dict[str, float],
    priorities: List[str]
) -> Dict[str, Any]:
    """
    Optimize budget allocation based on traveler priorities and constraints.
    
    Args:
        current_plan: Current travel plan with costs
        budget_constraints: Budget limits for different categories
        priorities: Ordered list of traveler priorities
    """
    try:
        # Priority weights
        priority_weights = {
            "luxury": 1.5,
            "comfort": 1.2,
            "budget": 0.8,
            "adventure": 1.1,
            "culture": 1.0,
            "relaxation": 1.0
        }
        
        # Calculate optimization recommendations
        optimizations = []
        
        # Check each category in current plan
        for category, details in current_plan.items():
            if category in budget_constraints:
                current_cost = details.get('cost', 0)
                budget_limit = budget_constraints[category]
                
                if current_cost > budget_limit:
                    # Suggest cost reduction
                    excess = current_cost - budget_limit
                    optimizations.append({
                        "category": category,
                        "type": "cost_reduction",
                        "current_cost": current_cost,
                        "target_cost": budget_limit,
                        "savings_needed": excess,
                        "suggestions": [
                            f"Consider lower-cost {category} options",
                            f"Look for deals and discounts",
                            f"Adjust duration or specifications"
                        ]
                    })
                elif current_cost < budget_limit * 0.8:
                    # Suggest potential upgrades
                    available_budget = budget_limit - current_cost
                    optimizations.append({
                        "category": category,
                        "type": "upgrade_opportunity",
                        "current_cost": current_cost,
                        "available_budget": available_budget,
                        "suggestions": [
                            f"Consider upgrading {category} within budget",
                            f"Add premium options or experiences",
                            f"Extend duration or add features"
                        ]
                    })
        
        return {
            "success": True,
            "optimization_recommendations": optimizations,
            "priority_based_adjustments": [
                f"Focus budget on {priority}" for priority in priorities[:3]
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Budget optimization failed: {str(e)}"
        }


@tool
def track_expenses(
    expense_entries: List[Dict[str, Any]],
    budget_limits: Dict[str, float]
) -> Dict[str, Any]:
    """
    Track travel expenses against budget categories.
    
    Args:
        expense_entries: List of expense records
        budget_limits: Budget limits for each category
    """
    try:
        # Categorize expenses
        expense_by_category = {}
        total_expenses = 0
        
        for expense in expense_entries:
            category = expense.get('category', 'miscellaneous')
            amount = expense.get('amount', 0)
            
            if category not in expense_by_category:
                expense_by_category[category] = {
                    'total': 0,
                    'entries': []
                }
            
            expense_by_category[category]['total'] += amount
            expense_by_category[category]['entries'].append(expense)
            total_expenses += amount
        
        # Calculate budget status
        budget_status = {}
        total_budget = sum(budget_limits.values())
        
        for category, limit in budget_limits.items():
            spent = expense_by_category.get(category, {}).get('total', 0)
            remaining = limit - spent
            utilization = (spent / limit * 100) if limit > 0 else 0
            
            budget_status[category] = {
                'budget_limit': limit,
                'spent': spent,
                'remaining': remaining,
                'utilization_percent': round(utilization, 2),
                'status': 'within_budget' if remaining >= 0 else 'over_budget'
            }
        
        return {
            "success": True,
            "expense_tracking": {
                "total_expenses": total_expenses,
                "total_budget": total_budget,
                "overall_remaining": total_budget - total_expenses,
                "category_breakdown": budget_status,
                "expense_details": expense_by_category
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Expense tracking failed: {str(e)}"
        }


@tool
def compare_cost_options(
    options: List[Dict[str, Any]],
    budget_constraint: float,
    value_factors: List[str]
) -> Dict[str, Any]:
    """
    Compare different travel options based on cost and value factors.
    
    Args:
        options: List of travel options with costs and features
        budget_constraint: Maximum budget available
        value_factors: Factors to consider for value assessment
    """
    try:
        # Score each option
        scored_options = []
        
        for option in options:
            cost = option.get('cost', 0)
            features = option.get('features', [])
            
            # Basic affordability check
            affordable = cost <= budget_constraint
            
            # Value score based on features matching value factors
            value_score = 0
            for factor in value_factors:
                if any(factor.lower() in feature.lower() for feature in features):
                    value_score += 1
            
            # Cost efficiency (value per dollar)
            cost_efficiency = value_score / cost if cost > 0 else 0
            
            scored_options.append({
                "option": option,
                "affordable": affordable,
                "value_score": value_score,
                "cost_efficiency": round(cost_efficiency, 4),
                "cost_vs_budget_percent": round((cost / budget_constraint * 100), 2) if budget_constraint > 0 else 0
            })
        
        # Sort by cost efficiency for affordable options
        affordable_options = [opt for opt in scored_options if opt['affordable']]
        affordable_options.sort(key=lambda x: x['cost_efficiency'], reverse=True)
        
        return {
            "success": True,
            "cost_comparison": {
                "total_options": len(options),
                "affordable_options": len(affordable_options),
                "best_value_option": affordable_options[0] if affordable_options else None,
                "all_options_ranked": scored_options,
                "budget_constraint": budget_constraint
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Cost comparison failed: {str(e)}"
        }