"""
Параллельный пересчёт итогов события.

Зачем поток на выступление, а не одним запросом GROUP BY:
1. По требованию задания нужна реальная многопоточность в проекте.
2. Каждое выступление считается независимо, поэтому это идеальная карта-задача
   для пула потоков. Узкое место — I/O в сторону Postgres, а GIL в этом случае
   не мешает (он отпускается на сетевых вызовах psycopg2).
3. Каждый поток открывает СВОЮ сессию (`SessionLocal()`) — сессии SQLAlchemy
   не потокобезопасны, шарить одну между потоками нельзя.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import List

from app.api.services.calculation_service import calculate_performance_score
from app.db.database import SessionLocal
from app.models.models import Performance


def _calc_one(performance_id: int) -> dict:
    """Тело воркера: открыть сессию, посчитать, закрыть."""
    db = SessionLocal()
    try:
        return {"id_performance": performance_id, **calculate_performance_score(db, performance_id)}
    finally:
        db.close()


def calculate_event_results_parallel(event_id: int, max_workers: int = 8) -> List[dict]:
    """Считает итоги по всем выступлениям события в пуле потоков и сортирует по убыванию итога."""
    db = SessionLocal()
    try:
        perfs = db.query(Performance).filter(Performance.id_event == event_id).all()
        meta = {p.id_performance: (p.performance_name, p.discipline) for p in perfs}
    finally:
        db.close()

    if not meta:
        return []

    workers = min(max_workers, len(meta)) or 1
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(_calc_one, list(meta.keys())))

    rows = []
    for r in results:
        name, discipline = meta[r["id_performance"]]
        rows.append({
            "id": r["id_performance"],
            "name": name,
            "discipline": discipline,
            "technical": r["technical_score"],
            "artistic": r["artistic_score"],
            "final": r["final_score"],
        })
    rows.sort(key=lambda x: x["final"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["place"] = i
    return rows


def calculate_event_results_sequential(event_id: int) -> List[dict]:
    """То же самое, но последовательно — нужно для бенчмарка."""
    db = SessionLocal()
    try:
        perfs = db.query(Performance).filter(Performance.id_event == event_id).all()
        rows = []
        for p in perfs:
            res = calculate_performance_score(db, p.id_performance)
            rows.append({
                "id": p.id_performance,
                "name": p.performance_name,
                "discipline": p.discipline,
                "technical": res["technical_score"],
                "artistic": res["artistic_score"],
                "final": res["final_score"],
            })
    finally:
        db.close()
    rows.sort(key=lambda x: x["final"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["place"] = i
    return rows
