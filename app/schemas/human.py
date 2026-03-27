from pydantic import BaseModel
from typing import Optional


class HumanBase(BaseModel):
    """Базовая схема человека"""
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class HumanCreate(HumanBase):
    """Схема для создания человека"""
    pass


class HumanUpdate(BaseModel):
    """Схема для обновления человека"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class HumanResponse(HumanBase):
    """Схема для ответа о человеке"""
    id: int

    class Config:
        from_attributes = True
