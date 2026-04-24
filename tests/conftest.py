"""
Общая фикстура: создаёт изолированное событие со своими критериями,
судьями и выступлениями, по окончании теста удаляет его (CASCADE по FK
вычистит критерии, оценки, судей и выступления).

Тесты гоняются на той же БД, что и приложение (DATABASE_URL), но не
пересекаются с реальными данными — все объекты помечены префиксом TEST-
и живут в новом event_id.
"""
import datetime
import time

import pytest

from app.core.auth import get_password_hash
from app.db.database import SessionLocal
from app.models.models import Criterion, Event, Human, Judge, Performance


@pytest.fixture()
def env():
    db = SessionLocal()
    created_event_id = None
    try:
        ev = Event(
            date=datetime.date.today(),
            city="TEST",
            name_event=f"TEST-{int(time.time()*1000)}",
        )
        db.add(ev)
        db.flush()
        created_event_id = ev.id_event

        c_tech = Criterion(name_criterion="T1", start_point=10.0, step=0.5,
                           id_event=ev.id_event, judge_type="technical")
        c_art = Criterion(name_criterion="A1", start_point=10.0, step=0.5,
                          id_event=ev.id_event, judge_type="artistry")
        db.add_all([c_tech, c_art])
        db.flush()

        h1 = Human(first_name="T", last_name="J")
        h2 = Human(first_name="A", last_name="J")
        db.add_all([h1, h2])
        db.flush()

        j_tech = Judge(id_human=h1.id, id_event=ev.id_event,
                       email=f"t{ev.id_event}@x", password_hash=get_password_hash("x"),
                       role="technical")
        j_art = Judge(id_human=h2.id, id_event=ev.id_event,
                      email=f"a{ev.id_event}@x", password_hash=get_password_hash("x"),
                      role="artistry")
        db.add_all([j_tech, j_art])
        db.flush()

        p = Performance(performance_name="P", discipline="Соло", id_event=ev.id_event)
        db.add(p)
        db.flush()

        ctx = {
            "event_id": ev.id_event,
            "criterion_tech_id": c_tech.id_criterion,
            "criterion_art_id": c_art.id_criterion,
            "judge_tech_id": j_tech.id_judge,
            "judge_art_id": j_art.id_judge,
            "performance_id": p.id_performance,
            "criterion_max": 10.0,
        }
        db.commit()
        yield ctx
    finally:
        try:
            cleanup = SessionLocal()
            if created_event_id is not None:
                ev = cleanup.query(Event).filter(Event.id_event == created_event_id).first()
                if ev is not None:
                    cleanup.delete(ev)
                    cleanup.commit()
            cleanup.close()
        except Exception:
            pass
        db.close()
