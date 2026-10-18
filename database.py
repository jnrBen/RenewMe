# ─────────────────────────────────────────────
# database.py — DB connection, query, search, disconnect
# ─────────────────────────────────────────────

import pandas as pd
from tkinter import messagebox, END
from sqlalchemy import create_engine, text

from constants import DB_TYPES
from config import state, save_col_map


# ─────────────────────────────────────────────
# CONNECTION
# ─────────────────────────────────────────────
def get_engine(host, user, password, database, port, db_type):
    if db_type == "MySQL":
        url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    elif db_type == "PostgreSQL":
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    elif db_type == "Microsoft SQL Server":
        url = (
            f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}"
            f"?driver=ODBC+Driver+17+for+SQL+Server"
        )
    else:
        raise ValueError(f"Unsupported DB type: {db_type}")
    return create_engine(url)


# ─────────────────────────────────────────────
# FIELD LOCKING
# ─────────────────────────────────────────────
def lock_connection_fields():
    for w in state.CONNECTION_WIDGETS:
        w.configure(state="disabled")
    state.conn_btn.configure(state="disabled")
    state.disconnect_btn.configure(state="normal")
    state.save_btn.configure(
        fg_color="gray30", hover_color="gray30",
        text_color="gray60", command=lambda: None)
    state.load_btn.configure(
        fg_color="gray30", hover_color="gray30",
        text_color="gray60", command=lambda: None)


def unlock_connection_fields():
    from utils import save_credentials, load_credentials
    for w in state.CONNECTION_WIDGETS:
        w.configure(state="normal")
    state.conn_btn.configure(state="normal")
    state.disconnect_btn.configure(state="disabled")
    state.save_btn.configure(
        fg_color=("#3B8ED0", "#1F6AA5"),
        hover_color=("#36719F", "#144870"),
        text_color="white",
        command=save_credentials)
    state.load_btn.configure(
        fg_color=("#3B8ED0", "#1F6AA5"),
        hover_color=("#36719F", "#144870"),
        text_color="white",
        command=load_credentials)


# ─────────────────────────────────────────────
# DISCONNECT
# ─────────────────────────────────────────────
def disconnect_database():
    from ui.users_tab import populate_users_tab
    from ui.customize_tab import refresh_preview

    state.soon_expiring = None

    for w in state.listbox_frame.winfo_children():
        w.destroy()
    for w in state.users_list_frame.winfo_children():
        w.destroy()

    state.detail_name.configure(text="Select a member")
    for val in state.detail_fields.values():
        val.configure(text="—")
    state.ind_send_btn.configure(state="disabled")
    state.ind_status.configure(text="")
    state.search_var.set("")
    state.search_notice.configure(text="Showing: expiring users")
    state.search_status.configure(text="")

    refresh_preview()

    state.send_btn.configure(state="disabled")
    state.status_bar.configure(text="Disconnected.")
    unlock_connection_fields()


# ─────────────────────────────────────────────
# CONNECT
# ─────────────────────────────────────────────
def connect_database():
    from ui.users_tab import populate_users_tab
    from ui.customize_tab import refresh_preview
    import customtkinter as ctk
    from constants import FONT_ENTRY

    col_map = state.col_map

    host           = state.host_entry.get().strip()
    user           = state.user_entry.get().strip()
    password       = state.pass_entry.get()
    database       = state.db_entry.get().strip()
    port           = state.port_entry.get().strip()
    state.api_key_global = state.api_entry.get().strip()
    db_type        = state.db_type_var.get()

    if not all([host, user, database, port, state.api_key_global]):
        messagebox.showerror("Missing Input", "Please fill in all required fields.")
        return

    try:
        port_int = int(port)
    except ValueError:
        messagebox.showerror("Invalid Port", "Port must be a numeric value.")
        return

    if db_type == "MySQL":
        query = f"""
            SELECT
                {col_map['name']}              AS name,
                {col_map['phone_number']}      AS phone_number,
                {col_map['end_date']}          AS end_date,
                {col_map['membership_number']} AS membership_number,
                {col_map['dob']}               AS dob,
                {col_map['email']}             AS email,
                DATEDIFF(end_date, CURDATE())  AS days_left
            FROM {col_map['table_name']}
            WHERE {col_map['end_date']} BETWEEN CURDATE()
                  AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        """
    elif db_type == "PostgreSQL":
        query = f"""
            SELECT
                {col_map['name']}              AS name,
                {col_map['phone_number']}      AS phone_number,
                {col_map['end_date']}          AS end_date,
                {col_map['membership_number']} AS membership_number,
                {col_map['dob']}               AS dob,
                {col_map['email']}             AS email,
                ({col_map['end_date']}::date - CURRENT_DATE) AS days_left
            FROM {col_map['table_name']}
            WHERE {col_map['end_date']} BETWEEN CURRENT_DATE
                  AND CURRENT_DATE + INTERVAL '30 days'
        """
    elif db_type == "Microsoft SQL Server":
        query = f"""
            SELECT
                {col_map['name']}              AS name,
                {col_map['phone_number']}      AS phone_number,
                {col_map['end_date']}          AS end_date,
                {col_map['membership_number']} AS membership_number,
                {col_map['dob']}               AS dob,
                {col_map['email']}             AS email,
                DATEDIFF(day, GETDATE(), {col_map['end_date']}) AS days_left
            FROM {col_map['table_name']}
            WHERE {col_map['end_date']} BETWEEN CAST(GETDATE() AS DATE)
                  AND DATEADD(day, 30, CAST(GETDATE() AS DATE))
        """

    try:
        engine = get_engine(host, user, password, database, port_int, db_type)
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to connect:\n{e}")
        return

    if df.empty:
        messagebox.showinfo("Connected", "No policies expiring within 30 days.")
        state.soon_expiring = df
        lock_connection_fields()
        state.status_bar.configure(
            text="Connected — no policies expiring within 30 days.")
        return

    state.soon_expiring = df

    for widget in state.listbox_frame.winfo_children():
        widget.destroy()
    for _, row in df.iterrows():
        ctk.CTkLabel(
            state.listbox_frame,
            text=f"  {row['name']}  |  {row['phone_number']}  |  {int(row['days_left'])} days left",
            font=FONT_ENTRY, anchor="w"
        ).pack(fill="x", padx=4, pady=1)

    state.send_btn.configure(state="normal")
    state.status_bar.configure(text=f"{len(df)} expiring users loaded.")
    populate_users_tab()
    refresh_preview()
    lock_connection_fields()
    messagebox.showinfo("Connected", f"{len(df)} expiring user(s) loaded.")


# ─────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────
def search_database(search_field, search_term):
    col_map = state.col_map
    host     = state.host_entry.get().strip()
    user     = state.user_entry.get().strip()
    password = state.pass_entry.get()
    database = state.db_entry.get().strip()
    port     = state.port_entry.get().strip()
    db_type  = state.db_type_var.get()

    if not all([host, user, database, port]):
        messagebox.showerror("Not Connected",
                             "Please fill in DB credentials and connect first.")
        return None

    try:
        port_int = int(port)
    except ValueError:
        messagebox.showerror("Invalid Port", "Port must be a numeric value.")
        return None

    if db_type not in DB_TYPES:
        messagebox.showerror("Config Error",
                             f"Invalid database type: '{db_type}'.")
        return None

    field_to_col = {
        "Name":           col_map["name"],
        "Phone Number":   col_map["phone_number"],
        "Membership No":  col_map["membership_number"],
        "Date of Birth":  col_map["dob"],
        "Email":          col_map["email"],
    }
    db_col = field_to_col.get(search_field, col_map["name"])

    if db_type == "MySQL":
        query = f"""
            SELECT
                {col_map['name']}              AS name,
                {col_map['phone_number']}      AS phone_number,
                {col_map['end_date']}          AS end_date,
                {col_map['membership_number']} AS membership_number,
                {col_map['dob']}               AS dob,
                {col_map['email']}             AS email,
                DATEDIFF({col_map['end_date']}, CURDATE()) AS days_left
            FROM {col_map['table_name']}
            WHERE {db_col} LIKE :term
        """
    elif db_type == "PostgreSQL":
        query = f"""
            SELECT
                {col_map['name']}              AS name,
                {col_map['phone_number']}      AS phone_number,
                {col_map['end_date']}          AS end_date,
                {col_map['membership_number']} AS membership_number,
                {col_map['dob']}               AS dob,
                {col_map['email']}             AS email,
                ({col_map['end_date']}::date - CURRENT_DATE) AS days_left
            FROM {col_map['table_name']}
            WHERE {db_col} LIKE :term
        """
    elif db_type == "Microsoft SQL Server":
        query = f"""
            SELECT
                {col_map['name']}              AS name,
                {col_map['phone_number']}      AS phone_number,
                {col_map['end_date']}          AS end_date,
                {col_map['membership_number']} AS membership_number,
                {col_map['dob']}               AS dob,
                {col_map['email']}             AS email,
                DATEDIFF(day, GETDATE(), {col_map['end_date']}) AS days_left
            FROM {col_map['table_name']}
            WHERE {db_col} LIKE :term
        """

    try:
        engine = get_engine(host, user, password, database, port_int, db_type)
        with engine.connect() as conn:
            df = pd.read_sql(
                text(query), conn,
                params={"term": f"%{search_term}%"}
            )
        return df
    except Exception as e:
        messagebox.showerror("Search Error", f"Search failed:\n{e}")
        return None
