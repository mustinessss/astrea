from decimal import Decimal
import logging
import os
from typing import List, Optional

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import func

from app.api.routes import auth_router, event_router, human_router, score_router, team_router
from app.api.services.calculation_service import calculate_performance_score
from app.api.services.event_calc import calculate_event_results_parallel
from app.api.services.score_service import upsert_score
from app.core.auth import create_token_pair, verify_password
from app.core.config import settings
from app.db.database import Base, SessionLocal, engine
from app.models.models import Criterion, Event, Judge, Performance, Score

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")
except Exception as e:
    logger.error(f"❌ Error creating database tables: {e}")
    raise

app = FastAPI(
    title="Астрея — Система судейства фехтования",
    description="Автоматизированная система судейства на фестивалях артистического фехтования",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(human_router)
app.include_router(event_router)
app.include_router(score_router)
app.include_router(team_router)


# ───────────────────────── Web pages ─────────────────────────


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_form(request: Request):
    """Логин по одному паролю — для коротких демо."""
    try:
        form = await request.form()
        password = form.get("password")

        if not password:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Пароль обязателен",
            })

        db = SessionLocal()
        try:
            judge = None
            for j in db.query(Judge).all():
                if j.is_active and verify_password(password, j.password_hash):
                    judge = j
                    break
        finally:
            db.close()

        if not judge:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Неверный пароль",
            })

        access_token, refresh_token, _ = create_token_pair(
            data={"sub": judge.id_judge, "role": judge.role}
        )
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie("access_token", access_token, max_age=28800)
        response.set_cookie("refresh_token", refresh_token, max_age=2592000)
        response.set_cookie("judge_id", str(judge.id_judge))
        return response
    except Exception as e:
        logger.exception("Login error")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": f"Ошибка при входе: {e}",
        })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    judge_id = request.cookies.get("judge_id")
    if not judge_id:
        return RedirectResponse(url="/", status_code=302)

    db = SessionLocal()
    try:
        judge = db.query(Judge).filter(Judge.id_judge == int(judge_id)).first()
        if not judge:
            return RedirectResponse(url="/", status_code=302)

        disciplines: dict[str, list[dict]] = {}
        scored_count = 0
        total_count = 0
        if judge.id_event is not None:
            perfs = db.query(Performance).filter(Performance.id_event == judge.id_event).all()
            # сколько критериев под мою роль в этом событии
            my_criteria_count = db.query(func.count(Criterion.id_criterion)).filter(
                Criterion.id_event == judge.id_event,
                Criterion.judge_type == judge.role,
            ).scalar() or 0
            # для каждого выступления — сколько критериев я уже оценил
            for p in perfs:
                my_scored = db.query(func.count(Score.id_scores)).filter(
                    Score.id_judge == judge.id_judge,
                    Score.id_performance == p.id_performance,
                ).scalar() or 0
                fully_scored = my_criteria_count > 0 and my_scored >= my_criteria_count
                if fully_scored:
                    scored_count += 1
                total_count += 1
                disciplines.setdefault(p.discipline, []).append({
                    "id": p.id_performance,
                    "name": p.performance_name,
                    "team": "—",
                    "scored": fully_scored,
                    "scored_count": my_scored,
                    "criteria_count": my_criteria_count,
                })
    finally:
        db.close()

    context = {
        "request": request,
        "judge": {"first_name": "Судья", "last_name": "Теста", "email": judge.email, "role": judge.role},
        "role_type": judge.role,
        "system": "faf",
        "disciplines": disciplines,
        "scored_count": scored_count,
        "total_count": total_count,
    }
    return templates.TemplateResponse("judge_dashboard.html", context)


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Сводка по событию — для главного судьи / преподавателя на защите."""
    judge_id = request.cookies.get("judge_id")
    if not judge_id:
        return RedirectResponse(url="/", status_code=302)

    db = SessionLocal()
    try:
        judge = db.query(Judge).filter(Judge.id_judge == int(judge_id)).first()
        if not judge or judge.id_event is None:
            return RedirectResponse(url="/dashboard", status_code=302)

        event = db.query(Event).filter(Event.id_event == judge.id_event).first()

        # Пересчёт итогов идёт в пуле потоков (см. event_calc.py).
        # Каждое выступление считается отдельным потоком со своей сессией БД.
        rows = calculate_event_results_parallel(judge.id_event)

        # Счётчики для шапки.
        judges_count = db.query(func.count(Judge.id_judge)).filter(Judge.id_event == judge.id_event).scalar() or 0
        scores_count = db.query(func.count(Score.id_scores)).filter(Score.id_event == judge.id_event).scalar() or 0
    finally:
        db.close()

    context = {
        "request": request,
        "event": event,
        "rows": rows,
        "judges_count": judges_count,
        "perf_count": len(rows),
        "scores_count": scores_count,
    }
    return templates.TemplateResponse("admin.html", context)


# ───────────────────────── Judging form (UI) ─────────────────────────


@app.get("/judge/performance/{performance_id}", response_class=HTMLResponse)
async def judge_performance_page(request: Request, performance_id: int):
    judge_id = request.cookies.get("judge_id")
    if not judge_id:
        return RedirectResponse(url="/", status_code=302)

    db = SessionLocal()
    try:
        judge = db.query(Judge).filter(Judge.id_judge == int(judge_id)).first()
        if not judge:
            return RedirectResponse(url="/", status_code=302)

        performance = db.query(Performance).filter(Performance.id_performance == performance_id).first()
        if not performance:
            raise HTTPException(status_code=404, detail="Performance not found")

        criteria = (
            db.query(Criterion)
            .filter(
                Criterion.id_event == performance.id_event,
                Criterion.judge_type == judge.role,
            )
            .order_by(Criterion.id_criterion)
            .all()
        )

        existing_rows = (
            db.query(Score)
            .filter(
                Score.id_judge == judge.id_judge,
                Score.id_performance == performance.id_performance,
            )
            .all()
        )
        existing_scores = {s.id_criterion: float(s.value) for s in existing_rows}

        return templates.TemplateResponse("judge_performance.html", {
            "request": request,
            "judge": {"email": judge.email, "role": judge.role, "id_judge": judge.id_judge},
            "performance": performance,
            "criteria": criteria,
            "existing_scores": existing_scores,
        })
    finally:
        db.close()


class _ScoreItem(BaseModel):
    criterion_id: int
    value: Decimal = Field(..., ge=0)


class _ScoreBatch(BaseModel):
    performance_id: int
    scores: List[_ScoreItem]


@app.post("/judge/score")
async def judge_submit_scores(request: Request, payload: _ScoreBatch = Body(...)):
    """Сохранение пачки оценок текущим судьёй (auth по cookie judge_id).

    Используется UI-формой. Полноценный JSON-API с JWT остаётся на /scores/.
    Внутри идёт upsert — повторная отправка обновит существующие оценки,
    что и реализует кнопку «изменить» в окне подтверждения.
    """
    judge_id_cookie = request.cookies.get("judge_id")
    if not judge_id_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = SessionLocal()
    try:
        judge = db.query(Judge).filter(Judge.id_judge == int(judge_id_cookie)).first()
        if not judge:
            raise HTTPException(status_code=401, detail="Judge not found")

        saved = 0
        for item in payload.scores:
            upsert_score(
                db=db,
                judge_id=judge.id_judge,
                performance_id=payload.performance_id,
                criterion_id=item.criterion_id,
                value=item.value,
            )
            saved += 1
        return JSONResponse({"saved": saved})
    finally:
        db.close()


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
