"""
Shared dependencies - auth, session, etc.
"""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Read Bearer token from Authorization header,
    find the user that owns this session token.
    """
    token = credentials.credentials
    user = (
        db.query(User)
        .filter(User.session_token == token, User.deleted_at.is_(None))
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Token is invalid or session has expired")
    return user
