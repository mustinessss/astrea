from pydantic import BaseModel, Field

class ScoreCreate(BaseModel):
    performance_id: int
    criterion_id: int
    value: float = Field(..., ge=0, le=10)  # ограничение

class ScoreResponse(BaseModel):
    id_score: int
    performance_id: int
    criterion_id: int
    judge_id: int
    value: float

    class Config:
        from_attributes = True