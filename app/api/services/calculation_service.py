from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import Score, Judge


def calculate_performance_score(db: Session, performance_id: int):

    # --- средняя по техническим судьям ---
    tech_avg = db.query(func.avg(Score.value))\
        .join(Judge, Score.id_judge == Judge.id_judge)\
        .filter(
            Score.id_performance == performance_id,
            Judge.role == "technical"
        ).scalar()

    # --- средняя по артистическим судьям ---
    art_avg = db.query(func.avg(Score.value))\
        .join(Judge, Score.id_judge == Judge.id_judge)\
        .filter(
            Score.id_performance == performance_id,
            Judge.role == "artistry"
        ).scalar()

    tech_avg = tech_avg or 0
    art_avg = art_avg or 0

    return {
        "technical_score": round(tech_avg, 2),
        "artistic_score": round(art_avg, 2),
        "final_score": round(tech_avg + art_avg, 2)
    }