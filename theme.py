from pathlib import Path
import streamlit as st


def get_active_theme():
    """Return Streamlit's active theme, with a safe config fallback."""
    try:
        theme_type = st.context.theme.type
    except Exception:
        theme_type = None

    if theme_type in ("light", "dark"):
        return theme_type

    try:
        configured = st.get_option("theme.base")
    except Exception:
        configured = None

    return configured if configured in ("light", "dark") else "light"


def apply_theme_css():
    """Load exactly one theme stylesheet for the current page run."""
    theme = get_active_theme()
    css_file = Path(__file__).resolve().parent / "assets" / f"{theme}_mode.css"
    css = css_file.read_text(encoding="utf-8")
    st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)
    return theme
