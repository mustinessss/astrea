#!/usr/bin/env python3
"""Restore test event and performances after database migration"""

from datetime import datetime
from app.db.database import SessionLocal
from app.models.models import Event, Performance

def restore_test_data():
    """Create test event 'тест' with 8 performances grouped by discipline"""
    session = SessionLocal()
    
    try:
        # Create test event
        test_event = Event(
            date=datetime.now().date(),
            city='Москва'
        )
        session.add(test_event)
        session.flush()  # Get the ID
        event_id = test_event.id_event
        print(f"✓ Event 'тест' created with ID: {event_id}")
        
        # Create performances grouped by discipline
        performances = [
            # Соло (Solo) - 2 performances
            {"performance_name": "Соло 1 - Петров", "discipline": "Соло", "id_event": event_id},
            {"performance_name": "Соло 2 - Волков", "discipline": "Соло", "id_event": event_id},
            
            # Дуэль (Duel) - 2 performances
            {"performance_name": "Дуэль 1 - Сидоров & Иванов", "discipline": "Дуэль", "id_event": event_id},
            {"performance_name": "Дуэль 2 - Козлов & Орлов", "discipline": "Дуэль", "id_event": event_id},
            
            # Группа (Group) - 2 performances
            {"performance_name": "Группа 1 - Команда A", "discipline": "Группа", "id_event": event_id},
            {"performance_name": "Группа 2 - Команда B", "discipline": "Группа", "id_event": event_id},
            
            # Ансамбль (Ensemble) - 2 performances
            {"performance_name": "Ансамбль 1 - Оркестр 1", "discipline": "Ансамбль", "id_event": event_id},
            {"performance_name": "Ансамбль 2 - Оркестр 2", "discipline": "Ансамбль", "id_event": event_id},
        ]
        
        for perf_data in performances:
            perf = Performance(**perf_data)
            session.add(perf)
            print(f"  ✓ Created: {perf_data['performance_name']}")
        
        session.commit()
        print(f"\n✅ Successfully restored test event with 8 performances")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error restoring test data: {e}")
        return False
    finally:
        session.close()
    
    return True

if __name__ == "__main__":
    restore_test_data()
