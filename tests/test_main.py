import unittest
import sys

from unittest.mock import patch, MagicMock

from components.config import Config
from components.initiate import initiate
from main import main

class TestMain(unittest.TestCase):
    @patch("builtins.input", return_value="Y")
    def test_main_with_config_file(self, mock_input):
        # Test if the program uses the provided config file
        with open("config.example.json", "w") as file:
            file.write("{\"whitelist_type\": \"json\", \"whitelist_path\": \"whitelist.json\", \"base_log_dir\": \"logs\", \"rcon_host\": \"localhost\", \"rcon_port\": 2302, \"rcon_password\": \"password\", \"heartbeat\": 15}")
        mock_setup_logging = patch("whitelist.setup_logging")
        mock_find_latest_log_dir = patch("whitelist.find_latest_log_dir")
        mock_tail_log_file = patch("whitelist.tail_log_file")
        mock_thread = patch("threading.Thread")
        mock_args = patch.dict(sys.modules[__name__], {"__file__": "main.py", "args": ["--cfg", "config.example.json"]})
        mock_config = Config("config.example.json")
        mock_config.check_config = MagicMock(return_value=True)
        mock_config.get_config_value = MagicMock(return_value=True)
        mock_initiate = patch("whitelist.initiate")
        mock_initiate.return_value = None
        mock_initiate.assert_called_once_with()
        main()
        # Assert that the setup_logging function is called
        mock_setup_logging.assert_called_once()
        # Assert that the find_latest_log_dir function is called
        mock_find_latest_log_dir.assert_called_once()
        # Assert that the tail_log_file function is called
        mock_tail_log_file.assert_called_once()
        # Assert that the thread function is called
        mock_thread.assert_called_once()

    @patch("builtins.input", return_value="N")
    def test_main_without_config_file(self, mock_input):
        # Test if the program uses the provided command-line arguments
        mock_setup_logging = patch("whitelist.setup_logging")
        mock_find_latest_log_dir = patch("whitelist.find_latest_log_dir")
        mock_tail_log_file = patch("whitelist.tail_log_file")
        mock_thread = patch("threading.Thread")
        mock_args = patch.dict(sys.modules[__name__], {"__file__": "main.py", "args": ["--json", "--db", "--wp", "whitelist.json", "--bl", "logs", "--rp", "2302", "--rpw", "password", "--hb", "15"]})
        mock_initiate = patch("whitelist.initiate")
        mock_initiate.return_value = None
        mock_initiate.assert_called_once_with
        main()
        # Assert that the setup_logging function is called
        mock_setup_logging.assert_called_once()
        # Assert that the find_latest_log_dir function is called
        mock_find_latest_log_dir.assert_called_once()
        # Assert that the tail_log_file function is called
        mock_tail_log_file.assert_called_once()
        # Assert that the thread function is called
        mock_thread.assert_called_once()

    def test_main_without_arguments(self):
        # Test if the program uses default values when no arguments are provided
        mock_setup_logging = patch("whitelist.setup_logging")
        mock_find_latest_log_dir = patch("whitelist.find_latest_log_dir")
        mock_tail_log_file = patch("whitelist.tail_log_file")
        mock_thread = patch("threading.Thread")
        mock_args = patch.dict(sys.modules[__name__], {"__file__": "main.py", "args": []})
        mock_initiate = patch("whitelist.initiate")
        mock_initiate.return_value = None
        mock_initiate.assert_called_once_with
        main()
        # Assert that the setup_logging function is called
        mock_setup_logging.assert_called_once()
        # Assert that the find_latest_log_dir function is called
        mock_find_latest_log_dir.assert_called_once()
        # Assert that the tail_log_file function is called
        mock_tail_log_file.assert_called_once()
        # Assert that the thread function is called
        mock_thread.assert_called_once()

    def test_main_with_invalid_arguments(self):
        # Test if the program handles invalid arguments gracefully
        mock_setup_logging = patch("whitelist.setup_logging")
        mock_find_latest_log_dir = patch("whitelist.find_latest_log_dir")
        mock_tail_log_file = patch("whitelist.tail_log_file")
        mock_thread = patch("threading.Thread")
        mock_args = patch.dict(sys.modules[__name__], {"__file__": "main.py", "args": ["--invalid_arg", "invalid_value"]})
        mock_initiate = patch("whitelist.initiate")
        mock_initiate.return_value = None
        main()
        # Assert that the setup_logging function is not called
        mock_setup_logging.assert_not_called()
        # Assert that the find_latest_log_dir function is not called
        mock_find_latest_log_dir.assert_not_called()
        # Assert that the tail_log_file function is not called
        mock_tail_log_file.assert_not_called()
        # Assert that the thread function is not called
        mock_thread.assert_not_called()

    def test_main_with_missing_arguments(self):
        # Test if the program handles missing arguments gracefully
        mock_setup_logging = patch("whitelist.setup_logging")
        mock_find_latest_log_dir = patch("whitelist.find_latest_log_dir")
        mock_tail_log_file = patch("whitelist.tail_log_file")
        mock_thread = patch("threading.Thread")
        mock_args = patch.dict(sys.modules[__name__], {"__file__": "main.py", "args": []})
        mock_initiate = patch("whitelist.initiate")
        mock_initiate.return_value = None
        main()
        # Assert that the setup_logging function is called
        mock_setup_logging.assert_called_once()
        # Assert that the find_latest_log_dir function is called
        mock_find_latest_log_dir.assert_called_once()
        # Assert that the tail_log_file function is called
        mock_tail_log_file.assert_called_once()
        # Assert that the thread function is called
        mock_thread.assert_called_once()

if __name__ == "__main__":
    unittest.main()
