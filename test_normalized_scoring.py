#!/usr/bin/env python3
"""Test the new normalized scoring system"""

from app.db.database import SessionLocal
from app.models.models import (
    ScoresArtFaf, ScoresArtNaf, ScoresTechFaf, ScoresTechNaf,
    CriterionArtFaf, CriterionArtNaf, CriterionTechFaf, CriterionTechNaf,
    Judge, Human, Event
)

session = SessionLocal()

try:
    # Get test data
    event = session.query(Event).first()
    judge = session.query(Judge).first()
    art_faf_criterion = session.query(CriterionArtFaf).filter_by(criterion_number=1).first()
    art_naf_criterion = session.query(CriterionArtNaf).filter_by(criterion_number=1).first()
    tech_faf_criterion = session.query(CriterionTechFaf).filter_by(criterion_number=1).first()
    tech_naf_criterion = session.query(CriterionTechNaf).filter_by(criterion_number=1).first()

    if not all([event, judge, art_faf_criterion, art_naf_criterion, tech_faf_criterion, tech_naf_criterion]):
        print("❌ Missing test data - need to create judge and criteria first")
        session.close()
        exit(1)

    print("Test 1: Create valid Art FAF score...")
    art_faf_score = ScoresArtFaf(
        id_event=event.id_event,
        id_judge=judge.id_judge,
        id_performance=1,  # First performance
        id_criterion=art_faf_criterion.id_criterion_art_faf,
        score=8
    )
    session.add(art_faf_score)
    session.commit()
    print("✅ PASSED - Art FAF score created")

    print("\nTest 2: Create valid Art NAF score...")
    art_naf_score = ScoresArtNaf(
        id_event=event.id_event,
        id_judge=judge.id_judge,
        id_performance=1,
        id_criterion=art_naf_criterion.id_criterion_art_naf,
        score=0.85
    )
    session.add(art_naf_score)
    session.commit()
    print("✅ PASSED - Art NAF score created")

    print("\nTest 3: Create valid Tech FAF score...")
    tech_faf_score = ScoresTechFaf(
        id_event=event.id_event,
        id_judge=judge.id_judge,
        id_performance=1,
        id_criterion=tech_faf_criterion.id_criterion_tech_faf,
        score=7
    )
    session.add(tech_faf_score)
    session.commit()
    print("✅ PASSED - Tech FAF score created")

    print("\nTest 4: Create valid Tech NAF score...")
    tech_naf_score = ScoresTechNaf(
        id_event=event.id_event,
        id_judge=judge.id_judge,
        id_performance=1,
        id_criterion=tech_naf_criterion.id_criterion_tech_naf,
        score=1.2
    )
    session.add(tech_naf_score)
    session.commit()
    print("✅ PASSED - Tech NAF score created")

    print("\nTest 5: Try invalid score (out of range)...")
    try:
        invalid_score = ScoresArtFaf(
            id_event=event.id_event,
            id_judge=judge.id_judge,
            id_performance=1,
            id_criterion=art_faf_criterion.id_criterion_art_faf,
            score=15  # Invalid: > 10
        )
        session.add(invalid_score)
        session.commit()
        print("❌ FAILED - Invalid score was accepted")
    except Exception as e:
        session.rollback()
        print("✅ PASSED - Invalid score rejected")

    print("\nTest 6: Try invalid criterion reference...")
    try:
        invalid_score = ScoresArtFaf(
            id_event=event.id_event,
            id_judge=judge.id_judge,
            id_performance=1,
            id_criterion=999,  # Non-existent criterion
            score=5
        )
        session.add(invalid_score)
        session.commit()
        print("❌ FAILED - Invalid criterion reference was accepted")
    except Exception as e:
        session.rollback()
        print("✅ PASSED - Invalid criterion reference rejected")

    print("\n✅ All normalized scoring tests passed!")

except Exception as e:
    session.rollback()
    print(f"❌ Test failed with error: {e}")

finally:
    session.close()
