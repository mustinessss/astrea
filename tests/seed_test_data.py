#!/usr/bin/env python3
"""Сидер тестовых выступлений и второго судьи для демонстрации формы оценок."""
from app.core.auth import get_password_hash
from app.db.database import SessionLocal
from app.models.models import Event, Human, Judge, Performance


def seed():
    db = SessionLocal()
    try:
        event = db.query(Event).first()
        if event is None:
            print("❌ Сначала запусти populate_criteria.py — нужно событие.")
            return False

        for j in db.query(Judge).filter(Judge.id_event.is_(None)).all():
            j.id_event = event.id_event
            print(f"  ↳ Судья id_judge={j.id_judge} ({j.role}) привязан к event={event.id_event}")

        artistry = db.query(Judge).filter(Judge.role == "artistry").first()
        if artistry is None:
            human = Human(first_name="Артистический", last_name="Судья", email="art@test.com")
            db.add(human)
            db.flush()
            artistry = Judge(
                id_human=human.id,
                id_event=event.id_event,
                email="art@test.com",
                password_hash=get_password_hash("artpass"),
                role="artistry",
                is_active=True,
            )
            db.add(artistry)
            print(f"✓ Создан артистический судья (пароль: artpass)")

        existing_perfs = db.query(Performance).filter(Performance.id_event == event.id_event).count()
        if existing_perfs == 0:
            samples = [
                ("Тёмный лес", "Соло"),
                ("Дуэль на рассвете", "Дуэль"),
                ("Ансамбль клинков", "Группа"),
            ]
            for name, discipline in samples:
                db.add(Performance(performance_name=name, discipline=discipline, id_event=event.id_event))
                print(f"  + Выступление: {name} ({discipline})")

        db.commit()
        print("\n✅ Готово.")
        return True
    except Exception as exc:
        db.rollback()
        print(f"❌ Ошибка: {exc}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    seed()
