# ─────────────────────────────────────────────
# config.py — Shared application state + config file helpers
# ─────────────────────────────────────────────

import json
import os
from constants import (
    COL_MAP_FILE, PROVIDERS_FILE, DEFAULT_COL_MAP
)


# ─────────────────────────────────────────────
# COLUMN MAP HELPERS
# ─────────────────────────────────────────────
def load_col_map():
    if os.path.exists(COL_MAP_FILE):
        with open(COL_MAP_FILE) as f:
            saved = json.load(f)
        return {**DEFAULT_COL_MAP, **saved}
    return DEFAULT_COL_MAP.copy()

def save_col_map(mapping):
    os.makedirs(os.path.dirname(COL_MAP_FILE), exist_ok=True)
    with open(COL_MAP_FILE, "w") as f:
        json.dump(mapping, f, indent=2)


# ─────────────────────────────────────────────
# PROVIDER CONFIG HELPERS
# ─────────────────────────────────────────────
def load_provider_config():
    if os.path.exists(PROVIDERS_FILE):
        with open(PROVIDERS_FILE) as f:
            return json.load(f)
    return {"active": "mNotify", "sender_id": "Ben Alert"}

def save_provider_config(data):
    os.makedirs(os.path.dirname(PROVIDERS_FILE), exist_ok=True)
    with open(PROVIDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────
# SHARED APPLICATION STATE
# ─────────────────────────────────────────────
class AppState:
    # Data
    soon_expiring   = None
    api_key_global  = ""
    current_user    = None
    current_mode    = "dark"
    col_map         = load_col_map()
    provider_config = load_provider_config()

    # Widget references — set by main.py and each tab after build
    window           = None
    send_btn         = None
    conn_btn         = None
    disconnect_btn   = None
    status_bar       = None
    live_label       = None
    theme_btn        = None
    log_box          = None
    listbox_frame    = None
    users_list_frame = None
    detail_fields    = {}
    detail_name      = None
    ind_send_btn     = None
    ind_status       = None
    search_var       = None
    search_notice    = None
    search_status    = None
    preview_box      = None
    save_btn         = None
    load_btn         = None
    db_menu          = None
    host_entry       = None
    user_entry       = None
    pass_entry       = None
    db_entry         = None
    port_entry       = None
    api_entry        = None
    db_type_var      = None
    CONNECTION_WIDGETS = []

    # Search state
    user_search_results = None
    selected_row_idx    = None


state = AppState()
