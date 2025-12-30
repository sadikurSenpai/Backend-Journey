from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from api.schemas.auth import UserAuth, UserInfo, UserSignup, TokenResponse, RefreshTokenRequest
from services.database import get_session
from services.hashing import hash_password, verify_password
from services.jwt_handler import create_access_token, create_refresh_token, verify_token

router = APIRouter()

@router.post('/signup/', response_model=dict)
def signup(user: UserSignup, session: Session = Depends(get_session)):
    existing_user = session.exec(select(UserAuth).where(UserAuth.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="This email already holds an account!")
    
    hashed_password = hash_password(user.password)
    user_auth = UserAuth(email=user.email, hashed=hashed_password)

    user_info = UserInfo(
        full_name=user.full_name,
        age=user.age, 
        gender=user.gender,
        auth=user_auth
    )

    session.add(user_info)
    session.commit()

    return JSONResponse(
        status_code=201, content={
        'message': 'Signed up successfully!'
        }
    )

@router.post('/login/', response_model=TokenResponse)
def login(user: UserAuth, session: Session = Depends(get_session)):
    existing_user = session.exec(select(UserAuth).where(UserAuth.email == user.email)).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid Email!")

    if not verify_password(user.hashed, existing_user.hashed):
        raise HTTPException(status_code=401, detail="Invalid password!")
    
    # create tokens
    access_token = create_access_token(data={
        'sub': str(existing_user.user_id),
        'email': existing_user.email
    })
    refresh_token = create_refresh_token(data={
        'sub': str(existing_user.user_id),
        'email': existing_user.email
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post('/refresh/', response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, session: Session = Depends(get_session)):
    """Get new access token using refresh token"""
    payload = verify_token(request.refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    email = payload.get("email")
    user_id = payload.get("sub")
    
    # Verify user still exists
    user = session.exec(select(UserAuth).where(UserAuth.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    new_access_token = create_access_token(data={
        "sub": str(user.user_id),
        "email": email
    })
    new_refresh_token = create_refresh_token(data={
        "sub": str(user.user_id),
        "email": email
    })
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )
