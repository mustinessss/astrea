#!/usr/bin/env python3
"""
recreate_database.py — воспроизведение схемы базы данных проекта «Астрея».

Скрипт самодостаточный: он не импортирует приложение, а создаёт всю схему
напрямую через DDL (psycopg2). Это удобно для разворачивания базы «с нуля»
на чистом PostgreSQL.

Схема соответствует ER-диаграмме проекта: 11 таблиц (human, event, team,
performance, judge, criterion, scores, chronometric, human_event,
human_performance, human_team) со всеми первичными и внешними ключами,
ограничениями CHECK и UNIQUE.

Использование:
    python recreate_database.py                 # создать таблицы (если их нет)
    python recreate_database.py --drop          # сначала удалить, затем создать
    python recreate_database.py --drop --yes    # то же без запроса подтверждения

Строка подключения берётся из переменной окружения DATABASE_URL, а при её
отсутствии — из файла .env (ключ DATABASE_URL=...). Пример:
    DATABASE_URL=postgresql://user:password@localhost:5432/astrea
"""
import argparse
import os
import sys

import psycopg2


# --- Порядок создания: родительские таблицы раньше зависимых -----------------
CREATE_ORDER = [
    "human",
    "event",
    "team",
    "performance",
    "judge",
    "criterion",
    "scores",
    "chronometric",
    "human_event",
    "human_performance",
    "human_team",
]

# DDL каждой таблицы. Целочисленные первичные ключи — GENERATED ALWAYS AS
# IDENTITY (стиль моделей SQLAlchemy в проекте). Внешние ключи каскадируют
# удаление, чтобы при удалении события/человека зависимые строки убирались.
DDL = {
    "human": """
        CREATE TABLE human (
            id          INTEGER GENERATED ALWAYS AS IDENTITY,
            first_name  VARCHAR(100) NOT NULL,
            last_name   VARCHAR(100) NOT NULL,
            phone       VARCHAR(20),
            email       VARCHAR(100),
            patronymic  VARCHAR,
            CONSTRAINT human_pkey PRIMARY KEY (id)
        );
    """,
    "event": """
        CREATE TABLE event (
            id_event    INTEGER GENERATED ALWAYS AS IDENTITY,
            date        DATE NOT NULL,
            city        TEXT NOT NULL,
            name_event  VARCHAR(200),
            CONSTRAINT event_pk PRIMARY KEY (id_event)
        );
    """,
    "team": """
        CREATE TABLE team (
            id_team     INTEGER GENERATED ALWAYS AS IDENTITY,
            team_name   VARCHAR NOT NULL,
            team_city   VARCHAR NOT NULL,
            CONSTRAINT team_pk PRIMARY KEY (id_team),
            CONSTRAINT team_name_unique UNIQUE (team_name)
        );
    """,
    "performance": """
        CREATE TABLE performance (
            id_performance    INTEGER GENERATED ALWAYS AS IDENTITY,
            performance_name  VARCHAR NOT NULL,
            discipline        VARCHAR NOT NULL,
            id_event          INTEGER NOT NULL,
            id_team           INTEGER,
            CONSTRAINT performance_pk PRIMARY KEY (id_performance),
            CONSTRAINT performance_discipline_check
                CHECK (discipline IN ('Соло', 'Дуэль', 'Группа', 'Ансамбль')),
            CONSTRAINT performance_event_fk
                FOREIGN KEY (id_event) REFERENCES event (id_event) ON DELETE CASCADE,
            CONSTRAINT performance_team_fk
                FOREIGN KEY (id_team) REFERENCES team (id_team) ON DELETE SET NULL
        );
    """,
    "judge": """
        CREATE TABLE judge (
            id_judge       INTEGER GENERATED ALWAYS AS IDENTITY,
            id_human       INTEGER NOT NULL,
            id_event       INTEGER,
            email          VARCHAR(100) NOT NULL,
            password_hash  VARCHAR(255) NOT NULL,
            role           VARCHAR(20) NOT NULL,
            access_code    VARCHAR(50),
            is_active      BOOLEAN NOT NULL DEFAULT TRUE,
            created_at     TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
            last_login     TIMESTAMP,
            CONSTRAINT judge_pk PRIMARY KEY (id_judge),
            CONSTRAINT judge_email_unique UNIQUE (email),
            CONSTRAINT judge_access_code_unique UNIQUE (access_code),
            CONSTRAINT judge_role_check CHECK (
                role IN ('judge', 'main_judge', 'technical', 'artistry',
                         'timekeeper', 'volunteer', 'medic', 'admin')
            ),
            CONSTRAINT judge_human_fk
                FOREIGN KEY (id_human) REFERENCES human (id) ON DELETE CASCADE,
            CONSTRAINT judge_event_fk
                FOREIGN KEY (id_event) REFERENCES event (id_event) ON DELETE CASCADE
        );
    """,
    "criterion": """
        CREATE TABLE criterion (
            id_criterion    INTEGER GENERATED ALWAYS AS IDENTITY,
            name_criterion  VARCHAR NOT NULL,
            start_point     NUMERIC(5, 2) NOT NULL,
            step            NUMERIC(5, 2) NOT NULL DEFAULT 0.5,
            id_event        INTEGER NOT NULL,
            judge_type      VARCHAR(20) NOT NULL,
            CONSTRAINT criterion_pk PRIMARY KEY (id_criterion),
            CONSTRAINT criterion_event_fk
                FOREIGN KEY (id_event) REFERENCES event (id_event) ON DELETE CASCADE
        );
    """,
    "scores": """
        CREATE TABLE scores (
            id_scores       INTEGER GENERATED ALWAYS AS IDENTITY,
            id_judge        INTEGER NOT NULL,
            id_criterion    INTEGER NOT NULL,
            id_performance  INTEGER NOT NULL,
            value           NUMERIC(5, 2) NOT NULL,
            CONSTRAINT scores_pk PRIMARY KEY (id_scores),
            CONSTRAINT scores_judge_fk
                FOREIGN KEY (id_judge) REFERENCES judge (id_judge) ON DELETE CASCADE,
            CONSTRAINT scores_criterion_fk
                FOREIGN KEY (id_criterion) REFERENCES criterion (id_criterion) ON DELETE CASCADE,
            CONSTRAINT scores_performance_fk
                FOREIGN KEY (id_performance) REFERENCES performance (id_performance) ON DELETE CASCADE
        );
    """,
    "chronometric": """
        CREATE TABLE chronometric (
            id_chronometric  INTEGER GENERATED ALWAYS AS IDENTITY,
            total_time       TIME NOT NULL,
            time_fencing     TIME NOT NULL,
            id_performance   INTEGER NOT NULL,
            id_human         INTEGER NOT NULL,
            CONSTRAINT chronometric_pk PRIMARY KEY (id_chronometric),
            CONSTRAINT chronometric_performance_fk
                FOREIGN KEY (id_performance) REFERENCES performance (id_performance) ON DELETE CASCADE,
            CONSTRAINT chronometric_human_fk
                FOREIGN KEY (id_human) REFERENCES human (id)
        );
    """,
    "human_event": """
        CREATE TABLE human_event (
            id_human_event  INTEGER GENERATED ALWAYS AS IDENTITY,
            id_human        INTEGER NOT NULL,
            id_event        INTEGER NOT NULL,
            role_event      VARCHAR NOT NULL,
            access_code     VARCHAR(50),
            judge_type      VARCHAR(20),
            another_role    VARCHAR(20),
            CONSTRAINT human_event_pk PRIMARY KEY (id_human_event),
            CONSTRAINT human_event_access_code_key UNIQUE (access_code),
            CONSTRAINT human_event_judge_type_check
                CHECK (judge_type IN ('technical', 'artistry', 'timekeeper')),
            CONSTRAINT human_event_another_role_check
                CHECK (another_role IN ('main_judge', 'volunteer', 'medic')),
            CONSTRAINT human_event_human_fk
                FOREIGN KEY (id_human) REFERENCES human (id) ON DELETE CASCADE,
            CONSTRAINT human_event_event_fk
                FOREIGN KEY (id_event) REFERENCES event (id_event) ON DELETE CASCADE
        );
    """,
    "human_performance": """
        CREATE TABLE human_performance (
            id_human_performance  INTEGER GENERATED ALWAYS AS IDENTITY,
            role                  VARCHAR NOT NULL,
            id_human              INTEGER NOT NULL,
            CONSTRAINT human_performance_pk PRIMARY KEY (id_human_performance),
            CONSTRAINT human_performance_human_fk
                FOREIGN KEY (id_human) REFERENCES human (id) ON DELETE CASCADE
        );
    """,
    "human_team": """
        CREATE TABLE human_team (
            id_human_team  INTEGER GENERATED ALWAYS AS IDENTITY,
            id_human       INTEGER NOT NULL,
            id_team        INTEGER NOT NULL,
            role           VARCHAR NOT NULL,
            CONSTRAINT human_team_pk PRIMARY KEY (id_human_team),
            CONSTRAINT human_team_human_fk
                FOREIGN KEY (id_human) REFERENCES human (id) ON DELETE CASCADE,
            CONSTRAINT human_team_team_fk
                FOREIGN KEY (id_team) REFERENCES team (id_team) ON DELETE CASCADE
        );
    """,
}


def load_database_url() -> str:
    """Берёт DATABASE_URL из окружения, иначе пытается прочитать из .env."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return url

    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("DATABASE_URL="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    print("❌ Не задана переменная DATABASE_URL (ни в окружении, ни в .env).")
    sys.exit(1)


def drop_all(cur) -> None:
    print("Шаг 1. Удаление существующих таблиц...")
    # DROP в обратном порядке + CASCADE на всякий случай
    for table in reversed(CREATE_ORDER):
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    print("  ✓ Таблицы удалены\n")


def create_all(cur) -> None:
    print("Шаг 2. Создание таблиц...")
    for table in CREATE_ORDER:
        cur.execute(DDL[table])
        print(f"  + {table}")
    print("  ✓ Таблицы созданы\n")


def verify(cur) -> None:
    print("Шаг 3. Проверка...")
    cur.execute(
        """
        SELECT COUNT(*) FROM information_schema.table_constraints
        WHERE table_schema = 'public'
          AND constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'CHECK', 'UNIQUE');
        """
    )
    total = cur.fetchone()[0]

    cur.execute(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
    )
    tables = [r[0] for r in cur.fetchall()]
    print(f"  Таблиц создано: {len(tables)}")
    print(f"  Ограничений: {total}")
    for t in tables:
        print(f"    • {t}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Воспроизведение схемы БД «Астрея».")
    parser.add_argument("--drop", action="store_true", help="удалить таблицы перед созданием")
    parser.add_argument("--yes", action="store_true", help="не запрашивать подтверждение для --drop")
    args = parser.parse_args()

    database_url = load_database_url()

    if args.drop and not args.yes:
        answer = input("Удалить все таблицы и пересоздать схему? [y/N] ").strip().lower()
        if answer not in ("y", "yes", "д", "да"):
            print("Отменено.")
            return 0

    print("=" * 60)
    print("Воспроизведение схемы базы данных «Астрея»")
    print("=" * 60 + "\n")

    conn = psycopg2.connect(database_url)
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            if args.drop:
                drop_all(cur)
            create_all(cur)
            conn.commit()
            verify(cur)
        print("✅ Готово.")
        return 0
    except Exception as exc:  # noqa: BLE001
        conn.rollback()
        print(f"❌ Ошибка: {exc}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
