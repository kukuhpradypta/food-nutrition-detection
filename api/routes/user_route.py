"""
User routes - registration, login, profile.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_user
from api.models.user import User
from api.schemas.user_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
    LoginData,
    ApiResponse,
    ValidateSessionRequest,
    ChangePasswordRequest,
)
from api.controllers.user_controller import (
    register_user,
    login_user,
    update_user,
    logout_user,
    validate_user_session,
    change_password,
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
            message="Registration successful",
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
        message="Login successful",
        data=login_data.model_dump(mode="json"),
    )


@router.post("/validateSession", response_model=ApiResponse)
def validate_session(data: ValidateSessionRequest, db: Session = Depends(get_db)):
    """
    Validate user session token.

    Required fields:
    - username
    - session_token
    """
    result = validate_user_session(db, data.model_dump())
    return ApiResponse(
        status=result["status"],
        message=result["message"],
        data=result["data"],
    )


@router.get("/me", response_model=ApiResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user profile.

    Header: Authorization: Bearer <session_token>
    """
    return ApiResponse(
        status=200,
        message="User data retrieved successfully",
        data=UserResponse.model_validate(current_user).model_dump(mode="json"),
    )


@router.put("/me", response_model=ApiResponse)
def edit_profile(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Edit current logged-in user profile.

    Header: Authorization: Bearer <session_token>
    All fields are optional — send only fields you want to update.
    """
    user = update_user(db, current_user.id, data.model_dump(exclude_unset=True))
    return ApiResponse(
        status=200,
        message="Profile updated successfully",
        data=UserResponse.model_validate(user).model_dump(mode="json"),
    )


@router.post("/logout", response_model=ApiResponse)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout user — clear session token.

    Header: Authorization: Bearer <session_token>
    """
    logout_user(db, current_user)
    return ApiResponse(
        status=200,
        message="Logout successful",
        data=None,
    )


@router.put("/me/password", response_model=ApiResponse)
def change_user_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change password for the logged-in user.

    Requires the correct old password.

    Header: Authorization: Bearer <session_token>
    """
    change_password(db, current_user, data.old_password, data.new_password)
    return ApiResponse(
        status=200,
        message="Password changed successfully",
        data=None,
    )
