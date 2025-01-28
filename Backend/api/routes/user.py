from fastapi import APIRouter
from services.user_service import UserService

router = APIRouter()

@router.get("/user")
def get_user(user_id: int):
    """Fetch user information."""
    return UserService.get_user(user_id)
