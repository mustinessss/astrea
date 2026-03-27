from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import Human
from app.schemas.human import HumanCreate, HumanUpdate, HumanResponse

router = APIRouter(prefix="/humans", tags=["humans"])


@router.get("", response_model=List[HumanResponse])
def get_humans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all humans"""
    humans = db.query(Human).offset(skip).limit(limit).all()
    return humans


@router.get("/{human_id}", response_model=HumanResponse)
def get_human(human_id: int, db: Session = Depends(get_db)):
    """Get human by ID"""
    human = db.query(Human).filter(Human.id == human_id).first()
    if not human:
        raise HTTPException(status_code=404, detail="Human not found")
    return human


@router.post("", response_model=HumanResponse)
def create_human(human: HumanCreate, db: Session = Depends(get_db)):
    """Create new human"""
    db_human = Human(**human.dict())
    db.add(db_human)
    db.commit()
    db.refresh(db_human)
    return db_human


@router.put("/{human_id}", response_model=HumanResponse)
def update_human(human_id: int, human: HumanUpdate, db: Session = Depends(get_db)):
    """Update human"""
    db_human = db.query(Human).filter(Human.id == human_id).first()
    if not db_human:
        raise HTTPException(status_code=404, detail="Human not found")
    
    update_data = human.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_human, field, value)
    
    db.add(db_human)
    db.commit()
    db.refresh(db_human)
    return db_human


@router.delete("/{human_id}")
def delete_human(human_id: int, db: Session = Depends(get_db)):
    """Delete human"""
    db_human = db.query(Human).filter(Human.id == human_id).first()
    if not db_human:
        raise HTTPException(status_code=404, detail="Human not found")
    
    db.delete(db_human)
    db.commit()
    return {"message": "Human deleted"}
