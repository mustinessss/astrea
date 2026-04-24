"""Схемы для админ-панели управления судьями."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.core.enums import JudgeRole


class JudgeAdminCreate(BaseModel):
    """Создание судьи из уже существующего человека."""
    id_human: int = Field(..., description="ID существующего человека (Human)")
    id_event: Optional[int] = Field(None, description="ID события, к которому привязать судью")
    email: str = Field(..., min_length=3, max_length=100)
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="Если не передан — будет сгенерирован случайный",
    )
    role: JudgeRole
    access_code: Optional[str] = Field(None, max_length=50)


class JudgeAdminResponse(BaseModel):
    id_judge: int
    id_human: int
    id_event: Optional[int]
    email: str
    role: str
    is_active: bool
    full_name: str
    generated_password: Optional[str] = Field(
        None,
        description="Заполняется только при создании, если пароль был сгенерирован сервером",
    )

    class Config:
        from_attributes = True


class JudgePasswordReset(BaseModel):
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="Если не передан — будет сгенерирован случайный",
    )
