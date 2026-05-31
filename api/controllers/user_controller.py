"""
User controller - business logic for user management.
"""
import hashlib
import uuid

from sqlalchemy.orm import Session
from fastapi import HTTPException

from api.models.user import User


def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    """Generate a unique session token."""
    return str(uuid.uuid4())

def validate_user_session(db: Session, data: dict):
    """Validate user session."""

    user = (
        db.query(User)
        .filter(
            User.username == data["username"],
            User.session_token == data["session_token"]
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid user session"
        )

    return {
        "status": 200,
        "message": "Token valid",
        "data": {
            "username": user.username,
            "session_token": user.session_token
        }
    }

def register_user(db: Session, data: dict) -> User:
    """Register a new user."""
    # Check if username already exists
    existing = db.query(User).filter(User.username == data["username"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username sudah terdaftar")

    user = User(
        name=data["name"],
        username=data["username"],
        password=hash_password(data["password"]),
        gender=data["gender"],
        height_cm=data["height_cm"],
        weight_kg=data["weight_kg"],
        age=data["age"],
        health_goal=data["health_goal"],
        activity_level=data["activity_level"],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, username: str, password: str) -> User:
    """Authenticate user by username and password."""
    user = db.query(User).filter(User.username == username, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Username atau password salah")

    if user.password != hash_password(password):
        raise HTTPException(status_code=401, detail="Username atau password salah")

    # Generate session token
    user.session_token = generate_token()
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return user


def update_user(db: Session, user_id: int, data: dict) -> User:
    """Update user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    for key, value in data.items():
        if value is not None:
            if key == "password":
                value = hash_password(value)
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def logout_user(db: Session, user_id: int) -> None:
    """Clear session token (logout)."""
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    user.session_token = None
    db.commit()
