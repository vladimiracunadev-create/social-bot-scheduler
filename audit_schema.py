import sqlite3
import json
import os

DB_PATH = "n8n/data/database.sqlite"


def audit_schema():
    if not os.path.exists(DB_PATH):
        print("DB not found")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(workflow_entity)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
    conn.close()


if __name__ == "__main__":
    audit_schema()
