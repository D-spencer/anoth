import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cryptography.fernet import Fernet, InvalidToken
from session_crypto import encode_session, decode_session, SESSION_SECONDS


class Halt(BaseException):
    pass


class Sessions(unittest.TestCase):
    def setUp(self):
        self.key = Fernet.generate_key().decode()
        self.session = SimpleNamespace(access_token='access', refresh_token='refresh', expires_at=10**12)
        self.user = SimpleNamespace(id='user1', email='test@example.com')
        self.st = ModuleType('streamlit')
        self.st.session_state = {}
        self.st.secrets = {'SESSION_ENCRYPTION_KEY': self.key, 'SUPABASE_URL': 'https://example.test', 'SUPABASE_KEY': 'anon'}
        self.st.stop = self.st.rerun = lambda: (_ for _ in ()).throw(Halt())
        self.st.error = lambda *a: None
        self.response = {'value': None}
        components = ModuleType('streamlit.components.v1')
        components.declare_component = lambda *a, **k: lambda **kw: self.response
        self.auth = SimpleNamespace(
            get_user=lambda *a: SimpleNamespace(user=self.user),
            get_session=lambda: self.session,
            set_session=lambda *a: SimpleNamespace(session=self.session),
            refresh_session=lambda *a: SimpleNamespace(session=self.session),
            sign_out=lambda *a: None,
        )
        db = ModuleType('database')
        db.supabase = SimpleNamespace(auth=self.auth)
        db.get_user_name = lambda *a: 'Test User'
        db.get_user_role = lambda *a: 'user'
        auto = ModuleType('streamlit_autorefresh')
        auto.st_autorefresh = lambda **k: None
        self.modules = patch.dict(sys.modules, {'streamlit': self.st, 'streamlit.components': ModuleType('streamlit.components'), 'streamlit.components.v1': components, 'database': db, 'streamlit_autorefresh': auto})
        self.modules.start()
        sys.modules.pop('persistent_session', None)
        import persistent_session
        self.mod = persistent_session

    def tearDown(self):
        self.modules.stop()
        sys.modules.pop('persistent_session', None)

    def test_crypto_roundtrip_and_tampering(self):
        token = encode_session(self.key, self.session, 1000 + SESSION_SECONDS)
        with patch('session_crypto.time.time', return_value=1000):
            self.assertEqual(decode_session(self.key, token)['refresh_token'], 'refresh')
            with self.assertRaises(InvalidToken):
                decode_session(self.key, token[:-8] + 'invalid!')
            with self.assertRaises(InvalidToken):
                decode_session(Fernet.generate_key(), token)
        with patch('session_crypto.time.time', return_value=1000 + SESSION_SECONDS):
            with self.assertRaises(ValueError):
                decode_session(self.key, token)

    def test_login_waits_for_browser_ack(self):
        self.mod.start_session(self.session)
        with self.assertRaises(Halt):
            self.mod.restore_session()
        pending = self.st.session_state['_session_write']
        self.response = {'value': pending['value'], 'ack': pending['id']}
        self.mod.restore_session()
        self.assertNotIn('_session_write', self.st.session_state)
        self.assertEqual(self.st.session_state['role'], 'user')

    def test_refresh_restores_original_deadline(self):
        self.mod.start_session(self.session)
        deadline = self.st.session_state['_session_deadline']
        token = self.st.session_state['_session_token']
        self.st.session_state.clear()
        self.response = {'value': token}
        with self.assertRaises(Halt):
            self.mod.restore_session()
        self.assertEqual(self.st.session_state['_session_deadline'], deadline)
        self.assertEqual(self.st.session_state['user'].id, 'user1')

    def test_expiry_and_logout_clear_private_state(self):
        self.mod.start_session(self.session)
        self.st.session_state.pop('_session_write')
        self.response = {'value': self.st.session_state['_session_token']}
        self.st.session_state['_session_deadline'] = 0
        self.st.session_state['private_predictions'] = ['private']
        with self.assertRaises(Halt):
            self.mod.restore_session()
        self.assertEqual(set(self.st.session_state), {'_session_write'})
        self.assertIsNone(self.st.session_state['_session_write']['value'])

    def test_rotation_keeps_deadline_and_persists_tokens(self):
        self.mod.start_session(self.session)
        deadline = self.st.session_state['_session_deadline']
        self.st.session_state.pop('_session_write')
        self.response = {'value': self.st.session_state['_session_token']}
        self.auth.get_session = lambda: SimpleNamespace(access_token='new', refresh_token='new-refresh', expires_at=10**12)
        with self.assertRaises(Halt):
            self.mod.restore_session()
        self.assertEqual(self.st.session_state['_session_deadline'], deadline)
        self.assertEqual(decode_session(self.key, self.st.session_state['_session_write']['value'])['access_token'], 'new')

    def test_anonymous_browser_does_not_inherit_user(self):
        self.mod.restore_session()
        self.assertIsNone(self.st.session_state.get('user'))

    def test_database_client_isolation(self):
        import importlib.util
        fake = ModuleType('supabase')
        fake.create_client = lambda *a: object()
        with patch.dict(sys.modules, {'supabase': fake}):
            spec = importlib.util.spec_from_file_location('isolated_database', Path(__file__).resolve().parents[1] / 'database.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            first = module.get_client()
            self.assertIs(first, module.get_client())
            self.st.session_state = {}
            self.assertIsNot(first, module.get_client())


if __name__ == '__main__':
    unittest.main()
