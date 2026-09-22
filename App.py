import streamlit as st
import time
from nav.tb_page import show_tb_page 
from nav.hiv_page import show_hiv_page
from auth import sign_up, login, logout, send_reset_otp, verify_otp_and_update_password,can_request_otp
from database import  get_user_role, save_feedback, get_user_name,supabase
from streamlit_extras.stylable_container import stylable_container
import qrcode
from io import BytesIO
import streamlit.components.v1 as components




# Page config
st.set_page_config(page_title="Disease Prediction App", layout="wide", initial_sidebar_state="collapsed")

# Hide default Streamlit elements (but keep sidebar toggle functionality)
hide_streamlit_style = """
    <style>
    /* Hide the main menu (hamburger menu) but keep sidebar toggle */
    #MainMenu {visibility: hidden;}

    /* Hide the footer */
    footer {visibility: hidden;}

    /* Hide the "Made with Streamlit" footer */
    .css-1d391kg {visibility: hidden;}

    /* Hide the three-dot menu in the top right */
    button[title="View fullscreen"] {visibility: hidden;}

    /* Hide the GitHub icon and other toolbar items */
    .css-14xtw13.e8zbici0 {visibility: hidden;}

    /* Hide toolbar elements but preserve sidebar controls */
    [data-testid="stDecoration"] {visibility: hidden;}

    /* Show status widget (includes running indicator) */
    [data-testid="stStatusWidget"] {visibility: visible !important;}

    /* Hide settings menu */
    button[kind="header"] {visibility: hidden;}

    /* Keep sidebar toggle button visible */
    button[data-testid="collapsedControl"] {visibility: visible !important;}

    /* Keep the sidebar toggle area visible */
    [data-testid="stSidebarNav"] {visibility: visible !important;}

    /* Ensure sidebar toggle button is accessible */
    .css-1544g2n {visibility: visible !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)






from persistent_session import restore_session

restore_session()
user = st.session_state.get("user")

# ---------------- HIDE SIDEBAR (ONLY IF NOT LOGGED IN) ----------------
if not user:
    hide_sidebar_style = """
        <style>
            section[data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)


# ---------------- SIDEBAR CONTENT  ----------------
if user and hasattr(user, "email"):
    name = st.session_state.get("full_name")

    if not name:
        name = user.email.split("@")[0]

    st.sidebar.success(f"Welcome, {name}")
    
else:
    st.sidebar.warning("Please log in")





st.markdown("""
<style> 
        .block-container{
            padding-top:1rem;
            padding-bottom: 0rem;
            margin-top: 1rem
            }
        
</style>
            """ , unsafe_allow_html=True)


# ================= AUTH PAGE =================
def auth_page():

    # ---------------- PAGE CONFIG ----------------
    st.set_page_config(
        page_title="Disease Prediction System",
        page_icon="🩺",
        layout="centered"
    )

    # ---------------- CSS ----------------
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a, #1e1b4b, #312e81, #111827);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Titles and Subtitles inside the white box */
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 10px;
        color: #5B4BDB;
    }

    .subtitle {
        text-align: center;
        color: #666; /* Darker gray for readability on white */
        margin-bottom: 30px;
        font-size: 16px;
    }

    /* Small text outside the box stays white */
    .stMarkdown p {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------- SESSION STATE ----------------
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "signin"

  
    if "reset_email_value" not in st.session_state:
        st.session_state.reset_email_value = ""

    if "reset_step" not in st.session_state:
        st.session_state.reset_step = "request"
    if "otp_timer_start" not in st.session_state:
        st.session_state.otp_timer_start = 0

    if "otp_cooldown" not in st.session_state:
        st.session_state.otp_cooldown = 60  # seconds

        \

    
        
    # ---------------- MAIN CONTAINER (CENTERED) ----------------
    # Use columns to NARROW the container on the screen
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1]) 

    with col2:
        with stylable_container(
        key="auth_box",
        css_styles="""
        {

            /* Default (dark mode fallback) */
            background-color: var(--secondary-background-color);
            padding: 40px;
            border-radius: 25px;
            box-shadow: 0px 10px 40px rgba(0,0,0,0.2);
            border: 1px solid rgba(128,128,128,0.2);

        }

        /* =====================================
        LIGHT MODE
        ===================================== */
        @media (prefers-color-scheme: light) {

            .st-key-st-key-auth_box {
                background: white !important;
                border-radius: 25px !important;
                padding: 40px !important;
                border: 1px solid #dee2e6 !important;
            }

            /* Form */
            [data-testid="stForm"] {
                background: #ffffff !important;
                color: #262730 !important;
                border: 1px solid #dee2e6 !important;
                border-top: none !important;
                border-top-left-radius: 0px !important;
                border-top-right-radius: 0px !important;
            }

            /* Labels */
            [data-testid="stForm"] label,
            [data-testid="stForm"] [data-testid="stWidgetLabel"] p {
                color: #262730 !important;
            }

            /* Inputs */
            [data-testid="stForm"] input[type="text"],
            [data-testid="stForm"] input[type="password"],
            [data-testid="stForm"] input[type="email"] {
                background: #f8f9fa !important;
                color: #262730 !important;
                border: 1px solid #dee2e6 !important;
            }

            /* Placeholders */
            [data-testid="stForm"] input::placeholder {
                color: rgba(38,39,48,0.6) !important;
            }
        }

        /* =====================================
        DARK MODE
        ===================================== */
        @media (prefers-color-scheme: dark) {
        /* Target form containers */
        [data-testid="stForm"] {
            background: var(--st-secondary-background-color, #0e1117) !important;
            color: var(--st-text-color, #fafafa) !important;
            border: 1px solid var(--st-border-color, #262730) !important;
        }

        .st-key-st-key-auth_box {
            background: var(--st-secondary-background-color, #0e1117) !important;
            border-radius: 25px !important;
            border: 1px solid var(--st-border-color, #262730) !important;
        }

        /* Target text and labels inside forms AND their containers */
        [data-testid="stForm"] .stMarkdown,
        [data-testid="stForm"] .stText,
        [data-testid="stForm"] label,
        [data-testid="stForm"] [data-testid="stWidgetLabel"] p,
        [data-testid="stVerticalBlock"]:has([data-testid="stForm"]) .stMarkdown,
        [data-testid="stVerticalBlock"]:has([data-testid="stForm"]) .stText,
        [data-testid="stVerticalBlock"]:has([data-testid="stForm"]) label,
        [data-testid="column"]:has([data-testid="stForm"]) .stMarkdown,
        [data-testid="column"]:has([data-testid="stForm"]) .stText,
        [data-testid="column"]:has([data-testid="stForm"]) label {
            color: var(--st-text-color, #fafafa) !important;
        }

        /* Target input placeholders inside forms */
        [data-testid="stForm"] input::placeholder,
        [data-testid="stVerticalBlock"]:has([data-testid="stForm"]) input::placeholder,
        [data-testid="column"]:has([data-testid="stForm"]) input::placeholder {
            color: rgba(250, 250, 250, 0.6) !important;
        }

        /* Target input fields inside forms and containers */
        [data-testid="stForm"] input[type="text"],
        [data-testid="stForm"] input[type="password"],
        [data-testid="stForm"] input[type="email"],
        [data-testid="stVerticalBlock"]:has([data-testid="stForm"]) input[type="text"],
        [data-testid="stVerticalBlock"]:has([data-testid="stForm"]) input[type="password"],
        [data-testid="stVerticalBlock"]:has([data-testid="stForm"]) input[type="email"],
        [data-testid="column"]:has([data-testid="stForm"]) input[type="text"],
        [data-testid="column"]:has([data-testid="stForm"]) input[type="password"],
        [data-testid="column"]:has([data-testid="stForm"]) input[type="email"] {
            background: var(--st-background-color, #0e1117) !important;
            color: var(--st-text-color, #fafafa) !important;
            border: 1px solid var(--st-border-color, #262730) !important;
        }

        /* If you're using custom glass-card class for containers */
        .glass-card:has([data-testid="stForm"]) {
            background: var(--st-secondary-background-color, #0e1117) !important;
            color: var(--st-text-color, #fafafa) !important;
            border: 1px solid var(--st-border-color, #262730) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
    }
        /* =====================================
        EMAIL + PASSWORD JOIN EFFECT
        ===================================== */

        div[data-testid="stVerticalBlock"] > div:has(input[key="auth_email"]) {
            width: calc(100% - 2px) !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-bottom: -32px !important;
        }

        input[key="auth_email"] {
            border-bottom-left-radius: 0px !important;
            border-bottom-right-radius: 0px !important;
            border-bottom: none !important;
        }

        [data-testid="stForm"] {
            border-top: none !important;
            border-top-left-radius: 0px !important;
            border-top-right-radius: 0px !important;
        }
        """,
    ):
                if st.session_state.auth_mode == "otp_reset":

                    st.markdown('<div class="title">Reset Password via OTP</div>', unsafe_allow_html=True)

                    # =================================================
                    # STEP 1: REQUEST OTP
                    # =================================================
                    if st.session_state.reset_step == "request":

                        email = st.text_input(
                            "Email",
                            placeholder="Enter your email",
                            key="auth_reset_email_input"
                        )

                        st.markdown('<div class="subtitle">A 6-digit code will be sent to your inbox</div>', unsafe_allow_html=True)

                        if st.button("Send Reset Code", use_container_width=True):

                            if not email:
                                st.warning("Please enter your email address.")

                            elif not can_request_otp() and st.session_state.otp_timer_start != 0:
                                st.warning("You can only request a new OTP after 1 minute.")

                            else:
                                with st.spinner("Sending code..."):

                                    success = send_reset_otp(email.strip())

                                    if success:
                                        st.success("A 6-digit code has been sent to your email.")

                                        st.session_state.reset_email_value = email.strip()
                                        st.session_state.reset_step = "verify"

                                        # START TIMER
                                        st.session_state.otp_timer_start = time.time()

                                        st.rerun()

                                    else:
                                        st.error("Failed to send code. Try again.")

                        if st.button("← Back to Sign In", use_container_width=True):
                            st.session_state.auth_mode = "signin"
                            st.rerun()


                    # =================================================
                    # STEP 2: VERIFY OTP + RESET PASSWORD
                    # =================================================
                    elif st.session_state.reset_step == "verify":

                        st.markdown(
                            '<div class="subtitle">Enter OTP and new password</div>',
                            unsafe_allow_html=True
                        )

                        otp_code = st.text_input(
                            "Enter 6-digit OTP Code",
                            max_chars=6,
                            placeholder="000000"
                        )

                        new_password = st.text_input(
                            "New Password",
                            type="password",
                            placeholder="Enter new password"
                        )

                        confirm_password = st.text_input(
                            "Confirm New Password",
                            type="password",
                            placeholder="Confirm new password"
                        )

                        # =================================================
                        # VERIFY BUTTON
                        # =================================================
                        if st.button("Verify & Update Password", use_container_width=True):

                            if not otp_code or not new_password or not confirm_password:
                                st.warning("Please fill out all fields.")

                            elif new_password != confirm_password:
                                st.error("Passwords do not match.")

                            else:
                                with st.spinner("Verifying code and updating password..."):

                                    success = verify_otp_and_update_password(
                                        st.session_state.reset_email_value,
                                        otp_code.strip(),
                                        new_password.strip()
                                    )

                                    if success:
                                        st.success(
                                            "Password updated successfully! Please sign in with your new password."
                                        )
                                        st.balloons()

                                        # RESET EVERYTHING
                                        st.session_state.auth_mode = "signin"
                                        st.session_state.reset_step = "request"
                                        st.session_state.reset_email_value = ""
                                        st.session_state.otp_timer_start = 0

                                        st.rerun()

                                    else:
                                        st.error("try the verify button again or Invalid/expired OTP code.")

                        # =================================================
                        # RESEND SECTION
                        # =================================================
                        st.markdown("---")
                        st.subheader("Need a new code?")

                        if st.button("Resend OTP", use_container_width=True):

                            if not can_request_otp():
                                st.warning("Please wait 1 minute before requesting a new code.")

                            else:
                                with st.spinner("Sending new code..."):

                                    success = send_reset_otp(
                                        st.session_state.reset_email_value
                                    )

                                    if success:
                                        st.success("New OTP sent! Check your email.")

                                        # Restart cooldown timer
                                        st.session_state.otp_timer_start = time.time()

                                        st.rerun()

                                    else:
                                        st.error("Failed to resend OTP.")

                        # =================================================
                        # CHANGE EMAIL
                        # =================================================
                        if st.button("Use Another Email", use_container_width=True):

                            st.session_state.reset_step = "request"
                            st.session_state.reset_email_value = ""

                            st.rerun()

                        # =================================================
                        # BACK TO SIGN IN
                        # =================================================
                        if st.button("← Back to Sign In", use_container_width=True):

                            st.session_state.auth_mode = "signin"
                            st.session_state.reset_step = "request"
                            st.session_state.reset_email_value = ""
                            st.session_state.otp_timer_start = 0

                            st.rerun()

                # =================================================
                #                   SIGN IN
                # =================================================
                elif st.session_state.auth_mode == "signin":
                    st.markdown('<div class="title">Welcome Back</div>', unsafe_allow_html=True)
                    st.markdown('<div class="subtitle">Sign in to continue</div>', unsafe_allow_html=True)

                    email = st.text_input("Email", placeholder="Enter your email", key="auth_email")

                    with st.form("signin_form"):
                    
                        password = st.text_input("Password", type="password", placeholder="Enter your password")
                        signin_btn = st.form_submit_button("Sign In", use_container_width=True)

                    
                    if st.button("Forgot Password?"):
                        st.session_state.auth_mode = "otp_reset"
                        st.rerun()

                    if signin_btn:
                        if email and password:

                            success = login(email, password)

                            if success:
                                st.success("Login successful")
                                st.balloons()
                                st.rerun()

                            else:
                                st.error("Invalid email or password")

                        else:
                            st.warning("Please fill all fields")

                    st.markdown("---")
                    st.markdown("<p style='color:#31333F; text-align:center;'>Don't have an account?</p>", unsafe_allow_html=True)
                    if st.button("Create New Account", use_container_width=True):
                        st.session_state.auth_mode = "signup"
                        st.rerun()

                # =================================================
                #                   SIGN UP
                # =================================================
                else:
                    st.markdown('<div class="title">Create Account</div>', unsafe_allow_html=True)
                    st.markdown('<div class="subtitle">Join the system</div>', unsafe_allow_html=True)

                    with st.form("signup_form"):
                        name = st.text_input("Full Name", placeholder="Enter your full name")
                        email = st.text_input("Email", placeholder="Enter your email")
                        password = st.text_input("Password", type="password")
                        confirm_password = st.text_input("Confirm Password", type="password")
                        terms = st.checkbox("I agree to the Terms & Conditions")
                        signup_btn = st.form_submit_button("Create Account", use_container_width=True)

                    #  Create an empty container 
                    
                    error_container = st.empty()

                    if signup_btn:
                        clean_name = name.strip()
                        clean_email = email.strip()
                        clean_password = password.strip()
                        clean_confirm = confirm_password.strip()

                       
                        if not all([clean_name, clean_email, clean_password, clean_confirm]):
                            error_container.warning("All fields are required. Please fill them out completely.")
                        
                        elif clean_password != clean_confirm:
                            error_container.error("Passwords do not match.")
                            
                        elif not terms:
                            error_container.error("You must agree to the Terms & Conditions.")
                            
                        else:
                            with st.spinner("Creating your account..."):
                                response = sign_up(clean_email, clean_password, clean_name)
                                
                                if response:
                                    st.success("Account created successfully!")
                                    st.balloons()
                                    
                                    st.session_state.auth_mode = "signin"
                                    st.rerun()

                    st.markdown("---")

                    if st.button("Sign In Instead", use_container_width=True):
                        st.session_state.auth_mode = "signin"
                        st.rerun()



def dashboard():

   

    disease_options = ["Tuberculosis", "HIV/AIDS"]

    # =========================
    # INIT STATE
    # =========================
    if "page" not in st.session_state:
        st.session_state.page = "Tuberculosis"

    if "use_quick_select" not in st.session_state:
        st.session_state.use_quick_select = False


    # =========================
    # URL ROUTING 
    # =========================
    query_params = st.query_params

    if "page" in query_params:
        url_page = query_params["page"]
        if url_page in disease_options:
            st.session_state.page = url_page


    def set_page(page):
        st.session_state.page = page
        st.query_params["page"] = page


    # =========================
    # HERO SECTION
    # =========================
    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-title">Disease Prediction System</div>
        <div class="hero-subtitle">
            ML-powered Tuberculosis & HIV/AIDS Prediction Platform
        </div>
        <br>
        <div style="opacity:0.85;">
            Logged in as: <b>{st.session_state['user'].email}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # =========================================================
    # 🎛 COMPACT & RESPONSIVE CONTROLS PANEL
    # =========================================================
    with stylable_container(
        key="responsive_control_panel",
        css_styles="""
        {
            display: flex;
            flex-direction: column;
            gap: 16px; /* Increased overall layout flex gap */
            align-items: flex-end;
            margin: 15px 30px;
            width: auto;
        }

        div[data-element-to-style="stVerticalBlock"] > div {
            width: 240px;
            background: rgba(15, 15, 35, 0.75);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 14px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }

        /* ===========================
        iOS STYLE SEGMENTED CONTROL
        =========================== */

        div[data-baseweb="button-group"] {
            position: relative;
            background: rgba(0,0,0,0.05) !important;
            border-radius: 12px;
            padding: 4px;
            border: 1px solid rgba(0,0,0,0.08);
            display: flex;
            overflow: hidden;
        }

        /* ALL BUTTONS */
        div[data-baseweb="button-group"] button {
            flex: 1;
            background: transparent !important;
            color: #444 !important;
            border: none !important;
            z-index: 2;
            transition: color 0.25s ease;
        }

        /* HIDE STREAMLIT ACTIVE STYLE */
        div[data-baseweb="button-group"] button[data-testid="stBaseButton-segmented_controlActive"] {
            background: transparent !important;
            color: #7b2cff !important;
        }

        /* SLIDING INDICATOR */
        div[data-baseweb="button-group"]::before {
            content: "";
            position: absolute;
            top: 4px;
            left: 4px;
            width: calc(50% - 4px);
            height: calc(100% - 8px);
            background: rgba(123, 44, 255, 0.25);
            border-radius: 10px;
            transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
            z-index: 1;
        }

        /* MOVE SLIDER WHEN SECOND BUTTON IS ACTIVE */
        div[data-baseweb="button-group"]:has(button[data-testid="stBaseButton-segmented_controlActive"]:nth-child(2))::before {
            transform: translateX(100%);
        }

        /* HOVER */
        div[data-baseweb="button-group"] button:hover {
            background: rgba(123, 44, 255, 0.08) !important;
        }
        @media (max-width: 768px) {
            {
                align-items: center !important;
                margin: 15px auto !important;
                width: 100% !important;
            }
            div[data-element-to-style="stVerticalBlock"] > div {
                width: 90% !important;
                max-width: 320px;
            }
        }
        """
    ):
        # 1. The Toggle Switch
        st.session_state.use_quick_select = st.checkbox(
            "Use quick selection",
            value=st.session_state.use_quick_select,
            key="quick_select_toggle"
        )

        # 2. Render Quick Switch layout if checked
        if st.session_state.use_quick_select:
            selected = st.segmented_control(
                "Quick Switch",
                options=disease_options,
                default=st.session_state.page,
                label_visibility="collapsed",
                key="quick_switch_widget"
            )
            
            # if selected is not None and selected != st.session_state.page:
            #     st.session_state.page = selected
            #     st.query_params["page"] = selected
            #     st.rerun()


            if selected is not None and selected != st.session_state.page:
                st.session_state.page = selected

                if st.query_params.get("page") != selected:
                    st.query_params["page"] = selected

                st.rerun()

   

    # =========================================================
    # 🎛 NAVIGATION STYLE 1: SIDEBAR (FALLBACK FULL CONTROL)
    # =========================================================
  
    if not st.session_state.use_quick_select:
        st.sidebar.subheader("Select a Disease")
        for disease in disease_options:
            # Instead of a complex callback sequence, we check the button state directly inline
            if st.sidebar.button(
                disease,
                use_container_width=True,
                type="primary" if st.session_state.page == disease else "secondary",
                key=f"btn_{disease}"
            ):
                st.session_state.page = disease
                st.query_params["page"] = disease
                st.rerun()


    


    # =========================
    # CONTENT ROUTING
    # =========================
    if st.session_state.page == "Tuberculosis":
        show_tb_page()

    elif st.session_state.page == "HIV/AIDS":
        show_hiv_page()



    # =====================================
    # SHARE APP SECTION
    # =====================================

    APP_URL = "testing2222222.streamlit.app"   

    st.sidebar.divider()

    with st.sidebar.expander(" Share This App", icon=":material/share:", expanded=False):

        # -------------------------
        # App Link
        # -------------------------
        st.text_input(
            "App Link",
            value=APP_URL,
            disabled=True,
            key="share_link"
        )

        # -------------------------
        # QR Code
        # -------------------------
        qr = qrcode.make(APP_URL)

        buf = BytesIO()
        qr.save(buf, format="PNG")

        st.image(
            buf.getvalue(),
            width=180,
            caption="Scan QR Code"
        )

        # -------------------------
        # Native Mobile Share
        # -------------------------
        # components.html(
        #     f"""
        #     <button id="shareBtn"
        #         style="
        #             width:100%;
        #             padding:10px;
        #             border:none;
        #             border-radius:10px;
        #             background:#7b2cff;
        #             color:white;
        #             cursor:pointer;
        #             font-weight:600;
        #         ">
        #         📱 Share on Device
        #     </button>

        components.html(
        f"""
        <button id="shareBtn"
            style="
                width:100%;
                padding:10px;
                border:none;
                border-radius:10px;
                background:#7b2cff;
                color:white;
                cursor:pointer;
                font-weight:600;
                display:flex;
                align-items:center;
                justify-content:center;
                gap:8px;
            ">
            Share on Device 
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
            </svg>
        </button>


            <script>
            document.getElementById("shareBtn").onclick = async () => {{
                try {{
                    await navigator.share({{
                        title: "Disease Prediction System",
                        text: "Try this TB & HIV Prediction App",
                        url: "{APP_URL}"
                    }});
                }} catch(err) {{
                    console.log(err);
                }}
            }};
            </script>
            """,
            height=60,
        )



    st.markdown("<br>", unsafe_allow_html=True)

    # --- Feedback section stays underneath ---
    st.badge("Feedback or Comment", color="primary", icon="💬")

    feedback = st.text_area(
        label="feedback",
        label_visibility="collapsed",
        placeholder="Your feedback helps us improve!",
        height=100
    ).strip()

    submit_feedback = st.button("Submit Feedback", use_container_width=True)
    
    if submit_feedback:
        if feedback:
            user_email = st.session_state["user"].email
            response = save_feedback(user_email, feedback)
            if response:
                st.success("Feedback submitted successfully")
        else:
            st.warning("Please enter your feedback first")

    st.divider()
    st.markdown("""
    <br><br>
    <div style='text-align:center; color:white; opacity:0.7;'>
         PREEMPTIVE DIAGNOSIS OF CHRONIC DISEASE:
TUBERCULOSIS And HIV/AIDS USING A QUESTIONNAIRE BASED MACHINE
LEARNING APPROACE <br>
        Built with Streamlit + Supabase + Machine Learning(Group 2)
    </div>
    """, unsafe_allow_html=True)
            
            
    
    if st.sidebar.button("Logout", icon=":material/logout:"):
        logout()
        st.rerun()

    # st.sidebar.button("Logout", icon=":material/exit_to_app:")
    
    







# ================= LOAD CSS =================
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )



# ================= APPLY CSS =================
local_css("styles.css")

  



## ----------Router -------
if st.session_state["user"] is None:
    auth_page()
else:
    dashboard()