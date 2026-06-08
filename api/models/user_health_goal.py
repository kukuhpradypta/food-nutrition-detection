"""
Database model for user health goals.

Global goals (user_id = NULL) are shared by all users.
Custom goals belong to a specific user.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy import Enum as SAEnum

from api.database import Base


class GoalCategory(str, enum.Enum):
    lose_weight = "lose_weight"
    gain_muscle = "gain_muscle"
    maintain_health = "maintain_health"
    custom = "custom"


class GoalGender(str, enum.Enum):
    male = "male"
    female = "female"


class UserHealthGoal(Base):
    __tablename__ = "user_health_goals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_category = Column(SAEnum(GoalCategory), nullable=False, index=True)
    gender = Column(SAEnum(GoalGender), nullable=True)
    nutrition = Column(JSON, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
