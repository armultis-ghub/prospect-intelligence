import sqlite3
import os
import shutil

db_path = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
sqlite_bin = shutil.which("sqlite3")
print(f"SQLite binary: {sqlite_bin}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT count(*) FROM queue WHERE status IN ('PENDING', 'RETRY');")
        count = cursor.fetchone()[0]
        print(f"Pending: {count}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
else:
    print("DB_NOT_FOUND")
