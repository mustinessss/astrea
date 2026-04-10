#!/usr/bin/env python3
"""
Скрипт для удаления и пересоздания таблиц БД с новыми constraints
"""

import psycopg2
from app.db.database import Base, engine
from app.models.models import *

print("=" * 60)
print("Step 1: Dropping all existing tables...")
print("=" * 60)

conn = psycopg2.connect(host='localhost', port=5432, database='steel_dawn', user='developer', password='mustiness')
cursor = conn.cursor()

# Получаем список всех таблиц
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name NOT LIKE 'pg_%'")
tables = cursor.fetchall()

# Удаляем все таблицы
for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')
        print(f"  ✓ Dropped: {table_name}")
    except Exception as e:
        print(f"  ✗ Error dropping {table_name}: {e}")

conn.commit()
cursor.close()
conn.close()

print("\n" + "=" * 60)
print("Step 2: Creating new tables with constraints...")
print("=" * 60)

# Пересоздаем все таблицы с новыми constraints
Base.metadata.create_all(bind=engine)
print("  ✓ All tables created successfully")

print("\n" + "=" * 60)
print("Step 3: Verifying constraints...")
print("=" * 60)

# Проверяем, что constraints созданы
conn = psycopg2.connect(host='localhost', port=5432, database='steel_dawn', user='developer', password='mustiness')
cursor = conn.cursor()

# Проверяем foreign keys
cursor.execute("""
    SELECT constraint_name, table_name, constraint_type 
    FROM information_schema.table_constraints 
    WHERE table_schema = 'public' AND constraint_type IN ('FOREIGN KEY', 'CHECK')
    ORDER BY table_name
""")

constraints = cursor.fetchall()
print(f"  Total constraints: {len(constraints)}")
for constraint in constraints[:15]:  # Показываем первые 15
    constraint_name, table_name, constraint_type = constraint
    print(f"    • {table_name}.{constraint_name} ({constraint_type})")

if len(constraints) > 15:
    print(f"    ... and {len(constraints) - 15} more")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("✅ Database migration completed successfully!")
print("=" * 60)
