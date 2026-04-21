from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.models.models import Judge, Human
from app.schemas.auth import LoginRequest, JudgeLoginResponse, Token, RefreshTokenRequest
from app.core.enums import JudgeRole
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_token_pair,
    decode_refresh_token,
    get_current_user,
    get_current_judge,
    get_main_judge
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=JudgeLoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Логин судьи с email и пароль
    Возвращает JWT токен
    """
    # Найти судью по email
    judge = db.query(Judge).filter(Judge.email == credentials.email).first()
    
    if not judge:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Проверить пароль
    if not verify_password(credentials.password, judge.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Проверить активен ли аккаунт
    if not judge.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Обновить last_login
    judge.last_login = datetime.now()
    db.add(judge)
    db.commit()
    
    # Получить информацию о человеке
    human = db.query(Human).filter(Human.id == judge.id_human).first()
    
    # Создать пару токенов
    access_token, refresh_token, expires_in = create_token_pair(
        data={"sub": judge.id_judge, "role": judge.role, "event": judge.id_event}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user_id": judge.id_judge,
        "first_name": human.first_name if human else "Unknown",
        "last_name": human.last_name if human else "Judge",
        "role": judge.role
    }


@router.post("/refresh", response_model=Token)
def refresh_token_endpoint(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Обновить access токен используя refresh токен
    """
    # Декодировать refresh токен
    payload = decode_refresh_token(request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    judge_id: int = payload.get("sub")
    if judge_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Проверить что судья существует и активен
    judge = db.query(Judge).filter(Judge.id_judge == judge_id).first()
    if not judge or not judge.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Создать новый access токен
    access_token, _, expires_in = create_token_pair(
        data={"sub": judge.id_judge, "role": judge.role, "event": judge.id_event}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user_id": judge.id_judge,
        "role": judge.role
    }


@router.post("/register", response_model=JudgeLoginResponse)
def register(
    human_id: int,
    email: str,
    password: str,
    role: JudgeRole,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового судьи
    (Только для администраторов в real-world приложении)
    """
    # Проверить существует ли такой human
    human = db.query(Human).filter(Human.id == human_id).first()
    if not human:
        raise HTTPException(status_code=404, detail="Human not found")
    
    # Проверить что email еще не зарегистрирован
    existing_judge = db.query(Judge).filter(Judge.email == email).first()
    if existing_judge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Валидация пароля
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Создать судью
    password_hash = get_password_hash(password)
    new_judge = Judge(
        id_human=human_id,
        email=email,
        password_hash=password_hash,
        role=role.value,
        is_active=True
    )
    db.add(new_judge)
    db.commit()
    db.refresh(new_judge)
    
    # Создать пару токенов
    access_token, refresh_token, expires_in = create_token_pair(
        data={"sub": new_judge.id_judge, "role": new_judge.role}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user_id": new_judge.id_judge,
        "first_name": human.first_name,
        "last_name": human.last_name,
        "role": new_judge.role
    }


@router.get("/me", response_model=dict)
def get_current_judge_info(current_user: dict = Depends(get_current_judge), db: Session = Depends(get_db)):
    """Получить информацию текущего судьи"""
    judge = db.query(Judge).filter(Judge.id_judge == current_user["user_id"]).first()
    human = db.query(Human).filter(Human.id == judge.id_human).first()
    
    return {
        "user_id": judge.id_judge,
        "first_name": human.first_name,
        "last_name": human.last_name,
        "email": judge.email,
        "role": judge.role,
        "event_id": judge.id_event,
        "access_code": judge.access_code,
        "is_active": judge.is_active,
        "last_login": judge.last_login
    }
