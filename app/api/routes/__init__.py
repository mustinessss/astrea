from .auth import router as auth_router
from .event import router as event_router
from .human import router as human_router
from .score import router as score_router
from .team import router as team_router
from app.api.routes.admin import router as admin_router  # NEW

__all__ = [
    "auth_router",
    "event_router",
    "human_router",
    "score_router",
    "team_router",
    "admin_router",
]