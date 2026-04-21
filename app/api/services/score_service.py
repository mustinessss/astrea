from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.models import Score


def create_score(db, judge_id, performance_id, criterion_id, value):

    existing = db.query(Score).filter(
        Score.id_judge == judge_id,
        Score.id_performance == performance_id,
        Score.id_criterion == criterion_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Score already exists")

    score = Score(
        id_judge=judge_id,
        id_performance=performance_id,
        id_criterion=criterion_id,
        value=value
    )

    db.add(score)
    db.commit()
    db.refresh(score)

    return score


def get_scores_by_performance(db: Session, performance_id: int):
    return db.query(Score).filter(
        Score.id_performance == performance_id
    ).all()