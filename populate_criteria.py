#!/usr/bin/env python3
"""
Наполняет таблицу `criterion` критериями для конкретного события.

Использование:
    python populate_criteria.py                # создать дефолтное событие и налить ФАФ туда
    python populate_criteria.py --event 5      # налить в существующее событие id_event=5
"""
import argparse
import datetime
from typing import Iterable

from app.db.database import SessionLocal
from app.models.models import Criterion, Event


# (judge_type, name, start_point, step)
ART_FAF: list[tuple[str, str, float, float]] = [
    ("artistry", "Музыкальность и ритм", 10.0, 0.5),
    ("artistry", "Артистическое выражение", 10.0, 0.5),
    ("artistry", "Работа с музыкой", 10.0, 0.5),
    ("artistry", "Сценическое присутствие", 10.0, 0.5),
    ("artistry", "Характер и эмоции", 10.0, 0.5),
    ("artistry", "Визуальная эффектность", 10.0, 0.5),
    ("artistry", "История/Повествование", 10.0, 0.5),
    ("artistry", "Оригинальность идеи", 10.0, 0.5),
    ("artistry", "Костюм и реквизит", 10.0, 0.5),
    ("artistry", "Мизансценирование пространства", 10.0, 0.5),
    ("artistry", "Переходы и связки", 10.0, 0.5),
    ("artistry", "Техсредства (свет, звук)", 10.0, 0.5),
    ("artistry", "Общее впечатление", 10.0, 0.5),
]

TECH_FAF: list[tuple[str, str, float, float]] = [
    ("technical", "1.1 Синхронность техники", 10.0, 0.5),
    ("technical", "1.2 Согласованность вооруженных и невооруженных действий", 10.0, 0.5),
    ("technical", "1.3 Правильность техники", 10.0, 0.5),
    ("technical", "1.4 Выравнивество движений", 10.0, 0.5),
    ("technical", "1.5 Легкость выполнения", 10.0, 0.5),
    ("technical", "2.1 Слаженность (группы) / Органичность (соло)", 10.0, 0.5),
    ("technical", "2.2 Достоверность", 10.0, 0.5),
    ("technical", "2.3 Качество исполнения", 10.0, 0.5),
    ("technical", "3.1 Темп (отсутствие проседаний, заминок)", 10.0, 0.5),
    ("technical", "3.2 Тактическая сложность", 10.0, 0.5),
    ("technical", "3.3 Координационно-двигательная сложность", 10.0, 0.5),
    ("technical", "3.4 Поощрение за сложность", 10.0, 0.5),
    ("technical", "3.5 Разнообразие действий нападения", 10.0, 0.5),
    ("technical", "3.6 Разнообразие действий обороны", 10.0, 0.5),
    ("technical", "3.7 Разнообразие действий подготовки", 10.0, 0.5),
    ("technical", "3.8 Общий уровень", 10.0, 0.5),
]


def _ensure_event(db) -> int:
    event = db.query(Event).first()
    if event is not None:
        return event.id_event
    event = Event(date=datetime.date.today(), city="Демо", name_event="Демо-фестиваль (ФАФ)")
    db.add(event)
    db.commit()
    db.refresh(event)
    print(f"✓ Создано дефолтное событие id_event={event.id_event}")
    return event.id_event


def _add_block(db, id_event: int, block: Iterable[tuple[str, str, float, float]], label: str) -> int:
    n = 0
    for judge_type, name, start_point, step in block:
        db.add(Criterion(
            name_criterion=name,
            start_point=start_point,
            step=step,
            id_event=id_event,
            judge_type=judge_type,
        ))
        n += 1
    print(f"  + {label}: {n}")
    return n


def populate_criteria(id_event: int | None = None) -> bool:
    db = SessionLocal()
    try:
        target_event = id_event if id_event is not None else _ensure_event(db)

        existing = db.query(Criterion).filter(Criterion.id_event == target_event).count()
        if existing:
            print(f"⚠️  В событии id_event={target_event} уже есть {existing} критериев — пропускаю.")
            return True

        print(f"Наполняю критерии для id_event={target_event}:")
        total = 0
        total += _add_block(db, target_event, TECH_FAF, "Технические (ФАФ)")
        total += _add_block(db, target_event, ART_FAF, "Артистические (ФАФ)")
        db.commit()
        print(f"\n✅ Готово. Всего критериев: {total}")
        return True
    except Exception as exc:
        db.rollback()
        print(f"❌ Ошибка: {exc}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", type=int, default=None)
    args = parser.parse_args()
    populate_criteria(args.event)
