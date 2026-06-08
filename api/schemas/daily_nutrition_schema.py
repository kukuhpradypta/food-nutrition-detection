"""
Daily nutrition request/response schemas.
"""
from datetime import date, datetime
from typing import Optional, Any, List

from pydantic import BaseModel

from api.schemas.user_schema import ApiResponse


class MealCategoryEnum(str):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"


class DailyNutritionCreateRequest(BaseModel):
    date: date
    category: str  # breakfast | lunch | dinner
    food_name: str
    nutrition: Any  # JSON — flexible structure
    food_image: Optional[str] = None


class FoodItemResponse(BaseModel):
    id: int
    food_name: str
    nutrition: Any
    food_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyNutritionResponse(BaseModel):
    user_id: int
    date: date
    breakfast: Optional[List[FoodItemResponse]] = None
    lunch: Optional[List[FoodItemResponse]] = None
    dinner: Optional[List[FoodItemResponse]] = None
