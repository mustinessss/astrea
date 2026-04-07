from typing import Optional
import datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Text, Time, UniqueConstraint
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
    id_performance: Mapped[int] = mapped_column(Integer, nullable=False)
    id_human: Mapped[str] = mapped_column(String, nullable=False)


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
    id_human: Mapped[int] = mapped_column(Integer, nullable=False)
    id_event: Mapped[int] = mapped_column(Integer, nullable=False)
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
    id_human: Mapped[int] = mapped_column(Integer, nullable=False)


class HumanTeam(Base):
    __tablename__ = 'human_team'
    __table_args__ = (
        PrimaryKeyConstraint('id_human_team', name='human_team_pk'),
    )

    id_human_team: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    role: Mapped[str] = mapped_column(String, nullable=False)


class Performance(Base):
    __tablename__ = 'performance'
    __table_args__ = (
        PrimaryKeyConstraint('id_performance', name='performance_pk'),
    )

    id_performance: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    performance_name: Mapped[str] = mapped_column(String, nullable=False)
    discipline: Mapped[str] = mapped_column(String, nullable=False)
    id_event: Mapped[int] = mapped_column(Integer, nullable=False)


class ScoresArtFaf(Base):
    """
    Оценки по артистике в системе ФАФ
    13 артистических критериев, диапазон 0-10, целые числа
    """
    __tablename__ = 'scores_art_faf'
    __table_args__ = (
        PrimaryKeyConstraint('id_scores_art_faf', name='scores_art_faf_pk'),
    )

    id_scores_art_faf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_human: Mapped[int] = mapped_column(Integer, nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 13 артистических критериев ФАФ (0-10, целые числа)
    criterion_1: Mapped[Optional[int]] = mapped_column(Integer)  # 1. Музыкальность и ритм
    criterion_2: Mapped[Optional[int]] = mapped_column(Integer)  # 2. Артистическое выражение
    criterion_3: Mapped[Optional[int]] = mapped_column(Integer)  # 3. Работа с музыкой
    criterion_4: Mapped[Optional[int]] = mapped_column(Integer)  # 4. Сценическое присутствие
    criterion_5: Mapped[Optional[int]] = mapped_column(Integer)  # 5. Характер и эмоции
    criterion_6: Mapped[Optional[int]] = mapped_column(Integer)  # 6. Визуальная эффектность
    criterion_7: Mapped[Optional[int]] = mapped_column(Integer)  # 7. История/Повествование
    criterion_8: Mapped[Optional[int]] = mapped_column(Integer)  # 8. Оригинальность идеи
    criterion_9: Mapped[Optional[int]] = mapped_column(Integer)  # 9. Костюм и реквизит
    criterion_10: Mapped[Optional[int]] = mapped_column(Integer)  # 10. Мизансценирование пространства
    criterion_11: Mapped[Optional[int]] = mapped_column(Integer)  # 11. Переходы и связки
    criterion_12: Mapped[Optional[int]] = mapped_column(Integer)  # 12. Техсредства (свет, звук)
    criterion_13: Mapped[Optional[int]] = mapped_column(Integer)  # 13. Общее впечатление


class ScoresArtNaf(Base):
    """
    Оценки по артистике в системе НАФ
    13 артистических критериев, диапазон 0-1, шаг 0.05
    """
    __tablename__ = 'scores_art_naf'
    __table_args__ = (
        PrimaryKeyConstraint('id_scores_art_naf', name='scores_art_naf_pk'),
    )

    id_scores_art_naf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_human: Mapped[int] = mapped_column(Integer, nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 13 артистических критериев НАФ (0-1, шаг 0.05)
    criterion_1: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 1. Музыкальность и ритм
    criterion_2: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 2. Артистическое выражение
    criterion_3: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 3. Работа с музыкой
    criterion_4: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 4. Сценическое присутствие
    criterion_5: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 5. Характер и эмоции
    criterion_6: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 6. Визуальная эффектность
    criterion_7: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 7. История/Повествование
    criterion_8: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 8. Оригинальность идеи
    criterion_9: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 9. Костюм и реквизит (0-0.5)
    criterion_10: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 10. Мизансценирование пространства
    criterion_11: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 11. Переходы и связки
    criterion_12: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 12. Техсредства (свет, звук) (0-0.5)
    criterion_13: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 13. Общее впечатление


class ScoresTechFaf(Base):
    """
    Оценки по технике в системе ФАФ
    16 технических подкритериев: Базовая техника (1.1-1.5), Мастерство (2.1-2.3), Сложность (3.1-3.8)
    Диапазон 0-10, целые числа
    """
    __tablename__ = 'scores_tech_faf'
    __table_args__ = (
        PrimaryKeyConstraint('id_scores_tech_faf', name='scores_tech_faf_pk'),
    )

    id_scores_tech_faf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_human: Mapped[int] = mapped_column(Integer, nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Группа 1: Базовая техника (5 подкритериев)
    criterion_1_1: Mapped[Optional[int]] = mapped_column(Integer)  # 1.1 Синхронность техники
    criterion_1_2: Mapped[Optional[int]] = mapped_column(Integer)  # 1.2 Согласованность вооруженных и невооруженных действий
    criterion_1_3: Mapped[Optional[int]] = mapped_column(Integer)  # 1.3 Правильность техники
    criterion_1_4: Mapped[Optional[int]] = mapped_column(Integer)  # 1.4 Выравнивество движений
    criterion_1_5: Mapped[Optional[int]] = mapped_column(Integer)  # 1.5 Легкость выполнения
    
    # Группа 2: Мастерство (3 подкритерия)
    criterion_2_1: Mapped[Optional[int]] = mapped_column(Integer)  # 2.1 Слаженность (группы) / Органичность (соло)
    criterion_2_2: Mapped[Optional[int]] = mapped_column(Integer)  # 2.2 Достоверность
    criterion_2_3: Mapped[Optional[int]] = mapped_column(Integer)  # 2.3 Качество исполнения
    
    # Группа 3: Сложность и уровень (8 подкритериев)
    criterion_3_1: Mapped[Optional[int]] = mapped_column(Integer)  # 3.1 Темп (отсутствие проседаний, заминок)
    criterion_3_2: Mapped[Optional[int]] = mapped_column(Integer)  # 3.2 Тактическая сложность
    criterion_3_3: Mapped[Optional[int]] = mapped_column(Integer)  # 3.3 Координационно-двигательная сложность
    criterion_3_4: Mapped[Optional[int]] = mapped_column(Integer)  # 3.4 Поощрение за сложность
    criterion_3_5: Mapped[Optional[int]] = mapped_column(Integer)  # 3.5 Разнообразие действий нападения
    criterion_3_6: Mapped[Optional[int]] = mapped_column(Integer)  # 3.6 Разнообразие действий обороны
    criterion_3_7: Mapped[Optional[int]] = mapped_column(Integer)  # 3.7 Разнообразие действий подготовки
    criterion_3_8: Mapped[Optional[int]] = mapped_column(Integer)  # 3.8 Общий уровень


class ScoresTechNaf(Base):
    """
    Оценки по технике в системе НАФ
    16 технических подкритериев: Базовая техника (1.1-1.5), Мастерство (2.1-2.3), Сложность (3.1-3.8)
    Диапазон 0-1 (для большинства), 0-2 (для слаженности/достоверности), шаг 0.05
    """
    __tablename__ = 'scores_tech_naf'
    __table_args__ = (
        PrimaryKeyConstraint('id_scores_tech_naf', name='scores_tech_naf_pk'),
    )

    id_scores_tech_naf: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_human: Mapped[int] = mapped_column(Integer, nullable=False)
    id_performance: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Группа 1: Базовая техника (5 подкритериев) - 0-1, шаг 0.05
    criterion_1_1: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 1.1 Синхронность техники
    criterion_1_2: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 1.2 Согласованность вооруженных и невооруженных действий
    criterion_1_3: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 1.3 Правильность техники
    criterion_1_4: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 1.4 Выравнивество движений
    criterion_1_5: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 1.5 Легкость выполнения
    
    # Группа 2: Мастерство (3 подкритерия)
    criterion_2_1: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 2.1 Слаженность (группы) / Органичность (соло) - 0-2
    criterion_2_2: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 2.2 Достоверность - 0-2
    criterion_2_3: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 2.3 Качество исполнения - 0-1
    
    # Группа 3: Сложность и уровень (8 подкритериев) - 0-1, шаг 0.05
    criterion_3_1: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 3.1 Темп (отсутствие проседаний, заминок)
    criterion_3_2: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 3.2 Тактическая сложность
    criterion_3_3: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 3.3 Координационно-двигательная сложность
    criterion_3_4: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 3.4 Поощрение за сложность
    criterion_3_5: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 3.5 Разнообразие действий нападения
    criterion_3_6: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 3.6 Разнообразие действий обороны
    criterion_3_7: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 3.7 Разнообразие действий подготовки
    criterion_3_8: Mapped[Optional[float]] = mapped_column(Numeric(precision=3, scale=2))  # 3.8 Общий уровень


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
    id_human: Mapped[int] = mapped_column(Integer, nullable=False)  # Связь с Human
    id_event: Mapped[Optional[int]] = mapped_column(Integer)  # На каком событии работает
    email: Mapped[str] = mapped_column(String(100), nullable=False)  # Email для логина
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # Хеш пароля
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # судья, главный судья, техник, артист и т.д.
    access_code: Mapped[Optional[str]] = mapped_column(String(50))  # Уникальный код доступа
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)  # Активен ли аккаунт
    created_at: Mapped[datetime.datetime] = mapped_column(nullable=False, default=datetime.datetime.utcnow)
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column()
