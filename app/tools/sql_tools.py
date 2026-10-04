import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "enterprise.db"


def get_schema() -> str:
    connection = sqlite3.connect(DB_PATH)

    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
        """
    ).fetchall()

    schema_parts = []

    for (table_name,) in tables:
        columns = connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()

        column_names = [
            column[1]
            for column in columns
        ]

        schema_parts.append(
            f"{table_name}({', '.join(column_names)})"
        )

    connection.close()

    return "\n".join(schema_parts)


def execute_read_only_query(sql: str) -> list[tuple]:

    normalized = sql.strip().lower()

    forbidden = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "replace ",
        "attach ",
        "detach ",
    ]

    if not normalized.startswith("select"):
        raise ValueError(
            "Only SELECT queries are allowed."
        )

    if any(keyword in normalized for keyword in forbidden):
        raise ValueError(
            "Potentially destructive SQL detected."
        )

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute(sql)
        rows = cursor.fetchall()
        return rows

    finally:
        connection.close()