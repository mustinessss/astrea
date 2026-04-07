#!/usr/bin/env python3
"""Тест аутентификации и создания судьи"""

import sys
sys.path.insert(0, 'c:/Users/ashst/OneDrive/Desktop/astrea')

from app.db.database import SessionLocal, Base, engine
from app.models.models import Human, Judge
from app.core.auth import get_password_hash

try:
    # Создать таблицы если их нет
    print("✓ Создаю таблицы в БД...")
    Base.metadata.create_all(bind=engine)
    print("  ✓ Таблицы готовы")
    
    # Создаем session
    db = SessionLocal()
    
    print("✓ Проверяю БД...")
    
    # Создам тестового человека если его нет
    human = db.query(Human).filter(Human.email == "judge@test.com").first()
    if not human:
        print("  Создаю тестового человека...")
        human = Human(
            first_name="Ivan",
            last_name="Smirnov",
            email="judge@test.com",
            phone="+7-900-123-45-67"
        )
        db.add(human)
        db.commit()
        db.refresh(human)
        print(f"  ✓ Человек создан с ID: {human.id}")
    else:
        print(f"  ✓ Человек найден с ID: {human.id}")
    
    # Создам судью
    judge = db.query(Judge).filter(Judge.email == "judge@test.com").first()
    if not judge:
        print("  Создаю тестового судью...")
        password_hash = get_password_hash("password123")
        judge = Judge(
            id_human=human.id,
            email="judge@test.com",
            password_hash=password_hash,
            role="judge",
            is_active=True
        )
        db.add(judge)
        db.commit()
        db.refresh(judge)
        print(f"  ✓ Судья создан с ID: {judge.id_judge}")
    else:
        print(f"  ✓ Судья найден с ID: {judge.id_judge}")
    
    print("\n✅ Данные успешно созданы!")
    print(f"   Email: judge@test.com")
    print(f"   Password: password123")
    print(f"   Role: judge")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
