# ─────────────────────────────────────────────
# ui/users_tab.py — Users tab
# ─────────────────────────────────────────────

import threading
import pandas as pd
import customtkinter as ctk
from tkinter import StringVar

from constants import (
    FONT_LABEL, FONT_LABEL_B, FONT_ENTRY,
    FONT_BTN, FONT_BTN_SM, FONT_HEADER, FONT_STATUS
)
from config import state
from database import search_database
from sms import send_individual


def build(parent):
    """Build the Users tab and register widgets into state."""

    # ── Search bar ──
    search_frame = ctk.CTkFrame(parent, fg_color="transparent")
    search_frame.pack(fill="x", padx=14, pady=(10, 4))

    ctk.CTkLabel(search_frame, text="Search by:",
                 font=FONT_LABEL_B).pack(side="left", padx=(0, 6))

    state.search_param_var = StringVar(value="Name")
    ctk.CTkOptionMenu(search_frame, variable=state.search_param_var,
                      values=["Name", "Phone Number", "Membership No",
                              "Date of Birth", "Email"],
                      font=FONT_ENTRY, width=160,
                      height=34, corner_radius=8).pack(side="left", padx=(0, 8))

    state.search_var   = StringVar()
    search_entry = ctk.CTkEntry(search_frame, textvariable=state.search_var,
                                font=FONT_ENTRY, width=200, height=34,
                                corner_radius=8,
                                placeholder_text="Search term…")
    search_entry.pack(side="left", padx=(0, 8))

    state.search_status = ctk.CTkLabel(search_frame, text="", font=FONT_STATUS)
    state.search_status.pack(side="left")

    state.search_notice = ctk.CTkLabel(parent, text="Showing: expiring users",
                                       font=FONT_STATUS, anchor="w")
    state.search_notice.pack(fill="x", padx=14, pady=(0, 2))

    # ── Main pane: list left, detail right ──
    users_pane = ctk.CTkFrame(parent, fg_color="transparent")
    users_pane.pack(fill="both", expand=True, padx=14, pady=4)
    users_pane.columnconfigure(0, weight=2)
    users_pane.columnconfigure(1, weight=3)
    users_pane.rowconfigure(0, weight=1)

    state.users_list_frame = ctk.CTkScrollableFrame(
        users_pane, corner_radius=8, label_text="Members")
    state.users_list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

    detail_frame = ctk.CTkFrame(users_pane, corner_radius=10)
    detail_frame.grid(row=0, column=1, sticky="nsew")

    state.detail_name = ctk.CTkLabel(detail_frame, text="Select a member",
                                     font=FONT_HEADER, anchor="w")
    state.detail_name.pack(fill="x", padx=14, pady=(14, 6))

    state.detail_fields = {}
    for field in ["Membership No", "Date of Birth", "Email",
                  "Phone", "Days Left", "Expiry Date"]:
        row_f = ctk.CTkFrame(detail_frame, fg_color="transparent")
        row_f.pack(fill="x", padx=14, pady=3)
        ctk.CTkLabel(row_f, text=f"{field}:", font=FONT_LABEL_B,
                     width=130, anchor="w").pack(side="left")
        val = ctk.CTkLabel(row_f, text="—", font=FONT_LABEL, anchor="w")
        val.pack(side="left")
        state.detail_fields[field] = val

    state.ind_send_btn = ctk.CTkButton(
        detail_frame, text="📨  Send Reminder",
        font=FONT_BTN, height=40, corner_radius=8,
        fg_color="#e94560", hover_color="#c73652",
        state="disabled", command=send_individual)
    state.ind_send_btn.pack(fill="x", padx=14, pady=(16, 4))

    state.ind_status = ctk.CTkLabel(detail_frame, text="",
                                    font=FONT_STATUS, anchor="w")
    state.ind_status.pack(fill="x", padx=14)

    # Search action buttons
    clear_btn = ctk.CTkButton(search_frame, text="✕",
                              font=FONT_BTN_SM, width=36, height=34,
                              corner_radius=8, fg_color="gray40",
                              hover_color="gray30",
                              command=clear_search)
    clear_btn.pack(side="left", padx=(0, 4))

    search_btn = ctk.CTkButton(search_frame, text="🔍  Search",
                               font=FONT_BTN_SM, width=110, height=34,
                               corner_radius=8, command=run_search)
    search_btn.pack(side="left")

    search_entry.bind("<Return>", lambda e: run_search())


# ─────────────────────────────────────────────
# POPULATION HELPERS
# ─────────────────────────────────────────────
def populate_users_tab():
    """Rebuild the users list with expiring users."""
    state.user_search_results = None
    for w in state.users_list_frame.winfo_children():
        w.destroy()
    if state.soon_expiring is None or state.soon_expiring.empty:
        return
    for i, (_, row) in enumerate(state.soon_expiring.iterrows()):
        btn = ctk.CTkButton(
            state.users_list_frame,
            text=f"  {row['name']}  ({int(row['days_left'])}d)",
            font=FONT_ENTRY, anchor="w", height=32,
            fg_color="transparent",
            hover_color=("gray80", "gray25"),
            text_color=("gray10", "gray90"),
            command=lambda idx=i: select_user(idx, None)
        )
        btn.pack(fill="x", pady=1)


def _populate_from_results(results):
    """Rebuild the users list from search results."""
    for w in state.users_list_frame.winfo_children():
        w.destroy()
    for i, (_, row) in enumerate(results.iterrows()):
        days = int(row['days_left']) if pd.notna(row.get('days_left')) else "—"
        tag  = f"{days}d" if isinstance(days, int) else days
        btn = ctk.CTkButton(
            state.users_list_frame,
            text=f"  {row['name']}  |  {row['phone_number']}  ({tag})",
            font=FONT_ENTRY, anchor="w", height=32,
            fg_color="transparent",
            hover_color=("gray80", "gray25"),
            text_color=("gray10", "gray90"),
            command=lambda idx=i: select_user(idx, results)
        )
        btn.pack(fill="x", pady=1)


def select_user(idx, source_override):
    state.selected_row_idx = idx
    source = source_override
    if source is None:
        source = state.user_search_results
    if source is None:
        source = state.soon_expiring
    if source is None or source.empty or idx >= len(source):
        return

    row = source.iloc[idx]
    state.detail_name.configure(text=row['name'])
    state.detail_fields["Membership No"].configure(
        text=str(row.get('membership_number', '—')))
    state.detail_fields["Date of Birth"].configure(
        text=str(row['dob'])[:10] if pd.notna(row.get('dob')) else '—')
    state.detail_fields["Email"].configure(text=str(row.get('email', '—')))
    state.detail_fields["Phone"].configure(text=str(row['phone_number']))
    days = int(row['days_left']) if pd.notna(row.get('days_left')) else "—"
    state.detail_fields["Days Left"].configure(
        text=f"{days} days" if isinstance(days, int) else str(days))
    state.detail_fields["Expiry Date"].configure(
        text=str(row['end_date'])[:10] if pd.notna(row.get('end_date')) else '—')
    state.ind_send_btn.configure(state="normal")
    state.ind_status.configure(text="")


# ─────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────
def run_search():
    term  = state.search_var.get().strip()
    field = state.search_param_var.get()

    if not term:
        populate_users_tab()
        state.search_notice.configure(text="Showing: expiring users")
        state.search_status.configure(text="")
        return

    state.search_status.configure(text="Searching…")
    state.window.update_idletasks()

    def _worker():
        results = search_database(field, term)
        if results is None:
            state.search_status.configure(text="Search failed.")
            return
        state.user_search_results = results
        if results.empty:
            state.search_status.configure(text="No results found.")
            state.search_notice.configure(
                text=f"Showing: results for '{term}' — 0 found")
            for w in state.users_list_frame.winfo_children():
                w.destroy()
            return
        _populate_from_results(results)
        state.search_status.configure(text=f"{len(results)} result(s) found.")
        state.search_notice.configure(
            text=f"Showing: results for '{term}' — {len(results)} found")

    threading.Thread(target=_worker, daemon=True).start()


def clear_search():
    state.search_var.set("")
    populate_users_tab()
    state.search_notice.configure(text="Showing: expiring users")
    state.search_status.configure(text="")
