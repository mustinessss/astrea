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

from app.api.routes import auth_router, event_router, human_router, score_router, team_router,admin_router
from app.api.services.calculation_service import calculate_performance_score
from app.api.services.event_calc import calculate_event_results_parallel
from app.api.services.score_service import upsert_score
from app.core.auth import create_token_pair, verify_password
from app.core.config import settings
from app.db.database import Base, SessionLocal, engine
from app.models.models import Criterion, Event, Judge, Performance, Score, Human

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
app.include_router(admin_router, prefix="/api", tags=["admin-api"])

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

        # Главный судья / админ: если событие отвалилось — подцепить самое свежее
        if judge.role in ("main_judge", "admin"):
            current_event = None
            if judge.id_event is not None:
                current_event = db.query(Event).filter(Event.id_event == judge.id_event).first()
            if current_event is None:
                current_event = db.query(Event).order_by(Event.id_event.desc()).first()
                if current_event is not None:
                    judge.id_event = current_event.id_event
                    db.add(judge)
                    db.commit()
                    db.refresh(judge)
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


def _require_main_judge(request: Request) -> Optional[Judge]:
    """Достаёт судью из cookie и пускает только если роль main_judge/admin.
    Возвращает Judge или None — если None, нужно делать редирект.
    """
    judge_id = request.cookies.get("judge_id")
    if not judge_id:
        return None
    db = SessionLocal()
    try:
        judge = db.query(Judge).filter(Judge.id_judge == int(judge_id)).first()
    finally:
        db.close()
    if not judge or judge.role not in ("main_judge", "admin"):
        return None
    return judge


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Сводка по событию — только для главного судьи. Авто-переподвязка к свежему событию."""
    judge = _require_main_judge(request)
    if judge is None:
        return RedirectResponse(url="/dashboard", status_code=302)

    db = SessionLocal()
    try:
        event = None
        if judge.id_event is not None:
            event = db.query(Event).filter(Event.id_event == judge.id_event).first()
        if event is None:
            event = db.query(Event).order_by(Event.id_event.desc()).first()
            if event is None:
                return RedirectResponse(url="/admin/judges", status_code=302)
            judge.id_event = event.id_event
            db.add(judge)
            db.commit()
            db.refresh(judge)

        rows = calculate_event_results_parallel(event.id_event)
        judges_count = db.query(func.count(Judge.id_judge)).filter(
            Judge.id_event == event.id_event
        ).scalar() or 0
        scores_count = db.query(func.count(Score.id_scores)).filter(
            Score.id_event == event.id_event
        ).scalar() or 0
    finally:
        db.close()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "event": event,
        "rows": rows,
        "judges_count": judges_count,
        "perf_count": len(rows),
        "scores_count": scores_count,
    })


@app.get("/admin/judges", response_class=HTMLResponse)
async def admin_judges_page(request: Request):
    """Страница управления судьями: создать судью из человека, раздать роли и пароли."""
    judge = _require_main_judge(request)
    if judge is None:
        return RedirectResponse(url="/dashboard", status_code=302)

    db = SessionLocal()
    try:
        humans = db.query(Human).order_by(Human.last_name, Human.first_name).all()
        events = db.query(Event).order_by(Event.id_event).all()
        judges = db.query(Judge).order_by(Judge.id_judge).all()
        humans_by_id = {h.id: h for h in db.query(Human).all()}
        judges_view = []
        for j in judges:
            h = humans_by_id.get(j.id_human)
            judges_view.append({
                "id_judge": j.id_judge,
                "full_name": f"{h.last_name} {h.first_name}".strip() if h else "—",
                "email": j.email,
                "role": j.role,
                "is_active": j.is_active,
                "id_event": j.id_event,
            })
    finally:
        db.close()

    return templates.TemplateResponse("admin_judges.html", {
        "request": request,
        "humans": humans,
        "events": events,
        "judges": judges_view,
        "current_event_id": judge.id_event,
    })

@app.get("/admin/events", response_class=HTMLResponse)
async def admin_events_page(request: Request):
    """Список и создание мероприятий, переключение активного события."""
    judge = _require_main_judge(request)
    if judge is None:
        return RedirectResponse(url="/dashboard", status_code=302)

    db = SessionLocal()
    try:
        evts = db.query(Event).order_by(Event.id_event.desc()).all()
        events_view = []
        for e in evts:
            perf_count = db.query(func.count(Performance.id_performance)).filter(
                Performance.id_event == e.id_event
            ).scalar() or 0
            j_count = db.query(func.count(Judge.id_judge)).filter(
                Judge.id_event == e.id_event
            ).scalar() or 0
            events_view.append({
                "id_event": e.id_event,
                "name_event": e.name_event,
                "city": e.city,
                "date": e.date,
                "perf_count": perf_count,
                "judges_count": j_count,
            })
    finally:
        db.close()

    return templates.TemplateResponse("admin_events.html", {
        "request": request,
        "events": events_view,
        "current_event_id": judge.id_event,
    })


@app.post("/admin/events")
async def admin_create_event(request: Request, payload: dict = Body(...)):
    judge = _require_main_judge(request)
    if judge is None:
        raise HTTPException(status_code=403, detail="Forbidden")

    name_event = (payload.get("name_event") or "").strip()
    city = (payload.get("city") or "").strip()
    date_str = payload.get("date")
    if not name_event or not city:
        raise HTTPException(status_code=400, detail="name_event и city обязательны")

    from datetime import date as _date
    parsed_date = None
    if date_str:
        try:
            parsed_date = _date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты, нужен YYYY-MM-DD")

    db = SessionLocal()
    try:
        new_event = Event(name_event=name_event, city=city, date=parsed_date)
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return {"id_event": new_event.id_event, "name_event": new_event.name_event}
    finally:
        db.close()


@app.post("/admin/events/{event_id}/set-active")
async def admin_set_active_event(request: Request, event_id: int):
    """Переключить активное событие для текущего главного судьи."""
    judge = _require_main_judge(request)
    if judge is None:
        raise HTTPException(status_code=403, detail="Forbidden")

    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id_event == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        j = db.query(Judge).filter(Judge.id_judge == judge.id_judge).first()
        j.id_event = event.id_event
        db.add(j)
        db.commit()
        return {"ok": True, "id_event": event.id_event}
    finally:
        db.close()
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
