"""
Loads the CSV files from ./data into Oracle tables created by create_db.sql.
"""
from __future__ import annotations

import os
from pathlib import Path

import oracledb
import pandas as pd

# List of tables and their corresponding CSV files
TABLE_FILES = [
    ("manufacturers", "manufacturers.csv"),
    ("pharmacies", "pharmacies.csv"),
    ("calendar_day", "calendar_day.csv"),
    ("products", "products.csv"),
    ("sales", "sales.csv"),
]

def get_connection() -> oracledb.Connection:
    # Using your provided credentials as defaults
    user = os.getenv("DB_USER", "RTOMS9124_SCHEMA_MXWBQ")
    password = os.getenv("DB_PASS", "QI24VPH4VZ!3QNGMrSD75V4QDBC3VT")
    dsn = os.getenv("DB_DSN", "db.freesql.com:1521/23ai_34ui2")

    return oracledb.connect(user=user, password=password, dsn=dsn)


def load_table(cursor: oracledb.Cursor, table_name: str, csv_path: Path) -> None:
    if not csv_path.exists():
        print(f"Warning: File {csv_path} not found. Skipping {table_name}.")
        return

    df = pd.read_csv(csv_path)

    # Special handling for date formats in Oracle
    if table_name == "calendar_day" and "date_value" in df.columns:
        df["date_value"] = pd.to_datetime(df["date_value"]).dt.strftime("%Y-%m-%d")

    columns = list(df.columns)
    # Oracle uses :1, :2 etc. or named binds for executemany
    bind_vars = ", ".join(f":{i + 1}" for i in range(len(columns)))
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({bind_vars})"

    # Convert DataFrame to list of tuples, handling NaN/Null values for Oracle
    rows = []
    for row in df.itertuples(index=False, name=None):
        rows.append(tuple(None if pd.isna(value) else value for value in row))

    cursor.executemany(sql, rows)
    print(f"Loaded {len(rows)} rows into {table_name}")


def main() -> None:
    # Assumes data folder is in the same directory as this script
    repo_root = Path(__file__).resolve().parent
    data_dir = repo_root / "data"

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        for table_name, filename in TABLE_FILES:
            load_table(cursor, table_name, data_dir / filename)
        
        conn.commit()
        print("--- All CSV files loaded successfully ---")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"An error occurred: {e}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    main()
