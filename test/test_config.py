import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
ROOT_CONFIG_FILE = ROOT_DIR / "config.json"


class ConfigLoadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._created_root_config = False
        if not ROOT_CONFIG_FILE.exists():
            ROOT_CONFIG_FILE.write_text(json.dumps({"auth-key": "test-auth"}), encoding="utf-8")
            cls._created_root_config = True

        old_env_auth_key = os.environ.get("WEBCHAT2API_AUTH_KEY")
        os.environ["WEBCHAT2API_AUTH_KEY"] = "test-auth"
        try:
            from services import config as config_module

            cls.config_module = config_module
        finally:
            if old_env_auth_key is None:
                os.environ.pop("WEBCHAT2API_AUTH_KEY", None)
            else:
                os.environ["WEBCHAT2API_AUTH_KEY"] = old_env_auth_key

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._created_root_config and ROOT_CONFIG_FILE.exists():
            ROOT_CONFIG_FILE.unlink()

    def test_load_settings_ignores_directory_config_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            data_dir = base_dir / "data"
            config_dir = base_dir / "config.json"
            os_auth_key = "env-auth"

            config_dir.mkdir()

            module = self.config_module
            old_base_dir = module.BASE_DIR
            old_data_dir = module.DATA_DIR
            old_config_file = module.CONFIG_FILE
            old_env_auth_key = module.os.environ.get("WEBCHAT2API_AUTH_KEY")
            old_login_secret = module.os.environ.get("LOGIN_SECRET")
            try:
                module.BASE_DIR = base_dir
                module.DATA_DIR = data_dir
                module.CONFIG_FILE = config_dir
                module.os.environ.pop("WEBCHAT2API_AUTH_KEY", None)
                module.os.environ["LOGIN_SECRET"] = os_auth_key

                settings = module._load_settings()

                self.assertEqual(settings.auth_key, os_auth_key)
                self.assertEqual(settings.refresh_account_interval_minute, 5)
            finally:
                module.BASE_DIR = old_base_dir
                module.DATA_DIR = old_data_dir
                module.CONFIG_FILE = old_config_file
                if old_env_auth_key is None:
                    module.os.environ.pop("WEBCHAT2API_AUTH_KEY", None)
                else:
                    module.os.environ["WEBCHAT2API_AUTH_KEY"] = old_env_auth_key
                if old_login_secret is None:
                    module.os.environ.pop("LOGIN_SECRET", None)
                else:
                    module.os.environ["LOGIN_SECRET"] = old_login_secret


if __name__ == "__main__":
    unittest.main()
