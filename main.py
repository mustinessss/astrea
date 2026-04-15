from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db.database import Base, engine
from app.core.config import settings
from app.models import *
from app.api.routes import auth_router, human_router, event_router, team_router, admin_router
from app.api.routes import scores

app.include_router(scores.router)
# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Астрея - Система судейства фехтования",
    description="Автоматизированная система судейства на фестивалях артистического фехтования",
    version="0.1.0"
)

# Mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
"""app.include_router(auth_router)
app.include_router(human_router)
app.include_router(event_router)
app.include_router(score_router)
app.include_router(team_router)
app.include_router(admin_router)"""





@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Астрею!",
        "version": "0.1.0",
        "status": "База данных инициализирована"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
