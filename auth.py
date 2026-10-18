# ─────────────────────────────────────────────
# auth.py — User authentication via SQLite
# ─────────────────────────────────────────────

import hashlib
import sqlite3
import os
from constants import AUTH_DB


def init_auth_db():
    """Create users table and default admin account if not exists."""
    os.makedirs(os.path.dirname(AUTH_DB), exist_ok=True)
    con = sqlite3.connect(AUTH_DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    default_pw = hashlib.sha256("admin123".encode()).hexdigest()
    cur.execute("""
        INSERT OR IGNORE INTO users (username, password)
        VALUES ('admin', ?)
    """, (default_pw,))
    con.commit()
    con.close()


def verify_login(username, password):
    """Return True if credentials match a record in the DB."""
    hashed = hashlib.sha256(password.encode()).hexdigest()
    con = sqlite3.connect(AUTH_DB)
    cur = con.cursor()
    cur.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username, hashed)
    )
    result = cur.fetchone()
    con.close()
    return result is not None


def add_user(username, password):
    """Add a new user. Returns True on success, False if username exists."""
    hashed = hashlib.sha256(password.encode()).hexdigest()
    try:
        con = sqlite3.connect(AUTH_DB)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        return False


def change_password(username, new_password):
    """Update password for an existing user."""
    hashed = hashlib.sha256(new_password.encode()).hexdigest()
    con = sqlite3.connect(AUTH_DB)
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET password=? WHERE username=?",
        (hashed, username)
    )
    con.commit()
    con.close()
