import sqlite3
import csv

# Settings
DATABASE = '../compact.sqlite3'
TABLE = 'items'
OUTPUT_CSV = 'item_assets.csv'

# Desired export columns in exact order
EXPORT_COLUMNS = [
    "id", "name", "category_id", "level", "description", "price", "refund", "bind_id",
    "pickup_limit", "max_stack_size", "icon_id", "sellable", "use_skill_id",
    "use_skill_as_reagent", "impl_id", "pickup_sound_id", "milestone_id", "buff_id",
    "gradable", "loot_multi", "loot_quest_id", "notify_ui", "use_or_equipment_sound_id",
    "honor_price", "exp_abs_lifetime", "exp_online_lifetime", "exp_date",
    "specialty_zone_id", "level_requirement", "comment", "auction_a_category_id",
    "auction_b_category_id", "auction_c_category_id", "level_limit", "fixed_grade",
    "disenchantable", "living_point_price", "actability_group_id",
    "actability_requirement", "grade_enchantable", "char_gender_id", "one_time_sale",
    "limited_sale_count", "male_icon_id", "over_icon_id", "translate",
    "auto_register_to_actionbar"
]

# Default values for multiple columns
DEFAULT_VALUES = {
    "comment": "",  # Default empty comment
    "milestone_id": 0,  # Default to 0 for milestone_id
    "grade_enchantable": "t",  # Default grade_enchantable to 1
    "translate": "f",  # Default translate to "f"
    "sellable": "t",  # Default sellable to "t"
    "auto_register_to_actionbar":"f",
    "disenchantable":"t",
    "use_skill_as_reagent":"f",
    "exp_data":"",
    "notify_ui":"t"
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
