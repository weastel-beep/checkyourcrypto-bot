from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, verify_token, get_password_hash
from app.models.admin import AdminUser
from app.schemas.auth import UserLogin, Token, UserResponse, UserCreate
from app.core.config import settings

router = APIRouter(tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> AdminUser:
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Вход в систему"""
    user = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: AdminUser = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user

@router.post("/create", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Создание нового администратора"""
    # Проверяем, существует ли пользователь
    db_user = db.query(AdminUser).filter(AdminUser.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user.password)
    db_user = AdminUser(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        is_staff=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
