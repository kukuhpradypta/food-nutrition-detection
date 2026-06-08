"""
Daily nutrition routes.
"""
import json
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_user
from api.models.user import User
from api.schemas.user_schema import ApiResponse
from api.schemas.daily_nutrition_schema import FoodItemResponse
from api.controllers.daily_nutrition_controller import (
    create_daily_nutrition,
    get_daily_nutrition,
    get_daily_nutrition_range,
    delete_daily_nutrition,
)

router = APIRouter(prefix="/daily-nutritions", tags=["Daily Nutrition"])


@router.post("/", response_model=ApiResponse, status_code=201)
async def insert_nutrition(
    date: date = Form(..., description="Date (YYYY-MM-DD)"),
    category: str = Form(..., description="breakfast | lunch | dinner"),
    food_name: str = Form(...),
    nutrition: str = Form(..., description="JSON string, e.g. {\"calories\": 200, \"protein\": 10}"),
    food_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Insert a daily nutrition entry with optional food image.

    - Send as **multipart/form-data**
    - `nutrition` field is a JSON string
    - `food_image` is optional file upload

    Header: Authorization: Bearer <session_token>
    """
    # Parse nutrition JSON string
    try:
        nutrition_data = json.loads(nutrition)
    except json.JSONDecodeError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="nutrition must be a valid JSON string")

    data = {
        "date": date,
        "category": category,
        "food_name": food_name,
        "nutrition": nutrition_data,
        "food_image": None,
    }

    entry = await create_daily_nutrition(db, current_user, data, food_image)
    return ApiResponse(
        status=201,
        message="Nutrition entry created successfully",
        data=FoodItemResponse.model_validate(entry).model_dump(mode="json"),
    )


@router.get("/", response_model=ApiResponse)
def get_nutrition(
    target_date: Optional[date] = Query(None, description="Single date (YYYY-MM-DD)"),
    start_date: Optional[date] = Query(None, description="Start date for range (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for range (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Filter: breakfast | lunch | dinner"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get daily nutrition data.

    - Single date: provide `target_date`
    - Date range: provide `start_date` and `end_date`
    - Filter by category: provide `category`

    Header: Authorization: Bearer <session_token>
    """
    if start_date and end_date:
        result = get_daily_nutrition_range(db, current_user.id, start_date, end_date, category)
        return ApiResponse(
            status=200,
            message="Nutrition data retrieved successfully",
            data=result,
        )

    if target_date is None:
        from datetime import date as date_cls
        target_date = date_cls.today()

    result = get_daily_nutrition(db, current_user.id, target_date, category)
    return ApiResponse(
        status=200,
        message="Nutrition data retrieved successfully",
        data=result,
    )


@router.delete("/{entry_id}", response_model=ApiResponse)
def delete_nutrition(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Soft delete a nutrition entry.

    Header: Authorization: Bearer <session_token>
    """
    delete_daily_nutrition(db, entry_id, current_user.id)
    return ApiResponse(
        status=200,
        message="Nutrition entry deleted successfully",
        data=None,
    )
