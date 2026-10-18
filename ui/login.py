# ─────────────────────────────────────────────
# ui/login.py — Login window
# ─────────────────────────────────────────────

import customtkinter as ctk
from tkinter import BooleanVar, END

from constants import FONT_TITLE, FONT_LABEL, FONT_LABEL_B, FONT_ENTRY, FONT_BTN
from auth import verify_login
from config import state


def show_login():
    login_win = ctk.CTk()

    # CTkFont objects must be created after a window exists
    font_err    = ctk.CTkFont(family="Segoe UI", size=10,
                              weight="bold", slant="italic")
    font_status = ctk.CTkFont(family="Segoe UI", size=11, slant="italic")

    login_win.title("RenewMe — Login")
    login_win.geometry("380x460")
    login_win.minsize(340, 420)
    login_win.resizable(True, True)

    try:
        login_win.iconbitmap("RenewMe.ico")
    except Exception:
        pass

    # ── Header ──
    ctk.CTkLabel(login_win, text="🔐  RenewMe",
                 font=FONT_TITLE,
                 text_color="#e94560").pack(pady=(36, 4))
    ctk.CTkLabel(login_win, text="NHIS Renewal Notifier",
                 font=FONT_LABEL).pack(pady=(0, 20))

    # ── Form card ──
    form = ctk.CTkFrame(login_win, corner_radius=12)
    form.pack(padx=30, fill="x")

    ctk.CTkLabel(form, text="Username", font=FONT_LABEL_B,
                 anchor="w").pack(fill="x", padx=16, pady=(16, 2))
    uname_entry = ctk.CTkEntry(form, font=FONT_ENTRY,
                               placeholder_text="Enter username",
                               height=38, corner_radius=8)
    uname_entry.pack(fill="x", padx=16, pady=(0, 10))

    ctk.CTkLabel(form, text="Password", font=FONT_LABEL_B,
                 anchor="w").pack(fill="x", padx=16, pady=(4, 2))
    pw_entry = ctk.CTkEntry(form, font=FONT_ENTRY,
                            placeholder_text="Enter password",
                            show="*", height=38, corner_radius=8)
    pw_entry.pack(fill="x", padx=16, pady=(0, 6))

    show_pw_var = BooleanVar(value=False)
    def toggle_pw():
        pw_entry.configure(show="" if show_pw_var.get() else "*")

    ctk.CTkCheckBox(form, text="Show password", variable=show_pw_var,
                    command=toggle_pw, font=FONT_LABEL).pack(
                        anchor="w", padx=16, pady=(0, 4))

    err_label = ctk.CTkLabel(form, text="", font=font_err,
                             text_color="#e94560")
    err_label.pack(pady=(2, 0))

    login_success = {"ok": False}

    def attempt_login(event=None):
        u = uname_entry.get().strip()
        p = pw_entry.get()
        if not u or not p:
            err_label.configure(text="Please enter both fields.")
            return
        if verify_login(u, p):
            login_success["ok"] = True
            state.current_user  = u
            login_win.destroy()
        else:
            err_label.configure(text="Invalid username or password.")
            pw_entry.delete(0, END)

    ctk.CTkButton(form, text="Login", font=FONT_BTN,
                  fg_color="#e94560", hover_color="#c73652",
                  height=42, corner_radius=8,
                  command=attempt_login).pack(
                      fill="x", padx=16, pady=(10, 18))

    pw_entry.bind("<Return>", attempt_login)
    uname_entry.bind("<Return>", attempt_login)

    login_win.mainloop()
    return login_success["ok"]
