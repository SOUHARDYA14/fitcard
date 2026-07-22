import json
import os
import random
import re
import sqlite3

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user

import auth
import firebase_otp
import msg91
import resend_email
import scoring
from auth import User
from vite_assets import vite_asset

load_dotenv()

app = Flask(__name__)

INSURANCE_SERVICE_URL = os.environ.get("INSURANCE_SERVICE_URL", "").rstrip("/")
_EXCLUDED_RESPONSE_HEADERS = {
    "content-encoding", "content-length", "transfer-encoding", "connection",
}

secret_key = os.environ.get("FLASK_SECRET_KEY")
if not secret_key:
    if os.environ.get("FLASK_DEBUG") == "1":
        secret_key = "dev-only-insecure-key"
    else:
        raise RuntimeError(
            "FLASK_SECRET_KEY is not set. A known secret key lets an attacker "
            "forge signed session cookies. Set FLASK_SECRET_KEY, or set "
            "FLASK_DEBUG=1 for local development only."
        )
app.secret_key = secret_key

google_enabled = auth.init_auth(app)

DEV_OTP_ALLOWED = os.environ.get("FLASK_DEBUG") == "1"

def get_db_connection():
    conn = sqlite3.connect("credit_cards.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.context_processor
def inject_globals():
    return {"google_enabled": google_enabled}


# Lets migrated templates do {{ vite_asset('pages/cards/main.jsx') }} to pull
# in that entry's built (or, under VITE_DEV=1, dev-server-hosted) JS/CSS --
# see vite_assets.py and the frontend migration plan for why this exists.
app.jinja_env.globals["vite_asset"] = vite_asset


# ---------------------------------------------------------------- auth ----
# Every login (password or phone) is followed by an OTP challenge sent to
# the matching email/phone before a session is actually established. Email
# codes are generated/stored in Firestore and delivered via Resend (Firebase
# Auth itself has no built-in typed-code-by-email product -- see
# firebase_otp.py); phone codes still go through MSG91. In local dev without
# those credentials configured, a random code is shown on-screen instead of
# being sent, so the flow can still be exercised end to end.

_NOT_CONFIGURED_ERRORS = (
    msg91.Msg91NotConfigured,
    resend_email.ResendNotConfigured,
    RuntimeError,  # firebase_otp raises this if the service account key is missing
)
_SEND_ERRORS = _NOT_CONFIGURED_ERRORS + (msg91.Msg91Error, resend_email.ResendError)


def _mask(contact):
    if "@" in contact:
        name, _, domain = contact.partition("@")
        return f"{name[:1]}{'*' * max(len(name) - 1, 1)}@{domain}"
    return f"{'*' * max(len(contact) - 4, 0)}{contact[-4:]}"


def _start_otp_challenge(user, channel):
    contact = user.email if channel == "email" else user.phone
    challenge_id = None
    try:
        if channel == "email":
            challenge_id, code = firebase_otp.create_challenge(contact, app_name="creditcard")
            resend_email.send_otp_email(contact, code)
        else:
            msg91.send_otp(phone=contact)
        session.pop("dev_otp", None)
    except _NOT_CONFIGURED_ERRORS:
        if not DEV_OTP_ALLOWED:
            raise
        session["dev_otp"] = f"{random.randint(0, 999999):06d}"

    session["pending_uid"] = user.id
    session["pending_channel"] = channel
    session["pending_contact"] = contact
    session["pending_challenge_id"] = challenge_id


def _verify_otp_challenge(code):
    channel = session.get("pending_channel")
    contact = session.get("pending_contact")
    if "dev_otp" in session:
        return code == session["dev_otp"]
    if channel == "email":
        return firebase_otp.verify_challenge(session.get("pending_challenge_id"), code)
    return msg91.verify_otp(code, phone=contact)


def _clear_otp_challenge():
    for key in ("pending_uid", "pending_channel", "pending_contact", "pending_challenge_id", "dev_otp"):
        session.pop(key, None)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("params_form"))

    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip() or None
        phone_invalid = phone is not None and not re.fullmatch(r"\d{10,15}", phone)

        if not email or "@" not in email:
            error = "Enter a valid email address."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif phone_invalid:
            error = "Phone number should be digits only, with country code (e.g. 919876543210)."
        elif User.get_by_email(email):
            error = "An account with that email already exists."
        elif phone and User.get_by_phone(phone):
            error = "An account with that phone number already exists."
        else:
            try:
                user = User.create(email=email, password=password, name=name or None, phone=phone)
            except sqlite3.IntegrityError:
                # Narrow window between the get_by_email/get_by_phone checks
                # above and this insert -- a concurrent signup for the same
                # email/phone can slip through and hit the UNIQUE constraint.
                error = "An account with that email or phone number already exists."
            else:
                try:
                    _start_otp_challenge(user, "email")
                except _SEND_ERRORS:
                    error = "Couldn't send a verification code right now. Try again shortly."
                else:
                    return redirect(url_for("login_verify"))

    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("params_form"))

    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.get_by_email(email)
        if user and user.check_password(password):
            try:
                _start_otp_challenge(user, "email")
            except _SEND_ERRORS:
                error = "Couldn't send a verification code right now. Try again shortly."
            else:
                return redirect(url_for("login_verify"))
        else:
            error = "Incorrect email or password."

    return render_template("login.html", error=error)


@app.route("/login/phone", methods=["GET", "POST"])
def login_phone():
    if current_user.is_authenticated:
        return redirect(url_for("params_form"))

    error = None
    if request.method == "POST":
        phone = (request.form.get("phone") or "").strip()
        user = User.get_by_phone(phone) if phone else None
        if not user:
            error = "No account is linked to that phone number."
        else:
            try:
                _start_otp_challenge(user, "phone")
            except _SEND_ERRORS:
                error = "Couldn't send a verification code right now. Try again shortly."
            else:
                return redirect(url_for("login_verify"))

    return render_template("login_phone.html", error=error)


@app.route("/login/verify", methods=["GET", "POST"])
def login_verify():
    if current_user.is_authenticated:
        return redirect(url_for("params_form"))
    if "pending_uid" not in session:
        return redirect(url_for("login"))

    error = None
    if request.method == "POST":
        code = (request.form.get("otp") or "").strip()
        try:
            verified = _verify_otp_challenge(code)
        except firebase_otp.ChallengeExpired:
            error = "That code expired. Request a new one below."
        except firebase_otp.TooManyAttempts:
            error = "Too many wrong attempts. Request a new code below."
        except firebase_otp.ChallengeNotFound:
            _clear_otp_challenge()
            return redirect(url_for("login"))
        except (firebase_otp.FirestoreOtpError, msg91.Msg91Error, msg91.Msg91NotConfigured):
            error = "Couldn't verify your code right now. Try again shortly."
        else:
            if verified:
                user = User.get(session["pending_uid"])
                _clear_otp_challenge()
                login_user(user)
                return redirect(url_for("params_form"))
            error = "That code didn't match. Check it and try again."

    return render_template(
        "verify_otp.html",
        error=error,
        contact=_mask(session["pending_contact"]),
        dev_otp=session.get("dev_otp"),
    )


@app.route("/login/resend", methods=["POST"])
def login_resend():
    if "pending_uid" not in session:
        return redirect(url_for("login"))
    channel = session["pending_channel"]
    contact = session["pending_contact"]
    try:
        if "dev_otp" in session:
            session["dev_otp"] = f"{random.randint(0, 999999):06d}"
        elif channel == "email":
            code = firebase_otp.regenerate_code(session["pending_challenge_id"])
            resend_email.send_otp_email(contact, code)
        else:
            msg91.resend_otp(phone=contact)
    except _SEND_ERRORS:
        pass
    except firebase_otp.ChallengeNotFound:
        _clear_otp_challenge()
        return redirect(url_for("login"))
    return redirect(url_for("login_verify"))


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("welcome"))


@app.route("/auth/google")
def auth_google():
    if not google_enabled:
        return redirect(url_for("login"))
    redirect_uri = url_for("auth_google_callback", _external=True)
    return auth.google.authorize_redirect(redirect_uri)


@app.route("/auth/google/callback")
def auth_google_callback():
    if not google_enabled:
        return redirect(url_for("login"))
    token = auth.google.authorize_access_token()
    userinfo = token.get("userinfo") or auth.google.parse_id_token(token)
    sub = userinfo["sub"]
    email = userinfo.get("email")
    name = userinfo.get("name")

    user = User.get_by_google_sub(sub)
    if not user and email:
        user = User.get_by_email(email)
        if user:
            user.link_google(sub, name)
    if not user:
        # users.email is UNIQUE NOT NULL, so an account can't be created
        # without one -- some Google accounts don't return an email claim
        # (e.g. scope not granted, or an unverified/managed account).
        if not email:
            return render_template(
                "login.html",
                error="Your Google account didn't share an email address, so we can't create an account for it. Try signing up with email/password instead.",
            )
        user = User.create(email=email, name=name, google_sub=sub)

    login_user(user)
    return redirect(url_for("params_form"))


# ------------------------------------------------------------- pages ----

@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/match")
def params_form():
    conn = get_db_connection()
    try:
        banks = conn.execute("SELECT id, bank_name FROM banks ORDER BY bank_name").fetchall()
    finally:
        conn.close()
    return render_template("match.html", banks=banks)


@app.route("/cards")
def all_cards():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT c.card_name, b.bank_name, c.joining_fee, c.return_percentage, c.best_suited_for
            FROM credit_cards c JOIN banks b ON b.id = c.bank_id
            ORDER BY b.bank_name, c.card_name
        """).fetchall()
    finally:
        conn.close()

    cards = []
    for r in rows:
        fee = r["joining_fee"]
        cards.append({
            "card_name": r["card_name"],
            "bank_name": r["bank_name"],
            "joining_fee": fee,
            "return": r["return_percentage"] or "NA",
            "tier": scoring.tier_label(fee),
            "best_suited_for": r["best_suited_for"] or "",
        })
    return render_template("cards.html", cards=cards)


@app.route("/recommend", methods=["POST"])
def recommend():
    # force=True parses the body as JSON regardless of Content-Type, which
    # means a cross-site request using a "simple" content type (e.g.
    # text/plain) skips the browser's CORS preflight entirely and still gets
    # parsed here -- combined with cookies being sent automatically, that let
    # an attacker's page silently write into a logged-in victim's
    # saved_recommendations. Requiring a real application/json body forces
    # the browser to preflight cross-origin requests, which this app never
    # opts into via CORS headers, so the browser blocks them itself.
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON with Content-Type: application/json."}), 400

    conn = get_db_connection()
    try:
        result = scoring.recommend(conn, data)

        if current_user.is_authenticated:
            conn.execute(
                "INSERT INTO saved_recommendations (user_id, inputs_json, results_json) VALUES (?, ?, ?)",
                (current_user.id, json.dumps(data), json.dumps(result["results"])),
            )
            conn.commit()
    finally:
        conn.close()

    return jsonify(result)


# --------------------------------------------------------- insurance ----

@app.route(
    "/insurance",
    defaults={"path": ""},
    strict_slashes=False,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
@app.route("/insurance/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def insurance_proxy(path):
    if not INSURANCE_SERVICE_URL:
        return "Insurance service is not configured.", 502

    target_url = f"{INSURANCE_SERVICE_URL}/insurance/{path}" if path else f"{INSURANCE_SERVICE_URL}/insurance"
    forward_headers = {k: v for k, v in request.headers if k.lower() != "host"}

    try:
        upstream = requests.request(
            method=request.method,
            url=target_url,
            headers=forward_headers,
            params=list(request.args.items(multi=True)),
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=60,
        )
    except requests.RequestException:
        return "The insurance service is unavailable right now.", 502

    response_headers = [
        (k, v) for k, v in upstream.raw.headers.items()
        if k.lower() not in _EXCLUDED_RESPONSE_HEADERS
    ]
    return Response(upstream.content, status=upstream.status_code, headers=response_headers)


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
