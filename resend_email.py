"""Sends the actual OTP email via Resend's REST API (no SDK needed for
something this small). Until a sending domain is verified in Resend, the
account can only send from onboarding@resend.dev and only to the address
the Resend account itself is registered with -- fine for development, but
real users won't receive anything until a domain (e.g. a wealthq.ai
subdomain) is verified there.
"""
import os

import requests

RESEND_API_URL = "https://api.resend.com/emails"


class ResendNotConfigured(RuntimeError):
    pass


class ResendError(RuntimeError):
    pass


def send_otp_email(to_email, code):
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise ResendNotConfigured("RESEND_API_KEY is not set")
    from_email = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")

    resp = requests.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "from": f"FitCard <{from_email}>",
            "to": [to_email],
            "subject": f"Your FitCard verification code: {code}",
            "html": (
                f"<p>Your FitCard verification code is:</p>"
                f"<p style='font-size:28px;font-weight:700;letter-spacing:4px'>{code}</p>"
                f"<p>This code expires in 10 minutes. If you didn't request this, you can ignore this email.</p>"
            ),
        },
        timeout=15,
    )
    if not resp.ok:
        raise ResendError(f"Resend send failed: {resp.status_code} {resp.text}")
