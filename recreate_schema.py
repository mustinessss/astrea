#!/usr/bin/env python3
"""Recreate database tables with new normalized schema"""

from app.db.database import engine
from app.models.models import Base

def recreate_tables():
    """Drop all tables and recreate with new schema"""

    print("============================================================\n"
          "Step 1: Dropping all existing tables...\n"
          "============================================================\n")

    try:
        # Drop all tables in correct order (reverse dependencies)
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped successfully\n")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False

    print("============================================================\n"
          "Step 2: Creating new tables with normalized schema...\n"
          "============================================================\n")

    try:
        # Create all tables with new schema
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully\n")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

    print("============================================================\n"
          "Step 3: Verifying constraints...\n"
          "============================================================\n")

    try:
        with engine.connect() as conn:
            # Simple count of constraints
            from sqlalchemy import text
            result = conn.execute(text("""
                SELECT COUNT(*) as total_constraints
                FROM information_schema.table_constraints
                WHERE constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'CHECK')
                  AND table_schema = 'public';
            """))

            total = result.fetchone()[0]
            print(f"Total constraints: {total}")

            # List all tables
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))

            tables = result.fetchall()
            print(f"Created tables: {len(tables)}")
            for table in tables:
                print(f"  • {table[0]}")

            print("\n✅ Database migration completed successfully!\n")

    except Exception as e:
        print(f"❌ Error verifying constraints: {e}")
        return False

    return True

if __name__ == "__main__":
    recreate_tables()
