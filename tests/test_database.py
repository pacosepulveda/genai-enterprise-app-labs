from pathlib import Path
import sqlite3


def test_sample_database_exists_and_has_customers():
    db = Path("data/enterprise.db")
    assert db.exists(), "Run python scripts/init_database.py"
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    assert count >= 3
