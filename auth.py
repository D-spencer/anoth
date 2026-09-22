from database import supabase, get_user_role, get_user_name
import streamlit as st
import time
from persistent_session import start_session, clear_session



# ---------------- SIGN UP ----------------
def sign_up(email, password, full_name):
    try:
        # Sanitize data
        email = email.strip()
        password = password.strip()
        full_name = full_name.strip()

        if not all([email, password, full_name]):
            raise ValueError("Email, password, and full name cannot be blank or empty spaces.")

        # ------------------ CREATE AUTH USER ------------------
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })

        if response.user:

            # Save profile information
            supabase.table("profiles").insert({
                "id": response.user.id,
                "email": email,
                "full_name": full_name
            }).execute()

            # Save default role
            supabase.table("user_roles").insert({
                "id": response.user.id,
                "email": email,
                "role": "user"
            }).execute()

            if response.session:
                start_session(response.session)

        return response

    except Exception as e:
        st.error(f"Signup Error: {e}")
        return None


# ---------------- LOGIN ----------------
def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })


        if response.user and response.session:


            start_session(response.session)
            return True
        

        return False

    except Exception as e:
        st.error(f"Login Error: {e}")
        return False


# ---------------- LOGOUT ----------------
def logout():
    clear_session()
    st.rerun()


# STEP 1: Send a true Password Reset OTP Code
def send_reset_otp(email):
    try:
        # This triggers the password reset track instead of the magic link track
        response = supabase.auth.reset_password_for_email(email)
        return True
    except Exception as e:
        print(f"Error sending password reset OTP: {e}")
        return False

def verify_otp_and_update_password(email, token, new_password):
    try:
        session = supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "recovery"
        })

        if session:
            supabase.auth.update_user({
                "password": new_password
            })
            clear_session()
            return True

        return False

    except Exception as e:
        print(f"Verification backend error: {e}")
        return False

def can_request_otp():
    return (time.time() - st.session_state.otp_timer_start) >= st.session_state.otp_cooldown


