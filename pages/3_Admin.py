import streamlit as st
import pandas as pd
from database import get_all_predictions,get_user_role,get_all_feedback
import plotly.express as px
from auth import logout




if st.session_state.get("user") is None:
    st.warning("You have been logged out. Please log in again from the home page.")
    st.stop()  # Aborts running the rest of the page instantly

# ================= LOAD CSS =================
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )



# ================= APPLY CSS =================
local_css("styles.css")
st.markdown("""
<style>

/* Metric cards */
[data-testid="stVerticalBlockBorderWrapper"]{
    border-radius:16px;
    border:1px solid rgba(128,128,128,.25);
    transition:.2s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover{
    transform:translateY(-2px);
    box-shadow:0 8px 18px rgba(0,0,0,.08);
}

</style>
""", unsafe_allow_html=True)


st.title("Admin Dashboard")

st.sidebar.info(
    f"Role: {st.session_state.get('role', 'user')}"
)

st.write(st.session_state["user"].email)


# -------------Auth check----------------
user_email = st.session_state['user'].email 
if st.session_state.get("role") != "admin":
    st.error("Access denied. Admins only.")
    st.stop()




# -------------Fetch all predictions----------------
data = get_all_predictions()
df = pd.DataFrame(data) if data else pd.DataFrame()


### feedback data---------------
feedback_data = get_all_feedback()
feedback_df = pd.DataFrame(feedback_data) if feedback_data else pd.DataFrame()


#---------------System Overview metrics----------------
# st.header("System Overview")
# col1, col2, col3, col4, col5 = st.columns(5)

# with col1:
#     st.metric(label="Total Predictions", value=len(df))

# with col2:
#     total_users = df['user_email'].nunique() if not df.empty else 0
#     st.metric("Total Users", total_users)

# with col3:
#     tb_count = len(df[df['disease'] == 'Tuberculosis']) if not df.empty else 0
#     st.metric("TB Cases", tb_count)

# with col4:
#     hiv_count = len(df[df['disease'] == 'HIV']) if not df.empty else 0
#     st.metric("HIV Cases", hiv_count)

# with col5:
#     st.metric(
#         "Total Feedback",
#         len(feedback_df)
#     )



# ===================== System Overview =====================

st.header("📊 System Overview")

# Metrics
total_predictions = len(df)
total_users = df["user_email"].nunique() if not df.empty else 0
tb_count = len(df[df["disease"] == "Tuberculosis"]) if not df.empty else 0
hiv_count = len(df[df["disease"] == "HIV"]) if not df.empty else 0
total_feedback = len(feedback_df)

# ---------------- Row 1 ----------------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.caption("Total Predictions")
        st.markdown(
            f"<h2 style='text-align:center; margin:0;'>{total_predictions}</h2>",
            unsafe_allow_html=True
        )

with col2:
    with st.container(border=True):
        st.caption("Total Users")
        st.markdown(
            f"<h2 style='text-align:center; margin:0;'>{total_users}</h2>",
            unsafe_allow_html=True
        )

# ---------------- Row 2 ----------------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.caption("TB Cases")
        st.markdown(
            f"<h2 style='text-align:center; margin:0;'>{tb_count}</h2>",
            unsafe_allow_html=True
        )

with col2:
    with st.container(border=True):
        st.caption("HIV Cases")
        st.markdown(
            f"<h2 style='text-align:center; margin:0;'>{hiv_count}</h2>",
            unsafe_allow_html=True
        )

# ---------------- Row 3 ----------------
with st.container(border=True):
    st.caption("Total Feedback")
    st.markdown(
        f"<h2 style='text-align:center; margin:0;'>{total_feedback}</h2>",
        unsafe_allow_html=True
    )
## ------------Filter --------------------------------
st.subheader("Filters")

col1, col2 = st.columns(2)

with col1:
    disease_filter = st.selectbox(
        "Filter by Disease",
        ["ALL", "TB","HIV"]
    )
with col2:
    user_filter = st.selectbox(
        "Filter by User",
        ["ALL"] + list(df["user_email"].unique() if not df.empty else ["ALL"])
    )


# ------------------Apply Filters----------------------
filtered_df = df.copy()

if disease_filter != "ALL":
    filtered_df = filtered_df[filtered_df["disease"] == disease_filter]

if user_filter != "ALL":
    filtered_df = filtered_df[filtered_df["user_email"] == user_filter]


#-----------Prediction Status----------------
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Prediction Results")

positive = len(df[df["prediction"] == 1]) if not df.empty else 0
negative = len(df[df["prediction"] == 0]) if not df.empty else 0

st.markdown(f"""
<style>

.results-container {{
    display: flex;
    gap: 15px;
    width: 100%;
}}

.result-card {{
    flex: 1;
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}}

.result-title {{
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
}}

.result-value {{
    font-size: 34px;
    font-weight: bold;
}}

</style>

<div class="results-container">

<div class="result-card">
<div class="result-title">Positive Cases</div>
<div class="result-value">{positive}</div>
</div>

<div class="result-card">
<div class="result-title">Negative Cases</div>
<div class="result-value">{negative}</div>
</div>

</div>
""", unsafe_allow_html=True)

#--------------Pie chart:TB VS HIV DISTRIBUTION------------

st.markdown("<hr>", unsafe_allow_html=True)
if not filtered_df.empty:
    disease_counts = filtered_df["disease"].value_counts()

    fig =  px.pie(
        values = disease_counts.values,
        names = disease_counts.index,
       
        color_discrete_sequence = px.colors.qualitative.Dark24,
        title = "Disease Distribution",
        hover_data = {"value": disease_counts.values},
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        
        textfont_size=16,
        hovertemplate="<b>%{label}</b><br>Cases: %{value}<br>Percentage: (%{percent})<extra></extra>",
        pull=[0.1 if i == 0 else 0.02 for i in range(len(disease_counts))]
    )
    fig.update_layout(
       
        title={
        'font': {
            'color': '#FFFFFF',
            'size': 24
            }
        },
    
        template ="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font_size=24,
        title_x=0.5,
        height=700,
        width=800,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=14, color="#FFFFFF"),
        showlegend=True,
        yaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",
        linecolor="rgba(255, 255, 255, 0.2)"
        ),
         xaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",
        linecolor="rgba(255, 255, 255, 0.2)"
        ),
        legend = dict(
            orientation="v",
            yanchor="middle",
            y=-0.5,
            xanchor="left",
            x=1.01,
            font=dict(color="#FFFFFF")
        ),
        modebar=dict(
        activecolor="#FFD700",  
        color="#FFFFFF",       
        bgcolor="rgba(0, 0, 0, 0)" # Keeps the toolbar background completely transparent
        )   
    )
    st.plotly_chart(fig, use_container_width=True)


# Bar Chart:Postive vs negative
st.markdown("<hr>", unsafe_allow_html=True)

if not filtered_df.empty:

    result_counts =(filtered_df["prediction"].value_counts().reset_index())

    result_counts.columns = ["prediction", "count"]

    result_counts["prediction"] = (result_counts["prediction"].map({0: "Negative", 1: "Positive"}))

    fig = px.bar(
        result_counts,
        x="prediction",
        y="count",
        color="prediction",
        color_discrete_sequence=["#636EFA", "#EF553B"],
        title="Prediction Outcome Distribution",
        text_auto=True,
    )
   
    fig.update_layout(
    # Make all general text white (title, legend, etc.)
    font=dict(color="#FFFFFF"),
    
    title={
        'font': {
            'color': '#FFFFFF',
            'size': 24
        }
    },
    
   
    legend={
        'font': {
            'color': '#FFFFFF'
        }
    },
    
   
    xaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",  
        linecolor="rgba(255, 255, 255, 0.2)"
    ),
    
    
    yaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",
        linecolor="rgba(255, 255, 255, 0.2)"
    ),
    
    # Make the default plot background blocks completely transparent
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    
    
    modebar=dict(
        activecolor="#FFD700",    
        color="#FFFFFF",          
        bgcolor="rgba(0, 0, 0, 0)"
    )
    )


    st.plotly_chart(fig, use_container_width=True)

##TB VS HIV + RESULT 
st.subheader("Disease Outcome Breakdown")

if not filtered_df.empty:
    grouped = (filtered_df.groupby(["disease","prediction"]).size().reset_index(name="Count"))
    grouped["prediction"] = (grouped["prediction"].map({0: "Negative", 1: "Positive"}))

    #plot
    fig = px.bar(
        grouped,
        x="disease",
        y="Count",
        color="prediction",
        barmode="group",
        title="TB VS HIV Outcomes",
        text_auto=True,
        color_discrete_sequence=["#636EFA", "#EF553B"],
    )

    
    fig.update_layout(
    # Make all general text white (title, legend, etc.)
    font=dict(color="#FFFFFF"),

    title={
        'font': {
            'color': '#FFFFFF',
            'size': 24
        }
    },
    
   
    legend={
        'font': {
            'color': '#FFFFFF'
        }
    },
    
    
    xaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",  
        linecolor="rgba(255, 255, 255, 0.2)"
    ),
    
    
    yaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",
        linecolor="rgba(255, 255, 255, 0.2)"
    ),
    
   
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    
   
    modebar=dict(
        activecolor="#FFD700",   
        color="#FFFFFF",         
        bgcolor="rgba(0, 0, 0, 0)"
    )
    )


    st.plotly_chart(fig, use_container_width=True)


    

##---------------------APP Usage Tracking-------------------
st.subheader("Daily App Usage")
if not filtered_df.empty:
    filtered_df["created_at"] = pd.to_datetime(filtered_df["created_at"])
    
    #extract date from datetime 
    filtered_df["date"] = (filtered_df["created_at"].dt.date)

    #count daily predictions
    daily_usage = (
        filtered_df.groupby("date").size().reset_index(name="Prediction")

    )
    fig = px.line(
        daily_usage,
        x="date",
        y="Prediction",
        title="Daily Prediction Activity",
        markers=True,
        template="plotly_white"
    )

    
    fig.update_layout(
    # Make all general text white (title, legend, etc.)
    font=dict(color="#FFFFFF"),
    
    title={
        'font': {
            'color': '#FFFFFF',
            'size': 24
        }
    },
    
    # 2. Style the Legend text color explicitly
    legend={
        'font': {
            'color': '#FFFFFF'
        }
    },
    
   
    xaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",  
        linecolor="rgba(255, 255, 255, 0.2)"
    ),
    
    
    yaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",
        linecolor="rgba(255, 255, 255, 0.2)"
    ),
    
    
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    
   
    modebar=dict(
        activecolor="#FFD700",   
        color="#FFFFFF",          
        bgcolor="rgba(0, 0, 0, 0)"
    )
    )


    fig.update_traces(
    line=dict(width=3), 
    marker=dict(size=8, color="#FFFFFF"),
    hoverlabel=dict(
        bgcolor="#090d1f", 
        font_size=14,
        font_color="#FFFFFF"
    )
    )


    st.plotly_chart(fig, use_container_width=True)
  


##----------------Most Active Users-------------------
st.subheader("Most Active Users")

if not filtered_df.empty:
    user_activity = (
        filtered_df["user_email"].value_counts().reset_index()
    )
    user_activity.columns = ["User", "predictions"]

    fig = px.bar(
        user_activity,
        x="User",
        y="predictions",
        title="User Activity",
        text_auto=True,
        template="plotly_white"
    )

    
    fig.update_layout(
    
    font=dict(color="#FFFFFF"),
  
    title={
        'font': {
            'color': '#FFFFFF',
            'size': 24
        }
    },
    
    
    legend={
        'font': {
            'color': '#FFFFFF'
        }
    },
    
    
    xaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",  
        linecolor="rgba(255, 255, 255, 0.2)"
    ),
    
    
    yaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="rgba(255, 255, 255, 0.1)",
        linecolor="rgba(255, 255, 255, 0.2)"
    ),
    
    
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    
    
    modebar=dict(
        activecolor="#FFD700",    
        color="#FFFFFF",          
        bgcolor="rgba(0, 0, 0, 0)"
    )
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------Full Data Table----------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("All Predictions Records")

if filtered_df.empty:
    st.info("No data found.")
else:
    st.dataframe(filtered_df, use_container_width=True)

#------------------Export Data----------------------
csv =filtered_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="admin_data_export.csv",
    mime="text/csv"
)


# =====================================================
# USER FEEDBACK
# =====================================================

st.divider()
st.header("User Feedback")

if feedback_df.empty:
    st.info("No feedback has been submitted yet.")

else:

    # convert date
    feedback_df["created_at"] = pd.to_datetime(
        feedback_df["created_at"]
    )

    # Search box
    search = st.text_input(
        "Search by Email",
        placeholder="example@gmail.com"
    )

    filtered_feedback = feedback_df.copy()

    if search:
        filtered_feedback = filtered_feedback[
            filtered_feedback["user_email"]
            .str.contains(search, case=False, na=False)
        ]

    # Latest first
    filtered_feedback = filtered_feedback.sort_values(
        by="created_at",
        ascending=False
    )

    st.subheader("Recent Feedback")

    if not filtered_feedback.empty:

        # ---------------- Sort Feedback ----------------
        filtered_feedback = filtered_feedback.sort_values(
            by="created_at",
            ascending=False
        ).reset_index(drop=True)

        # ---------------- Pagination Settings ----------------
        feedbacks_per_page = 10

        total_feedback = len(filtered_feedback)
        total_pages = max(
            1,
            (total_feedback + feedbacks_per_page - 1) // feedbacks_per_page
        )

        # ---------------- Current Page ----------------
        if "feedback_page" not in st.session_state:
            st.session_state.feedback_page = 1

        # Prevent invalid page numbers
        if st.session_state.feedback_page > total_pages:
            st.session_state.feedback_page = total_pages

        if st.session_state.feedback_page < 1:
            st.session_state.feedback_page = 1

        page = st.session_state.feedback_page

        # ---------------- Slice Current Page ----------------
        start = (page - 1) * feedbacks_per_page
        end = start + feedbacks_per_page

        page_feedback = filtered_feedback.iloc[start:end]

        # ---------------- Info ----------------
        st.caption(
            f"Showing {start + 1} - {min(end, total_feedback)} of {total_feedback} feedback(s)"
        )

        # ---------------- Feedback Expanders ----------------
        for _, row in page_feedback.iterrows():

            date = pd.to_datetime(row["created_at"]).strftime(
                "%d %b %Y • %I:%M %p"
            )

            with st.expander(f"👤 {row['user_email']}   |   🕒 {date}"):

                st.write(row["feedback"])

        # ---------------- Bottom Pagination ----------------
        st.divider()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button(
                "⬅ Previous",
                disabled=(page == 1),
                use_container_width=True,
                key="feedback_previous"
            ):
                st.session_state.feedback_page -= 1
                st.rerun()

        with col2:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:18px;
                    font-weight:600;
                    padding-top:8px;
                ">
                    Page {page} of {total_pages}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            if st.button(
                "Next ➡",
                disabled=(page == total_pages),
                use_container_width=True,
                key="feedback_next"
            ):
                st.session_state.feedback_page += 1
                st.rerun()

    else:
        st.info("No feedback available.")



###download feedback as CSV### 
feedback_csv = filtered_feedback.to_csv(index=False)

st.download_button(
    "Download Feedback CSV",
    feedback_csv,
    "feedback_export.csv",
    "text/csv"
)



st.sidebar.divider()
if st.sidebar.button("Logout", icon=":material/power_settings_new:"):
    logout()
    st.rerun()