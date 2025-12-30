from fastapi import FastAPI, status
from middleware.error_handler import DatabaseErrorMiddleware
from services.database import create_db_tables, check_database_connection, get_session
import logging
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from api.endpoints import auth, get_profile
from api.schemas.auth import UserAuth, UserInfo

app = FastAPI()

# add middleware
app.add_middleware(DatabaseErrorMiddleware)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(get_profile.router, tags=["Profile"])

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

