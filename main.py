# ─────────────────────────────────────────────
# main.py — Entry point for RenewMe
# ─────────────────────────────────────────────


import sys
import ctypes
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from constants import FONT_LABEL, FONT_LABEL_B, FONT_BTN_SM, FONT_STATUS
from config import state
from auth import init_auth_db
from utils import check_internet_connection
from ui.login import show_login
import ui.connection_tab as connection_tab
import ui.log_tab        as log_tab
import ui.users_tab      as users_tab
import ui.customize_tab  as customize_tab


# ─────────────────────────────────────────────
# INIT AUTH DB
# ─────────────────────────────────────────────
init_auth_db()

# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
if not show_login():
    sys.exit()

# ─────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────
window = ctk.CTk()
window.title("RenewMe — NHIS Renewal Notifier")
window.geometry("700x760")
window.minsize(520, 600)
window.resizable(True, True)
window.update()

state.window = window

try:
    window.iconbitmap("RenewMe.ico")
    myappid = "ben.alert.renewme"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# ─────────────────────────────────────────────
# TOP BAR
# ─────────────────────────────────────────────
top_bar = ctk.CTkFrame(window, height=100, corner_radius=0)
top_bar.pack(fill="x", side="top")
top_bar.pack_propagate(False)

# Row 1 — live indicator, username, theme toggle
info_row = ctk.CTkFrame(top_bar, fg_color="transparent", height=38)
info_row.pack(fill="x", side="top")
info_row.pack_propagate(False)

state.live_label = ctk.CTkLabel(info_row, text="Checking…", font=FONT_LABEL_B)
state.live_label.pack(side="left", padx=14)

def toggle_theme():
    if state.current_mode == "dark":
        state.current_mode = "light"
        ctk.set_appearance_mode("light")
        state.theme_btn.configure(text="🌙  Dark Mode")
    else:
        state.current_mode = "dark"
        ctk.set_appearance_mode("dark")
        state.theme_btn.configure(text="☀  Light Mode")

state.theme_btn = ctk.CTkButton(
    info_row, text="☀  Light Mode",
    font=FONT_BTN_SM, width=130,
    fg_color="transparent",
    hover_color=("gray80", "gray25"),
    command=toggle_theme)
state.theme_btn.pack(side="right", padx=10, pady=4)

ctk.CTkLabel(info_row, text=f"👤  {state.current_user}",
             font=FONT_LABEL).pack(side="right", padx=6)

# Row 2 — navigation buttons
nav_row = ctk.CTkFrame(top_bar, fg_color="transparent", height=46)
nav_row.pack(fill="x", side="top")
nav_row.pack_propagate(False)

nav_inner = ctk.CTkFrame(nav_row, fg_color="transparent")
nav_inner.place(relx=0.5, rely=0.5, anchor="center")

# ─────────────────────────────────────────────
# CONTENT AREA & TAB FRAMES
# ─────────────────────────────────────────────
content_area = ctk.CTkFrame(window, corner_radius=0, fg_color="transparent")
content_area.pack(fill="both", expand=True, padx=12, pady=(4, 4), side="top")

tab_conn      = ctk.CTkFrame(content_area, corner_radius=10)
tab_log       = ctk.CTkFrame(content_area, corner_radius=10)
tab_users     = ctk.CTkFrame(content_area, corner_radius=10)
tab_customize = ctk.CTkFrame(content_area, corner_radius=10)

all_tabs = [tab_conn, tab_log, tab_users, tab_customize]

# ─────────────────────────────────────────────
# TAB CONTENT
# ─────────────────────────────────────────────
connection_tab.build(tab_conn)
log_tab.build(tab_log)
users_tab.build(tab_users)
customize_tab.build(tab_customize)

# ─────────────────────────────────────────────
# NAV BUTTONS
# ─────────────────────────────────────────────
tab_buttons = {}

NAV_ITEMS = [
    ("⚙   Connection", tab_conn),
    ("📋  SMS Log",     tab_log),
    ("👥  Users",       tab_users),
    ("🛠  Customize",   tab_customize),
]

for label, tab in NAV_ITEMS:
    btn = ctk.CTkButton(
        nav_inner,
        text=label,
        font=FONT_BTN_SM,
        width=150, height=34,
        corner_radius=8,
        fg_color="transparent",
        hover_color=("gray80", "gray25"),
        command=lambda t=tab: show_tab(t)
    )
    btn.pack(side="left", padx=4)
    tab_buttons[btn] = tab


def show_tab(tab):
    for t in all_tabs:
        t.pack_forget()
    tab.pack(fill="both", expand=True)
    for btn, t in tab_buttons.items():
        if t == tab:
            btn.configure(fg_color=("#3B8ED0", "#1F6AA5"))
        else:
            btn.configure(fg_color="transparent")


# Show Connection tab on launch
show_tab(tab_conn)

# ─────────────────────────────────────────────
# STATUS BAR
# ─────────────────────────────────────────────
state.status_bar = ctk.CTkLabel(window, text="Ready.",
                                font=FONT_STATUS, anchor="w")
state.status_bar.pack(fill="x", side="top", padx=14, pady=(2, 6))

# ─────────────────────────────────────────────
# LIVE INDICATOR LOOP
# ─────────────────────────────────────────────
def on_closing():
    """Cleanly shut down all scheduled callbacks before destroying the window."""
    try:
        window.after_cancel(live_status_id)
    except Exception:
        pass
    window.quit()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

live_status_id = None

def update_live_status():
    global live_status_id
    if check_internet_connection():
        state.live_label.configure(text="●  LIVE", text_color="#00ff88")
    else:
        state.live_label.configure(text="●  OFFLINE", text_color="#e94560")
    live_status_id = window.after(5000, update_live_status)

update_live_status()
window.mainloop()
