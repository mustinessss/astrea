from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import Team
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=List[TeamResponse])
def get_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all teams"""
    teams = db.query(Team).offset(skip).limit(limit).all()
    return teams


@router.get("/{team_name}", response_model=TeamResponse)
def get_team(team_name: str, db: Session = Depends(get_db)):
    """Get team by name"""
    team = db.query(Team).filter(Team.team_name == team_name).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    """Create new team"""
    # Check if team already exists
    existing_team = db.query(Team).filter(Team.team_name == team.team_name).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team already exists")
    
    db_team = Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.put("/{team_name}", response_model=TeamResponse)
def update_team(team_name: str, team: TeamUpdate, db: Session = Depends(get_db)):
    """Update team"""
    db_team = db.query(Team).filter(Team.team_name == team_name).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    update_data = team.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_team, field, value)
    
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.delete("/{team_name}")
def delete_team(team_name: str, db: Session = Depends(get_db)):
    """Delete team"""
    db_team = db.query(Team).filter(Team.team_name == team_name).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db.delete(db_team)
    db.commit()
    return {"message": "Team deleted"}
