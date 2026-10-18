# ─────────────────────────────────────────────
# ui/connection_tab.py — Connection tab
# ─────────────────────────────────────────────

import customtkinter as ctk
from tkinter import StringVar, END

from constants import (
    DB_TYPES, FONT_LABEL, FONT_LABEL_B, FONT_ENTRY,
    FONT_BTN, FONT_BTN_SM, FONT_HEADER, FONT_ERR
)
from config import state
from utils import save_credentials, load_credentials
from database import connect_database, disconnect_database
from sms import send_notifications
from auth import add_user, change_password


def build(parent):
    """Build the Connection tab and register widgets into state."""
    conn_scroll = ctk.CTkScrollableFrame(parent)
    conn_scroll.pack(fill="both", expand=True)

    def make_row(label_text, show=None, placeholder=""):
        ctk.CTkLabel(conn_scroll, text=label_text, font=FONT_LABEL,
                     anchor="w").pack(fill="x", padx=16, pady=(8, 0))
        e = ctk.CTkEntry(conn_scroll, font=FONT_ENTRY, height=36,
                         corner_radius=8, placeholder_text=placeholder)
        if show:
            e.configure(show=show)
        e.pack(fill="x", padx=16, pady=(2, 0))
        return e

    # DB type
    ctk.CTkLabel(conn_scroll, text="Database Type", font=FONT_LABEL,
                 anchor="w").pack(fill="x", padx=16, pady=(12, 0))
    state.db_type_var = StringVar(value="MySQL")
    state.db_menu = ctk.CTkOptionMenu(conn_scroll, variable=state.db_type_var,
                                      values=DB_TYPES, font=FONT_ENTRY,
                                      height=36, corner_radius=8)
    state.db_menu.pack(fill="x", padx=16, pady=(2, 0))

    state.host_entry = make_row("Database Host", placeholder="localhost")
    state.host_entry.insert(0, "localhost")

    state.user_entry = make_row("Database User", placeholder="root")
    state.user_entry.insert(0, "root")

    state.pass_entry = make_row("Database Password", show="*")
    state.db_entry   = make_row("Database Name", placeholder="my_database")
    state.db_entry.insert(0, "ben")

    state.port_entry = make_row("Database Port", placeholder="3306")
    state.port_entry.insert(0, "3306")

    state.api_entry  = make_row("mNotify API Key", show="*",
                                placeholder="Your API key")

    # Register lockable widgets
    state.CONNECTION_WIDGETS = [
        state.db_menu, state.host_entry, state.user_entry,
        state.pass_entry, state.db_entry, state.port_entry,
        state.api_entry
    ]

    # Credential buttons
    cred_row = ctk.CTkFrame(conn_scroll, fg_color="transparent")
    cred_row.pack(fill="x", padx=16, pady=(10, 4))

    state.save_btn = ctk.CTkButton(cred_row, text="💾  Save Creds",
                                   font=FONT_BTN_SM, width=130, height=34,
                                   corner_radius=8, command=save_credentials)
    state.save_btn.pack(side="left", padx=(0, 8))

    state.load_btn = ctk.CTkButton(cred_row, text="📂  Load Creds",
                                   font=FONT_BTN_SM, width=130, height=34,
                                   corner_radius=8, command=load_credentials)
    state.load_btn.pack(side="left", padx=(0, 8))

    # Manage users button
    manage_btn = ctk.CTkButton(cred_row, text="👤  Manage Users",
                               font=FONT_BTN_SM, width=140, height=34,
                               corner_radius=8, command=_show_user_manager)
    manage_btn.pack(side="left")

    # Connect / Disconnect / Send
    state.conn_btn = ctk.CTkButton(
        conn_scroll, text="⚡  Connect & Load Expiring Users",
        font=FONT_BTN, height=44, corner_radius=10,
        command=connect_database)
    state.conn_btn.pack(fill="x", padx=16, pady=(12, 4))

    state.disconnect_btn = ctk.CTkButton(
        conn_scroll, text="🔌  Disconnect",
        font=FONT_BTN, height=44, corner_radius=10,
        fg_color="#e94560", hover_color="#c73652",
        state="disabled", command=disconnect_database)
    state.disconnect_btn.pack(fill="x", padx=16, pady=(0, 4))

    state.send_btn = ctk.CTkButton(
        conn_scroll, text="📤  Send Notifications",
        font=FONT_BTN, height=44, corner_radius=10,
        fg_color="gray40", hover_color="gray30",
        state="disabled", command=send_notifications)
    state.send_btn.pack(fill="x", padx=16, pady=(0, 10))

    # Expiring users list
    ctk.CTkLabel(conn_scroll, text="Expiring Users",
                 font=FONT_LABEL_B, anchor="w").pack(
                     fill="x", padx=16, pady=(4, 2))
    state.listbox_frame = ctk.CTkScrollableFrame(conn_scroll, height=160,
                                                  corner_radius=8)
    state.listbox_frame.pack(fill="x", padx=16, pady=(0, 10))


def _show_user_manager():
    um = ctk.CTkToplevel(state.window)
    um.title("Manage Users")
    um.geometry("340x360")
    um.resizable(False, False)
    um.grab_set()

    ctk.CTkLabel(um, text="Add New User", font=FONT_HEADER).pack(pady=(16, 6))

    ctk.CTkLabel(um, text="Username", font=FONT_LABEL,
                 anchor="w").pack(fill="x", padx=20)
    new_uname = ctk.CTkEntry(um, font=FONT_ENTRY, height=34, corner_radius=8)
    new_uname.pack(fill="x", padx=20, pady=(2, 8))

    ctk.CTkLabel(um, text="Password", font=FONT_LABEL,
                 anchor="w").pack(fill="x", padx=20)
    new_pw = ctk.CTkEntry(um, font=FONT_ENTRY, show="*",
                          height=34, corner_radius=8)
    new_pw.pack(fill="x", padx=20, pady=(2, 6))

    msg = ctk.CTkLabel(um, text="", font=FONT_ERR)
    msg.pack()

    def do_add():
        u = new_uname.get().strip()
        p = new_pw.get()
        if not u or not p:
            msg.configure(text="Both fields required.", text_color="#e94560")
            return
        if add_user(u, p):
            msg.configure(text=f"User '{u}' added.", text_color="#00ff88")
            new_uname.delete(0, END)
            new_pw.delete(0, END)
        else:
            msg.configure(text=f"'{u}' already exists.", text_color="#e94560")

    ctk.CTkButton(um, text="Add User", font=FONT_BTN,
                  height=36, corner_radius=8,
                  command=do_add).pack(fill="x", padx=20, pady=8)

    ctk.CTkLabel(um, text="─── Change Your Password ───",
                 font=FONT_LABEL, text_color="gray").pack(pady=(6, 2))
    new_pw2 = ctk.CTkEntry(um, font=FONT_ENTRY, show="*",
                           height=34, corner_radius=8)
    new_pw2.pack(fill="x", padx=20, pady=(2, 6))

    def do_change():
        p = new_pw2.get()
        if not p:
            msg.configure(text="Enter a new password.", text_color="#e94560")
            return
        change_password(state.current_user, p)
        msg.configure(text="Password updated.", text_color="#00ff88")
        new_pw2.delete(0, END)

    ctk.CTkButton(um, text="Change Password", font=FONT_BTN_SM,
                  height=34, corner_radius=8,
                  command=do_change).pack(fill="x", padx=20)
