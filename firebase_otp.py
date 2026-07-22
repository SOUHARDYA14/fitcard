"""Email OTP challenges backed by Firebase (Firestore for storage) and
Resend (for actually sending the email) -- Firebase Authentication itself
has no built-in "type a code emailed to you" product (only Email/Password
and Email Link/magic-link), so this is a small custom implementation on top
of Firestore rather than a first-party Firebase feature.

Firestore collection `otpChallenges`: one document per pending login, holding
a hash of the code (never the code itself), an expiry, and an attempt count.
"""
import hashlib
import json
import os
import random
import secrets
from datetime import datetime, timedelta, timezone

import firebase_admin
from firebase_admin import credentials, firestore

CODE_TTL_MINUTES = 10
MAX_ATTEMPTS = 5
COLLECTION = "otpChallenges"

_app = None
_db = None


class ChallengeNotFound(Exception):
    pass


class ChallengeExpired(Exception):
    pass


class TooManyAttempts(Exception):
    pass


class FirestoreOtpError(RuntimeError):
    """Wraps unexpected Firestore/network failures (timeouts, transient
    outages, credential issues) so they don't propagate as a raw exception
    type the caller isn't watching for -- app.py's _SEND_ERRORS/except
    clauses only catch this and the three challenge-state errors above."""
    pass


def _guard(fn):
    """Every public function in this module either raises one of the four
    exception classes above deliberately, or should raise FirestoreOtpError
    for anything unexpected -- never a bare firebase_admin/network exception
    the caller has no reason to know about."""
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (ChallengeNotFound, ChallengeExpired, TooManyAttempts):
            raise
        except Exception as e:
            raise FirestoreOtpError(f"Firestore OTP operation failed: {e}") from e
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


def _client():
    global _app, _db
    if _db is not None:
        return _db

    raw_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if raw_json:
        cert = credentials.Certificate(json.loads(raw_json))
    else:
        path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")
        if not os.path.exists(path):
            raise RuntimeError(
                f"Firebase service account key not found at {path}. Set "
                "FIREBASE_SERVICE_ACCOUNT_JSON (the key file's raw contents) for "
                "deployed environments, or FIREBASE_SERVICE_ACCOUNT_PATH / place the "
                "downloaded JSON key there for local development."
            )
        cert = credentials.Certificate(path)

    _app = firebase_admin.initialize_app(cert)
    _db = firestore.client(_app)
    return _db


def _hash_code(code):
    return hashlib.sha256(code.encode()).hexdigest()


def _generate_code():
    return f"{random.randint(0, 999999):06d}"


@_guard
def create_challenge(email, app_name="creditcard"):
    """Create a new pending challenge and return (challenge_id, code). The
    caller is responsible for emailing `code` to the user -- it is never
    stored in Firestore, only its hash."""
    db = _client()
    code = _generate_code()
    challenge_id = secrets.token_urlsafe(24)
    now = datetime.now(timezone.utc)
    db.collection(COLLECTION).document(challenge_id).set({
        "email": email.lower(),
        "codeHash": _hash_code(code),
        "expiresAt": now + timedelta(minutes=CODE_TTL_MINUTES),
        "attempts": 0,
        "verified": False,
        "app": app_name,
        "createdAt": now,
    })
    return challenge_id, code


@_guard
def regenerate_code(challenge_id):
    """For a resend: issue a fresh code against the same challenge, resetting expiry."""
    db = _client()
    ref = db.collection(COLLECTION).document(challenge_id)
    doc = ref.get()
    if not doc.exists:
        raise ChallengeNotFound(challenge_id)
    code = _generate_code()
    ref.update({
        "codeHash": _hash_code(code),
        "expiresAt": datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES),
        "attempts": 0,
    })
    return code


@_guard
def get_email(challenge_id):
    db = _client()
    doc = db.collection(COLLECTION).document(challenge_id).get()
    if not doc.exists:
        raise ChallengeNotFound(challenge_id)
    return doc.to_dict()["email"]


@_guard
def verify_challenge(challenge_id, code):
    """Returns True/False for a correct/incorrect code. Raises
    ChallengeNotFound/ChallengeExpired/TooManyAttempts for those cases so the
    caller can show a more specific message than a flat "wrong code"."""
    db = _client()
    ref = db.collection(COLLECTION).document(challenge_id)

    # A plain get()-then-later-update() on `attempts` is a check-then-act
    # race: parallel verify calls for the same challenge_id can each read the
    # same pre-increment count before either write lands, letting an
    # attacker land more guesses than MAX_ATTEMPTS. @firestore.transactional
    # makes the read-check-write atomic (Firestore retries the transaction on
    # contention rather than letting two reads interleave).
    @firestore.transactional
    def _verify(transaction):
        doc = ref.get(transaction=transaction)
        if not doc.exists:
            raise ChallengeNotFound(challenge_id)

        data = doc.to_dict()
        if data["attempts"] >= MAX_ATTEMPTS:
            raise TooManyAttempts(challenge_id)

        expires_at = data["expiresAt"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise ChallengeExpired(challenge_id)

        if _hash_code(code) != data["codeHash"]:
            transaction.update(ref, {"attempts": data["attempts"] + 1})
            return False

        transaction.update(ref, {"verified": True})
        return True

    return _verify(db.transaction())


@_guard
def delete_challenge(challenge_id):
    _client().collection(COLLECTION).document(challenge_id).delete()
