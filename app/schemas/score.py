from pydantic import BaseModel
from typing import Optional


# ==================== ФАФ Артистика ====================
class ScoresArtFafBase(BaseModel):
    """Базовая схема оценок по артистике ФАФ"""
    id_human: int
    id_performance: int
    criterion_1: Optional[int] = None
    criterion_2: Optional[int] = None
    criterion_3: Optional[int] = None
    criterion_4: Optional[int] = None
    criterion_5: Optional[int] = None
    criterion_6: Optional[int] = None
    criterion_7: Optional[int] = None
    criterion_8: Optional[int] = None
    criterion_9: Optional[int] = None
    criterion_10: Optional[int] = None
    criterion_11: Optional[int] = None
    criterion_12: Optional[int] = None
    criterion_13: Optional[int] = None


class ScoresArtFafCreate(ScoresArtFafBase):
    """Схема для создания оценок по артистике ФАФ"""
    pass


class ScoresArtFafResponse(ScoresArtFafBase):
    """Схема для ответа об оценках по артистике ФАФ"""
    id_scores_art_faf: int

    class Config:
        from_attributes = True


# ==================== ФАФ Техника ====================
class ScoresTechFafBase(BaseModel):
    """Базовая схема оценок по технике ФАФ"""
    id_human: int
    id_performance: int
    criterion_1_1: Optional[int] = None
    criterion_1_2: Optional[int] = None
    criterion_1_3: Optional[int] = None
    criterion_1_4: Optional[int] = None
    criterion_1_5: Optional[int] = None
    criterion_2_1: Optional[int] = None
    criterion_2_2: Optional[int] = None
    criterion_2_3: Optional[int] = None
    criterion_3_1: Optional[int] = None
    criterion_3_2: Optional[int] = None
    criterion_3_3: Optional[int] = None
    criterion_3_4: Optional[int] = None
    criterion_3_5: Optional[int] = None
    criterion_3_6: Optional[int] = None
    criterion_3_7: Optional[int] = None
    criterion_3_8: Optional[int] = None


class ScoresTechFafCreate(ScoresTechFafBase):
    """Схема для создания оценок по технике ФАФ"""
    pass


class ScoresTechFafResponse(ScoresTechFafBase):
    """Схема для ответа об оценках по технике ФАФ"""
    id_scores_tech_faf: int

    class Config:
        from_attributes = True


# ==================== НАФ Артистика ====================
class ScoresArtNafBase(BaseModel):
    """Базовая схема оценок по артистике НАФ"""
    id_human: int
    id_performance: int
    criterion_1: Optional[float] = None
    criterion_2: Optional[float] = None
    criterion_3: Optional[float] = None
    criterion_4: Optional[float] = None
    criterion_5: Optional[float] = None
    criterion_6: Optional[float] = None
    criterion_7: Optional[float] = None
    criterion_8: Optional[float] = None
    criterion_9: Optional[float] = None
    criterion_10: Optional[float] = None
    criterion_11: Optional[float] = None
    criterion_12: Optional[float] = None
    criterion_13: Optional[float] = None


class ScoresArtNafCreate(ScoresArtNafBase):
    """Схема для создания оценок по артистике НАФ"""
    pass


class ScoresArtNafResponse(ScoresArtNafBase):
    """Схема для ответа об оценках по артистике НАФ"""
    id_scores_art_naf: int

    class Config:
        from_attributes = True


# ==================== НАФ Техника ====================
class ScoresTechNafBase(BaseModel):
    """Базовая схема оценок по технике НАФ"""
    id_human: int
    id_performance: int
    criterion_1_1: Optional[float] = None
    criterion_1_2: Optional[float] = None
    criterion_1_3: Optional[float] = None
    criterion_1_4: Optional[float] = None
    criterion_1_5: Optional[float] = None
    criterion_2_1: Optional[float] = None
    criterion_2_2: Optional[float] = None
    criterion_2_3: Optional[float] = None
    criterion_3_1: Optional[float] = None
    criterion_3_2: Optional[float] = None
    criterion_3_3: Optional[float] = None
    criterion_3_4: Optional[float] = None
    criterion_3_5: Optional[float] = None
    criterion_3_6: Optional[float] = None
    criterion_3_7: Optional[float] = None
    criterion_3_8: Optional[float] = None


class ScoresTechNafCreate(ScoresTechNafBase):
    """Схема для создания оценок по технике НАФ"""
    pass


class ScoresTechNafResponse(ScoresTechNafBase):
    """Схема для ответа об оценках по технике НАФ"""
    id_scores_tech_naf: int

    class Config:
        from_attributes = True
