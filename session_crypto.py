import json
import time

from cryptography.fernet import Fernet


SESSION_LIFETIME_SECONDS = 7 * 24 * 60 * 60


def encrypt_session(key, session, expires_at, page="Tuberculosis"):
    payload = {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expires_at": expires_at,
        "page": page,
    }

    return Fernet(key).encrypt(
        json.dumps(payload).encode("utf-8")
    ).decode("utf-8")


def decrypt_session(key, encrypted_value):
    payload = json.loads(
        Fernet(key).decrypt(encrypted_value.encode("utf-8"))
    )

    expires_at = payload.get("expires_at")
    now = time.time()

    if not isinstance(expires_at, (int, float)):
        raise ValueError("Invalid session expiry")

    if not now < expires_at <= now + SESSION_LIFETIME_SECONDS:
        raise ValueError("Session expired")

    for field in ("access_token", "refresh_token"):
        if not isinstance(payload.get(field), str) or not payload[field]:
            raise ValueError("Invalid session data")

    return payload
