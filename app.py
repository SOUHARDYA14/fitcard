import json
import os
import sqlite3

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

import auth
import scoring
from auth import User

load_dotenv()

app = Flask(__name__)

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


def get_db_connection():
    conn = sqlite3.connect("credit_cards.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.context_processor
def inject_globals():
    return {"google_enabled": google_enabled}


# ---------------------------------------------------------------- auth ----

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("params_form"))

    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        name = (request.form.get("name") or "").strip()

        if not email or "@" not in email:
            error = "Enter a valid email address."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif User.get_by_email(email):
            error = "An account with that email already exists."
        else:
            user = User.create(email=email, password=password, name=name or None)
            login_user(user)
            return redirect(url_for("params_form"))

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
            login_user(user)
            return redirect(url_for("params_form"))
        error = "Incorrect email or password."

    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
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
        user = User.create(email=email, name=name, google_sub=sub)

    login_user(user)
    return redirect(url_for("params_form"))


# ------------------------------------------------------------- pages ----

@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/match")
@login_required
def params_form():
    conn = get_db_connection()
    banks = conn.execute("SELECT id, bank_name FROM banks ORDER BY bank_name").fetchall()
    conn.close()
    return render_template("match.html", banks=banks)


@app.route("/cards")
def all_cards():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT c.card_name, b.bank_name, c.joining_fee, c.return_percentage, c.best_suited_for
        FROM credit_cards c JOIN banks b ON b.id = c.bank_id
        ORDER BY b.bank_name, c.card_name
    """).fetchall()
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
@login_required
def recommend():
    data = request.get_json(force=True) or {}
    conn = get_db_connection()
    result = scoring.recommend(conn, data)

    conn.execute(
        "INSERT INTO saved_recommendations (user_id, inputs_json, results_json) VALUES (?, ?, ?)",
        (current_user.id, json.dumps(data), json.dumps(result["results"])),
    )
    conn.commit()
    conn.close()

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
