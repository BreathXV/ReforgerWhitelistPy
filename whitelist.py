"""

argparse => Used for parsing command line arguments.
subprocess => Used for executing RCON application.
re => Used to check player identifiers using regex.
sqlite3 => Used for interacting with the database.
json => Used for interacting with a JSON.
time => Used for heartbeart function.
os => Used for paths and directories.
datetime => Used to generate date and time for logging.
threading => Used to create threads per player checks.
logging / logging.handlers => Used for handling the logging functionality.

"""

import argparse
import subprocess
import re
import sqlite3
import json
import time
import os
import datetime
import threading
import logging
import logging.handlers


def setup_logging(log_directory) -> None:
    """
    Initiates the log for the whitelist.
    """
    log_file = os.path.join(log_directory, "whitelist.log")

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    file_handler = logging.FileHandler(log_file, mode="a")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])


def heartbeat() -> None:
    """
    Initiates the heartbeat for application whilst it is running.
    """
    while True:
        logging.info("Whitelist is running...")
        time.sleep(15)


def find_latest_log_dir(base_log_dir) -> str or None:
    """
    Used to find the latest game server log directory.
    """
    dir_pattern = re.compile(r"logs_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}")
    log_dirs = [
        d
        for d in os.listdir(base_log_dir)
        if os.path.isdir(os.path.join(base_log_dir, d)) and dir_pattern.match(d)
    ]

    if not log_dirs:
        return None

    latest_log_dir = max(
        log_dirs, key=lambda d: datetime.datetime.strptime(d, "logs_%Y-%m-%d_%H-%M-%S")
    )
    return os.path.join(base_log_dir, latest_log_dir, "console.log")


def is_player_in_database(player_name, identity_id, db_path) -> bool:
    """
    Checks if the player's identifier is in the database.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT whitelisted 
                FROM user_data 
                WHERE (LOWER(game_name) = LOWER(?) OR LOWER(game_name) = LOWER(?)) 
                AND whitelisted = 1
                """,
                (player_name, identity_id),
            )
            is_whitelisted = cur.fetchone()
            if is_whitelisted is not None:
                logging.info(
                    "Player %s or IdentityId %s found in database and is whitelisted.",
                    player_name,
                    identity_id,
                )
                return True
            else:
                logging.info(
                    "Player %s or IdentityId %s not found in database or not whitelisted.",
                    player_name,
                    identity_id,
                )
                return False
    except sqlite3.Error as database_error:
        logging.error("Database error: %s", database_error)
        return False


def is_player_in_json(player_name, identity_id, json_path) -> bool:
    """
    Checks if the player's identifier is in the JSON.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for player in data.get("players", []):
                if (
                    player_name.lower() == player.get("game_name", "").lower()
                    or identity_id.lower() == player.get("identity_id", "").lower()
                ):
                    if player.get("whitelisted", 0) == 1:
                        logging.info(
                            "Player %s or IdentityId %s found in JSON and is whitelisted.",
                            player_name,
                            identity_id,
                        )
                        return True
            logging.info(
                "Player %s or IdentityId %s not found in JSON or not whitelisted.",
                player_name,
                identity_id,
            )
            return False
    except json.JSONDecodeError as json_error:
        logging.error("JSON error: %s", json_error)
        return False


def execute_kick_command(player_id, rcon_host, rcon_port, rcon_password) -> None:
    """
    IF player is not whitelisted, 
    this initiates the RCON application to remove the player from the server.
    """

    def kick_player():
        command = [
            "BERCon",
            "-host",
            rcon_host,
            "-port",
            rcon_port,
            "-pw",
            rcon_password,
            "-cmd",
            f"kick {player_id}",
            "-cmd",
            "exit",
        ]
        try:
            subprocess.run(command, check=True)
            logging.info(
                "Successfully executed kick command for player ID %s", player_id
            )
        except subprocess.CalledProcessError as kick_error:
            logging.error(
                "Error executing kick command for player ID %s: %s",
                player_id,
                kick_error,
            )
        except Exception:
            logging.exception("Unexpected error when kicking player ID %s", player_id)

    kick_thread = threading.Thread(target=kick_player, name=f"KickThread-{player_id}")
    kick_thread.start()


def tail_log_file(file_path, callback) -> None:
    """
    This functions grabs the last line of the log.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as log_file:
            log_file.seek(0, 2)
            while True:
                chunk = log_file.read(1024)
                if not chunk:
                    time.sleep(0.05)
                    continue
                for line in chunk.splitlines():
                    callback(line)
    except FileNotFoundError:
        logging.error("Log file not found: %s", file_path)
    except Exception:
        logging.exception("Error reading log file")


def process_log_line(
    line, whitelist_type, whitelist_path, rcon_host, rcon_port, rcon_password
) -> None:
    """
    Processes and checks the line of the log, passes it for checks if it is a player join event.
    """
    match = re.search(
        r"(Creating|Updating) player: PlayerId=(\d+), Name=([^,]+), IdentityId=([a-f0-9-]+)",
        line,
    )
    if match:
        action, player_id, player_name, identity_id = match.groups()
        player_name = player_name.strip()
        logging.info(
            "%s Player - ID: %s, Name: %s, IdentityId: %s",
            action,
            player_id,
            player_name,
            identity_id,
        )

        if whitelist_type == "database":
            is_whitelisted = is_player_in_database(
                player_name, identity_id, whitelist_path
            )
        elif whitelist_type == "json":
            is_whitelisted = is_player_in_json(player_name, identity_id, whitelist_path)
        else:
            logging.error("Unknown whitelist type: %s", whitelist_type)
            return

        if not is_whitelisted:
            logging.warning(
                "Player: %s with IdentityId: %s is NOT whitelisted! Kicking...",
                player_name,
                identity_id,
            )
            execute_kick_command(player_id, rcon_host, rcon_port, rcon_password)
        else:
            logging.info(
                "Player: %s with IdentityId: %s is whitelisted!",
                player_name,
                identity_id,
            )
    else:
        logging.debug("Unmatched line: %s", line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Reforger Whitelist",
        description="Whitelist script to monitor logs and kick unwhitelisted players.",
    )
    parser.add_argument(
        "--log-directory",
        type=str,
        default="logs",
        help="Directory to store log files.",
    )
    parser.add_argument(
        "--whitelist-type",
        type=str,
        choices=["database", "json"],
        required=True,
        help="Type of whitelist to use (database or json).",
    )
    parser.add_argument(
        "--whitelist-path",
        type=str,
        required=True,
        help="Path to the whitelist file (database or JSON).",
    )
    parser.add_argument(
        "--base-log-dir",
        type=str,
        required=True,
        help="Base directory to look for log files.",
    )
    parser.add_argument(
        "--rcon-host", type=str, required=True, help="RCON host address."
    )
    parser.add_argument(
        "--rcon-port", type=int, required=True, help="RCON port number."
    )
    parser.add_argument(
        "--rcon-password", type=str, required=True, help="RCON password."
    )

    args = parser.parse_args()

    setup_logging(args.log_directory)

    heartbeat_thread = threading.Thread(target=heartbeat, name="HeartbeatThread")
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

    latest_console_log_path = find_latest_log_dir(args.base_log_dir)

    try:
        if latest_console_log_path:
            tail_log_file(
                latest_console_log_path,
                lambda line: process_log_line(
                    line,
                    args.whitelist_type,
                    args.whitelist_path,
                    args.rcon_host,
                    args.rcon_port,
                    args.rcon_password,
                ),
            )
        else:
            logging.error("No recent log file found to process.")
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    except Exception as e:
        logging.exception("Unexpected error occurred in main process: %s", e)
