"""
User request/response schemas.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel


class GenderEnum(str, Enum):
    pria = "pria"
    wanita = "wanita"


class HealthGoalEnum(str, Enum):
    turunkan_berat_badan = "turunkan_berat_badan"
    tambah_masa_otot = "tambah_masa_otot"
    menjaga_kesehatan = "menjaga_kesehatan"


class ActivityLevelEnum(str, Enum):
    sangat_jarang = "sangat_jarang"
    ringan = "ringan"
    sedang = "sedang"
    berat = "berat"
    atlet = "atlet"


# ── Base API response wrapper ──────────────────────────────────────────────────
class ApiResponse(BaseModel):
    status: int
    message: str
    data: Optional[Any] = None


# ── User schemas ───────────────────────────────────────────────────────────────
class UserRegisterRequest(BaseModel):
    name: str
    username: str
    password: str
    gender: GenderEnum
    height_cm: float
    weight_kg: float
    age: int
    health_goal: HealthGoalEnum
    activity_level: ActivityLevelEnum


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    gender: GenderEnum
    height_cm: float
    weight_kg: float
    age: int
    health_goal: HealthGoalEnum
    activity_level: ActivityLevelEnum
    created_at: datetime

    class Config:
        from_attributes = True


class LoginData(BaseModel):
    session_token: str
    user: UserResponse


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    gender: Optional[GenderEnum] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age: Optional[int] = None
    health_goal: Optional[HealthGoalEnum] = None
    activity_level: Optional[ActivityLevelEnum] = None


class ValidateSessionRequest(BaseModel):
    username: str
    session_token: str


class LogoutRequest(BaseModel):
    session_token: str
