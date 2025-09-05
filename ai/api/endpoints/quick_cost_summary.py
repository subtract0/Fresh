from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

router = APIRouter()


class CostItem(BaseModel):
    """Model representing a single cost entry."""
    category: str
    amount: float
    date: Optional[datetime] = None

    @validator("amount")
    def validate_amount(cls, v: float) -> float:
        if v < 0:
            raise ValueError("amount must be a non-negative number")
        return v

    @validator("category")
    def validate_category(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("category must be a non-empty string")
        return v.strip()


class quick_cost_summaryRequest(BaseModel):
    """Request model for quick_cost_summary."""
    data: Dict[str, Any]

    @validator("data")
    def validate_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if "costs" not in v or not isinstance(v["costs"], list):
            raise ValueError("data must include a 'costs' list")
        # Validate each cost using CostItem
        _ = [CostItem(**item) for item in v["costs"]]
        if "budgets" in v and not isinstance(v["budgets"], dict):
            raise ValueError("'budgets' must be a dictionary when provided")
        return v


class quick_cost_summaryResponse(BaseModel):
    """Response model for quick_cost_summary."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


def _aggregate_costs(cost_items: List[CostItem]) -> Dict[str, Any]:
    """
    Aggregate cost data by category and overall total.

    Args:
        cost_items (List[CostItem]): Validated list of cost items.

    Returns:
        Dict[str, Any]: Aggregated results.
    """
    per_category: Dict[str, float] = {}
    total_cost: float = 0.0

    for item in cost_items:
        per_category[item.category] = per_category.get(item.category, 0.0) + item.amount
        total_cost += item.amount

    return {"total_cost": total_cost, "per_category_costs": per_category}


def _calculate_budget_usage(costs_by_category: Dict[str, float], budgets: Dict[str, float]) -> Dict[str, Any]:
    """
    Calculate budget utilisation for each category.

    Args:
        costs_by_category (Dict[str, float]): Cost sums per category.
        budgets (Dict[str, float]): Budget limit per category.

    Returns:
        Dict[str, Any]: Budget usage details.
    """
    budget_details: Dict[str, Any] = {}
    for category, budget in budgets.items():
        spent: float = costs_by_category.get(category, 0.0)
        utilisation: float = (spent / budget) * 100 if budget else 0.0
        budget_details[category] = {
            "budget": budget,
            "spent": spent,
            "utilisation_percentage": round(utilisation, 2),
            "over_budget": spent > budget,
        }
    return budget_details


@router.post("/api/v1/quick-cost-summary", response_model=quick_cost_summaryResponse)
async def quick_cost_summary_endpoint(
    request: quick_cost_summaryRequest,
) -> quick_cost_summaryResponse:
    """
    Summarise cost data and, when supplied, compare it to budget limits.

    Request `data` structure:
    {
        "costs": [
            {"category": "infrastructure", "amount": 120.5, "date": "2024-05-12"},
            ...
        ],
        "budgets": {
            "infrastructure": 1000,
            "marketing": 500
        }
    }
    """
    try:
        # Validate and parse cost items
        cost_items = [CostItem(**item) for item in request.data.get("costs", [])]

        # Aggregate costs
        aggregated = _aggregate_costs(cost_items)

        # Compute budget utilisation if budgets provided
        budgets_input = request.data.get("budgets")
        budget_summary: Optional[Dict[str, Any]] = None
        if budgets_input:
            budget_summary = _calculate_budget_usage(aggregated["per_category_costs"], budgets_input)

        result_data = {
            "aggregated_costs": aggregated,
            "budget_overview": budget_summary,
        }

        return quick_cost_summaryResponse(
            success=True,
            message="quick_cost_summary executed successfully",
            data=result_data,
        )

    except ValueError as ve:
        # Input validation errors
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Unhandled errors
        raise HTTPException(
            status_code=500,
            detail=f"quick_cost_summary execution failed: {str(e)}",
        )


__all__ = ["router", "quick_cost_summaryRequest", "quick_cost_summaryResponse"]