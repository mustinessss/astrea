#!/usr/bin/env python3
"""
Бенчмарк: пересчёт итогов события — последовательно vs пул потоков.

Что делает:
  1. Создаёт временное событие «BENCH-…».
  2. Наполняет его N выступлений (по умолчанию 60), судьями и оценками.
  3. Меряет время `calculate_event_results_sequential` и
     `calculate_event_results_parallel` (3 прогона каждое — берём минимум,
     чтобы убрать шум первого прогрева пула соединений).
  4. Печатает таблицу и ускорение.
  5. Удаляет временные данные (CASCADE по event).

Запуск:
    python benchmark.py            # 60 выступлений, 6 судей
    python benchmark.py --perfs 120 --judges 8 --workers 16
"""
import argparse
import datetime
import random
import time

from app.api.services import calculation_service
from app.api.services.event_calc import (
    calculate_event_results_parallel,
    calculate_event_results_sequential,
)
from app.core.auth import get_password_hash
from app.db.database import SessionLocal
from app.models.models import Criterion, Event, Human, Judge, Performance, Score


def _patch_io_delay(seconds: float) -> None:
    """
    Оборачивает calculate_performance_score sleep'ом, чтобы сымитировать
    сетевую задержку до удалённой БД. На локальном Postgres (<1мс на запрос)
    выигрыш от потоков теряется на накладных расходах, но как только
    появляется реальный I/O — параллельная версия начинает обгонять
    последовательную в N раз. Это и хочется показать на защите.
    """
    if seconds <= 0:
        return
    original = calculation_service.calculate_performance_score

    def slow(db, performance_id):
        time.sleep(seconds)
        return original(db, performance_id)

    calculation_service.calculate_performance_score = slow
    # event_calc.py импортирует функцию по имени, поэтому пропатчим и там
    from app.api.services import event_calc
    event_calc.calculate_performance_score = slow


CRITERIA_BLUEPRINT = [
    ("technical", "Тех-критерий"),
    ("artistry", "Арт-критерий"),
]


def _seed_event(perfs: int, judges: int, criteria_per_type: int) -> int:
    db = SessionLocal()
    try:
        ev = Event(
            date=datetime.date.today(),
            city="BENCH",
            name_event=f"BENCH-{int(time.time())}",
        )
        db.add(ev)
        db.flush()

        crit_ids: list[int] = []
        for judge_type, label in CRITERIA_BLUEPRINT:
            for k in range(criteria_per_type):
                c = Criterion(
                    name_criterion=f"{label} #{k+1}",
                    start_point=10.0,
                    step=0.5,
                    id_event=ev.id_event,
                    judge_type=judge_type,
                )
                db.add(c)
                db.flush()
                crit_ids.append(c.id_criterion)

        judge_ids: list[int] = []
        for j in range(judges):
            h = Human(first_name=f"B{j}", last_name="Bench")
            db.add(h)
            db.flush()
            jdg = Judge(
                id_human=h.id,
                id_event=ev.id_event,
                email=f"bench{j}_{ev.id_event}@x",
                password_hash=get_password_hash("x"),
                role="technical" if j % 2 == 0 else "artistry",
            )
            db.add(jdg)
            db.flush()
            judge_ids.append(jdg.id_judge)

        perf_ids: list[int] = []
        for i in range(perfs):
            p = Performance(
                performance_name=f"Perf {i+1}",
                discipline=random.choice(["Соло", "Дуэль", "Группа", "Ансамбль"]),
                id_event=ev.id_event,
            )
            db.add(p)
            db.flush()
            perf_ids.append(p.id_performance)

        rng = random.Random(42)
        bulk = []
        for pid in perf_ids:
            for jid in judge_ids:
                for cid in crit_ids:
                    bulk.append(Score(
                        id_event=ev.id_event,
                        id_judge=jid,
                        id_performance=pid,
                        id_criterion=cid,
                        value=round(rng.uniform(5.0, 10.0), 1),
                    ))
        db.bulk_save_objects(bulk)
        db.commit()
        return ev.id_event
    finally:
        db.close()


def _drop_event(event_id: int) -> None:
    db = SessionLocal()
    try:
        ev = db.query(Event).filter(Event.id_event == event_id).first()
        if ev:
            db.delete(ev)
            db.commit()
    finally:
        db.close()


def _bench(label: str, fn, *args, runs: int = 3) -> float:
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn(*args)
        times.append(time.perf_counter() - t0)
    best = min(times)
    print(f"  {label:35} best={best*1000:8.1f} ms   runs={['%.1f'%(t*1000) for t in times]}")
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perfs", type=int, default=60)
    ap.add_argument("--judges", type=int, default=6)
    ap.add_argument("--criteria", type=int, default=8, help="критериев на каждый judge_type")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--io-delay", type=float, default=0.0,
                    help="искусственная задержка на каждый пересчёт выступления (сек), имитирует удалённую БД")
    ap.add_argument("--keep", action="store_true", help="не удалять созданное событие")
    args = ap.parse_args()

    _patch_io_delay(args.io_delay)

    expected_scores = args.perfs * args.judges * args.criteria * 2
    print(f"Сидим бенч-событие: {args.perfs} выступлений × {args.judges} судей × "
          f"{args.criteria*2} критериев = ~{expected_scores} оценок…")
    t0 = time.perf_counter()
    event_id = _seed_event(args.perfs, args.judges, args.criteria)
    print(f"  готово за {time.perf_counter()-t0:.2f}s, event_id={event_id}\n")

    print("Замеряю пересчёт итогов:")
    seq = _bench("sequential", calculate_event_results_sequential, event_id)
    par = _bench(f"parallel (workers={args.workers})", calculate_event_results_parallel, event_id, args.workers)

    speedup = seq / par if par > 0 else float("inf")
    print(f"\n  Ускорение: x{speedup:.2f}")

    rows_seq = calculate_event_results_sequential(event_id)
    rows_par = calculate_event_results_parallel(event_id, max_workers=args.workers)
    same = [(a["id"], a["final"]) for a in rows_seq] == [(b["id"], b["final"]) for b in rows_par]
    print(f"  Результаты совпадают: {'да' if same else 'НЕТ — баг!'}")
    print(f"  Топ-3:")
    for r in rows_par[:3]:
        print(f"    {r['place']}. {r['name']:10}  тех={r['technical']:.2f}  арт={r['artistic']:.2f}  итог={r['final']:.2f}")

    if args.keep:
        print(f"\nСобытие {event_id} оставлено (--keep).")
    else:
        _drop_event(event_id)
        print(f"\nВременное событие {event_id} удалено.")


if __name__ == "__main__":
    main()
