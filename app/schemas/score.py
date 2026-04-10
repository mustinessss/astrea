
from pydantic import BaseModel

class ScoreCreate(BaseModel):
    id_performance: int
    id_criteria: int
    value: float