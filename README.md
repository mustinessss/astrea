# Астрея — система судейства артистического фехтования

Веб-приложение для проведения соревнований: судьи выставляют оценки через браузер, система автоматически считает итоговую таблицу.

---

## Что нужно перед началом

Убедитесь, что на компьютере установлено:

| Что | Где скачать | Как проверить |
|-----|-------------|---------------|
| **Python 3.12** | https://www.python.org/downloads/ | `python --version` |
| **PostgreSQL 14+** | https://www.postgresql.org/download/ | `psql --version` |
| **Git** | https://git-scm.com/downloads | `git --version` |

> **Windows:** все команды ниже выполняйте в **PowerShell** или **Git Bash**.  
> **macOS/Linux:** используйте **Терминал**.

---

## Шаг 1 — Скачать проект

```bash
git clone https://github.com/mustinessss/astrea.git
cd astrea
```

---

## Шаг 2 — Создать виртуальное окружение

Виртуальное окружение изолирует зависимости проекта от остальной системы.

```bash
# macOS / Linux
python3.12 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

После активации в начале строки появится `(.venv)`.

---

## Шаг 3 — Установить зависимости

```bash
pip install -r requirements.txt
```

---

## Шаг 4 — Создать базу данных

Откройте **другое** окно терминала и зайди в PostgreSQL:

```bash
psql -U postgres
```

Создайте базу данных для проекта:

```sql
CREATE DATABASE astrea;
\q
```

---

## Шаг 5 — Настроить подключение

Скопируйте файл с настройками:

```bash
# macOS / Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Откройте файл `.env` любым текстовым редактором и заполни:

```
DATABASE_URL=postgresql://postgres:ТУТ_ТВОЙ_ПАРОЛЬ@localhost:5432/astrea
SECRET_KEY=любая-длинная-случайная-строка
```

> **Как получить надёжный SECRET_KEY:**
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(48))"
> ```
> Скопируйте результат в `.env`.

---

## Шаг 6 — Создать таблицы в базе данных

```bash
python recreate_database.py
```

Вы увидите список из 11 созданных таблиц. Если нужно **пересоздать** базу с нуля (например, при повторной установке):

```bash
python recreate_database.py --drop --yes
```

---

## Шаг 7 — Заполнить базу начальными данными

```bash
# Создать критерии оценивания (стандарт ФАФ: 16 технических + 13 артистических)
python populate_criteria.py

# Создать тестового технического судью (логин по паролю: testpass)
python create_test_judge.py

# Создать тестового артистического судью (artpass) и 3 тестовых выступления
python seed_test_data.py
```

---

## Шаг 8 — Запустить приложение

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Откройте браузер и перейди по адресу: **http://localhost:8000**

---

## Как войти

| Роль | Пароль |
|------|--------|
| Технический судья | `testpass` |
| Артистический судья | `artpass` |

---

## Что делать дальше

- **Оценить выступление** — войди как судья, выбери выступление, выстави баллы по каждому критерию, нажми «Подтвердить».
- **Посмотреть итоги** — перейдите на http://localhost:8000/admin.

---

## Тесты

Чтобы убедиться, что всё работает корректно:

```bash
pytest -v
```

Тесты создают изолированное событие и удаляют его — реальные данные не затрагиваются.

---

## Частые проблемы

**`psycopg2.OperationalError: could not connect to server`**  
→ PostgreSQL не запущен. Запустите его через системные службы или командой `pg_ctl start`.

**`password authentication failed for user "postgres"`**  
→ Неверный пароль в `DATABASE_URL`. Проверь `.env`.

**`ModuleNotFoundError`**  
→ Виртуальное окружение не активировано. Вернись к шагу 2.

**`(.venv)` пропало после закрытия терминала**  
→ Нужно активировать окружение заново каждый раз (шаг 2).
