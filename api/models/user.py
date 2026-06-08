"""
Database model for users.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, DateTime, Enum
import enum

from api.database import Base


class Gender(str, enum.Enum):
    pria = "pria"
    wanita = "wanita"


class HealthGoal(str, enum.Enum):
    lose_weight = "lose_weight"
    gain_muscle = "gain_muscle"
    maintain_health = "maintain_health"
    custom = "custom"


class ActivityLevel(str, enum.Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    very_active = "athlete"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    health_goal = Column(Enum(HealthGoal), nullable=False)
    activity_level = Column(Enum(ActivityLevel), nullable=False)
    session_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
