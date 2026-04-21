from typing import Optional
import datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Chronometric(Base):
    __tablename__ = 'chronometric'
    __table_args__ = (
        PrimaryKeyConstraint('id_chronometric', name='chronometric_pk'),
    )

    id_chronometric: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    total_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    time_fencing: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, ForeignKey('performance.id_performance', ondelete='CASCADE'), nullable=False)
    id_human: Mapped[int] = mapped_column(Integer, ForeignKey('human.id'), nullable=False)


class Event(Base):
    __tablename__ = 'event'
    __table_args__ = (
        PrimaryKeyConstraint('id_event', name='event_pk'),
    )

    id_event: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
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
        CheckConstraint("another_role::text = ANY (ARRAY['main_judge'::character varying, 'volunteer'::character varying, 'medic'::character varying]::text[])", name='human_event_another_role_check'),
        CheckConstraint("judge_type::text = ANY (ARRAY['technical'::character varying, 'artistry'::character varying, 'timekeeper'::character varying]::text[])", name='human_event_judge_type_check'),
        PrimaryKeyConstraint('id_human_event', name='human_event_pk'),
        UniqueConstraint('access_code', name='human_event_access_code_key')
    )

    id_human_event: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
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

    id_human_team: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_human: Mapped[int] = mapped_column(Integer, ForeignKey('human.id', ondelete='CASCADE'), nullable=False)
    id_team: Mapped[str] = mapped_column(String, ForeignKey('team.team_name', ondelete='CASCADE'), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)


class CriterionArtFaf(Base):
    """
    Справочник критериев артистических оценок ФАФ
    """
    __tablename__ = 'criterion_art_faf'
    __table_args__ = (
        PrimaryKeyConstraint('id_criterion_art_faf', name='criterion_art_faf_pk'),
        UniqueConstraint('criterion_number', name='criterion_art_faf_number_unique'),
    )

    id_criterion_art_faf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    criterion_number: Mapped[int] = mapped_column(Integer, nullable=False)
    criterion_name: Mapped[str] = mapped_column(String, nullable=False)
    min_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_value: Mapped[int] = mapped_column(Integer, nullable=False, default=10)


class CriterionArtNaf(Base):
    """
    Справочник критериев артистических оценок НАФ
    """
    __tablename__ = 'criterion_art_naf'
    __table_args__ = (
        PrimaryKeyConstraint('id_criterion_art_naf', name='criterion_art_naf_pk'),
        UniqueConstraint('criterion_number', name='criterion_art_naf_number_unique'),
    )

    id_criterion_art_naf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    criterion_number: Mapped[int] = mapped_column(Integer, nullable=False)
    criterion_name: Mapped[str] = mapped_column(String, nullable=False)
    min_value: Mapped[float] = mapped_column(Numeric(precision=3, scale=2), nullable=False, default=0.0)
    max_value: Mapped[float] = mapped_column(Numeric(precision=3, scale=2), nullable=False, default=1.0)


class CriterionTechFaf(Base):
    """
    Справочник критериев технических оценок ФАФ
    """
    __tablename__ = 'criterion_tech_faf'
    __table_args__ = (
        PrimaryKeyConstraint('id_criterion_tech_faf', name='criterion_tech_faf_pk'),
        UniqueConstraint('criterion_number', name='criterion_tech_faf_number_unique'),
    )

    id_criterion_tech_faf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    criterion_number: Mapped[int] = mapped_column(Integer, nullable=False)
    criterion_name: Mapped[str] = mapped_column(String, nullable=False)
    min_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_value: Mapped[int] = mapped_column(Integer, nullable=False, default=10)


class CriterionTechNaf(Base):
    """
    Справочник критериев технических оценок НАФ
    """
    __tablename__ = 'criterion_tech_naf'
    __table_args__ = (
        PrimaryKeyConstraint('id_criterion_tech_naf', name='criterion_tech_naf_pk'),
        UniqueConstraint('criterion_number', name='criterion_tech_naf_number_unique'),
    )

    id_criterion_tech_naf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    criterion_number: Mapped[int] = mapped_column(Integer, nullable=False)
    criterion_name: Mapped[str] = mapped_column(String, nullable=False)
    min_value: Mapped[float] = mapped_column(Numeric(precision=3, scale=2), nullable=False, default=0.0)
    max_value: Mapped[float] = mapped_column(Numeric(precision=3, scale=2), nullable=False, default=1.0)


class Performance(Base):
    __tablename__ = 'performance'
    __table_args__ = (
        PrimaryKeyConstraint('id_performance', name='performance_pk'),
        CheckConstraint("discipline IN ('Соло', 'Дуэль', 'Группа', 'Ансамбль')", name='performance_discipline_check'),
    )

    id_performance: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    performance_name: Mapped[str] = mapped_column(String, nullable=False)
    discipline: Mapped[str] = mapped_column(String, nullable=False)
    id_event: Mapped[int] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'), nullable=False)


class ScoresArtFaf(Base):
    """
    Оценки по артистике в системе ФАФ
    Нормализованная структура: id_score, id_event, id_judge, id_criterion, score
    """
    __tablename__ = 'scores_art_faf'
    __table_args__ = (
        PrimaryKeyConstraint('id_scores_art_faf', name='scores_art_faf_pk'),
        CheckConstraint('score >= 0 AND score <= 10', name='scores_art_faf_score_check'),
    )

    id_scores_art_faf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_event: Mapped[int] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'), nullable=False)
    id_judge: Mapped[int] = mapped_column(Integer, ForeignKey('judge.id_judge', ondelete='CASCADE'), nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, ForeignKey('performance.id_performance', ondelete='CASCADE'), nullable=False)
    id_criterion: Mapped[int] = mapped_column(Integer, ForeignKey('criterion_art_faf.id_criterion_art_faf', ondelete='CASCADE'), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)


class ScoresArtNaf(Base):
    """
    Оценки по артистике в системе НАФ
    Нормализованная структура: id_score, id_event, id_judge, id_criterion, score
    """
    __tablename__ = 'scores_art_naf'
    __table_args__ = (
        PrimaryKeyConstraint('id_scores_art_naf', name='scores_art_naf_pk'),
        CheckConstraint('score >= 0 AND score <= 1', name='scores_art_naf_score_check'),
    )

    id_scores_art_naf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_event: Mapped[int] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'), nullable=False)
    id_judge: Mapped[int] = mapped_column(Integer, ForeignKey('judge.id_judge', ondelete='CASCADE'), nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, ForeignKey('performance.id_performance', ondelete='CASCADE'), nullable=False)
    id_criterion: Mapped[int] = mapped_column(Integer, ForeignKey('criterion_art_naf.id_criterion_art_naf', ondelete='CASCADE'), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(precision=3, scale=2), nullable=False)


class ScoresTechFaf(Base):
    """
    Оценки по технике в системе ФАФ
    Нормализованная структура: id_score, id_event, id_judge, id_criterion, score
    """
    __tablename__ = 'scores_tech_faf'
    __table_args__ = (
        PrimaryKeyConstraint('id_scores_tech_faf', name='scores_tech_faf_pk'),
        CheckConstraint('score >= 0 AND score <= 10', name='scores_tech_faf_score_check'),
    )

    id_scores_tech_faf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_event: Mapped[int] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'), nullable=False)
    id_judge: Mapped[int] = mapped_column(Integer, ForeignKey('judge.id_judge', ondelete='CASCADE'), nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, ForeignKey('performance.id_performance', ondelete='CASCADE'), nullable=False)
    id_criterion: Mapped[int] = mapped_column(Integer, ForeignKey('criterion_tech_faf.id_criterion_tech_faf', ondelete='CASCADE'), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)


class ScoresTechNaf(Base):
    """
    Оценки по технике в системе НАФ
    Нормализованная структура: id_score, id_event, id_judge, id_criterion, score
    """
    __tablename__ = 'scores_tech_naf'
    __table_args__ = (
        PrimaryKeyConstraint('id_scores_tech_naf', name='scores_tech_naf_pk'),
        CheckConstraint('score >= 0 AND score <= 2', name='scores_tech_naf_score_check'),
    )

    id_scores_tech_naf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_event: Mapped[int] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'), nullable=False)
    id_judge: Mapped[int] = mapped_column(Integer, ForeignKey('judge.id_judge', ondelete='CASCADE'), nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, ForeignKey('performance.id_performance', ondelete='CASCADE'), nullable=False)
    id_criterion: Mapped[int] = mapped_column(Integer, ForeignKey('criterion_tech_naf.id_criterion_tech_naf', ondelete='CASCADE'), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(precision=3, scale=2), nullable=False)


class Team(Base):
    __tablename__ = 'team'
    __table_args__ = (
        PrimaryKeyConstraint('team_name', name='team_pk'),
    )

    id_team: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), nullable=False)
    team_name: Mapped[str] = mapped_column(String, primary_key=True)
    team_city: Mapped[str] = mapped_column(String, nullable=False)


class Judge(Base):
    """
    Учетные данные судей
    Хранит email, пароль и роль судьи для аутентификации
    """
    __tablename__ = 'judge'
    __table_args__ = (
        PrimaryKeyConstraint('id_judge', name='judge_pk'),
        UniqueConstraint('email', name='judge_email_unique'),
        UniqueConstraint('access_code', name='judge_access_code_unique'),
        CheckConstraint("role::text = ANY (ARRAY['judge'::character varying, 'main_judge'::character varying, 'technical'::character varying, 'artistry'::character varying, 'timekeeper'::character varying, 'volunteer'::character varying, 'medic'::character varying]::text[])", name='judge_role_check'),
    )

    id_judge: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_human: Mapped[int] = mapped_column(Integer, ForeignKey('human.id', ondelete='CASCADE'), nullable=False)  # Связь с Human
    id_event: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('event.id_event', ondelete='CASCADE'))  # На каком событии работает
    email: Mapped[str] = mapped_column(String(100), nullable=False)  # Email для логина
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # Хеш пароля
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # судья, главный судья, техник, артист и т.д.
    access_code: Mapped[Optional[str]] = mapped_column(String(50))  # Уникальный код доступа
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)  # Активен ли аккаунт
    created_at: Mapped[datetime.datetime] = mapped_column(nullable=False, default=datetime.datetime.utcnow)
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column()
