from pydantic import BaseModel
from typing import Optional


class TeamBase(BaseModel):
    """Базовая схема команды"""
    team_name: str
    team_city: str


class TeamCreate(TeamBase):
    """Схема для создания команды"""
    pass


class TeamUpdate(BaseModel):
    """Схема для обновления команды"""
    team_city: Optional[str] = None


class TeamResponse(TeamBase):
    """Схема для ответа о команде"""
    id_team: int

    class Config:
        from_attributes = True
