from schema import UserAuth, UserInfo, UserSignup, TokenData, TokenResponse, RefreshTokenRequest
from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import FastAPI, Depends, HTTPException, status
from services.hashing import hash_password, verify_password
from middleware.error_handler import DatabaseErrorMiddleware
from services.database import create_db_tables, check_database_connection, get_session
import logging
from fastapi.responses import JSONResponse
from services.jwt_handler import create_access_token, create_refresh_token, verify_token
from middleware.auth_middleware import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# add middleware
app.add_middleware(DatabaseErrorMiddleware)

@app.on_event('startup')
def on_start():
    logger.info("Starting up...")

    if create_db_tables():
        logger.info('Database tables are ready')
    else:
        logger.warning("Database tables could not be created. Server will start anyway.")
        logger.warning("Database operations will fail until connection is restored.")


@app.get('/')
def home():
    return {
        'version':'1.0',
        'message':'Welcome to the Authentication'
    }

@app.get('/health/db')
def health_db():
    """Check database connectivity"""
    is_connected = check_database_connection()
    
    if is_connected:
        return {
            'status': 'healthy',
            'database': 'connected'
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                'status': 'unhealthy',
                'database': 'disconnected'
            }
        )


@app.post('/signup/', response_model=dict)
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


@app.post('/login/', response_model=TokenResponse)
def login(user: UserAuth, session: Session = Depends(get_session)):
    existing_user = session.exec(select(UserAuth).where(UserAuth.email == user.email)).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid Email!")

    if not verify_password(user.hashed, existing_user.hashed):
        raise HTTPException(status_code=401, detail="Invalid password!")
    
    # create tokens
    access_token = create_access_token(data={
        'sub': existing_user.email
    })
    refresh_token = create_refresh_token(data={
        'sub': existing_user.email
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

# Refresh token endpoint
@app.post('/refresh/', response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, session: Session = Depends(get_session)):
    """Get new access token using refresh token"""
    payload = verify_token(request.refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    email = payload.get("sub")
    
    # Verify user still exists
    user = session.exec(select(UserAuth).where(UserAuth.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": email})
    new_refresh_token = create_refresh_token(data={"sub": email})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@app.get('/me/', response_model=dict)
def get_my_profile(current_user: UserAuth = Depends(get_current_user)):
    """
    Protected route - requires valid JWT token
    Returns current user's information
    """
    return {
        'user_id': str(current_user.user_id),
        'email': current_user.email,
        'message': 'This is your protected profile!'
    }