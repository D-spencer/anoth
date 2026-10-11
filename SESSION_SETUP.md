# Session setup

The login session now survives page refreshes and browser restarts for up to
seven days. The seven-day period starts when the user signs in and is not
extended by refreshing the page.

Generate an encryption key once:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the generated value to the same Streamlit Secrets area that contains
`SUPABASE_URL` and `SUPABASE_KEY`:

```toml
SESSION_ENCRYPTION_KEY = "paste-the-generated-key-here"
```

Keep this value private and do not change it after deployment. Changing it
will invalidate existing saved sessions and users will need to sign in again.

The session is also cleared when the user logs out, clears browser site data,
or when Supabase rejects or revokes the saved authentication tokens.
