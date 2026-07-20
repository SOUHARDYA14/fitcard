"""Auth: email/password (Flask-Login + werkzeug hashing) and Google OAuth
(Authlib). User rows live in the `users` table inside credit_cards.db
(see migrate_auth.py).
"""
import os
import sqlite3

from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = "credit_cards.db"

login_manager = LoginManager()
login_manager.login_view = "login"
oauth = OAuth()
google = None  # set in init_auth() once we have an app/config


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class User(UserMixin):
    def __init__(self, row):
        self.id = str(row["id"])
        self.email = row["email"]
        self.name = row["name"]
        self.password_hash = row["password_hash"]
        self.google_sub = row["google_sub"]

    @staticmethod
    def get(user_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return User(row) if row else None

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
        conn.close()
        return User(row) if row else None

    @staticmethod
    def create(email, password=None, name=None, google_sub=None):
        conn = get_db()
        pw_hash = generate_password_hash(password, method="pbkdf2:sha256") if password else None
        cur = conn.execute(
            "INSERT INTO users (email, password_hash, name, google_sub) VALUES (?, ?, ?, ?)",
            (email.lower(), pw_hash, name, google_sub),
        )
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        return User.get(user_id)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def link_google(self, google_sub, name=None):
        conn = get_db()
        conn.execute("UPDATE users SET google_sub = ?, name = COALESCE(name, ?) WHERE id = ?",
                     (google_sub, name, self.id))
        conn.commit()
        conn.close()
        self.google_sub = google_sub

    @staticmethod
    def get_by_google_sub(sub):
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE google_sub = ?", (sub,)).fetchone()
        conn.close()
        return User(row) if row else None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def init_auth(app):
    login_manager.init_app(app)
    oauth.init_app(app)

    global google
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if client_id and client_secret:
        google = oauth.register(
            name="google",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )
    return google is not None
