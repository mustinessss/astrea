"""
Создание первого администратора (main_judge).

Запуск: python create_admin.py

Скрипт создаёт запись Human + запись Judge с ролью main_judge.
"""
import os
import sys

# Добавляем корень проекта в path
sys.path.insert(0, os.path.dirname(__file__))

from app.db.database import Base, SessionLocal, engine
from app.models.models import Human, Judge
from app.core.auth import get_password_hash

Base.metadata.create_all(bind=engine)

print("=== Создание администратора Астреи ===\n")

first_name = input("Имя: ").strip()
last_name = input("Фамилия: ").strip()
email = input("Email: ").strip().lower()
password = input("Пароль (мин. 8 символов): ").strip()

if len(password) < 8:
    print("❌ Пароль слишком короткий")
    sys.exit(1)

db = SessionLocal()
try:
    existing = db.query(Judge).filter(Judge.email == email).first()
    if existing:
        print(f"❌ Судья с email {email} уже существует")
        sys.exit(1)

    human = Human(first_name=first_name, last_name=last_name)
    db.add(human)
    db.flush()

    judge = Judge(
        id_human=human.id,
        email=email,
        password_hash=get_password_hash(password),
        role="main_judge",
        is_active=True,
    )
    db.add(judge)
    db.commit()
    print(f"\n✅ Администратор создан!")
    print(f"   Email: {email}")
    print(f"   Роль:  main_judge")
    print(f"   ID судьи: {judge.id_judge}")
finally:
    db.close()
