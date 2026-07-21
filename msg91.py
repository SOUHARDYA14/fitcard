"""MSG91 OTP integration (https://docs.msg91.com/otp).

Requires an MSG91 account with:
  - MSG91_AUTH_KEY          the account Auth Key
  - MSG91_SMS_TEMPLATE_ID   a DLT-approved OTP SMS template id
  - MSG91_EMAIL_TEMPLATE_ID an approved OTP email template id

Until those are set, send_otp()/verify_otp() raise Msg91NotConfigured so
callers can fall back to the local dev flow (see app.py DEV_OTP_BYPASS).
"""
import os

import requests

BASE_URL = "https://control.msg91.com/api/v5"


class Msg91NotConfigured(RuntimeError):
    pass


class Msg91Error(RuntimeError):
    pass


def _auth_key():
    key = os.environ.get("MSG91_AUTH_KEY")
    if not key:
        raise Msg91NotConfigured("MSG91_AUTH_KEY is not set")
    return key


def send_otp(*, phone=None, email=None):
    """Send an OTP to a phone number (SMS) or email address. Exactly one of
    phone/email must be given. Phone numbers must be in `<countrycode><number>`
    format with no leading '+' (e.g. "919876543210")."""
    if bool(phone) == bool(email):
        raise ValueError("send_otp needs exactly one of phone or email")

    params = {"authkey": _auth_key(), "otp_length": 6, "otp_expiry": 10}
    if phone:
        template_id = os.environ.get("MSG91_SMS_TEMPLATE_ID")
        if not template_id:
            raise Msg91NotConfigured("MSG91_SMS_TEMPLATE_ID is not set")
        params.update(template_id=template_id, mobile=phone)
    else:
        template_id = os.environ.get("MSG91_EMAIL_TEMPLATE_ID")
        if not template_id:
            raise Msg91NotConfigured("MSG91_EMAIL_TEMPLATE_ID is not set")
        params.update(template_id=template_id, email=email)

    resp = requests.post(f"{BASE_URL}/otp", params=params, timeout=15)
    body = resp.json()
    if body.get("type") != "success":
        raise Msg91Error(body.get("message", "MSG91 send OTP failed"))


def verify_otp(otp, *, phone=None, email=None):
    if bool(phone) == bool(email):
        raise ValueError("verify_otp needs exactly one of phone or email")

    params = {"authkey": _auth_key(), "otp": otp}
    params["mobile"] = phone if phone else email

    resp = requests.post(f"{BASE_URL}/otp/verify", params=params, timeout=15)
    body = resp.json()
    return body.get("type") == "success"


def resend_otp(*, phone=None, email=None, via="text"):
    if bool(phone) == bool(email):
        raise ValueError("resend_otp needs exactly one of phone or email")

    params = {"authkey": _auth_key(), "retrytype": via}
    params["mobile"] = phone if phone else email

    resp = requests.post(f"{BASE_URL}/otp/retry", params=params, timeout=15)
    body = resp.json()
    if body.get("type") != "success":
        raise Msg91Error(body.get("message", "MSG91 resend OTP failed"))
