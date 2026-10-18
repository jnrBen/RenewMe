# ─────────────────────────────────────────────
# ui/log_tab.py — SMS Log tab
# ─────────────────────────────────────────────

import os
import customtkinter as ctk
from tkinter import END

from constants import LOG_FILE, FONT_HEADER, FONT_BTN_SM, FONT_LOG
from config import state


def build(parent):
    """Build the SMS Log tab and register log_box into state."""
    ctk.CTkLabel(parent, text="SMS Delivery Log",
                 font=FONT_HEADER, anchor="w").pack(
                     fill="x", padx=14, pady=(10, 4))

    state.log_box = ctk.CTkTextbox(parent, font=FONT_LOG,
                                   corner_radius=8, state="disabled")
    state.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 4))

    # Load existing log on startup
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding="utf-8") as f:
            existing = f.read()
        if existing:
            state.log_box.configure(state="normal")
            state.log_box.insert(END, existing)
            state.log_box.configure(state="disabled")

    ctk.CTkButton(parent, text="🗑  Clear Log", font=FONT_BTN_SM,
                  width=140, height=34, corner_radius=8,
                  fg_color="#e94560", hover_color="#c73652",
                  command=_clear_log).pack(pady=(0, 8))


def _clear_log():
    state.log_box.configure(state="normal")
    state.log_box.delete("1.0", END)
    state.log_box.configure(state="disabled")
    open(LOG_FILE, "w").close()
