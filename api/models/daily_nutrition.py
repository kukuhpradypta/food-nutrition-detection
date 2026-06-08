"""
Database model for daily nutrition tracking.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, JSON
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from api.database import Base


class MealCategory(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"


class DailyNutrition(Base):
    __tablename__ = "daily_nutritions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    category = Column(SAEnum(MealCategory), nullable=False)
    food_name = Column(String(255), nullable=False)
    nutrition = Column(JSON, nullable=False)
    food_image = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="daily_nutritions")
