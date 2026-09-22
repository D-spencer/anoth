import json
import time
from cryptography.fernet import Fernet

SESSION_SECONDS = 7 * 24 * 60 * 60


def encode_session(key, session, deadline):
    return Fernet(key).encrypt(json.dumps({
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "deadline": deadline,
    }).encode()).decode()


def decode_session(key, token):
    data = json.loads(Fernet(key).decrypt(token.encode()))
    if not isinstance(data, dict) or not isinstance(data.get("deadline"), (int, float)):
        raise ValueError("Invalid session")
    if not time.time() < data["deadline"] <= time.time() + SESSION_SECONDS:
        raise ValueError("Session expired")
    if not all(isinstance(data.get(k), str) and data[k] for k in ("access_token", "refresh_token")):
        raise ValueError("Invalid session")
    return data
