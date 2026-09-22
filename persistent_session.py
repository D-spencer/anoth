from pathlib import Path
import hashlib
import time
import uuid
import streamlit as st
import streamlit.components.v1 as components
from cryptography.fernet import Fernet
from streamlit_autorefresh import st_autorefresh
from database import supabase, get_user_name, get_user_role
from session_crypto import SESSION_SECONDS, encode_session, decode_session

_bridge = components.declare_component("dmd_session", path=str(Path(__file__).parent / "session_component"))


def _key():
    key = st.secrets.get("SESSION_ENCRYPTION_KEY", "")
    try:
        Fernet(key)
    except (ValueError, TypeError):
        st.error("Set SESSION_ENCRYPTION_KEY in your Streamlit secrets. See UPDATE_NOTES.md.")
        st.stop()
    return key


def _queue(value):
    st.session_state["_session_write"] = {"id": uuid.uuid4().hex, "value": value}


def _set_user(session):
    user = supabase.auth.get_user(session.access_token).user
    if not user:
        raise ValueError("Invalid user session")
    role = get_user_role(user.id)
    name = get_user_name(user.id)
    st.session_state.update(user=user, session=session, role=role,
                            full_name=name or "", active_user_id=user.id)


def _persist(session):
    token = encode_session(_key(), session, st.session_state["_session_deadline"])
    st.session_state["_session_token"] = token
    _queue(token)


def start_session(session):
    _set_user(session)
    st.session_state["_session_deadline"] = time.time() + SESSION_SECONDS
    _persist(session)


def clear_session():
    try:
        supabase.auth.sign_out({"scope": "local"})
    except Exception:
        pass
    st.session_state.clear()
    _queue(None)


def restore_session():
    for name, value in {"user": None, "session": None, "role": "user", "full_name": "", "active_user_id": None}.items():
        st.session_state.setdefault(name, value)
    key = _key()
    pending = st.session_state.get("_session_write")
    result = _bridge(
        storage_key="dmd-session-" + hashlib.sha256(st.secrets["SUPABASE_URL"].encode()).hexdigest()[:16],
        command=pending, default=None, key="dmd_browser_session",
    )
    if result is None:
        st.stop()
    if result.get("error"):
        st.error("Browser storage is unavailable. Allow site storage and reload to sign in.")
        st.stop()
    if pending:
        if result.get("ack") != pending["id"]:
            st.stop()
        st.session_state.pop("_session_write", None)
    browser_token = result.get("value")
    if st.session_state.get("user") and not browser_token:
        clear_session()
        st.rerun()
    try:
        if st.session_state.get("user"):
            if time.time() >= st.session_state["_session_deadline"]:
                clear_session()
                st.rerun()
            if browser_token != st.session_state.get("_session_token"):
                # Another tab changed the account or refreshed the credentials.
                st.session_state.clear()
                st.rerun()
            session = supabase.auth.get_session()
            if not session:
                raise ValueError("Missing session")
            if session.expires_at <= time.time() + 90:
                session = supabase.auth.refresh_session(session.refresh_token).session
            _set_user(session)
            data = decode_session(key, browser_token)
            if data["refresh_token"] != session.refresh_token or data["access_token"] != session.access_token:
                _persist(session)
                st.rerun()
        elif browser_token:
            data = decode_session(key, browser_token)
            response = supabase.auth.set_session(data["access_token"], data["refresh_token"])
            _set_user(response.session)
            st.session_state["_session_deadline"] = data["deadline"]
            _persist(response.session)
            st.rerun()
    except Exception:
        clear_session()
        st.rerun()
    if st.session_state.get("user"):
        st_autorefresh(interval=60_000, key="session_expiry_check")
