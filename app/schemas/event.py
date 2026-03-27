from pydantic import BaseModel
from typing import Optional
from datetime import date


class EventBase(BaseModel):
    """Базовая схема события"""
    name_event: str
    date: date
    city: str


class EventCreate(EventBase):
    """Схема для создания события"""
    pass


class EventUpdate(BaseModel):
    """Схема для обновления события"""
    name_event: Optional[str] = None
    date: Optional[date] = None
    city: Optional[str] = None


class EventResponse(EventBase):
    """Схема для ответа о событии"""
    id_event: int

    class Config:
        from_attributes = True


class PerformanceBase(BaseModel):
    """Базовая схема выступления"""
    performance_name: str
    discipline: str
    id_event: int


class PerformanceCreate(PerformanceBase):
    """Схема для создания выступления"""
    pass


class PerformanceUpdate(BaseModel):
    """Схема для обновления выступления"""
    performance_name: Optional[str] = None
    discipline: Optional[str] = None


class PerformanceResponse(PerformanceBase):
    """Схема для ответа о выступлении"""
    id_performance: int

    class Config:
        from_attributes = True
