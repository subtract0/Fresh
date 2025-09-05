from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import calendar

router = APIRouter()


def _days_in_month(year: int, month: int) -> int:
    """
    Return the number of days in a given month and year.

    Args:
        year (int): The year in YYYY format.
        month (int): The month as an integer between 1 and 12.

    Returns:
        int: Number of days in the specified month.
    """
    return calendar.monthrange(year, month)[1]


class forecast_monthly_costRequest(BaseModel):
    """
    Request model for forecasting monthly cost.

    Attributes:
        year (int): Year in YYYY format.
        month (int): Month as an integer between 1 and 12.
        daily_costs (List[float]): Costs incurred for each day so far in the month.
        budget (Optional[float]): Optional monthly budget to compare against.
    """
    year: int
    month: int
    daily_costs: List[float]
    budget: Optional[float] = None

    @validator("year")
    def validate_year(cls, v: int) -> int:
        if v < 2000 or v > 2100:
            raise ValueError("Year must be between 2000 and 2100.")
        return v

    @validator("month")
    def validate_month(cls, v: int) -> int:
        if v < 1 or v > 12:
            raise ValueError("Month must be between 1 and 12.")
        return v

    @validator("daily_costs")
    def validate_daily_costs(cls, v: List[float], values) -> List[float]:
        if not v:
            raise ValueError("daily_costs cannot be empty.")
        if any(cost < 0 for cost in v):
            raise ValueError("All daily costs must be non-negative.")
        year = values.get("year")
        month = values.get("month")
        if year and month:
            max_days = _days_in_month(year, month)
            if len(v) > max_days:
                raise ValueError(
                    f"daily_costs length cannot exceed {max_days} for the specified month."
                )
        return v

    @validator("budget")
    def validate_budget(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Budget must be non-negative.")
        return v


class forecast_monthly_costResponse(BaseModel):
    """
    Response model for forecasting monthly cost.

    Attributes:
        success (bool): Indicates if request was successful.
        message (str): Human-readable response message.
        data (Optional[Dict[str, Any]]): Payload containing forecast details.
        timestamp (datetime): Time at which the response was generated.
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


@router.post("/api/v1/forecast-monthly-cost", response_model=forecast_monthly_costResponse)
async def forecast_monthly_cost_endpoint(
    request: forecast_monthly_costRequest,
) -> forecast_monthly_costResponse:
    """
    Forecast the total monthly cost based on provided daily costs to date.

    The endpoint:
    - Calculates average daily spend so far.
    - Projects spend for remaining days of the month.
    - Compares projected spend with optional budget.
    - Returns a detailed forecast report.

    Args:
        request (forecast_monthly_costRequest): Incoming request payload.

    Returns:
        forecast_monthly_costResponse: API response containing forecast details.
    """
    try:
        year = request.year
        month = request.month
        daily_costs = request.daily_costs
        budget = request.budget

        days_in_month = _days_in_month(year, month)
        days_covered = len(daily_costs)
        days_remaining = days_in_month - days_covered

        if days_remaining < 0:
            raise HTTPException(
                status_code=400,
                detail="Number of provided daily costs exceeds the number of days in the specified month.",
            )

        total_spent_to_date = sum(daily_costs)
        avg_daily_cost = total_spent_to_date / days_covered
        projected_remaining_cost = avg_daily_cost * days_remaining
        forecast_total = total_spent_to_date + projected_remaining_cost

        report: Dict[str, Any] = {
            "year": year,
            "month": month,
            "days_in_month": days_in_month,
            "days_covered": days_covered,
            "days_remaining": days_remaining,
            "total_spent_to_date": round(total_spent_to_date, 2),
            "average_daily_cost": round(avg_daily_cost, 2),
            "projected_remaining_cost": round(projected_remaining_cost, 2),
            "forecast_total_cost": round(forecast_total, 2),
        }

        if budget is not None:
            budget_difference = budget - forecast_total
            report["budget"] = round(budget, 2)
            report["budget_difference"] = round(budget_difference, 2)
            report["within_budget"] = budget_difference >= 0

        return forecast_monthly_costResponse(
            success=True,
            message="Monthly cost forecast generated successfully.",
            data=report,
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        # Log the exception in production settings
        raise HTTPException(
            status_code=500,
            detail=f"forecast_monthly_cost execution failed: {str(exc)}",
        ) from exc


__all__ = ["router", "forecast_monthly_costRequest", "forecast_monthly_costResponse"]