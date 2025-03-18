from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.auth_helpers import get_current_user
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    
class LoginRequest(BaseModel):
    username: str
    password: str

ACCESS_TOKEN_EXPIRE_MINUTES = 7

router = APIRouter()

@router.post("/register/")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    username = user_data.username  
    password = user_data.password
    
    if db.query(User).filter(User.name == username).first():
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = User(name=username)
    new_user.set_password(password)  

    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login/")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    username = request.username
    password = request.password
    
    user = db.query(User).filter(User.name == username).first()
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = jwt.encode(
    {"sub": user.name, "exp": expires_at.timestamp()},
    SECRET_KEY, algorithm=ALGORITHM
    )

    return {"access_token": access_token, "token_type": "bearer"}

