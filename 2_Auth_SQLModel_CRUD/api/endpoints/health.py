from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from services.database import check_database_connection

router = APIRouter()

@router.get('/')
def home():
    return {
        'version':'1.0',
        'message':'Welcome to the Authentication'
    }

@router.get('/health/db')
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
