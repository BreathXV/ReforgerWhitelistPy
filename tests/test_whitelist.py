# test_whitelist.py

import pytest
from unittest import mock
import os
import json
import sqlite3
import re
from main import (
    setup_logging,
    heartbeat,
    find_latest_log_dir,
    is_player_in_database,
    is_player_in_json,
    execute_kick_command,
    tail_log_file,
    process_log_line,
)


def test_setup_logging(tmp_path):
    log_dir = tmp_path / "logs"
    setup_logging(str(log_dir))

    log_file = log_dir / "whitelist.log"
    assert log_file.exists()


def test_heartbeat(mocker):
    mock_sleep = mocker.patch("time.sleep", side_effect=KeyboardInterrupt)
    with pytest.raises(KeyboardInterrupt):
        heartbeat(1)
    assert mock_sleep.call_count == 1


def test_find_latest_log_dir(tmp_path):
    base_log_dir = tmp_path / "logs"
    os.makedirs(base_log_dir / "logs_2024-01-01_12-00-00")
    os.makedirs(base_log_dir / "logs_2024-01-02_12-00-00")

    latest_log_path = find_latest_log_dir(str(base_log_dir))
    assert latest_log_path == str(
        base_log_dir / "logs_2024-01-02_12-00-00" / "console.log"
    )


def test_is_player_in_database(mocker):
    mock_connect = mocker.patch("sqlite3.connect")
    mock_cursor = mock_connect.return_value.__enter__.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = (1,)

    assert is_player_in_database("player1", "id1", "db_path")
    mock_cursor.execute.assert_called_once()


def test_is_player_in_json(tmp_path):
    json_data = {
        "players": [
            {"game_name": "player1", "identity_id": "id1", "whitelisted": 1},
        ]
    }
    json_path = tmp_path / "whitelist.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f)

    assert is_player_in_json("player1", "id1", str(json_path))


def test_execute_kick_command(mocker):
    mock_client = mocker.patch("rcon.battleye.Client")
    mock_instance = mock_client.return_value.__enter__.return_value

    execute_kick_command("player1", "localhost", 2302, "password")
    mock_instance.run.assert_called_once_with("#kick player1")


def test_tail_log_file(tmp_path, mocker):
    log_file_path = tmp_path / "console.log"
    with open(log_file_path, "w", encoding="utf-8") as f:
        f.write("Test log line\n")

    mock_callback = mocker.Mock()
    mock_sleep = mocker.patch("time.sleep", side_effect=KeyboardInterrupt)

    with pytest.raises(KeyboardInterrupt):
        tail_log_file(str(log_file_path), mock_callback)

    mock_callback.assert_called_with("Test log line")


def test_process_log_line(mocker):
    mock_is_player_in_database = mocker.patch(
        "whitelist.is_player_in_database", return_value=False
    )
    mock_is_player_in_json = mocker.patch(
        "whitelist.is_player_in_json", return_value=False
    )
    mock_execute_kick_command = mocker.patch("whitelist.execute_kick_command")

    log_line = "07:38:19.358   NETWORK      : ### Updating player: PlayerId=3, Name=TestGamertag, IdentityId=6fa40f96-f8e9-44ac-be26-e0660c79b88a"

    process_log_line(log_line, "database", "db_path", "localhost", 2302, "password")
    mock_is_player_in_database.assert_called_once_with("TestGamertag", "6fa40f96-f8e9-44ac-be26-e0660c79b88a", "db_path")
    mock_execute_kick_command.assert_called_once_with(
        "3", "localhost", 2302, "password"
    )

    process_log_line(log_line, "json", "json_path", "localhost", 2302, "password")
    mock_is_player_in_json.assert_called_once_with("TestGamertag", "6fa40f96-f8e9-44ac-be26-e0660c79b88a", "json_path")
    assert mock_execute_kick_command.call_count == 2


def test_main(mocker):
    mock_setup_logging = mocker.patch("whitelist.setup_logging")
    mock_find_latest_log_dir = mocker.patch(
        "whitelist.find_latest_log_dir", return_value="latest_log_path"
    )
    mock_tail_log_file = mocker.patch("whitelist.tail_log_file")
    mock_thread = mocker.patch("threading.Thread")

    args = [
        "--whitelist-type",
        "json",
        "--whitelist-path",
        "whitelist.json",
        "--base-log-dir",
        "base_log_dir",
        "--rcon-host",
        "localhost",
        "--rcon-port",
        "2302",
        "--rcon-password",
        "password",
    ]
    mocker.patch("sys.argv", ["whitelist.py"] + args)
    mock_input = mocker.patch("builtins.input", return_value="Y")

    import main

    main.main()

    mock_setup_logging.assert_called_once()
    mock_find_latest_log_dir.assert_called_once_with("base_log_dir")
    mock_tail_log_file.assert_called_once_with("latest_log_path", mocker.ANY)
    mock_thread.assert_called()


if __name__ == "__main__":
    pytest.main()
