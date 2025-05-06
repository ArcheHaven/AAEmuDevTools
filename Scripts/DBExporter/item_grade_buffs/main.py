import sqlite3
import csv

# Settings
DATABASE = '../compact.sqlite3'
TABLE = 'item_grade_buffs'
OUTPUT_CSV = 'item_grade_buffs.csv'

# Only the fields you want, in the exact order you want
EXPORT_COLUMNS = [
    "id","item_id","item_grade_id","buff_id"
]

def export():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Confirm all requested columns exist
    cur.execute(f"PRAGMA table_info({TABLE});")
    available = {col[1] for col in cur.fetchall()}
    missing = [col for col in EXPORT_COLUMNS if col not in available]
    if missing:
        raise ValueError(f"Missing columns in table: {missing}")

    # Export only the desired columns in correct order
    cur.execute(f"SELECT {', '.join(EXPORT_COLUMNS)} FROM {TABLE}")
    rows = cur.fetchall()

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(EXPORT_COLUMNS)
        for row in rows:
            if len(row) != len(EXPORT_COLUMNS):
                print(f"⚠️ Skipping malformed row: {row}")
                continue
            writer.writerow(row)

    print(f"✅ Exported {len(rows)} rows to {OUTPUT_CSV}")

export()
