from schema import UserAuth, UserInfo, UserSignup
from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import FastAPI, Depends, HTTPException, status
from services.hashing import hash_password, verify_password
from middleware.error_handler import DatabaseErrorMiddleware
from services.database import create_db_tables, check_database_connection, get_session
import logging
from fastapi.responses import JSONResponse

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

    return {
        'status_code': 201,
        'message': 'Signed up successfully!'
    }

@app.post('/login/', response_model=dict)
def login(user: UserAuth, session: Session = Depends(get_session)):
    existing_user = session.exec(select(UserAuth).where(UserAuth.email == user.email)).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid Email!")

    if not verify_password(user.hashed, existing_user.hashed):
        raise HTTPException(status_code=401, detail="Invalid password!")
    
    return JSONResponse(status_code=200, content={
        'message': 'Successfully logged in!'
    })