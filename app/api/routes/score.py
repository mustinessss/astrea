from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.services.score_service import create_score, get_scores_by_performance
from app.schemas.score import ScoreCreate, ScoreResponse
from app.core.auth import get_current_judge

router = APIRouter(prefix="/scores", tags=["scores"])   

@router.post("/", response_model=ScoreResponse)
def create_score_route(
    data: ScoreCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_judge)  
):
    return create_score(
        db=db,
        judge_id=current_user.id,  
        performance_id=data.performance_id,
        criterion_id=data.criterion_id,
        value=data.value
    )

@router.get("/performance/{performance_id}", response_model=list[ScoreResponse])
def get_scores(performance_id: int, db: Session = Depends(get_db)):
    return get_scores_by_performance(db, performance_id)