from typing import Optional
import datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Chronometric(Base):
    __tablename__ = 'chronometric'
    __table_args__ = (
        PrimaryKeyConstraint('id_chronometric', name='chronometric_pk'),
    )

    id_chronometric: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1), primary_key=True)
    total_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    time_fencing: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, ForeignKey('performance.id_performance', ondelete='CASCADE'), nullable=False)
    id_human: Mapped[int] = mapped_column(Integer, ForeignKey('human.id'), nullable=False)


class Event(Base):
    __tablename__ = 'event'
    __table_args__ = (
        PrimaryKeyConstraint('id_event', name='event_pk'),
    )

    id_event: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1), primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    name_event: Mapped[Optional[str]] = mapped_column(String(200))


class Human(Base):
    __tablename__ = 'human'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='human_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    patronymic: Mapped[Optional[str]] = mapped_column(String)


class HumanEvent(Base):
    __tablename__ = 'human_event'
    __table_args__ = (
        CheckConstraint(
            "another_role::text = ANY (ARRAY['main_judge'::character varying, 'volunteer'::character varying, 'medic'::character varying]::text[])",
            name='human_event_another_role_check',
        ),
        CheckConstraint(
            "judge_type::text = ANY (ARRAY['technical'::character varying, 'artistry'::character varying, 'timekeeper'::character varying]::text[])",
            name='human_event_judge_type_check',
        ),
        PrimaryKeyConstraint('id_human_event', name='human_event_pk'),
        UniqueConstraint('access_code', name='human_event_access_code_key'),
    )

    id_human_event: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1), primary_key=True)
    id_human: Mapped[int] = mapped_column(Integer, ForeignKey('human.id', ondelete='CASCADE'), nullable=False)
    id_event: Mapped[int] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'), nullable=False)
    role_event: Mapped[str] = mapped_column(String, nullable=False)
    access_code: Mapped[Optional[str]] = mapped_column(String(50))
    judge_type: Mapped[Optional[str]] = mapped_column(String(20))
    another_role: Mapped[Optional[str]] = mapped_column(String(20))


class HumanPerformance(Base):
    __tablename__ = 'human_performance'
    __table_args__ = (
        PrimaryKeyConstraint('id_human_performance', name='human_performance_pk'),
    )

    id_human_performance: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String, nullable=False)
    id_human: Mapped[int] = mapped_column(Integer, ForeignKey('human.id', ondelete='CASCADE'), nullable=False)


class HumanTeam(Base):
    __tablename__ = 'human_team'
    __table_args__ = (
        PrimaryKeyConstraint('id_human_team', name='human_team_pk'),
    )

    id_human_team: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1), primary_key=True)
    id_human: Mapped[int] = mapped_column(Integer, ForeignKey('human.id', ondelete='CASCADE'), nullable=False)
    id_team: Mapped[str] = mapped_column(String, ForeignKey('team.team_name', ondelete='CASCADE'), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)


class Performance(Base):
    __tablename__ = 'performance'
    __table_args__ = (
        PrimaryKeyConstraint('id_performance', name='performance_pk'),
        CheckConstraint("discipline IN ('Соло', 'Дуэль', 'Группа', 'Ансамбль')", name='performance_discipline_check'),
    )

    id_performance: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1), primary_key=True)
    performance_name: Mapped[str] = mapped_column(String, nullable=False)
    discipline: Mapped[str] = mapped_column(String, nullable=False)
    id_event: Mapped[int] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'), nullable=False)


class Team(Base):
    __tablename__ = 'team'
    __table_args__ = (
        PrimaryKeyConstraint('team_name', name='team_pk'),
    )

    id_team: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1), nullable=False)
    team_name: Mapped[str] = mapped_column(String, primary_key=True)
    team_city: Mapped[str] = mapped_column(String, nullable=False)


class Judge(Base):
    """Учетные данные судей"""
    __tablename__ = 'judge'
    __table_args__ = (
        PrimaryKeyConstraint('id_judge', name='judge_pk'),
        UniqueConstraint('email', name='judge_email_unique'),
        UniqueConstraint('access_code', name='judge_access_code_unique'),
        CheckConstraint(
            "role::text = ANY (ARRAY['judge'::character varying, 'main_judge'::character varying, 'technical'::character varying, 'artistry'::character varying, 'timekeeper'::character varying, 'volunteer'::character varying, 'medic'::character varying]::text[])",
            name='judge_role_check',
        ),
    )

    id_judge: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1), primary_key=True)
    id_human: Mapped[int] = mapped_column(Integer, ForeignKey('human.id', ondelete='CASCADE'), nullable=False)
    id_event: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'))
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    access_code: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(nullable=False, default=datetime.datetime.utcnow)
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column()


class Criterion(Base):
    """
    Унифицированный справочник критериев. Раньше было 4 отдельных таблицы
    (criterion_art_faf / art_naf / tech_faf / tech_naf), теперь — одна.

    judge_type — кто этот критерий выставляет ('technical' / 'artistry' /
    в будущем что угодно). Сама система (ФАФ/НАФ/кастом) определяется
    набором критериев конкретного события (id_event).

    start_point — верхняя граница шкалы (например 10.0 для ФАФ, 1.0 / 2.0 для НАФ).
    step        — шаг выставления оценки (0.5 для ФАФ, 0.1 для НАФ — наполняется в populate_criteria).
    """
    __tablename__ = 'criterion'
    __table_args__ = (
        PrimaryKeyConstraint('id_criterion', name='criterion_pk'),
    )

    id_criterion: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1), primary_key=True)
    name_criterion: Mapped[str] = mapped_column(String, nullable=False)
    start_point: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    step: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.5)
    id_event: Mapped[int] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'), nullable=False)
    judge_type: Mapped[str] = mapped_column(String(20), nullable=False)


class Score(Base):
    """
    Унифицированная таблица оценок. Раньше было 4 отдельных таблицы
    (scores_art_faf / art_naf / tech_faf / tech_naf), теперь — одна.

    Одна строка = один балл, выставленный конкретным судьёй конкретному
    выступлению по конкретному критерию.

    UNIQUE на (id_judge, id_performance, id_criterion) на уровне БД сознательно
    не ставится: UI защищает от дублей, а сервис делает upsert (см. score_service.py),
    чтобы кнопка «изменить» в подтверждении могла переписать существующую оценку.
    """
    __tablename__ = 'scores'
    __table_args__ = (
        PrimaryKeyConstraint('id_scores', name='scores_pk'),
    )

    id_scores: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1), primary_key=True)
    id_event: Mapped[int] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'), nullable=False)
    id_judge: Mapped[int] = mapped_column(Integer, ForeignKey('judge.id_judge', ondelete='CASCADE'), nullable=False)
    id_criterion: Mapped[int] = mapped_column(Integer, ForeignKey('criterion.id_criterion', ondelete='CASCADE'), nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, ForeignKey('performance.id_performance', ondelete='CASCADE'), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
