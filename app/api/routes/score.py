from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.services.score_service import get_scores_by_performance, upsert_score
from app.core.auth import get_current_judge
from app.db.database import get_db
from app.schemas.score import ScoreCreate, ScoreResponse

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("/", response_model=ScoreResponse)
def create_or_update_score(
    data: ScoreCreate,
    db: Session = Depends(get_db),
    current_judge: dict = Depends(get_current_judge),
):
    return upsert_score(
        db=db,
        judge_id=int(current_judge["user_id"]),
        performance_id=data.id_performance,
        criterion_id=data.id_criterion,
        value=data.value,
    )


@router.get("/performance/{performance_id}", response_model=list[ScoreResponse])
def list_scores_for_performance(performance_id: int, db: Session = Depends(get_db)):
    return get_scores_by_performance(db, performance_id)
