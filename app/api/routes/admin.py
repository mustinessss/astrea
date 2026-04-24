"""Админ-роутер: управление судьями (только main_judge/admin)."""
import secrets
import string
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_main_judge, get_password_hash
from app.db.database import get_db
from app.models.models import Event, Human, Judge
from app.schemas.human import HumanResponse
from app.schemas.judge_admin import (
    JudgeAdminCreate,
    JudgeAdminResponse,
    JudgePasswordReset,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _generate_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _to_response(
    db: Session, judge: Judge, generated_password: Optional[str] = None
) -> JudgeAdminResponse:
    human = db.query(Human).filter(Human.id == judge.id_human).first()
    full_name = (
        f"{human.last_name} {human.first_name}".strip() if human else "—"
    )
    return JudgeAdminResponse(
        id_judge=judge.id_judge,
        id_human=judge.id_human,
        id_event=judge.id_event,
        email=judge.email,
        role=judge.role,
        is_active=judge.is_active,
        full_name=full_name,
        generated_password=generated_password,
    )


@router.get("/humans", response_model=List[HumanResponse])
def list_humans(
    db: Session = Depends(get_db),
    _: dict = Depends(get_main_judge),
):
    return db.query(Human).order_by(Human.last_name, Human.first_name).all()


@router.get("/judges", response_model=List[JudgeAdminResponse])
def list_judges(
    db: Session = Depends(get_db),
    _: dict = Depends(get_main_judge),
):
    return [_to_response(db, j) for j in db.query(Judge).order_by(Judge.id_judge).all()]


@router.post("/judges", response_model=JudgeAdminResponse, status_code=201)
def create_judge(
    data: JudgeAdminCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_main_judge),
):
    human = db.query(Human).filter(Human.id == data.id_human).first()
    if not human:
        raise HTTPException(status_code=404, detail="Human not found")

    if data.id_event is not None:
        event = db.query(Event).filter(Event.id_event == data.id_event).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

    if db.query(Judge).filter(Judge.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    password_plain = data.password or _generate_password()
    new_judge = Judge(
        id_human=data.id_human,
        id_event=data.id_event,
        email=data.email,
        password_hash=get_password_hash(password_plain),
        role=data.role.value,
        access_code=data.access_code,
        is_active=True,
    )
    db.add(new_judge)
    db.commit()
    db.refresh(new_judge)

    return _to_response(
        db,
        new_judge,
        generated_password=password_plain if not data.password else None,
    )


@router.post("/judges/{judge_id}/reset-password", response_model=JudgeAdminResponse)
def reset_password(
    judge_id: int,
    data: JudgePasswordReset,
    db: Session = Depends(get_db),
    _: dict = Depends(get_main_judge),
):
    judge = db.query(Judge).filter(Judge.id_judge == judge_id).first()
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")

    password_plain = data.password or _generate_password()
    judge.password_hash = get_password_hash(password_plain)
    db.add(judge)
    db.commit()
    db.refresh(judge)
    return _to_response(
        db, judge, generated_password=password_plain if not data.password else None
    )


@router.post("/judges/{judge_id}/toggle-active", response_model=JudgeAdminResponse)
def toggle_active(
    judge_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_main_judge),
):
    judge = db.query(Judge).filter(Judge.id_judge == judge_id).first()
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    judge.is_active = not judge.is_active
    db.add(judge)
    db.commit()
    db.refresh(judge)
    return _to_response(db, judge)