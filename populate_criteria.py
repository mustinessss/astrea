#!/usr/bin/env python3
"""Populate criterion reference tables with all scoring criteria"""

from app.db.database import SessionLocal
from app.models.models import (
    CriterionArtFaf, CriterionArtNaf,
    CriterionTechFaf, CriterionTechNaf
)

def populate_criteria():
    """Fill all criterion tables with predefined criteria"""

    session = SessionLocal()

    try:
        # Artistry FAF criteria (13 criteria, 0-10)
        art_faf_criteria = [
            (1, "Музыкальность и ритм"),
            (2, "Артистическое выражение"),
            (3, "Работа с музыкой"),
            (4, "Сценическое присутствие"),
            (5, "Характер и эмоции"),
            (6, "Визуальная эффектность"),
            (7, "История/Повествование"),
            (8, "Оригинальность идеи"),
            (9, "Костюм и реквизит"),
            (10, "Мизансценирование пространства"),
            (11, "Переходы и связки"),
            (12, "Техсредства (свет, звук)"),
            (13, "Общее впечатление"),
        ]

        for num, name in art_faf_criteria:
            criterion = CriterionArtFaf(
                criterion_number=num,
                criterion_name=name,
                min_value=0,
                max_value=10
            )
            session.add(criterion)
            print(f"✓ Added Art FAF criterion {num}: {name}")

        # Artistry NAF criteria (13 criteria, 0-1, except 9,12: 0-0.5)
        art_naf_criteria = [
            (1, "Музыкальность и ритм", 0.0, 1.0),
            (2, "Артистическое выражение", 0.0, 1.0),
            (3, "Работа с музыкой", 0.0, 1.0),
            (4, "Сценическое присутствие", 0.0, 1.0),
            (5, "Характер и эмоции", 0.0, 1.0),
            (6, "Визуальная эффектность", 0.0, 1.0),
            (7, "История/Повествование", 0.0, 1.0),
            (8, "Оригинальность идеи", 0.0, 1.0),
            (9, "Костюм и реквизит", 0.0, 0.5),  # Special range
            (10, "Мизансценирование пространства", 0.0, 1.0),
            (11, "Переходы и связки", 0.0, 1.0),
            (12, "Техсредства (свет, звук)", 0.0, 0.5),  # Special range
            (13, "Общее впечатление", 0.0, 1.0),
        ]

        for num, name, min_val, max_val in art_naf_criteria:
            criterion = CriterionArtNaf(
                criterion_number=num,
                criterion_name=name,
                min_value=min_val,
                max_value=max_val
            )
            session.add(criterion)
            print(f"✓ Added Art NAF criterion {num}: {name} ({min_val}-{max_val})")

        # Technical FAF criteria (16 criteria, 0-10)
        tech_faf_criteria = [
            (1, "1.1 Синхронность техники"),
            (2, "1.2 Согласованность вооруженных и невооруженных действий"),
            (3, "1.3 Правильность техники"),
            (4, "1.4 Выравнивество движений"),
            (5, "1.5 Легкость выполнения"),
            (6, "2.1 Слаженность (группы) / Органичность (соло)"),
            (7, "2.2 Достоверность"),
            (8, "2.3 Качество исполнения"),
            (9, "3.1 Темп (отсутствие проседаний, заминок)"),
            (10, "3.2 Тактическая сложность"),
            (11, "3.3 Координационно-двигательная сложность"),
            (12, "3.4 Поощрение за сложность"),
            (13, "3.5 Разнообразие действий нападения"),
            (14, "3.6 Разнообразие действий обороны"),
            (15, "3.7 Разнообразие действий подготовки"),
            (16, "3.8 Общий уровень"),
        ]

        for num, name in tech_faf_criteria:
            criterion = CriterionTechFaf(
                criterion_number=num,
                criterion_name=name,
                min_value=0,
                max_value=10
            )
            session.add(criterion)
            print(f"✓ Added Tech FAF criterion {num}: {name}")

        # Technical NAF criteria (16 criteria, varying ranges)
        tech_naf_criteria = [
            (1, "1.1 Синхронность техники", 0.0, 1.0),
            (2, "1.2 Согласованность вооруженных и невооруженных действий", 0.0, 1.0),
            (3, "1.3 Правильность техники", 0.0, 1.0),
            (4, "1.4 Выравнивество движений", 0.0, 1.0),
            (5, "1.5 Легкость выполнения", 0.0, 1.0),
            (6, "2.1 Слаженность (группы) / Органичность (соло)", 0.0, 2.0),  # 0-2
            (7, "2.2 Достоверность", 0.0, 2.0),  # 0-2
            (8, "2.3 Качество исполнения", 0.0, 1.0),
            (9, "3.1 Темп (отсутствие проседаний, заминок)", 0.0, 1.0),
            (10, "3.2 Тактическая сложность", 0.0, 1.0),
            (11, "3.3 Координационно-двигательная сложность", 0.0, 1.0),
            (12, "3.4 Поощрение за сложность", 0.0, 1.0),
            (13, "3.5 Разнообразие действий нападения", 0.0, 1.0),
            (14, "3.6 Разнообразие действий обороны", 0.0, 1.0),
            (15, "3.7 Разнообразие действий подготовки", 0.0, 1.0),
            (16, "3.8 Общий уровень", 0.0, 1.0),
        ]

        for num, name, min_val, max_val in tech_naf_criteria:
            criterion = CriterionTechNaf(
                criterion_number=num,
                criterion_name=name,
                min_value=min_val,
                max_value=max_val
            )
            session.add(criterion)
            print(f"✓ Added Tech NAF criterion {num}: {name} ({min_val}-{max_val})")

        session.commit()
        print(f"\n✅ Successfully populated all criterion tables:")
        print(f"   • Art FAF: {len(art_faf_criteria)} criteria")
        print(f"   • Art NAF: {len(art_naf_criteria)} criteria")
        print(f"   • Tech FAF: {len(tech_faf_criteria)} criteria")
        print(f"   • Tech NAF: {len(tech_naf_criteria)} criteria")

    except Exception as e:
        session.rollback()
        print(f"❌ Error populating criteria: {e}")
        return False
    finally:
        session.close()

    return True

if __name__ == "__main__":
    populate_criteria()
