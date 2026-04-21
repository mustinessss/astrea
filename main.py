from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import logging
import os

from app.db.database import Base, engine, SessionLocal
from app.core.config import settings
from app.api.routes import auth_router, human_router, event_router, team_router
from app.models.models import Judge
from app.core.auth import verify_password, create_token_pair

# Логирование
logger = logging.getLogger(__name__)

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Создать таблицы с обработкой ошибок
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")
except Exception as e:
    logger.error(f"❌ Error creating database tables: {e}")
    raise

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
app.include_router(auth_router)
app.include_router(human_router)
app.include_router(event_router)
app.include_router(team_router)





@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})


@app.post("/login")
async def login_form(request: Request):
    """Handle HTML form login with password only"""
    try:
        form = await request.form()
        password = form.get("password")
        
        if not password:
            return templates.TemplateResponse(request, "login.html", {
                "request": request,
                "error": "Пароль обязателен"
            })
        
        # Find judge with matching password
        db = SessionLocal()
        judges = db.query(Judge).all()
        judge = None
        
        for j in judges:
            if verify_password(password, j.password_hash) and j.is_active:
                judge = j
                break
        
        if not judge:
            db.close()
            return templates.TemplateResponse(request, "login.html", {
                "request": request,
                "error": "Неверный пароль"
            })
        
        # Create token pair
        access_token, refresh_token, expires_in = create_token_pair(
            data={"sub": judge.id_judge, "role": judge.role}
        )
        
        db.close()
        
        # Redirect to dashboard with tokens in cookies
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie("access_token", access_token, max_age=28800)
        response.set_cookie("refresh_token", refresh_token, max_age=2592000)
        response.set_cookie("judge_id", str(judge.id_judge))
        
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse(request, "login.html", {
            "request": request,
            "error": f"Ошибка при входе: {str(e)}"
        })




@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    try:
        judge_id = request.cookies.get("judge_id")
        
        if not judge_id:
            return RedirectResponse(url="/", status_code=302)
        
        db = SessionLocal()
        judge = db.query(Judge).filter(Judge.id_judge == int(judge_id)).first()
        db.close()
        
        if not judge:
            return RedirectResponse(url="/", status_code=302)
        
        context = {
            "request": request,
            "judge": {"first_name": "Судья", "last_name": "Теста", "email": judge.email, "role": judge.role},
            "role_type": judge.role,
            "system": "faf"
        }
        return templates.TemplateResponse(request, "judge_dashboard.html", context)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return RedirectResponse(url="/", status_code=302)


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    try:
        judge_id = request.cookies.get("judge_id")
        
        if not judge_id:
            return RedirectResponse(url="/", status_code=302)
        
        context = {"request": request, "error": None}
        return templates.TemplateResponse(request, "admin.html", context)
    except Exception as e:
        logger.error(f"Admin error: {e}")
        return RedirectResponse(url="/", status_code=302)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
