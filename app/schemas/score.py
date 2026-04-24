from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ScoreCreate(BaseModel):
    """
    id_event сознательно не принимается — он подтягивается на бэке из
    performance, чтобы судья не мог записать оценку «не в то событие».
    Диапазон значения проверяется на бэке против criterion.start_point.
    """
    id_performance: int
    id_criterion: int
    value: Decimal = Field(..., ge=0)


class ScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_scores: int
    id_event: int
    id_judge: int
    id_performance: int
    id_criterion: int
    value: Decimal
