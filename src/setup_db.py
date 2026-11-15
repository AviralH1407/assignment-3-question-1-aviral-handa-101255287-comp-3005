"""
One-time setup: creates the university_db database (if missing) and loads
db/schema_and_seed.sql into it (if the students table is empty or missing).
Run from the project root:  python3 src/setup_db.py
"""
import os
import psycopg2

# Same connection settings as app.py
DB_NAME = os.environ.get("DB_NAME", "university_db")
BASE = {
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "root"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
}
SQL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "db", "schema_and_seed.sql")

def main():
    # 1. Connect to the built-in "postgres" database and create university_db if needed
    conn = psycopg2.connect(dbname="postgres", **BASE)
    conn.autocommit = True  # CREATE DATABASE can't run inside a transaction
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
        if cur.fetchone():
            print(f"Database '{DB_NAME}' already exists.")
        else:
            cur.execute(f'CREATE DATABASE "{DB_NAME}";')
            print(f"Created database '{DB_NAME}'.")
    conn.close()

    # 2. Connect to university_db and load the schema + 3 starting students if needed
    conn = psycopg2.connect(dbname=DB_NAME, **BASE)
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.students');")
        table_exists = cur.fetchone()[0] is not None
        row_count = 0
        if table_exists:
            cur.execute("SELECT COUNT(*) FROM students;")
            row_count = cur.fetchone()[0]

        if row_count == 0:
            with open(SQL_FILE) as f:
                cur.execute(f.read())
            conn.commit()
            print("Created the students table and inserted the starting students.")
        else:
            print(f"students table already has {row_count} rows - left it as is.")

        cur.execute("SELECT student_id, first_name, last_name, email FROM students ORDER BY student_id;")
        for row in cur.fetchall():
            print("  ", row)
    conn.close()
    print("Done. Refresh http://127.0.0.1:5001")


if __name__ == "__main__":
    main()
