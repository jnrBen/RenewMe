# ─────────────────────────────────────────────
# sms.py — SMS sending via multiple providers
# ─────────────────────────────────────────────

import json
import threading
import requests
import keyring
from tkinter import messagebox

from constants import KEYRING_SVC
from config import state
from utils import format_phone_number, log_sms


# ─────────────────────────────────────────────
# GENERIC SENDER
# ─────────────────────────────────────────────
def send_sms(recipient, message):
    """Route SMS to the active provider and return (success, result)."""
    provider = state.provider_config.get("active", "mNotify")

    def get_cred(key):
        return keyring.get_password(f"{KEYRING_SVC}_sms_{provider}", key) or ""

    if provider == "mNotify":
        api_key   = state.api_key_global or get_cred("api_key")
        sender_id = state.provider_config.get("sender_id", "RenewMe")
        url       = f"https://api.mnotify.com/api/sms/quick?key={api_key}"
        payload   = {
            "recipient":     [recipient],
            "sender":        sender_id,
            "message":       message,
            "is_schedule":   False,
            "schedule_date": ""
        }
        response = requests.post(url, json=payload, timeout=10)
        result   = response.json()
        status   = result.get("status", "unknown")
        return status in ("1", 1, "success"), result

    elif provider == "Hubtel":
        client_id     = get_cred("client_id")
        client_secret = get_cred("client_secret")
        sender_id     = state.provider_config.get("sender_id", "RenewMe")
        url           = "https://smsc.hubtel.com/v1/messages/send"
        params = {
            "clientsecret": client_secret,
            "clientid":     client_id,
            "from":         sender_id,
            "to":           recipient,
            "content":      message,
        }
        response = requests.get(url, params=params, timeout=10)
        result   = response.json()
        return result.get("status", -1) == 0, result

    elif provider == "Africa's Talking":
        api_key   = get_cred("api_key")
        username  = state.provider_config.get("username", "sandbox")
        sender_id = state.provider_config.get("sender_id", "")
        url       = "https://api.africastalking.com/version1/messaging"
        headers   = {
            "apiKey":       api_key,
            "Accept":       "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"username": username, "to": recipient, "message": message}
        if sender_id:
            data["from"] = sender_id
        response  = requests.post(url, headers=headers, data=data, timeout=10)
        result    = response.json()
        recipients = result.get("SMSMessageData", {}).get("Recipients", [])
        success    = any(r.get("status") == "Success" for r in recipients)
        return success, result

    elif provider == "Twilio":
        account_sid = state.provider_config.get("account_sid", "")
        auth_token  = get_cred("auth_token")
        from_number = state.provider_config.get("from_number", "")
        url         = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{account_sid}/Messages.json"
        )
        data     = {"From": from_number, "To": recipient, "Body": message}
        response = requests.post(url, data=data,
                                 auth=(account_sid, auth_token), timeout=10)
        result   = response.json()
        success  = result.get("status") in ("queued", "sent", "delivered")
        return success, result

    elif provider == "Custom":
        endpoint    = state.provider_config.get("endpoint", "")
        auth_method = state.provider_config.get("auth_method", "param")
        auth_value  = get_cred("auth_value")
        sender_id   = state.provider_config.get("sender_id", "")
        extra_raw   = state.provider_config.get("extra_fields", "{}")
        try:
            extra = json.loads(extra_raw)
        except Exception:
            extra = {}
        payload = {"to": recipient, "message": message, "from": sender_id, **extra}
        headers = {}
        if auth_method.lower() == "header":
            headers["Authorization"] = f"Bearer {auth_value}"
        else:
            payload["api_key"] = auth_value
        response = requests.post(endpoint, json=payload,
                                 headers=headers, timeout=10)
        try:
            result = response.json()
        except Exception:
            result = {"raw": response.text}
        return response.status_code in (200, 201), result

    else:
        return False, {"error": f"Unknown provider: {provider}"}


# ─────────────────────────────────────────────
# BULK SEND
# ─────────────────────────────────────────────
def _send_worker():
    if state.soon_expiring is None or state.soon_expiring.empty:
        messagebox.showinfo("No Users", "No users to notify.")
        return

    state.send_btn.configure(state="disabled", text="Sending…")
    success_count = 0
    fail_count    = 0

    for _, row in state.soon_expiring.iterrows():
        name      = row['name']
        days_left = int(row['days_left'])
        phone     = format_phone_number(row['phone_number'])

        if not phone:
            log_sms(name, row['phone_number'], days_left,
                    "FAILED", "Invalid phone format")
            fail_count += 1
            continue

        msg = (
            f"Dear {name}, your National Health Insurance Membership Policy "
            f"will expire in {days_left} days. Please renew to avoid "
            f"service interruptions. Dial *929# or call 054-000-0000 for assistance."
        )

        try:
            success, result = send_sms(phone, msg)
            if success:
                log_sms(name, phone, days_left, "SENT")
                success_count += 1
            else:
                log_sms(name, phone, days_left, "FAILED", str(result))
                fail_count += 1
        except Exception as e:
            log_sms(name, phone, days_left, "ERROR", str(e))
            fail_count += 1

    state.send_btn.configure(state="normal", text="📤  Send Notifications")
    state.status_bar.configure(
        text=f"Done — {success_count} sent  | {fail_count} failed")
    messagebox.showinfo(
        "Completed",
        f"Notifications sent!\n\nSuccessful: {success_count}\nFailed: {fail_count}"
    )


def send_notifications():
    threading.Thread(target=_send_worker, daemon=True).start()


# ─────────────────────────────────────────────
# INDIVIDUAL SEND
# ─────────────────────────────────────────────
def send_individual():
    source = (state.user_search_results
              if state.user_search_results is not None
              else state.soon_expiring)
    if source is None or source.empty or state.selected_row_idx is None:
        return
    if state.selected_row_idx >= len(source):
        state.ind_status.configure(text="Selection out of range.")
        return

    row   = source.iloc[state.selected_row_idx]
    phone = format_phone_number(row['phone_number'])
    if not phone:
        state.ind_status.configure(text="Invalid phone number")
        return

    msg = (
        f"Dear {row['name']}, your National Health Insurance Membership "
        f"will expire in {int(row['days_left'])} days. Please renew to avoid "
        f"service interruptions. Dial *929# or call 054-000-0000 for assistance."
    )

    def _worker():
        try:
            success, result = send_sms(phone, msg)
            if success:
                log_sms(row['name'], phone, int(row['days_left']), "SENT")
                state.ind_status.configure(text="Message sent!")
            else:
                log_sms(row['name'], phone, int(row['days_left']),
                        "FAILED", str(result))
                state.ind_status.configure(text="Send failed")
        except Exception as e:
            log_sms(row['name'], phone, int(row['days_left']), "ERROR", str(e))
            state.ind_status.configure(text=f"Error: {e}")
        finally:
            state.ind_send_btn.configure(
                state="normal", text="📨  Send Reminder")

    state.ind_send_btn.configure(state="disabled", text="Sending…")
    threading.Thread(target=_worker, daemon=True).start()
