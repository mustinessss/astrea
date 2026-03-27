from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.core.config import settings
from app.models import *
from app.api.routes import human_router, event_router, score_router, team_router

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Астрея - Система судейства фехтования",
    description="Автоматизированная система судейства на фестивалях артистического фехтования",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(human_router)
app.include_router(event_router)
app.include_router(score_router)
app.include_router(team_router)


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
