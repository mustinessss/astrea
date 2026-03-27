from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import ScoresArtFaf, ScoresTechFaf, ScoresArtNaf, ScoresTechNaf
from app.schemas.score import (
    ScoresArtFafCreate, ScoresArtFafResponse,
    ScoresTechFafCreate, ScoresTechFafResponse,
    ScoresArtNafCreate, ScoresArtNafResponse,
    ScoresTechNafCreate, ScoresTechNafResponse
)

router = APIRouter(tags=["scores"])


# ==================== ФАФ АРТИСТИКА ====================
@router.get("/scores/art/faf", response_model=List[ScoresArtFafResponse])
def get_art_faf_scores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all ФАФ artistry scores"""
    scores = db.query(ScoresArtFaf).offset(skip).limit(limit).all()
    return scores


@router.get("/scores/art/faf/performance/{performance_id}", response_model=List[ScoresArtFafResponse])
def get_art_faf_scores_by_performance(performance_id: int, db: Session = Depends(get_db)):
    """Get ФАФ artistry scores for a performance"""
    scores = db.query(ScoresArtFaf).filter(ScoresArtFaf.id_performance == performance_id).all()
    return scores


@router.post("/scores/art/faf", response_model=ScoresArtFafResponse)
def create_art_faf_score(score: ScoresArtFafCreate, db: Session = Depends(get_db)):
    """Create new ФАФ artistry score"""
    db_score = ScoresArtFaf(**score.dict())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


@router.put("/scores/art/faf/{score_id}", response_model=ScoresArtFafResponse)
def update_art_faf_score(score_id: int, score: ScoresArtFafCreate, db: Session = Depends(get_db)):
    """Update ФАФ artistry score"""
    db_score = db.query(ScoresArtFaf).filter(ScoresArtFaf.id_scores_art_faf == score_id).first()
    if not db_score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    for field, value in score.dict().items():
        setattr(db_score, field, value)
    
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


# ==================== ФАФ ТЕХНИКА ====================
@router.get("/scores/tech/faf", response_model=List[ScoresTechFafResponse])
def get_tech_faf_scores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all ФАФ technical scores"""
    scores = db.query(ScoresTechFaf).offset(skip).limit(limit).all()
    return scores


@router.get("/scores/tech/faf/performance/{performance_id}", response_model=List[ScoresTechFafResponse])
def get_tech_faf_scores_by_performance(performance_id: int, db: Session = Depends(get_db)):
    """Get ФАФ technical scores for a performance"""
    scores = db.query(ScoresTechFaf).filter(ScoresTechFaf.id_performance == performance_id).all()
    return scores


@router.post("/scores/tech/faf", response_model=ScoresTechFafResponse)
def create_tech_faf_score(score: ScoresTechFafCreate, db: Session = Depends(get_db)):
    """Create new ФАФ technical score"""
    db_score = ScoresTechFaf(**score.dict())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


@router.put("/scores/tech/faf/{score_id}", response_model=ScoresTechFafResponse)
def update_tech_faf_score(score_id: int, score: ScoresTechFafCreate, db: Session = Depends(get_db)):
    """Update ФАФ technical score"""
    db_score = db.query(ScoresTechFaf).filter(ScoresTechFaf.id_scores_tech_faf == score_id).first()
    if not db_score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    for field, value in score.dict().items():
        setattr(db_score, field, value)
    
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


# ==================== НАФ АРТИСТИКА ====================
@router.get("/scores/art/naf", response_model=List[ScoresArtNafResponse])
def get_art_naf_scores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all НАФ artistry scores"""
    scores = db.query(ScoresArtNaf).offset(skip).limit(limit).all()
    return scores


@router.get("/scores/art/naf/performance/{performance_id}", response_model=List[ScoresArtNafResponse])
def get_art_naf_scores_by_performance(performance_id: int, db: Session = Depends(get_db)):
    """Get НАФ artistry scores for a performance"""
    scores = db.query(ScoresArtNaf).filter(ScoresArtNaf.id_performance == performance_id).all()
    return scores


@router.post("/scores/art/naf", response_model=ScoresArtNafResponse)
def create_art_naf_score(score: ScoresArtNafCreate, db: Session = Depends(get_db)):
    """Create new НАФ artistry score"""
    db_score = ScoresArtNaf(**score.dict())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


@router.put("/scores/art/naf/{score_id}", response_model=ScoresArtNafResponse)
def update_art_naf_score(score_id: int, score: ScoresArtNafCreate, db: Session = Depends(get_db)):
    """Update НАФ artistry score"""
    db_score = db.query(ScoresArtNaf).filter(ScoresArtNaf.id_scores_art_naf == score_id).first()
    if not db_score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    for field, value in score.dict().items():
        setattr(db_score, field, value)
    
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


# ==================== НАФ ТЕХНИКА ====================
@router.get("/scores/tech/naf", response_model=List[ScoresTechNafResponse])
def get_tech_naf_scores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all НАФ technical scores"""
    scores = db.query(ScoresTechNaf).offset(skip).limit(limit).all()
    return scores


@router.get("/scores/tech/naf/performance/{performance_id}", response_model=List[ScoresTechNafResponse])
def get_tech_naf_scores_by_performance(performance_id: int, db: Session = Depends(get_db)):
    """Get НАФ technical scores for a performance"""
    scores = db.query(ScoresTechNaf).filter(ScoresTechNaf.id_performance == performance_id).all()
    return scores


@router.post("/scores/tech/naf", response_model=ScoresTechNafResponse)
def create_tech_naf_score(score: ScoresTechNafCreate, db: Session = Depends(get_db)):
    """Create new НАФ technical score"""
    db_score = ScoresTechNaf(**score.dict())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


@router.put("/scores/tech/naf/{score_id}", response_model=ScoresTechNafResponse)
def update_tech_naf_score(score_id: int, score: ScoresTechNafCreate, db: Session = Depends(get_db)):
    """Update НАФ technical score"""
    db_score = db.query(ScoresTechNaf).filter(ScoresTechNaf.id_scores_tech_naf == score_id).first()
    if not db_score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    for field, value in score.dict().items():
        setattr(db_score, field, value)
    
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score
