"""Тесты на расчёт итогов выступления и события."""
from decimal import Decimal

from app.api.services.calculation_service import calculate_performance_score
from app.api.services.event_calc import (
    calculate_event_results_parallel,
    calculate_event_results_sequential,
)
from app.api.services.score_service import upsert_score
from app.db.database import SessionLocal


def test_final_score_is_sum_of_avg_technical_and_avg_artistry(env):
    """Итог = средний тех + средний арт. Считаем ровно по judge_type критерия."""
    db = SessionLocal()
    try:
        # Технический судья ставит 8.0 по тех-критерию
        upsert_score(db, env["judge_tech_id"], env["performance_id"],
                     env["criterion_tech_id"], Decimal("8.0"))
        # Артистический судья ставит 6.0 по арт-критерию
        upsert_score(db, env["judge_art_id"], env["performance_id"],
                     env["criterion_art_id"], Decimal("6.0"))

        res = calculate_performance_score(db, env["performance_id"])
        assert res["technical_score"] == 8.0
        assert res["artistic_score"] == 6.0
        assert res["final_score"] == 14.0
    finally:
        db.close()


def test_parallel_and_sequential_event_results_match(env):
    """Многопоточная и однопоточная версии обязаны давать одинаковый результат."""
    db = SessionLocal()
    try:
        upsert_score(db, env["judge_tech_id"], env["performance_id"],
                     env["criterion_tech_id"], Decimal("7.5"))
        upsert_score(db, env["judge_art_id"], env["performance_id"],
                     env["criterion_art_id"], Decimal("8.5"))
    finally:
        db.close()

    seq = calculate_event_results_sequential(env["event_id"])
    par = calculate_event_results_parallel(env["event_id"], max_workers=4)

    assert len(seq) == len(par) == 1
    assert seq[0]["final"] == par[0]["final"] == 16.0
    assert seq[0]["place"] == par[0]["place"] == 1
