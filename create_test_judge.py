#!/usr/bin/env python3
"""Create test judge for scoring tests"""

from app.db.database import SessionLocal
from app.models.models import Human, Judge, Event
from app.core.auth import get_password_hash

session = SessionLocal()

try:
    # Create test human
    test_human = Human(
        first_name="Тестовый",
        last_name="Судья",
        email="judge@test.com"
    )
    session.add(test_human)
    session.flush()

    # Create test judge
    test_judge = Judge(
        id_human=test_human.id,
        email="judge@test.com",
        password_hash=get_password_hash("testpass"),
        role="technical",
        is_active=True
    )
    session.add(test_judge)
    session.commit()

    print("✅ Test judge created successfully")
    print(f"   Human ID: {test_human.id}")
    print(f"   Judge ID: {test_judge.id_judge}")
    print(f"   Email: {test_judge.email}")

except Exception as e:
    session.rollback()
    print(f"❌ Error creating test judge: {e}")

finally:
    session.close()
