from fastapi import APIRouter, Depends
from api.schemas.auth import UserAuth
from middleware.auth_middleware import get_current_user

router = APIRouter()

@router.get('/me/', response_model=dict)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Protected route - requires valid JWT token
    Returns current user's information
    """
    print(current_user)
    return {
        'user_id': str(current_user['user_id']),
        'email': current_user['email'],
        'message': 'This is your protected profile!'
    }
