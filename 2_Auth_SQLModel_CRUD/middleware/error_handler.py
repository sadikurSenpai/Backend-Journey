from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class DatabaseErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # process the request
            response = await call_next(request)
            return response
        
        except OperationalError as e:
            logger.error(f"Database operational error: {e}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "error": "Service Unavailable",
                    "message": "Database is currently unavailable. Please try again later.",
                    "detail": "The service cannot connect to the database."
                }
            )
        
        except IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "Conflict",
                    "message": "The request could not be completed due to a conflict with the current state of the resource.",
                    "detail": "The request could not be completed due to a conflict with the current state of the resource."
                }
            )
        except DatabaseError as e:
            # General database errors
            logger.error(f"Database error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": "A database error occurred while processing your request.",
                    "detail": "Please contact support if this persists."
                }
            )
        
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                    "detail": str(e)
                }
            )
        