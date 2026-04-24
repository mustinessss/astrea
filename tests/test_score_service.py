"""Тесты на запись оценок: upsert и валидация диапазона."""
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.api.services.score_service import get_scores_by_performance, upsert_score
from app.db.database import SessionLocal


def test_upsert_creates_then_updates_same_row(env):
    """Повторный вызов с тем же judge+performance+criterion должен апдейтить, а не плодить дубли."""
    db = SessionLocal()
    try:
        first = upsert_score(
            db=db,
            judge_id=env["judge_tech_id"],
            performance_id=env["performance_id"],
            criterion_id=env["criterion_tech_id"],
            value=Decimal("5.5"),
        )
        second = upsert_score(
            db=db,
            judge_id=env["judge_tech_id"],
            performance_id=env["performance_id"],
            criterion_id=env["criterion_tech_id"],
            value=Decimal("9.0"),
        )

        assert first.id_scores == second.id_scores, "upsert обязан обновлять ту же строку"
        assert second.value == Decimal("9.00")

        rows = get_scores_by_performance(db, env["performance_id"])
        assert len(rows) == 1, "не должно быть дублей"
        assert rows[0].id_event == env["event_id"], "id_event подтягивается из performance"
    finally:
        db.close()


def test_upsert_rejects_out_of_range(env):
    """Значение вне [0, criterion.start_point] — 400."""
    db = SessionLocal()
    try:
        with pytest.raises(HTTPException) as exc:
            upsert_score(
                db=db,
                judge_id=env["judge_tech_id"],
                performance_id=env["performance_id"],
                criterion_id=env["criterion_tech_id"],
                value=Decimal("99"),
            )
        assert exc.value.status_code == 400
        assert "Value must be in" in exc.value.detail

        with pytest.raises(HTTPException) as exc2:
            upsert_score(
                db=db,
                judge_id=env["judge_tech_id"],
                performance_id=env["performance_id"],
                criterion_id=env["criterion_tech_id"],
                value=Decimal("-1"),
            )
        assert exc2.value.status_code == 400
    finally:
        db.close()


def test_upsert_rejects_criterion_from_other_event(env):
    """Критерий из чужого события нельзя повесить на это выступление."""
    import datetime
    import time as _time

    from app.models.models import Criterion, Event

    db = SessionLocal()
    other_event_id = None
    try:
        other = Event(date=datetime.date.today(), city="X",
                      name_event=f"OTHER-{int(_time.time()*1000)}")
        db.add(other)
        db.flush()
        other_event_id = other.id_event
        alien = Criterion(name_criterion="alien", start_point=10.0, step=0.5,
                          id_event=other.id_event, judge_type="technical")
        db.add(alien)
        db.commit()

        with pytest.raises(HTTPException) as exc:
            upsert_score(
                db=db,
                judge_id=env["judge_tech_id"],
                performance_id=env["performance_id"],
                criterion_id=alien.id_criterion,
                value=Decimal("5"),
            )
        assert exc.value.status_code == 400
    finally:
        if other_event_id is not None:
            ev = db.query(Event).filter(Event.id_event == other_event_id).first()
            if ev:
                db.delete(ev)
                db.commit()
        db.close()
