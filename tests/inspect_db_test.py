from app.db.database import engine
from sqlalchemy import inspect

def test_print_db_structure():
    ins = inspect(engine)
    for t in ins.get_table_names():
        print(f"TABLE: {t}")
        for c in ins.get_columns(t):
            print(f"  - {c['name']} : {c['type']}")
    assert True
