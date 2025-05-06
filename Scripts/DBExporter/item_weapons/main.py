import sqlite3
import csv

# Settings
DATABASE = '../compact.sqlite3'
TABLE = 'item_weapons'
OUTPUT_CSV = 'item_weapons_export.csv'

EXPORT_COLUMNS = [
    "id", "item_id", "asset_id", "base_enchantable", "holdable_id",
    "mod_set_id", "eiset_id", "repairable",
    "durability_multiplier", "base_equipment", "drawn_scale",
    "worn_scale", "recharge_buff_id", "charge_lifetime",
    "charge_count", "useAsStat", "skin_kind_id", "fixed_visual_effect_id"
]

# Default values for multiple columns
DEFAULT_VALUES = {
    "repairable":"t",
    "fixed_visual_effect_id":"",
    "useAsStat":"t",
    "recharge_buff_id":"",
    "base_enchantable":"t",
    "eiset_id":"",
    "base_equipment":"t",
    "or_unit_reqs":"f"

}


def export():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Get all available columns
    cur.execute(f"PRAGMA table_info({TABLE});")
    available = {col[1] for col in cur.fetchall()}

    # Determine which columns are in DB and which need defaults
    columns_in_db = [col for col in EXPORT_COLUMNS if col in available]
    columns_missing = [col for col in EXPORT_COLUMNS if col not in available]

    # Fetch only available columns
    cur.execute(f"SELECT {', '.join(columns_in_db)} FROM {TABLE}")
    rows = cur.fetchall()

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(EXPORT_COLUMNS)

        for row in rows:
            row_dict = dict(zip(columns_in_db, row))

            # Add default values for missing columns and override with specific defaults
            for col in columns_missing:
                row_dict[col] = DEFAULT_VALUES.get(col, None)

            # Override multiple columns with default values
            for col, default_value in DEFAULT_VALUES.items():
                if col in row_dict:  # Only override if column exists in the data
                    row_dict[col] = default_value

            # Write full row in correct order
            writer.writerow([row_dict.get(col, '') for col in EXPORT_COLUMNS])

    print(f"✅ Exported {len(rows)} rows to {OUTPUT_CSV}")


export()
