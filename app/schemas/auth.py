from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    role: str


class RefreshToken(BaseModel):
    """Схема refresh токена"""
    refresh_token: str
    token_type: str = "bearer"


class TokenPair(BaseModel):
    """Пара access + refresh токенов"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    role: str


class Judge(BaseModel):
    """Базовая информация о судье"""
    user_id: int
    first_name: str
    last_name: str
    role: str  # 'judge', 'main_judge', 'technical', 'artistry', 'timekeeper'


class LoginRequest(BaseModel):
    """Запрос на логин"""
    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление access токена"""
    refresh_token: str


class JudgeLoginResponse(BaseModel):
    """Ответ на логин судьи"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    first_name: str
    last_name: str
    role: str
