import streamlit as st
import pandas as pd
from database import get_all_predictions, get_all_feedback
import plotly.express as px
from persistent_session import restore_persistent_session

restore_persistent_session()

DARK_MODE = st.get_option("theme.base") == "dark"
CHART_TEXT = "#f4fbf7" if DARK_MODE else "#263a31"
CHART_GRID = "rgba(197,224,208,.20)" if DARK_MODE else "#e1e9e3"
CHART_GREEN = "#20e875" if DARK_MODE else "#087653"
CHART_GREEN_LIGHT = "#8cf59b" if DARK_MODE else "#68b878"
CHART_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": True,
}

if st.session_state.get("user") is None:
    st.warning("You have been logged out. Please log in again from the home page.")
    st.stop()

user_email = st.session_state["user"].email
if st.session_state.get("role") != "admin":
    st.error("Access denied. Admins only.")
    st.stop()

data = get_all_predictions()
df = pd.DataFrame(data) if data else pd.DataFrame()
feedback_data = get_all_feedback()
feedback_df = pd.DataFrame(feedback_data) if feedback_data else pd.DataFrame()


st.markdown(
    f"""
    <style>
    :root {{
        --dash-green: {CHART_GREEN};
        --dash-green-dark: {"#00b95c" if DARK_MODE else "#064b3b"};
        --dash-bg: {"#080f11" if DARK_MODE else "#f6f4ef"};
        --dash-card: {"#10191b" if DARK_MODE else "#fffdfa"};
        --dash-text: {"#f7fcf9" if DARK_MODE else "#17231f"};
        --dash-muted: {"#c5d6ce" if DARK_MODE else "#64756c"};
        --dash-border: {"#304044" if DARK_MODE else "#e2e6e1"};
        --dash-metric-value: {"#ffffff" if DARK_MODE else "#173d30"};
        --dash-metric-label: {"#f1faf5" if DARK_MODE else "#455b50"};
        --dash-caption: {"#c4d5cc" if DARK_MODE else "#64756c"};
        --dash-grid: {"#334348" if DARK_MODE else "#e7ece8"};
    }}
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        background: var(--dash-bg) !important; color: var(--dash-text) !important;
    }}
    [data-testid="stHeader"] {{ background: var(--dash-bg) !important; }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #063d32 0%, #03251f 100%) !important;
        border-right: 1px solid rgba(255,255,255,.10);
    }}
    [data-testid="stSidebar"] * {{ color: #f5fbf7; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color: #d7e8df; }}
    [data-testid="stSidebar"] [data-testid="stAlert"] {{ background: rgba(255,255,255,.10); }}
    .block-container {{ max-width: 1500px; padding-top: 2rem; padding-bottom: 3rem; }}
    h1, h2, h3, [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3,
    [data-testid="stTitle"] {{ color: var(--dash-text) !important; letter-spacing: -.025em; }}
    h1 {{ font-size: 2.15rem !important; font-weight: 750 !important; margin-bottom: .15rem !important; }}
    h2 {{ font-size: 1.35rem !important; font-weight: 700 !important; }}
    h3 {{ font-size: 1.05rem !important; font-weight: 700 !important; }}
    p, label, [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] p, .stCaption {{ color: var(--dash-muted) !important; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--dash-card) !important; border: 1px solid var(--dash-border) !important;
        border-radius: 17px !important;
        box-shadow: {"0 10px 28px rgba(0,0,0,.24)" if DARK_MODE else "0 5px 18px rgba(34,48,40,.07)"} !important;
    }}
    [data-testid="stMetric"] {{ padding: .65rem .45rem; }}
    [data-testid="stMetricLabel"] p {{
        color: var(--dash-metric-label) !important; font-size: .94rem !important; font-weight: 750 !important;
    }}
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] div {{
        color: var(--dash-metric-value) !important; font-weight: 850 !important; font-size: 2.4rem !important;
    }}
    [data-testid="stMetricDelta"] {{ font-weight: 750 !important; }}
    [data-testid="stCaptionContainer"] p, .stCaption {{ color: var(--dash-caption) !important; }}
    [data-testid="stMetric"] [data-testid="stTooltipIcon"] {{ display: none !important; }}
    .js-plotly-plot, .js-plotly-plot .plot-container,
    .js-plotly-plot .svg-container {{ background: transparent !important; }}
    .js-plotly-plot .modebar, .js-plotly-plot .modebar-container,
    .js-plotly-plot .modebar-group, .js-plotly-plot .modebar-btn {{
        background: transparent !important; border: 0 !important; box-shadow: none !important;
    }}
    .js-plotly-plot .modebar-btn path {{
        fill: {"#d8e9df" if DARK_MODE else "#53675c"} !important;
    }}
    .js-plotly-plot .modebar-btn:hover path {{ fill: var(--dash-green) !important; }}
    [data-testid="stSelectbox"] > div > div, [data-testid="stTextInput"] > div > div {{ border-radius: 10px; }}
    [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label {{ color: var(--dash-metric-label) !important; }}
    .dash-eyebrow {{
        color: var(--dash-green); font-size: .78rem; font-weight: 800;
        letter-spacing: .12em; text-transform: uppercase; margin-bottom: .35rem;
    }}
    .dash-subtitle {{ color: var(--dash-muted); font-size: .98rem; margin-top: 0; margin-bottom: 1.25rem; }}
    .dash-section-note {{ color: var(--dash-muted); font-size: .85rem; margin-top: -.55rem; margin-bottom: .8rem; }}
    .dash-pill {{ display:inline-block; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700; white-space:nowrap; }}
    .dash-positive {{ background:#e5f3e8; color:#176b39; }}
    .dash-negative {{ background:#fce8e6; color:#a33b35; }}
    .dash-neutral {{ background:#edf0ed; color:#526158; }}
    div[data-testid="stDownloadButton"] button, div[data-testid="stButton"] button {{
        border-radius: 10px; border: 1px solid var(--dash-border); font-weight: 700;
    }}
    div[data-testid="stDownloadButton"] button {{ background: #087653; color: white; }}
    div[data-testid="stDownloadButton"] button:hover {{ background: #00a85a; color: white; border-color:#00a85a; }}
    hr {{ border-color: var(--dash-border); }}
    @media (max-width: 800px) {{
        .block-container {{ padding: 1.2rem 1rem 2rem; }}
        h1 {{ font-size: 1.7rem !important; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown('<div class="dash-eyebrow">Disease Prediction System · Administration</div>', unsafe_allow_html=True)
st.title("Admin Dashboard")
st.markdown("<div class='dash-subtitle'>Overview of predictions, disease activity and system usage</div>", unsafe_allow_html=True)
st.caption(f"Signed in as {user_email}")


total_predictions = len(df)
total_users = df["user_email"].nunique() if not df.empty and "user_email" in df.columns else 0
tb_count = len(df[df["disease"].astype(str).str.lower().isin(["tb", "tuberculosis"])]) if not df.empty and "disease" in df.columns else 0
hiv_count = len(df[df["disease"].astype(str).str.lower().isin(["hiv", "hiv/aids", "hiv aids"])]) if not df.empty and "disease" in df.columns else 0
total_feedback_count = len(feedback_df)

st.markdown("### System Overview")
metric_cols = st.columns(4, gap="medium")
metric_items = [
    ("Total Users", total_users, "Unique users with prediction records"),
    ("Total Predictions", total_predictions, "All recorded predictions"),
    ("HIV/AIDS Predictions", hiv_count, "HIV-related records"),
    ("Tuberculosis Predictions", tb_count, "TB-related records"),
]
for col, (label, value, help_text) in zip(metric_cols, metric_items):
    with col:
        with st.container(border=True):
            st.metric(label, f"{value:,}")
            st.caption(help_text)


st.markdown("### Explore Prediction Records")
filter_cols = st.columns([1, 1, 2], gap="medium")
with filter_cols[0]:
    disease_filter = st.selectbox("Filter by Disease", ["ALL", "Tuberculosis", "HIV"], key="admin_disease_filter")
with filter_cols[1]:
    user_options = sorted(df["user_email"].dropna().astype(str).unique().tolist()) if not df.empty and "user_email" in df.columns else []
    user_filter = st.selectbox("Filter by User", ["ALL"] + user_options, key="admin_user_filter")
with filter_cols[2]:
    st.markdown("<div style='padding-top:2rem;color:#718078;font-size:.88rem'>Use the filters to update the analytics and prediction records below.</div>", unsafe_allow_html=True)

filtered_df = df.copy()
if not filtered_df.empty and disease_filter != "ALL" and "disease" in filtered_df.columns:
    if disease_filter == "Tuberculosis":
        filtered_df = filtered_df[filtered_df["disease"].astype(str).str.lower().isin(["tb", "tuberculosis"])]
    else:
        filtered_df = filtered_df[filtered_df["disease"].astype(str).str.lower().isin(["hiv", "hiv/aids", "hiv aids"])]
if not filtered_df.empty and user_filter != "ALL" and "user_email" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["user_email"] == user_filter]

chart_df = filtered_df.copy()
if not chart_df.empty and "created_at" in chart_df.columns:
    chart_df["created_at"] = pd.to_datetime(chart_df["created_at"], errors="coerce", utc=True)
    chart_df = chart_df.dropna(subset=["created_at"])


st.markdown("### Prediction Analytics")
left, right = st.columns([1.45, 1], gap="medium")

with left:
    with st.container(border=True):
        st.markdown("#### Prediction Trends")
        st.caption("Monthly prediction activity by disease")
        if not chart_df.empty and "disease" in chart_df.columns:
            trend_df = chart_df.copy()
            trend_df["Month"] = trend_df["created_at"].dt.strftime("%b %Y")
            trend_df["_month_sort"] = trend_df["created_at"].dt.to_period("M").astype(str)
            trend = trend_df.groupby(["_month_sort", "Month", "disease"], as_index=False).size().rename(columns={"size": "Predictions"})
            trend = trend.sort_values("_month_sort")
            fig = px.line(
                trend, x="Month", y="Predictions", color="disease", markers=True,
                color_discrete_map={"HIV": CHART_GREEN, "HIV/AIDS": CHART_GREEN, "Tuberculosis": CHART_GREEN_LIGHT, "TB": CHART_GREEN_LIGHT},
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=7))
            fig.update_layout(
                height=330, margin=dict(l=8, r=8, t=12, b=8),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=CHART_TEXT), legend_title_text="Disease",
                xaxis=dict(title=None, showgrid=False, color=CHART_TEXT, linecolor=CHART_GRID),
                yaxis=dict(title="Number of predictions", gridcolor=CHART_GRID, zeroline=False, color=CHART_TEXT),
            )
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("Prediction trend data will appear here when records are available.")

with right:
    with st.container(border=True):
        st.markdown("#### Prediction Outcomes")
        st.caption("Positive and negative prediction results")
        if not filtered_df.empty and "prediction" in filtered_df.columns:
            outcome_values = pd.to_numeric(filtered_df["prediction"], errors="coerce")
            positive_count = int((outcome_values == 1).sum())
            negative_count = int((outcome_values == 0).sum())
            other_count = int(outcome_values.isna().sum())
            outcome_labels = ["Positive", "Negative"]
            outcome_counts = [positive_count, negative_count]
            if other_count:
                outcome_labels.append("Other / Unavailable")
                outcome_counts.append(other_count)
            if sum(outcome_counts):
                fig = px.pie(
                    names=outcome_labels, values=outcome_counts, hole=.68,
                    color=outcome_labels,
                    color_discrete_map={"Positive": CHART_GREEN, "Negative": CHART_GREEN_LIGHT, "Other / Unavailable": "#82938a"},
                )
                fig.update_traces(textinfo="percent", textposition="inside", hole=.68)
                fig.update_layout(
                    height=330, margin=dict(l=8, r=8, t=8, b=8),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=CHART_TEXT), legend=dict(orientation="h", y=-.08, x=.5, xanchor="center", font=dict(color=CHART_TEXT)),
                    annotations=[dict(text=f"{sum(outcome_counts):,}<br><span style='font-size:12px'>Total</span>", x=.5, y=.5, showarrow=False, font=dict(size=21, color=CHART_TEXT))],
                )
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
            else:
                st.info("No classified prediction outcomes are available.")
        else:
            st.info("Prediction outcome data will appear here when records are available.")


st.markdown("### Activity Overview")
left, right = st.columns([1, 1.2], gap="medium")
with left:
    with st.container(border=True):
        st.markdown("#### Predictions by Disease")
        st.caption("Share of records for each disease")
        if not filtered_df.empty and "disease" in filtered_df.columns:
            disease_counts = filtered_df["disease"].value_counts().rename_axis("Disease").reset_index(name="Predictions")
            disease_counts["Share"] = disease_counts["Predictions"] / max(1, disease_counts["Predictions"].sum()) * 100
            for _, item in disease_counts.iterrows():
                st.markdown(f"**{item['Disease']}** · {int(item['Predictions']):,} ({item['Share']:.1f}%)")
                st.progress(float(item["Share"]) / 100)
        else:
            st.info("No disease records match the selected filters.")

with right:
    with st.container(border=True):
        st.markdown("#### Recent Predictions")
        st.caption("Most recently recorded predictions")
        if not filtered_df.empty:
            recent = filtered_df.copy()
            if "created_at" in recent.columns:
                recent["created_at"] = pd.to_datetime(recent["created_at"], errors="coerce", utc=True)
                recent = recent.sort_values("created_at", ascending=False, na_position="last")
            display_cols = [c for c in ["user_email", "disease", "prediction", "created_at"] if c in recent.columns]
            recent = recent[display_cols].head(5).copy()
            if "prediction" in recent.columns:
                recent["prediction"] = recent["prediction"].map({1: "Positive", 0: "Negative", True: "Positive", False: "Negative"}).fillna(recent["prediction"].astype(str))
            if "created_at" in recent.columns:
                recent["created_at"] = recent["created_at"].dt.strftime("%d %b %Y, %I:%M %p UTC")
            recent = recent.rename(columns={"user_email": "User", "disease": "Disease", "prediction": "Result", "created_at": "Date"})
            st.dataframe(recent, use_container_width=True, hide_index=True)
        else:
            st.info("No recent predictions match the selected filters.")


st.markdown("### Detailed Analytics")
if not filtered_df.empty:
    detail_left, detail_right = st.columns(2, gap="medium")
    with detail_left:
        with st.container(border=True):
            st.markdown("#### Disease Outcome Breakdown")
            if {"disease", "prediction"}.issubset(filtered_df.columns):
                grouped = filtered_df.copy()
                grouped["Outcome"] = pd.to_numeric(grouped["prediction"], errors="coerce").map({0: "Negative", 1: "Positive"})
                grouped = grouped.dropna(subset=["Outcome"]).groupby(["disease", "Outcome"]).size().reset_index(name="Predictions")
                if not grouped.empty:
                    fig = px.bar(
                        grouped, x="disease", y="Predictions", color="Outcome", barmode="group", text_auto=True,
                        color_discrete_map={"Negative": CHART_GREEN_LIGHT, "Positive": CHART_GREEN},
                    )
                    fig.update_layout(height=320, margin=dict(l=8, r=8, t=10, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=CHART_TEXT), legend_title_text="", xaxis_title=None, yaxis_title="Predictions", xaxis=dict(color=CHART_TEXT, linecolor=CHART_GRID), yaxis=dict(gridcolor=CHART_GRID, color=CHART_TEXT))
                    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
                else:
                    st.info("No outcome breakdown is available.")
            else:
                st.info("The required prediction fields are unavailable.")
    with detail_right:
        with st.container(border=True):
            st.markdown("#### Daily App Usage")
            if not chart_df.empty:
                daily_usage = chart_df.assign(Date=chart_df["created_at"].dt.date).groupby("Date").size().reset_index(name="Predictions")
                daily_usage = daily_usage.sort_values("Date").tail(30)
                fig = px.area(daily_usage, x="Date", y="Predictions")
                fig.update_traces(line=dict(color=CHART_GREEN, width=3), fillcolor="rgba(32,232,117,.20)" if DARK_MODE else "rgba(104,184,120,.18)")
                fig.update_layout(height=320, margin=dict(l=8, r=8, t=10, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=CHART_TEXT), xaxis_title=None, yaxis_title="Predictions", xaxis=dict(color=CHART_TEXT, linecolor=CHART_GRID), yaxis=dict(gridcolor=CHART_GRID, color=CHART_TEXT))
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
            else:
                st.info("Daily usage data is not available.")

    with st.container(border=True):
        st.markdown("#### Most Active Users")
        if "user_email" in filtered_df.columns:
            user_activity = filtered_df["user_email"].value_counts().head(10).rename_axis("User").reset_index(name="Predictions")
            fig = px.bar(user_activity, x="Predictions", y="User", orientation="h", text_auto=True)
            fig.update_traces(marker_color=CHART_GREEN)
            fig.update_layout(height=max(260, 38 * len(user_activity)), margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=CHART_TEXT), xaxis=dict(title="Predictions", gridcolor=CHART_GRID, color=CHART_TEXT), yaxis=dict(title=None, autorange="reversed", color=CHART_TEXT))
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
else:
    st.info("Detailed analytics will appear when prediction records match the selected filters.")


with st.container(border=True):
    st.markdown("#### All Prediction Records")
    st.caption(f"{len(filtered_df):,} record(s) match the current filters")
    if filtered_df.empty:
        st.info("No data found.")
    else:
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="admin_data_export.csv",
        mime="text/csv",
        use_container_width=False,
    )


st.markdown("### User Feedback")
with st.container(border=True):
    st.caption(f"{total_feedback_count:,} feedback submission(s) received")
    if feedback_df.empty:
        st.info("No feedback has been submitted yet.")
    else:
        feedback_df["created_at"] = pd.to_datetime(feedback_df["created_at"], errors="coerce", utc=True)
        search = st.text_input("Search feedback by email", placeholder="example@gmail.com", key="admin_feedback_search")
        filtered_feedback = feedback_df.copy()
        if search:
            filtered_feedback = filtered_feedback[filtered_feedback["user_email"].astype(str).str.contains(search, case=False, na=False)]
        filtered_feedback = filtered_feedback.sort_values(by="created_at", ascending=False, na_position="last").reset_index(drop=True)
        if filtered_feedback.empty:
            st.info("No feedback matches your search.")
        else:
            feedbacks_per_page = 10
            total_pages = max(1, (len(filtered_feedback) + feedbacks_per_page - 1) // feedbacks_per_page)
            if "feedback_page" not in st.session_state:
                st.session_state.feedback_page = 1
            st.session_state.feedback_page = min(max(1, st.session_state.feedback_page), total_pages)
            page = st.session_state.feedback_page
            start = (page - 1) * feedbacks_per_page
            page_feedback = filtered_feedback.iloc[start:start + feedbacks_per_page]
            st.caption(f"Showing {start + 1}–{min(start + feedbacks_per_page, len(filtered_feedback))} of {len(filtered_feedback)} feedback submission(s)")
            for _, row in page_feedback.iterrows():
                timestamp = row["created_at"].strftime("%d %b %Y · %I:%M %p UTC") if pd.notna(row["created_at"]) else "Date unavailable"
                with st.expander(f"{row.get('user_email', 'Unknown user')}  ·  {timestamp}"):
                    st.write(row.get("feedback", ""))
            prev_col, page_col, next_col = st.columns([1, 2, 1])
            with prev_col:
                if st.button("← Previous", disabled=(page == 1), use_container_width=True, key="feedback_previous"):
                    st.session_state.feedback_page -= 1
                    st.rerun()
            with page_col:
                st.markdown(f"<div style='text-align:center;padding:.55rem;color:#64756c;font-weight:650'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
            with next_col:
                if st.button("Next →", disabled=(page == total_pages), use_container_width=True, key="feedback_next"):
                    st.session_state.feedback_page += 1
                    st.rerun()
