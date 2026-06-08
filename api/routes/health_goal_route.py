"""
Health goal routes.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_user
from api.models.user import User
from api.schemas.user_schema import ApiResponse
from api.controllers.health_goal_controller import get_health_goal, list_global_goals_by_gender

router = APIRouter(prefix="/health-goals", tags=["Health Goals"])


@router.get("/", response_model=ApiResponse)
def get_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the health goal for the logged-in user, based on the user's own
    `health_goal` setting (custom returns the user's personal goal,
    otherwise the global goal matching the user's gender).

    Header: Authorization: Bearer <session_token>
    """
    data = get_health_goal(db, current_user)
    return ApiResponse(
        status=200,
        message="Health goal retrieved successfully",
        data=data,
    )


@router.get("/list", response_model=ApiResponse)
def list_goals(
    gender: str = Query(..., description="male | female"),
    db: Session = Depends(get_db),
):
    """
    List all global health goals for a gender (excludes 'custom').

    No authentication required.
    """
    data = list_global_goals_by_gender(db, gender)
    return ApiResponse(
        status=200,
        message="Health goals retrieved successfully",
        data=data,
    )
