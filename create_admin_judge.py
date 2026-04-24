#!/usr/bin/env python3
"""Create or update an admin (main) judge tied to the default event.

Usage:
    python create_admin_judge.py [password]

If no password is provided, default is 'mustiness'.
"""
import sys
from app.db.database import SessionLocal
from app.models.models import Human, Judge, Event
from app.core.auth import get_password_hash

password = sys.argv[1] if len(sys.argv) > 1 else "mustiness"

db = SessionLocal()
try:
    event = db.query(Event).first()
    if event is None:
        event = Event(date=None, city="Default", name_event="Default Event")
        db.add(event)
        db.commit()
        db.refresh(event)

    # create human
    human = Human(first_name="Главный", last_name="Судья", email="admin@local")
    db.add(human)
    db.flush()

    # if admin judge already exists, update
    existing = db.query(Judge).filter(Judge.email == "admin@local").first()
    if existing:
        existing.password_hash = get_password_hash(password)
        existing.role = "main_judge"
        existing.id_event = event.id_event
        existing.is_active = True
        db.add(existing)
        db.commit()
        print(f"Updated existing admin judge id_judge={existing.id_judge}")
    else:
        admin = Judge(
            id_human=human.id,
            id_event=event.id_event,
            email="admin@local",
            password_hash=get_password_hash(password),
            role="main_judge",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Created admin judge id_judge={admin.id_judge}, password={password}")

except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
