"""
Health goal request/response schemas.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel


class GoalCategoryEnum(str, Enum):
    lose_weight = "lose_weight"
    gain_muscle = "gain_muscle"
    maintain_health = "maintain_health"
    custom = "custom"


class HealthGoalResponse(BaseModel):
    id: int
    goal_category: GoalCategoryEnum
    nutrition: Any
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
