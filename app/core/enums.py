"""Enum для ролей судей"""
from enum import Enum


class JudgeRole(str, Enum):
    """Допустимые роли судей"""
    JUDGE = "judge"
    MAIN_JUDGE = "main_judge"
    TECHNICAL = "technical"
    ARTISTRY = "artistry"
    TIMEKEEPER = "timekeeper"
    VOLUNTEER = "volunteer"
    MEDIC = "medic"
    ADMIN = "admin"
    
    class Config:
        use_enum_values = True
