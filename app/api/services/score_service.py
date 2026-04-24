"""CRUD для оценок (унифицированная таблица scores)."""
from decimal import Decimal
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Criterion, Performance, Score


def upsert_score(
    db: Session,
    judge_id: int,
    performance_id: int,
    criterion_id: int,
    value: Decimal,
) -> Score:
    """
    Создаёт оценку, либо обновляет уже существующую для пары
    (judge, performance, criterion). Это позволяет кнопке «изменить»
    в форме подтверждения корректно переписывать значение, а двойной
    клик не падает с уникальным конфликтом.

    id_event подтягивается из performance — клиенту его передавать не нужно
    и нельзя (иначе судья сможет записать оценку «не в то событие»).
    """
    performance = db.query(Performance).filter(
        Performance.id_performance == performance_id
    ).first()
    if performance is None:
        raise HTTPException(status_code=404, detail="Performance not found")

    criterion = db.query(Criterion).filter(
        Criterion.id_criterion == criterion_id
    ).first()
    if criterion is None:
        raise HTTPException(status_code=404, detail="Criterion not found")

    if criterion.id_event != performance.id_event:
        raise HTTPException(
            status_code=400,
            detail="Criterion does not belong to the performance's event",
        )

    if value < 0 or value > criterion.start_point:
        raise HTTPException(
            status_code=400,
            detail=f"Value must be in [0, {criterion.start_point}]",
        )

    existing = db.query(Score).filter(
        Score.id_judge == judge_id,
        Score.id_performance == performance_id,
        Score.id_criterion == criterion_id,
    ).first()

    if existing is not None:
        existing.value = value
        db.commit()
        db.refresh(existing)
        return existing

    score = Score(
        id_event=performance.id_event,
        id_judge=judge_id,
        id_performance=performance_id,
        id_criterion=criterion_id,
        value=value,
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


def get_scores_by_performance(db: Session, performance_id: int) -> List[Score]:
    return db.query(Score).filter(Score.id_performance == performance_id).all()


def get_scores_by_judge(db: Session, judge_id: int) -> List[Score]:
    return db.query(Score).filter(Score.id_judge == judge_id).all()
