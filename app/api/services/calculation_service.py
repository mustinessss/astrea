"""Подсчёт итогового балла за выступление.

Финалка = средний технический балл + средний артистический балл.
В таске 4 этот же модуль распараллеливается через ThreadPoolExecutor для
пересчёта итогов по всему событию.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Criterion, Score


def _avg_for_judge_type(db: Session, performance_id: int, judge_type: str) -> float:
    """Среднее по всем оценкам выступления, чьи критерии относятся к judge_type."""
    avg = (
        db.query(func.avg(Score.value))
        .join(Criterion, Score.id_criterion == Criterion.id_criterion)
        .filter(
            Score.id_performance == performance_id,
            Criterion.judge_type == judge_type,
        )
        .scalar()
    )
    return float(avg) if avg is not None else 0.0


def calculate_performance_score(db: Session, performance_id: int) -> dict:
    technical = _avg_for_judge_type(db, performance_id, "technical")
    artistic = _avg_for_judge_type(db, performance_id, "artistry")
    return {
        "technical_score": round(technical, 2),
        "artistic_score": round(artistic, 2),
        "final_score": round(technical + artistic, 2),
    }
