from fastapi import APIRouter, Depends, HTTPException,Header
from pydantic import BaseModel
from db.db_handler import DatabaseHandler
from config.config import Config
from jose import jwt, JWTError

router = APIRouter()
db = DatabaseHandler()
db.create_users_table()  # Ensure the Users table exists

class RegisterModel(BaseModel):
    username: str
    email: str
    password: str

class LoginModel(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(user: RegisterModel):
    """Register a new user"""
    result = db.register_user(user.username, user.email, user.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/login")
def login(user: LoginModel):
    """Authenticate user and return JWT token"""
    token = db.authenticate_user(user.email, user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token



def verify_token(token: str = Header(None)):
    """Verify and decode JWT token"""
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        return payload  # ✅ Returns user data if token is valid
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/protected")
def protected_route(user: dict = Depends(verify_token)):
    """Protected route example"""
    return {"message": f"Hello {user['username']}, you have access!"}