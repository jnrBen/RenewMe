# ─────────────────────────────────────────────
# utils.py — Utility functions
# ─────────────────────────────────────────────

import socket
import json
import os
import keyring
from datetime import datetime
from tkinter import messagebox, END

from constants import CREDS_FILE, KEYRING_SVC, LOG_FILE
from config import state


# ─────────────────────────────────────────────
# PHONE
# ─────────────────────────────────────────────
def format_phone_number(phone_number):
    phone = str(phone_number).strip()
    if phone.startswith("+233") and len(phone) == 13:
        return phone
    elif phone.startswith("0") and len(phone) == 10:
        return "+233" + phone[1:]
    elif len(phone) == 9 and phone.isdigit():
        return "+233" + phone
    return None


# ─────────────────────────────────────────────
# INTERNET
# ─────────────────────────────────────────────
def check_internet_connection():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False


# ─────────────────────────────────────────────
# SMS LOG
# ─────────────────────────────────────────────
def log_sms(name, phone, days_left, status, reason=""):
    """Write one SMS log entry to file and mirror to the log widget."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"[{timestamp}] | Name: {name} | Phone: {phone} "
        f"| Days Left: {days_left} | Status: {status}"
    )
    if reason:
        line += f" | Reason: {reason}"
    line += "\n"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    append_log(line)


def append_log(text):
    """Thread-safe append to the log textbox widget."""
    if state.log_box is None:
        return
    state.log_box.configure(state="normal")
    state.log_box.insert(END, text)
    state.log_box.see(END)
    state.log_box.configure(state="disabled")


# ─────────────────────────────────────────────
# CREDENTIALS
# ─────────────────────────────────────────────
def save_credentials():
    data = {
        "host":    state.host_entry.get(),
        "user":    state.user_entry.get(),
        "db":      state.db_entry.get(),
        "port":    state.port_entry.get(),
        "db_type": state.db_type_var.get(),
    }
    os.makedirs(os.path.dirname(CREDS_FILE), exist_ok=True)
    with open(CREDS_FILE, "w") as f:
        json.dump(data, f)
    keyring.set_password(KEYRING_SVC, "db_password", state.pass_entry.get())
    keyring.set_password(KEYRING_SVC, "api_key",     state.api_entry.get())
    messagebox.showinfo("Saved", "Credentials saved securely.")


def load_credentials():
    if os.path.exists(CREDS_FILE):
        with open(CREDS_FILE) as f:
            data = json.load(f)
        state.host_entry.delete(0, END)
        state.host_entry.insert(0, data.get("host", ""))
        state.user_entry.delete(0, END)
        state.user_entry.insert(0, data.get("user", ""))
        state.db_entry.delete(0, END)
        state.db_entry.insert(0, data.get("db", ""))
        state.port_entry.delete(0, END)
        state.port_entry.insert(0, data.get("port", ""))
        state.db_type_var.set(data.get("db_type", "MySQL"))
    pw  = keyring.get_password(KEYRING_SVC, "db_password") or ""
    api = keyring.get_password(KEYRING_SVC, "api_key")     or ""
    state.pass_entry.delete(0, END)
    state.pass_entry.insert(0, pw)
    state.api_entry.delete(0, END)
    state.api_entry.insert(0, api)
