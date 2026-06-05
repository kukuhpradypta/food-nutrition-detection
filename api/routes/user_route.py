"""
User routes - registration, login, profile.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas.user_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
    LoginData,
    ApiResponse,
    ValidateSessionRequest,
    LogoutRequest,
)
from api.controllers.user_controller import (
    register_user,
    login_user,
    get_user_by_id,
    update_user,
    logout_user,
    validate_user_session,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=ApiResponse, status_code=201)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    user = register_user(db, data.model_dump())
    return JSONResponse(
        status_code=201,
        content=ApiResponse(
            status=201,
            message="Registrasi berhasil",
            data=UserResponse.model_validate(user).model_dump(mode="json"),
        ).model_dump(),
    )


@router.post("/login", response_model=ApiResponse)
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user with username and password."""
    user = login_user(db, data.username, data.password)
    login_data = LoginData(
        session_token=user.session_token,
        user=UserResponse.model_validate(user),
    )
    return ApiResponse(
        status=200,
        message="Login berhasil",
        data=login_data.model_dump(mode="json"),
    )


@router.post("/validateSession", response_model=ApiResponse)
def validate_session(data: ValidateSessionRequest, db: Session = Depends(get_db)):
    """
    Validasi session token user.

    Data yang dibutuhkan:
    - username
    - session_token
    """
    result = validate_user_session(db, data.model_dump())
    return ApiResponse(
        status=result["status"],
        message=result["message"],
        data=result["data"],
    )


@router.get("/{user_id}", response_model=ApiResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID."""
    user = get_user_by_id(db, user_id)
    return ApiResponse(
        status=200,
        message="Data user berhasil diambil",
        data=UserResponse.model_validate(user).model_dump(mode="json"),
    )


@router.put("/{user_id}", response_model=ApiResponse)
def edit_profile(user_id: int, data: UserUpdateRequest, db: Session = Depends(get_db)):
    """Edit user profile. Semua field optional."""
    user = update_user(db, user_id, data.model_dump(exclude_unset=True))
    return ApiResponse(
        status=200,
        message="Profil berhasil diperbarui",
        data=UserResponse.model_validate(user).model_dump(mode="json"),
    )


@router.post("/logout", response_model=ApiResponse)
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    """Logout user — clear session token."""
    logout_user(db, data.session_token)
    return ApiResponse(
        status=200,
        message="Logout berhasil",
        data=None,
    )
