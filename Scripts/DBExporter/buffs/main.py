import sqlite3
import csv

# Settings
DATABASE = '../compact.sqlite3'
TABLE = 'buffs'
OUTPUT_CSV = 'buffs_export.csv'

# Desired export columns in exact order
EXPORT_COLUMNS = [
    "id", "name", "desc", "icon_id", "anim_start_id", "anim_end_id", "duration", "tick",
    "silence", "root", "sleep", "stun", "crippled", "stealth", "remove_on_source_dead",
    "link_buff_id", "tick_mana_cost", "stack_rule_id", "init_min_charge", "init_max_charge",
    "max_stack", "damage_absorption_type_id", "damage_absorption_per_hit", "aura_radius",
    "mana_shield_ratio", "fx_group_id", "framehold", "ragdoll", "one_time", "reflection_chance",
    "reflection_type_id", "require_buff_id", "taunt", "taunt_with_top_aggro",
    "remove_on_use_skill", "melee_immune", "spell_immune", "ranged_immune", "siege_immune",
    "immune_damage", "skill_controller_id", "resurrection_health", "resurrection_mana",
     "level_duration", "reflection_ratio", "reflection_target_ratio",
    "knockback_immune", "immune_buff_tag_id", "aura_relation_id", "group_id", "group_rank",
    "per_unit_creation", "tick_area_radius", "tick_area_relation_id", "remove_on_move",
    "use_source_faction", "faction_id", "exempt", "tick_area_front_angle", "tick_area_angle",
    "psychokinesis", "no_collide", "psychokinesis_speed", "remove_on_death", "combat_text_start",
    "combat_text_end", "tick_anim_id", "tick_active_weapon_id", "conditional_tick", "system",
    "aura_slave_buff_id", "non_pushable", "active_weapon_id", "custom_dual_material_id",
    "custom_dual_material_fade_time", "max_charge", "detect_stealth", "remove_on_exempt",
    "remove_on_land", "gliding", "gliding_rotate_speed", "knock_down", "tick_area_exclude_source",
    "string_instrument_start_anim_id", "percussion_instrument_start_anim_id",
    "tube_instrument_start_anim_id", "string_instrument_tick_anim_id",
    "percussion_instrument_tick_anim_id", "tube_instrument_tick_anim_id", "gliding_startup_time",
    "gliding_startup_speed", "gliding_fall_speed_slow", "gliding_fall_speed_normal",
    "gliding_fall_speed_fast", "gliding_smooth_time", "gliding_lift_count", "gliding_lift_height",
    "gliding_lift_valid_time", "gliding_lift_duration", "gliding_lift_speed",
    "gliding_land_height", "gliding_sliding_time", "gliding_move_speed_slow",
    "gliding_move_speed_normal", "gliding_move_speed_fast", "fall_damage_immune", "kind_id",
    "ag_stance", "transform_buff_id", "blank_minded", "fastened", "slave_applicable", "pacifist",
    "remove_on_interaction", "remove_on_unmount", "aura_child_only", "remove_on_mount",
    "remove_on_start_skill", "sprint_motion", "telescope_range", "mainhand_tool_id",
    "offhand_tool_id", "tick_mainhand_tool_id", "tick_offhand_tool_id", "tick_level_mana_cost",
    "walk_only", "cannot_jump", "crowd_radius", "crowd_number", "evade_telescope",
    "transfer_telescope_range", "remove_on_attack_spell_dot", "remove_on_attack_etc_dot",
    "remove_on_attack_buff_trigger", "remove_on_attack_etc", "remove_on_attacked_spell_dot",
    "remove_on_attacked_etc_dot", "remove_on_attacked_buff_trigger", "remove_on_attacked_etc",
    "remove_on_damage_spell_dot", "remove_on_damage_etc_dot", "remove_on_damage_buff_trigger",
    "remove_on_damage_etc", "remove_on_damaged_spell_dot", "remove_on_damaged_etc_dot",
    "remove_on_damaged_buff_trigger", "remove_on_damaged_etc", "owner_only",
    "remove_on_autoattack", "save_rule_id", "idle_anim", "anti_stealth", "scale", "scaleDuration",
    "immune_except_creator", "find_school_of_fish_range",
    "anim_action_id", "dead_applicable", "tick_area_use_origin_source", "real_time",
    "do_not_remove_by_other_skill_controller", "cooldown_skill_time",
    "mana_burn_immune", "freeze_ship", "no_collide_rigid", "crowd_friendly", "crowd_hostile",
    "name_tr", "desc_tr", "no_exp_penalty"
]

# Boolean columns that need conversion from 0/1 to t/f
BOOLEAN_COLUMNS = {
    "silence", "root", "sleep", "stun", "crippled", "stealth", "remove_on_source_dead",
    "framehold", "ragdoll", "one_time", "taunt", "taunt_with_top_aggro", "remove_on_use_skill",
    "melee_immune", "spell_immune", "ranged_immune", "siege_immune", "knockback_immune",
    "per_unit_creation", "remove_on_move", "use_source_faction", "exempt", "psychokinesis",
    "no_collide", "remove_on_death", "combat_text_start", "combat_text_end", "conditional_tick",
    "system", "non_pushable", "detect_stealth", "remove_on_exempt", "remove_on_land", "gliding",
    "knock_down", "tick_area_exclude_source", "fall_damage_immune", "blank_minded", "fastened",
    "slave_applicable", "pacifist", "remove_on_interaction", "crime", "remove_on_unmount",
    "aura_child_only", "remove_on_mount", "remove_on_start_skill", "sprint_motion", "walk_only",
    "cannot_jump", "evade_telescope", "remove_on_attack_spell_dot", "remove_on_attack_etc_dot",
    "remove_on_attack_buff_trigger", "remove_on_attack_etc", "remove_on_attacked_spell_dot",
    "remove_on_attacked_etc_dot", "remove_on_attacked_buff_trigger", "remove_on_attacked_etc",
    "remove_on_damage_spell_dot", "remove_on_damage_etc_dot", "remove_on_damage_buff_trigger",
    "remove_on_damage_etc", "remove_on_damaged_spell_dot", "remove_on_damaged_etc_dot",
    "remove_on_damaged_buff_trigger", "remove_on_damaged_etc", "owner_only",
    "remove_on_autoattack", "anti_stealth", "immune_except_creator", "dead_applicable",
    "tick_area_use_origin_source", "real_time", "do_not_remove_by_other_skill_controller",
    "mana_burn_immune", "freeze_ship", "no_collide_rigid", "crowd_friendly", "crowd_hostile",
}

# Default values for specific columns (only for columns that truly need defaults)
DEFAULT_VALUES = {
    "name_tr": "t",
    "desc_tr": "t",
    "resurrection_per":"f",
    "group_id":"0",
    "anim_end_id":"",
    "resurrection_percent":"",
    "crime":'',
    "transform_buff_id":"",
    "no_exp_penalty":""
}

NULL_TO_EMPTY_COLUMNS = {
    "mainhand_tool_id", "offhand_tool_id", "tick_mainhand_tool_id", "tick_offhand_tool_id",
    "active_weapon_id", "custom_dual_material_id","transform_buff_id"
    "tube_instrument_tick_anim_id","percussion_instrument_tick_anim_id","string_instrument_tick_anim_id",
    "tube_instrument_start_anim_id","percussion_instrument_start_anim_id","string_instrument_start_anim_id",
    "custom_dual_material_id","aura_slave_buff_id","tick_anim_id","faction_id",
    "immune_buff_tag_id","required_buff_id","fx_group_id","link_buff_id","anim_start_id",
    "crowd_buff_id","immune_except_skill_tag_id","cooldown_skill_id"
}


def convert_value(col, value):
    """Handle NULL/boolean conversion based on column type"""
    if value is None:
        return ''  # Always convert NULL to empty string

    if col in BOOLEAN_COLUMNS:
        if isinstance(value, int):
            return 't' if value else 'f'
        if isinstance(value, str):
            return 't' if value.lower() in ('t', 'true', '1') else 'f'

    # Special handling for weapon/tool IDs - treat 0 as empty string
    if col in NULL_TO_EMPTY_COLUMNS and value == 0:
        return ''

    return value


def export():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Get column info
    cur.execute(f"PRAGMA table_info({TABLE});")
    available_columns = {col[1] for col in cur.fetchall()}

    # Determine export columns
    columns_in_db = [col for col in EXPORT_COLUMNS if col in available_columns]
    columns_missing = [col for col in EXPORT_COLUMNS if col not in available_columns]

    # Fetch data
    cur.execute(f"SELECT {', '.join(columns_in_db)} FROM {TABLE}")
    rows = cur.fetchall()

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(EXPORT_COLUMNS)

        for row in rows:
            row_dict = dict(zip(columns_in_db, row))
            output_row = {}

            for col in EXPORT_COLUMNS:
                if col in row_dict:
                    value = row_dict[col]
                    output_row[col] = convert_value(col, value)
                else:
                    output_row[col] = DEFAULT_VALUES.get(col, '')

            writer.writerow([output_row[col] for col in EXPORT_COLUMNS])

    print(f"✅ Exported {len(rows)} rows to {OUTPUT_CSV}")

export()