# Как применить изменения к локальному репо `astrea`

Содержимое этого архива — все файлы, которые добавились или изменились
за время работы. Структура папок повторяет проект: просто распакуй
архив поверх своего клона репозитория, перезаписав файлы.

## 1. Скопировать файлы поверх своего репо

```bash
unzip astrea-changes.zip
cp -r astrea-changes/. /path/to/your/astrea/
cd /path/to/your/astrea
```

(если на Windows — распакуй в папку рядом и перетащи содержимое
`astrea-changes/` в свою папку `astrea/` с заменой)

## 2. Удалить устаревшие файлы

Они импортируют старые модели (ScoresArtFaf и т.п.), которых больше нет,
и ломают `pytest`:

```bash
rm test_normalized_scoring.py restore_test_data.py
```

## 3. Поставить новые зависимости

В requirements.txt добавился `pytest`. Также в этой версии `PyJWT==2.8.0`
и `jinja2>=3.1.0`.

```bash
.venv/bin/pip install -r requirements.txt
```

## 4. Пересобрать схему БД

В моделях полностью заменены 8 старых таблиц (`scores_art_faf`,
`criterion_tech_naf` и т.п.) на унифицированные `criterion` и `scores`.
Миграцию писать не стал — для зачётной работы проще пересоздать схему:

```bash
.venv/bin/python recreate_schema.py
.venv/bin/python populate_criteria.py
.venv/bin/python create_test_judge.py
.venv/bin/python seed_test_data.py
```

⚠️ `recreate_schema.py` дропает таблицы. Если в `steel_dawn` есть данные,
которые жалко — сделай `pg_dump steel_dawn > backup.sql` ДО шага 4.

## 5. Запустить и проверить

```bash
.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
.venv/bin/pytest -v             # 5 тестов должны быть зелёными
.venv/bin/python benchmark.py --perfs 40 --io-delay 0.05   # x6 ускорение
```

Логин: `testpass` (тех-судья) или `artpass` (арт-судья).

## Что внутри архива

Новые файлы:
- `seed_test_data.py`, `benchmark.py`, `README.md`, `.env.example`
- `app/api/services/event_calc.py`
- `templates/judge_performance.html`, `templates/admin.html`
- `tests/` (4 файла)

Изменённые:
- `main.py`, `requirements.txt`, `populate_criteria.py`
- `app/models/models.py`, `app/models/__init__.py`
- `app/api/__init__.py`, `app/api/routes/__init__.py`, `app/api/routes/score.py`
- `app/api/services/score_service.py`, `app/api/services/calculation_service.py`
- `app/schemas/score.py`
- `templates/judge_dashboard.html`
