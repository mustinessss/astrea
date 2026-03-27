#!/usr/bin/env python3
"""Простой тест подключения к БД и импорта моделей"""

import sys
sys.path.insert(0, 'c:/Users/ashst/OneDrive/Desktop/astrea')

try:
    print("✓ Загружаю конфиг...")
    from app.core.config import settings
    print(f"  DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    
    print("\n✓ Загружаю БД...")
    from app.db.database import engine, Base
    print(f"  Engine: {engine}")
    
    print("\n✓ Загружаю модели...")
    from app.models.models import (
        Chronometric, Event, Human, HumanEvent, HumanPerformance,
        HumanTeam, Performance, ScoresArtFaf, ScoresArtNaf,
        ScoresTechFaf, ScoresTechNaf, Team
    )
    print(f"  Загружено {12} моделей")
    
    print("\n✓ Проверяю подключение к БД...")
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1;"))
        print(f"  Результат: {result.fetchone()}")
    
    print("\n✓ Все таблицы в БД:")
    inspector = __import__('sqlalchemy').inspect(engine)
    for table_name in inspector.get_table_names():
        print(f"    - {table_name}")
    
    print("\n✅ Все успешно!")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
