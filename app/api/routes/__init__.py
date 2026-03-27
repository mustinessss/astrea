from .human import router as human_router
from .event import router as event_router
from .score import router as score_router
from .team import router as team_router

__all__ = ["human_router", "event_router", "score_router", "team_router"]
