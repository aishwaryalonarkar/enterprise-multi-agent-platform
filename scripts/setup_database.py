import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "enterprise.db"


def create_database():
    connection = sqlite3.connect(DB_PATH)

    datasets = {
        "customers": DATA_DIR / "customers.csv",
        "transactions": DATA_DIR / "transactions.csv",
        "support_tickets": DATA_DIR / "support_tickets.csv",
    }

    for table_name, file_path in datasets.items():
        df = pd.read_csv(file_path)

        df.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
        )

        print(f"Loaded {len(df)} rows into '{table_name}'")

    connection.close()

    print(f"\nDatabase created at: {DB_PATH}")


if __name__ == "__main__":
    create_database()