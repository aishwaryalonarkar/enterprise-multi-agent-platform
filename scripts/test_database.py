import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "enterprise.db"


connection = sqlite3.connect(DB_PATH)

tables = connection.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    """
).fetchall()

print("Tables:")
for table in tables:
    print(f" - {table[0]}")


print("\nRefunded transactions:")

rows = connection.execute(
    """
    SELECT customer_id, amount, transaction_date
    FROM transactions
    WHERE status = 'refunded'
    """
).fetchall()

for row in rows:
    print(row)


connection.close()