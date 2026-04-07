from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import Event, Performance
from app.schemas.event import EventCreate, EventUpdate, EventResponse, PerformanceCreate, PerformanceUpdate, PerformanceResponse

router = APIRouter(tags=["events"])


# ==================== EVENT ROUTES ====================
@router.get("/events", response_model=List[EventResponse])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all events"""
    events = db.query(Event).offset(skip).limit(limit).all()
    return events


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event by ID"""
    event = db.query(Event).filter(Event.id_event == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events", response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create new event"""
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event: EventUpdate, db: Session = Depends(get_db)):
    """Update event"""
    db_event = db.query(Event).filter(Event.id_event == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete event"""
    db_event = db.query(Event).filter(Event.id_event == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(db_event)
    db.commit()
    return {"message": "Event deleted"}


# ==================== PERFORMANCE ROUTES ====================
@router.get("/events/{event_id}/performances", response_model=List[PerformanceResponse])
def get_performances(event_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all performances for an event"""
    performances = db.query(Performance).filter(
        Performance.id_event == event_id
    ).offset(skip).limit(limit).all()
    return performances


@router.get("/performances/{performance_id}", response_model=PerformanceResponse)
def get_performance(performance_id: int, db: Session = Depends(get_db)):
    """Get performance by ID"""
    performance = db.query(Performance).filter(Performance.id_performance == performance_id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    return performance


@router.post("/events/{event_id}/performances", response_model=PerformanceResponse)
def create_performance(event_id: int, performance: PerformanceCreate, db: Session = Depends(get_db)):
    """Create new performance"""
    # Check if event exists
    event = db.query(Event).filter(Event.id_event == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    performance_data = performance.dict()
    performance_data['id_event'] = event_id
    db_performance = Performance(**performance_data)
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)
    return db_performance


@router.put("/performances/{performance_id}", response_model=PerformanceResponse)
def update_performance(performance_id: int, performance: PerformanceUpdate, db: Session = Depends(get_db)):
    """Update performance"""
    db_performance = db.query(Performance).filter(Performance.id_performance == performance_id).first()
    if not db_performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    
    update_data = performance.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_performance, field, value)
    
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)
    return db_performance


@router.delete("/performances/{performance_id}")
def delete_performance(performance_id: int, db: Session = Depends(get_db)):
    """Delete performance"""
    db_performance = db.query(Performance).filter(Performance.id_performance == performance_id).first()
    if not db_performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    
    db.delete(db_performance)
    db.commit()
    return {"message": "Performance deleted"}
