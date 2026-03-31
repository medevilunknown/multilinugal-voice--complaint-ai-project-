import sqlite3
import os

DB_PATH = "cyberguard.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. Nothing to migrate.")
        return

    print(f"Checking for missing columns in {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Existing columns: {columns}")

    needed = [
        ("google_id", "VARCHAR(255)"),
        ("custom_gemini_key", "VARCHAR(255)"),
        ("is_managed_ai", "BOOLEAN DEFAULT 1")
    ]

    for col_name, col_type in needed:
        if col_name not in columns:
            print(f"Adding column {col_name} to users table...")
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added {col_name}")
            except Exception as e:
                print(f"❌ Failed to add {col_name}: {e}")
        else:
            print(f"Column {col_name} already exists.")

    # Get existing columns for complaints table
    cursor.execute("PRAGMA table_info(complaints)")
    complaints_columns = [row[1] for row in cursor.fetchall()]

    needed_complaints = [
        ("suspect_vpa", "VARCHAR(100)"),
        ("suspect_phone", "VARCHAR(100)"),
        ("suspect_bank_account", "VARCHAR(100)")
    ]

    for col_name, col_type in needed_complaints:
        if col_name not in complaints_columns:
            print(f"Adding column {col_name} to complaints table...")
            try:
                cursor.execute(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added {col_name} to complaints")
            except Exception as e:
                print(f"❌ Failed to add {col_name} to complaints: {e}")
        else:
            print(f"Column {col_name} in complaints already exists.")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
