"""
User routes - registration, login, profile.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas.user_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
    LoginResponse,
    ValidateSessionRequest,
)
from api.controllers.user_controller import register_user, login_user, get_user_by_id, update_user, logout_user, validate_user_session

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.

    Data yang dibutuhkan:
    - name: Nama lengkap
    - username: Username (unique)
    - password: Password
    - gender: "pria" atau "wanita"
    - height_cm: Tinggi badan (cm)
    - weight_kg: Berat badan (kg)
    - age: Usia (tahun)
    - health_goal: "turunkan_berat_badan" | "tambah_masa_otot" | "menjaga_kesehatan"
    - activity_level: "sangat_jarang" | "ringan" | "sedang" | "berat" | "atlet"
    """
    user = register_user(db, data.model_dump())
    return user


@router.post("/login", response_model=LoginResponse)
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user with username and password."""
    user = login_user(db, data.username, data.password)
    return LoginResponse(
        message="Login berhasil",
        session_token=user.session_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID."""
    return get_user_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def edit_profile(user_id: int, data: UserUpdateRequest, db: Session = Depends(get_db)):
    """
    Edit user profile.

    Semua field optional — kirim hanya field yang ingin diubah.
    """
    return update_user(db, user_id, data.model_dump(exclude_unset=True))


@router.post("/{user_id}/logout")
def logout(user_id: int, db: Session = Depends(get_db)):
    """Logout user — clear session token."""
    logout_user(db, user_id)
    return {"message": "Logout berhasil"}

@router.post("/validateSession")
def validate_session(data: ValidateSessionRequest, db: Session = Depends(get_db)):
    """
    Register a new user.

    Data yang dibutuhkan:
    - username
    - session_token
    """
    user = validate_user_session(db, data.model_dump())
    return user
