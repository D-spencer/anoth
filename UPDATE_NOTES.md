# Update setup

1. Replace the project files with this folder, including `session_component/`.
2. Install requirements: `pip install -r requirements.txt`.
3. Generate a private encryption key once:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
4. In Streamlit Community Cloud → app Settings → Secrets, keep your existing
   `SUPABASE_URL` and `SUPABASE_KEY`, and add this top-level entry:
   ```toml
   SESSION_ENCRYPTION_KEY = "paste-your-generated-key-here"
   ```
   For local development, put the same entries in `.streamlit/secrets.toml`.
   Keep this key private and stable across restarts. Changing it logs everyone out.
5. Restart the app (`streamlit run App.py` locally).

## Login behaviour

Login persists across refreshes and browser restarts on the same browser profile
for seven days from sign-in. Token refresh does not extend that deadline.
All three pages restore the session before checking access. Logout clears stored
credentials and account-specific Streamlit state; tabs receive storage changes.
Open pages check expiry every minute, and each interaction checks it again.
Supabase clients are isolated per Streamlit session instead of shared globally.

Browser storage contains an encrypted, authenticated token bundle; passwords and
roles are not stored there. Supabase verifies the user and the role is fetched
from the database. This browser storage is JavaScript-accessible (not an HttpOnly
cookie), so use HTTPS and do not add untrusted scripts. It remains a bearer
credential even when encrypted. Clearing site data, private browsing ending,
Supabase revocation, connection failures during validation, or shorter Supabase
session policies can require an earlier login. Existing users sign in once after
this update. Database row-level security must continue to enforce data access.

## Dashboard and styles

Admin uses the login's indigo gradient and a white content panel, with indigo
chart text and controls. Admin-only rules are in `admin.css`; shared rules stay
in `styles.css`. Conflicting sidebar-toggle definitions, redundant header/form
properties and obsolete animation code were consolidated. Dropdown backgrounds
are scoped to listboxes instead of every unordered list.

Also fixed empty-feedback export and inconsistent TB/HIV dashboard filtering.
Prediction model files and questionnaire logic were not changed.

## Verification

Automated checks cover encrypted round trips, tampering, seven-day expiry,
session isolation, restore/write acknowledgements, refresh, and logout using
mocked services. Live Supabase login and deployed appearance still need checking
with your account configuration. No production credentials were provided.

After deployment: sign in, refresh Home/History/Admin, close and reopen the
browser, then log out and refresh. Try a separate browser profile to confirm it
starts signed out. Check admin charts, filters and the empty-feedback state.
