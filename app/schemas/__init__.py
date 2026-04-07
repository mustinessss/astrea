# Schemas package
from app.schemas.human import HumanCreate, HumanUpdate, HumanResponse
from app.schemas.event import EventCreate, EventUpdate, EventResponse, PerformanceCreate, PerformanceUpdate, PerformanceResponse
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.schemas.score import (
    ScoresArtFafCreate, ScoresArtFafResponse,
    ScoresTechFafCreate, ScoresTechFafResponse,
    ScoresArtNafCreate, ScoresArtNafResponse,
    ScoresTechNafCreate, ScoresTechNafResponse
)
from app.schemas.auth import Token, Judge, LoginRequest, JudgeLoginResponse

__all__ = [
    "HumanCreate", "HumanUpdate", "HumanResponse",
    "EventCreate", "EventUpdate", "EventResponse",
    "PerformanceCreate", "PerformanceUpdate", "PerformanceResponse",
    "TeamCreate", "TeamUpdate", "TeamResponse",
    "ScoresArtFafCreate", "ScoresArtFafResponse",
    "ScoresTechFafCreate", "ScoresTechFafResponse",
    "ScoresArtNafCreate", "ScoresArtNafResponse",
    "ScoresTechNafCreate", "ScoresTechNafResponse",
    "Token", "Judge", "LoginRequest", "JudgeLoginResponse",
]
