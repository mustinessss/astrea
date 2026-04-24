# Астрея — система судейства артистического фехтования

Учебный проект (FastAPI + SQLAlchemy + PostgreSQL) для зачёта.
Автоматизирует выставление оценок судьями на фестивале и сводит итоговую таблицу.

## Возможности

- Авторизация судьи по паролю (cookie + JWT).
- Дашборд: выступления события, статус «оценено / не закончено / не оценено», прогресс.
- Форма судейства: слайдеры по критериям с шагом из БД, окно подтверждения, повторная отправка обновляет (upsert), а не дублирует.
- Страница итогов события `/admin`: таблица мест, средний технический + средний артистический балл, итог = сумма средних.
- Многопоточный пересчёт итогов через `ThreadPoolExecutor` (см. бенчмарк ниже).

## Стек

Python 3.12, FastAPI 0.104, SQLAlchemy 2, PostgreSQL, Jinja2, JWT, pytest.

## Структура

```
app/
  api/
    routes/        — HTTP-роуты (auth, event, human, score, team)
    services/      — бизнес-логика
      score_service.py        — upsert оценок, валидация диапазона
      calculation_service.py  — итог = avg(technical) + avg(artistry)
      event_calc.py           — параллельный пересчёт всего события
  core/            — auth, конфиг
  db/              — engine, Base, SessionLocal
  models/          — ORM-модели (Criterion, Score, Judge, Performance, Event, …)
  schemas/         — Pydantic-схемы
templates/         — HTML (login, judge_dashboard, judge_performance, admin)
tests/             — pytest
main.py            — FastAPI-приложение и UI-роуты
recreate_schema.py — пересоздать схему БД
populate_criteria.py — наполнить критерии для дефолтного события
seed_test_data.py  — тестовые судья + 3 выступления
create_test_judge.py — создать тех-судью с паролем testpass
benchmark.py       — последовательный vs параллельный пересчёт
```

## Запуск с нуля

```bash
git clone https://github.com/mustinessss/astrea.git
cd astrea

python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env
# отредактируй DATABASE_URL и SECRET_KEY

.venv/bin/python recreate_schema.py        # создать таблицы
.venv/bin/python populate_criteria.py      # 16 тех + 13 арт критериев ФАФ
.venv/bin/python create_test_judge.py      # тех-судья, пароль testpass
.venv/bin/python seed_test_data.py         # арт-судья (artpass) + 3 выступления

.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Открыть http://localhost:8000, войти паролем `testpass` (технический судья) или `artpass` (артистический).

## Тесты

```bash
.venv/bin/pytest -v
```

Тесты создают изолированное событие и удаляют его по окончании — реальные данные не затрагиваются.

## Бенчмарк многопоточности

```bash
# Локальная БД (запросы быстрее накладных расходов на потоки)
.venv/bin/python benchmark.py

# Имитация удалённой БД (50 мс на пересчёт выступления)
.venv/bin/python benchmark.py --perfs 40 --io-delay 0.05 --workers 8
```

Типичные результаты:

| Сценарий                        | Sequential | Parallel (8) | Ускорение |
|--------------------------------|-----------|--------------|-----------|
| Локальный Postgres, 60 перф    | ~150 мс   | ~227 мс      | x0.66     |
| Имитация удалённой БД, 40 перф | ~2150 мс  | ~350 мс      | **x6.1**  |

Вывод: на быстрой локальной БД накладные расходы на потоки и установку соединений превышают экономию. На реальной нагрузке с сетевой задержкой параллельная версия выигрывает в разы. В `/admin` используется параллельный путь.

## Архитектурные решения

- **Одна таблица `criterion` + одна таблица `scores`** вместо четырёх (tech_faf / art_faf / tech_naf / art_naf). Систему (ФАФ/НАФ/кастом) определяет набор критериев конкретного события (`id_event` + `judge_type` + `start_point` + `step`). Это убирает дублирование схемы и кода.
- **Upsert вместо INSERT** для оценок — нужен, чтобы кнопка «изменить» в окне подтверждения корректно переписывала уже выставленную оценку, а двойной клик не падал.
- **`id_event` подтягивается из `performance`** на бэке — судья не может записать оценку «не в то событие».
- **Пул потоков для пересчёта**: каждый поток открывает свою сессию, потому что сессии SQLAlchemy не потокобезопасны.
