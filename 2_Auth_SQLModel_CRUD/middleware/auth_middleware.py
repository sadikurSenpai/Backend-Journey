from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.jwt_handler import verify_token
from services.database import get_session
from schema import UserAuth
from sqlmodel import Session, select
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> UserAuth:
    """
    Dependency to get current authenticated user
    Use this in protected endpoints: user: UserAuth = Depends(get_current_user)
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user email from token
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = session.exec(select(UserAuth).where(UserAuth.email == email)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Optional: Create a dependency for refresh token validation
def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify refresh token and return payload"""
    token = credentials.credentials
    
    payload = verify_token(token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload