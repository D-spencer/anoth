import hashlib
import time
import uuid
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from cryptography.fernet import Fernet
from streamlit_autorefresh import st_autorefresh

from database import get_user_name, get_user_role, supabase
from session_crypto import SESSION_LIFETIME_SECONDS, decrypt_session, encrypt_session


_storage = components.declare_component(
    "dmd_persistent_session",
    path=str(Path(__file__).parent / "session_component")
)


def _encryption_key():
    key = st.secrets.get("SESSION_ENCRYPTION_KEY", "")

    try:
        Fernet(key)
    except (TypeError, ValueError):
        st.error(
            "SESSION_ENCRYPTION_KEY is missing or invalid. "
            "Add it to your Streamlit secrets."
        )
        st.stop()

    return key


def _storage_key():
    project_hash = hashlib.sha256(
        st.secrets["SUPABASE_URL"].encode("utf-8")
    ).hexdigest()[:16]

    return f"dmd-session-{project_hash}"


def _queue_browser_write(value):
    st.session_state["_session_browser_write"] = {
        "id": uuid.uuid4().hex,
        "value": value,
    }


def _set_authenticated_user(session):
    response = supabase.auth.get_user(session.access_token)
    user = response.user

    if not user:
        raise ValueError("Invalid authenticated session")

    st.session_state["user"] = user
    st.session_state["session"] = session
    st.session_state["role"] = get_user_role(user.id) or "user"
    st.session_state["full_name"] = get_user_name(user.id) or ""
    st.session_state["active_user_id"] = user.id


def _save_browser_token(session):
    encrypted_value = encrypt_session(
        _encryption_key(),
        session,
        st.session_state["_session_deadline"],
        st.session_state.get("page", "Tuberculosis")
    )

    st.session_state["_session_encrypted_value"] = encrypted_value
    _queue_browser_write(encrypted_value)


def remember_disease(page):
    if page not in ("Tuberculosis", "HIV/AIDS"):
        return
    st.session_state["page"] = page
    _save_browser_token(st.session_state["session"])


def save_persistent_session(session):
    _set_authenticated_user(session)
    st.session_state["_session_deadline"] = (
        time.time() + SESSION_LIFETIME_SECONDS
    )
    _save_browser_token(session)


def clear_persistent_session():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.clear()
    _queue_browser_write(None)


def restore_persistent_session():
    defaults = {
        "user": None,
        "session": None,
        "role": "user",
        "full_name": "",
        "active_user_id": None,
    }

    for name, value in defaults.items():
        st.session_state.setdefault(name, value)

    encryption_key = _encryption_key()
    # Only the session transport containers are removed from document flow.
    # Their iframes remain mounted so storage and timer messages still work.
    st.html("""
        <style>
        .st-key-dmd_session_transport,
        .st-key-dmd_session_timer,
        [data-testid="stElementContainer"]:has(.st-key-dmd_session_transport),
        [data-testid="stElementContainer"]:has(.st-key-dmd_session_timer) {
            position: absolute !important;
            width: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            overflow: hidden !important;
            padding: 0 !important;
            margin: 0 !important;
            pointer-events: none !important;
        }
        </style>
    """)
    pending_write = st.session_state.get("_session_browser_write")
    with st.container(key="dmd_session_transport"):
        browser_result = _storage(
            storage_key=_storage_key(),
            command=pending_write,
            default=None,
            key="dmd_session_storage"
        )

    if browser_result is None:
        st.stop()

    if browser_result.get("error"):
        st.error(
            "Browser storage is unavailable. Allow site storage and refresh."
        )
        st.stop()

    if pending_write:
        if browser_result.get("ack") != pending_write["id"]:
            st.stop()

        st.session_state.pop("_session_browser_write", None)

    browser_value = browser_result.get("value")

    try:
        if st.session_state.get("user"):
            if not browser_value:
                clear_persistent_session()
                st.rerun()

            if time.time() >= st.session_state["_session_deadline"]:
                clear_persistent_session()
                st.rerun()

            if browser_value != st.session_state.get("_session_encrypted_value"):
                st.session_state.clear()
                st.rerun()

            session = supabase.auth.get_session()

            if not session:
                raise ValueError("Missing Supabase session")

            if session.expires_at <= time.time() + 90:
                session = supabase.auth.refresh_session(
                    session.refresh_token
                ).session

            _set_authenticated_user(session)
            payload = decrypt_session(encryption_key, browser_value)

            if (
                payload["access_token"] != session.access_token
                or payload["refresh_token"] != session.refresh_token
            ):
                _save_browser_token(session)
                st.rerun()

        elif browser_value:
            payload = decrypt_session(encryption_key, browser_value)
            response = supabase.auth.set_session(
                payload["access_token"],
                payload["refresh_token"]
            )

            _set_authenticated_user(response.session)
            st.session_state["_session_deadline"] = payload["expires_at"]
            saved_page = payload.get("page", "Tuberculosis")
            if saved_page in ("Tuberculosis", "HIV/AIDS"):
                st.session_state["page"] = saved_page
            _save_browser_token(response.session)
            st.rerun()

    except Exception:
        clear_persistent_session()
        st.rerun()

    if st.session_state.get("user"):
        st.html("""<style>
            [data-testid="stMainBlockContainer"] {
                padding-top: 0.5rem !important;
                margin-top: 0 !important;
            }
        </style>""")
        with st.container(key="dmd_session_timer"):
            st_autorefresh(
                interval=60_000,
                key="persistent_session_expiry_check"
            )
