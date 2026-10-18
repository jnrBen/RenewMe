# ─────────────────────────────────────────────
# constants.py — Static constants, fonts, config keys
# ─────────────────────────────────────────────

APP_NAME       = "RenewMe"
LOG_FILE       = "data/sms_log.txt"
CREDS_FILE     = "data/saved_creds.json"
COL_MAP_FILE   = "data/column_map.json"
PROVIDERS_FILE = "data/providers.json"
AUTH_DB        = "data/renewme_users.db"
KEYRING_SVC    = "RenewMe"

DB_TYPES = ["MySQL", "PostgreSQL", "Microsoft SQL Server"]

DEFAULT_COL_MAP = {
    "table_name":        "insurance_data",
    "name":              "name",
    "phone_number":      "phone_number",
    "end_date":          "end_date",
    "membership_number": "membership_number",
    "dob":               "dob",
    "email":             "email",
}

FIELD_LABELS = {
    "table_name":        "Table Name",
    "name":              "Member Name",
    "phone_number":      "Phone Number",
    "end_date":          "Policy End Date",
    "membership_number": "Membership Number",
    "dob":               "Date of Birth",
    "email":             "Email Address",
}

PROVIDER_FIELDS = {
    "mNotify": [
        {"key": "api_key",   "label": "API Key",   "secret": True},
        {"key": "sender_id", "label": "Sender ID", "secret": False},
    ],
    "Hubtel": [
        {"key": "client_id",     "label": "Client ID",     "secret": False},
        {"key": "client_secret", "label": "Client Secret", "secret": True},
        {"key": "sender_id",     "label": "Sender ID",     "secret": False},
    ],
    "Africa's Talking": [
        {"key": "api_key",   "label": "API Key",   "secret": True},
        {"key": "username",  "label": "Username",  "secret": False},
        {"key": "sender_id", "label": "Sender ID", "secret": False},
    ],
    "Twilio": [
        {"key": "account_sid", "label": "Account SID", "secret": False},
        {"key": "auth_token",  "label": "Auth Token",  "secret": True},
        {"key": "from_number", "label": "From Number", "secret": False},
    ],
    "Custom": [
        {"key": "endpoint",     "label": "API Endpoint URL",           "secret": False},
        {"key": "auth_method",  "label": "Auth Method (header/param)", "secret": False},
        {"key": "auth_value",   "label": "Auth Value / Token",         "secret": True},
        {"key": "sender_id",    "label": "Sender ID",                  "secret": False},
        {"key": "extra_fields", "label": "Extra Fields (JSON)",        "secret": False},
    ],
}

PROVIDER_NAMES = list(PROVIDER_FIELDS.keys())

# ─────────────────────────────────────────────
# FONTS — defined as tuples (CTkFont assigned in main after window exists)
# ─────────────────────────────────────────────
FONT_TITLE   = ("Segoe UI", 20, "bold")
FONT_HEADER  = ("Segoe UI", 13, "bold")
FONT_LABEL   = ("Segoe UI", 12)
FONT_LABEL_B = ("Segoe UI", 12, "bold")
FONT_BTN     = ("Segoe UI", 12, "bold")
FONT_BTN_SM  = ("Segoe UI", 11, "bold")
FONT_ENTRY   = ("Segoe UI", 12)
FONT_STATUS  = ("Segoe UI", 11)
FONT_DETAIL  = ("Segoe UI", 11, "bold")
FONT_LOG     = ("Consolas", 11)
FONT_ERR     = ("Segoe UI", 10, "bold")
