# ─────────────────────────────────────────────
# ui/customize_tab.py — Customize tab (column mapping + provider)
# ─────────────────────────────────────────────

import keyring
import customtkinter as ctk
from tkinter import StringVar, END

from constants import (
    FONT_LABEL, FONT_LABEL_B, FONT_ENTRY, FONT_LOG,
    FONT_BTN_SM, FONT_STATUS,
    FIELD_LABELS, DEFAULT_COL_MAP,
    PROVIDER_FIELDS, PROVIDER_NAMES, KEYRING_SVC
)
from config import state, save_col_map, save_provider_config


def build(parent):
    """Build the Customize tab with mapping/provider toggle."""
    customize_scroll = ctk.CTkScrollableFrame(parent)
    customize_scroll.pack(fill="both", expand=True)

    # ── Toggle buttons ──
    toggle_frame = ctk.CTkFrame(customize_scroll, fg_color="transparent")
    toggle_frame.pack(fill="x", padx=14, pady=(14, 8))

    mapping_section        = ctk.CTkFrame(customize_scroll, fg_color="transparent")
    provider_section_frame = ctk.CTkFrame(customize_scroll, fg_color="transparent")

    # Forward-declare so both functions can reference each other's button
    mapping_toggle_btn_ref  = {}
    provider_toggle_btn_ref = {}

    def show_mapping_section():
        provider_section_frame.pack_forget()
        mapping_section.pack(fill="both", expand=True)
        mapping_toggle_btn_ref["btn"].configure(fg_color=("#3B8ED0", "#1F6AA5"))
        provider_toggle_btn_ref["btn"].configure(fg_color="transparent")

    def show_provider_section():
        mapping_section.pack_forget()
        provider_section_frame.pack(fill="both", expand=True)
        provider_toggle_btn_ref["btn"].configure(fg_color=("#3B8ED0", "#1F6AA5"))
        mapping_toggle_btn_ref["btn"].configure(fg_color="transparent")

    m_btn = ctk.CTkButton(toggle_frame, text="🗂  Column Mapping",
                          font=FONT_BTN_SM, width=180, height=36,
                          corner_radius=8,
                          fg_color=("#3B8ED0", "#1F6AA5"),
                          hover_color=("gray80", "gray25"),
                          command=show_mapping_section)
    m_btn.pack(side="left", padx=(0, 8))
    mapping_toggle_btn_ref["btn"] = m_btn

    p_btn = ctk.CTkButton(toggle_frame, text="📡  API Provider",
                          font=FONT_BTN_SM, width=180, height=36,
                          corner_radius=8,
                          fg_color="transparent",
                          hover_color=("gray80", "gray25"),
                          command=show_provider_section)
    p_btn.pack(side="left")
    provider_toggle_btn_ref["btn"] = p_btn

    # ─────────────────────────
    #  MAPPING SECTION
    # ─────────────────────────
    ctk.CTkLabel(mapping_section,
                 text="Map your database column names to app fields.",
                 font=FONT_LABEL, anchor="w").pack(
                     fill="x", padx=14, pady=(4, 0))
    ctk.CTkLabel(mapping_section,
                 text="Leave a field as-is if your column name already matches.",
                 font=("Segoe UI", 11), text_color="gray",
                 anchor="w").pack(fill="x", padx=14, pady=(0, 8))

    col_entries = {}
    map_frame   = ctk.CTkFrame(mapping_section, fg_color="transparent")
    map_frame.pack(fill="x", padx=14, pady=4)

    for app_field, friendly in FIELD_LABELS.items():
        row_f = ctk.CTkFrame(map_frame, fg_color="transparent")
        row_f.pack(fill="x", pady=4)
        ctk.CTkLabel(row_f, text=friendly, font=FONT_LABEL_B,
                     width=180, anchor="w").pack(side="left")
        ctk.CTkLabel(row_f, text="→", font=FONT_LABEL,
                     text_color="gray").pack(side="left", padx=8)
        e = ctk.CTkEntry(row_f, font=FONT_ENTRY, height=32,
                         corner_radius=8, width=200)
        e.insert(0, state.col_map.get(app_field, app_field))
        e.pack(side="left")
        col_entries[app_field] = e

    map_msg = ctk.CTkLabel(mapping_section, text="",
                           font=FONT_STATUS, anchor="w")
    map_msg.pack(fill="x", padx=14, pady=(4, 0))

    map_btn_row = ctk.CTkFrame(mapping_section, fg_color="transparent")
    map_btn_row.pack(fill="x", padx=14, pady=(4, 8))

    def do_save_col_map():
        state.col_map = {
            field: entry.get().strip() or DEFAULT_COL_MAP[field]
            for field, entry in col_entries.items()
        }
        save_col_map(state.col_map)
        map_msg.configure(text="Mappings saved. Reconnect to apply.",
                          text_color="#00ff88")
        refresh_preview()

    def do_reset_col_map():
        state.col_map = DEFAULT_COL_MAP.copy()
        for field, entry in col_entries.items():
            entry.delete(0, END)
            entry.insert(0, state.col_map[field])
        save_col_map(state.col_map)
        map_msg.configure(text="Reset to defaults.", text_color="#00ff88")
        refresh_preview()

    ctk.CTkButton(map_btn_row, text="💾  Save Mappings",
                  font=FONT_BTN_SM, width=150, height=34,
                  corner_radius=8,
                  command=do_save_col_map).pack(side="left", padx=(0, 10))

    ctk.CTkButton(map_btn_row, text="Reset to Defaults",
                  font=FONT_BTN_SM, width=160, height=34,
                  corner_radius=8, fg_color="gray40", hover_color="gray30",
                  command=do_reset_col_map).pack(side="left")

    ctk.CTkLabel(mapping_section, text="── Live Column Preview",
                 font=FONT_LABEL_B, anchor="w").pack(
                     fill="x", padx=14, pady=(8, 2))

    state.preview_box = ctk.CTkTextbox(mapping_section, font=FONT_LOG,
                                       corner_radius=8, height=180,
                                       state="disabled")
    state.preview_box.pack(fill="x", padx=14, pady=(0, 8))

    # ─────────────────────────
    #  PROVIDER SECTION
    # ─────────────────────────
    ctk.CTkLabel(provider_section_frame,
                 text="Select your SMS provider and enter its credentials.",
                 font=FONT_LABEL, anchor="w").pack(
                     fill="x", padx=14, pady=(4, 0))
    ctk.CTkLabel(provider_section_frame,
                 text="Credentials are stored securely in your system keyring.",
                 font=("Segoe UI", 11), text_color="gray",
                 anchor="w").pack(fill="x", padx=14, pady=(0, 8))

    provider_var = StringVar(
        value=state.provider_config.get("active", "mNotify"))

    provider_fields_frame = ctk.CTkFrame(provider_section_frame,
                                         fg_color="transparent")
    provider_fields_frame.pack(fill="x", padx=14)

    provider_entries = {}

    provider_msg = ctk.CTkLabel(provider_section_frame, text="",
                                font=FONT_STATUS, anchor="w")
    provider_msg.pack(fill="x", padx=14, pady=(6, 0))

    def render_provider_fields(provider):
        for w in provider_fields_frame.winfo_children():
            w.destroy()
        provider_entries.clear()
        for field in PROVIDER_FIELDS.get(provider, []):
            ctk.CTkLabel(provider_fields_frame, text=field["label"],
                         font=FONT_LABEL, anchor="w").pack(
                             fill="x", pady=(4, 0))
            e = ctk.CTkEntry(provider_fields_frame, font=FONT_ENTRY,
                             height=34, corner_radius=8,
                             show="*" if field["secret"] else "")
            val = (keyring.get_password(
                       f"{KEYRING_SVC}_sms_{provider}", field["key"]) or ""
                   if field["secret"]
                   else state.provider_config.get(field["key"], ""))
            e.insert(0, val)
            e.pack(fill="x", pady=(2, 0))
            provider_entries[field["key"]] = e

    def on_provider_change(choice):
        state.provider_config["active"] = choice
        render_provider_fields(choice)
        provider_msg.configure(text="")

    ctk.CTkOptionMenu(provider_section_frame,
                      variable=provider_var,
                      values=PROVIDER_NAMES,
                      font=FONT_ENTRY, height=36, corner_radius=8,
                      command=on_provider_change).pack(
                          fill="x", padx=14, pady=(0, 8))

    def save_provider_settings():
        provider = provider_var.get()
        state.provider_config["active"] = provider
        for field in PROVIDER_FIELDS.get(provider, []):
            entry = provider_entries.get(field["key"])
            if entry is None:
                continue
            text = entry.get().strip()
            if field["secret"]:
                keyring.set_password(
                    f"{KEYRING_SVC}_sms_{provider}", field["key"], text)
            else:
                state.provider_config[field["key"]] = text
        save_provider_config(state.provider_config)
        provider_msg.configure(
            text="Provider settings saved.", text_color="#00ff88")

    ctk.CTkButton(provider_section_frame,
                  text="💾  Save Provider Settings",
                  font=FONT_BTN_SM, height=36, corner_radius=8,
                  command=save_provider_settings).pack(
                      fill="x", padx=14, pady=(10, 8))

    render_provider_fields(provider_var.get())

    # Show mapping by default
    show_mapping_section()

    # Initial preview
    refresh_preview()


def refresh_preview():
    """Update the live column preview box."""
    if state.preview_box is None:
        return
    state.preview_box.configure(state="normal")
    state.preview_box.delete("1.0", END)

    if state.soon_expiring is not None and not state.soon_expiring.empty:
        state.preview_box.insert(END, "Sample from loaded data:\n\n")
        for _, row in state.soon_expiring.head(3).iterrows():
            state.preview_box.insert(END,
                f"  Name            : {row.get('name', '—')}\n"
                f"  Phone           : {row.get('phone_number', '—')}\n"
                f"  Expiry Date     : {str(row.get('end_date', '—'))[:10]}\n"
                f"  Membership No.  : {row.get('membership_number', '—')}\n"
                f"  Date of Birth   : {str(row.get('dob', '—'))[:10]}\n"
                f"  Email           : {row.get('email', '—')}\n"
                f"  {'─' * 36}\n"
            )
    else:
        state.preview_box.insert(
            END, "No data loaded yet.\n\nCurrent column mappings:\n\n")
        for app_field, friendly in FIELD_LABELS.items():
            mapped = state.col_map.get(app_field, app_field)
            state.preview_box.insert(END, f"  {friendly:<22} → {mapped}\n")

    state.preview_box.configure(state="disabled")
