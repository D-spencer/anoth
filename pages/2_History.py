import streamlit as st
import pandas as pd
from auth import logout
from database import get_prediction_history
from persistent_session import restore_persistent_session
from theme import apply_theme_css

restore_persistent_session()

hide_streamlit_style = """
    <style>
    /* Hide the main menu (hamburger menu) but keep sidebar toggle */
    #MainMenu {visibility: hidden;}

    /* Hide the footer */
    footer {visibility: hidden;}

    /* Hide the "Made with Streamlit" footer */
    .css-1d391kg {visibility: hidden;}

    /* Keep Streamlit's top header and toolbar available. */
    /* Show status widget (includes running indicator) */
    [data-testid="stStatusWidget"] {visibility: visible !important;}

    /* Hide only the settings menu; keep sidebar collapse/expand controls available. */
    button[title="Settings"] {visibility: hidden;}

    /* Keep sidebar toggle button visible */
    button[data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] {display: inline-flex !important; visibility: visible !important; opacity: 1 !important; pointer-events: auto !important;}

    /* Keep the sidebar toggle area visible */
    [data-testid="stSidebarNav"] {visibility: visible !important;}

    /* Ensure sidebar toggle button is accessible */
    .css-1544g2n {visibility: visible !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Keep the Streamlit running indicator and sidebar toggle, but hide page toolbar actions.
st.markdown("""<style>
[data-testid="stToolbarActions"] { display: none !important; visibility: hidden !important; }
[data-testid="stMainMenu"], button[aria-label="Main menu"], button[title="Main menu"] { display: none !important; visibility: hidden !important; }
[data-testid="stStatusWidget"] { display: flex !important; visibility: visible !important; opacity: 1 !important; }
[data-testid="stSidebarCollapseButton"], button[data-testid="collapsedControl"] { visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; }
</style>""", unsafe_allow_html=True)



if st.session_state.get("user") is None:
    st.warning("You have been logged out. Please log in again from the home page.")
    st.stop()  

# ================= APPLY ACTIVE THEME =================
apply_theme_css()


# ---------------- LOGIN CHECK ----------------
if "user" not in st.session_state:
    st.warning("Please login first")
    st.stop()


# ---------------- PAGE HERO ----------------
user_email = st.session_state["user"].email
st.markdown(f'''
<div class="hero-section">
  <div class="hero-title">Prediction History</div>
  <div class="hero-subtitle">Review and download your previous tuberculosis and HIV/AIDS screening results</div>
  <div class="hero-meta">Signed in as: <b>{user_email}</b></div>
</div>
''' , unsafe_allow_html=True)


# ---------------- GET USER DATA ----------------
data = get_prediction_history(user_email)


# ---------------- EMPTY CHECK ----------------
if not data:
    st.info("No prediction history found.")

else:

    # ---------------- DATAFRAME ----------------
    df = pd.DataFrame(data)

    # ---------------- FILTER ----------------
    filter_disease = st.selectbox(
        "Filter by Disease",
        ["All", "Tuberculosis", "HIV/AIDS"]
    )

    # ---------------- APPLY FILTER ----------------
    if filter_disease != "All":

        df = df[
            df["disease"].str.contains(filter_disease)
        ]

    # ---------------- METRICS ----------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Predictions",
            len(df)
        )

    with col2:
        positive_count = len(
            df[df["prediction"] == 1]
        )

        st.metric(
            "Positive Results",
            positive_count
        )

    with col3:
        negative_count = len(
            df[df["prediction"] == 0]
        )

        st.metric(
            "Negative Results",
            negative_count
        )

    # ---------------- TABLE ----------------
    st.subheader("Prediction Records")

    display_df = df.copy()

    display_df["prediction"] = (
        display_df["prediction"]
        .map({
            1: "Positive",
            0: "Negative"
        })
    )

    st.dataframe(
        display_df[[
            "disease",
            "prediction",
            "probability",
            "created_at"
        ]],
        use_container_width=True
    )

    # ---------------- DOWNLOAD CSV ----------------
    csv = df.to_csv(index=False)

    st.download_button(
        label="Download History",
        data=csv,
        file_name="prediction_history.csv",
        mime="text/csv"
    )

    # ---------------- DETAILS ----------------
    st.subheader("Detailed Records")

    for _, row in df.iterrows():

        result_label = (
            "Positive"
            if row["prediction"] == 1
            else "Negative"
        )

        with st.expander(
            f"{row['disease']} | "
            f"{result_label} | "
            f"{row['created_at']}"
        ):

            st.write(
                f"Probability: {row['probability']}"
            )

            st.json(row["input_data"])





if  st.sidebar.button("Logout", icon=":material/door_open:"):
    logout()
    st.rerun()
