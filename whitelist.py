# whitelist.py

"""

argparse => Used for parsing command line arguments.
subprocess => Used for executing RCON application.
re => Used to check player identifiers using regex.
sqlite3 => Used for interacting with the database.
json => Used for interacting with a JSON.
time => Used for heartbeat function.
os => Used for paths and directories.
sys => Used for stopping the application. 
datetime => Used to generate date and time for logging.
threading => Used to create threads per player checks.
logging / logging.handlers => Used for handling the logging functionality.
rcon.battleye => Used for executing kick commands on the server.

"""

import argparse
import re
import sqlite3
import json
import time
import os
import datetime
import threading
import logging
import logging.handlers

from rcon.battleye import Client


def setup_logging(log_directory: str) -> None:
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


def heartbeat(count: int) -> None:
    """
    Initiates the heartbeat for application whilst it is running.
    """
    while True:
        logging.info("Whitelist is running...")
        time.sleep(count)


def find_latest_log_dir(base_log_dir: str) -> str:
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


def is_player_in_database(player_name: str, identity_id: str, db_path: str) -> bool:
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
                    "Player %s or IdentityId %s found in database and is whitelisted." % (
                        player_name,
                        identity_id,
                    )
                )
                return True
            else:
                logging.info(
                    "Player %s or IdentityId %s not found in database or not whitelisted." % (
                        player_name,
                        identity_id,
                    )
                )
                return False
    except sqlite3.Error as database_error:
        logging.error("Database error: %s" % database_error)
        return False


def is_player_in_json(player_name: str, identity_id: str, json_path: str) -> bool:
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
                            "Player %s or IdentityId %s found in JSON and is whitelisted." % (
                                player_name,
                                identity_id,
                            )
                        )
                        return True
            logging.info(
                "Player %s or IdentityId %s not found in JSON or not whitelisted." % (
                    player_name,
                    identity_id,
                )
            )
            return False
    except json.JSONDecodeError as json_error:
        logging.error("JSON error: %s" % json_error)
        return False


def execute_kick_command(
    player_id: str, rcon_host: str, rcon_port: int, rcon_password: str
) -> None:
    """
    Initiates the kick_thread IF a player is not whitelisted.
    """
    def kick_player():
        """
        Establishes a connection with BERCon and executes the kick command.
        """
        command = "#kick %s" % player_id
        
        try:
            with Client(host=rcon_host, port=rcon_port, passwd=rcon_password) as client:
                rsp = client.run(command=command)
                client.close()
            logging.info(
                "Successfully executed kick command for player ID %s" % player_id
            )
        except Exception as e:
            logging.error(
                "Unexpected error executing kick command for player ID %s: %s" % (
                    player_id,
                    e
                )
            )

    kick_thread = threading.Thread(target=kick_player, name=f"KickThread-{player_id}")
    kick_thread.start()


def tail_log_file(file_path: str, callback: callable) -> None:
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
        logging.error("Log file not found: %s" % file_path)
    except Exception:
        logging.exception("Error reading log file")


def process_log_line(
    line: str,
    whitelist_type: str,
    whitelist_path: str,
    rcon_host: str,
    rcon_port: int,
    rcon_password: str,
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
            "%s Player - ID: %s, Name: %s, IdentityId: %s" % (
                action,
                player_id,
                player_name,
                identity_id,
            )
        )

        if whitelist_type == "database":
            is_whitelisted = is_player_in_database(
                player_name, identity_id, whitelist_path
            )
        elif whitelist_type == "json":
            is_whitelisted = is_player_in_json(player_name, identity_id, whitelist_path)
        else:
            logging.error("Unknown whitelist type: %s" % whitelist_type)
            return

        if not is_whitelisted:
            logging.warning(
                "Player: %s with IdentityId: %s is NOT whitelisted! Kicking..." % (
                    player_name,
                    identity_id,
                )
            )
            execute_kick_command(player_id, rcon_host, rcon_port, rcon_password)
        else:
            logging.info(
                "Player: %s with IdentityId: %s is whitelisted!" % (
                    player_name,
                    identity_id,
                )
            )
    else:
        logging.debug("Unmatched line: %s" % line)


def main():
    parser = argparse.ArgumentParser(
        prog="Reforger Whitelist",
        description="Whitelist script to monitor logs and kick non-whitelisted players.",
    )
    parser.add_argument(
        "--ld", "--log-directory",
        type=str,
        default="logs",
        help="Directory to store log files from ReforgerWhitelist.",
        dest="log_directory",
    )
    parser.add_argument(
        "--wt", "--whitelist-type",
        type=str,
        choices=["database", "json"],
        required=True,
        help="Type of whitelist to use (database or json).",
        dest="whitelist_type",
    )
    parser.add_argument(
        "--wp", "--whitelist-path",
        type=str,
        required=True,
        help="Path to the whitelist file (database or JSON).",
        dest="whitelist_path",
    )
    parser.add_argument(
        "--bl", "--base-log-dir",
        type=str,
        required=True,
        help="Base directory to look for log files for whitelist.",
        dest="base_log_dir",
    )
    parser.add_argument(
        "--rh", "--rcon-host", 
        type=str, 
        required=True, 
        help="RCON host address.",
        dest="rcon_host",
    )
    parser.add_argument(
        "--rp", "--rcon-port", 
        type=int, 
        required=True, 
        help="RCON port number.",
        dest="rcon_port",
    )
    parser.add_argument(
        "--rpw", "--rcon-password", 
        type=str, 
        required=True, 
        help="RCON password.",
        dest="rcon_password",
    )
    parser.add_argument(
        "--hb", "--heartbeat",
        type=int,
        default=15,
        help="Interval in seconds when the application should log it's alive.",
        dest="heartbeat",
    )

    args = parser.parse_args()

    confirm_args = input(
        """
    Log Directory: %s\n
    Whitelist Type: %s\n
    Whitelist Path: %s\n
    Base Game Log Directory: %s\n
    RCON Host: %s\n
    RCON Port: %s\n
    RCON Password: %s\n
    Heartbeat Count (secs): %s\n
    Correct? [Y/n]: 
    """ % (
            args.log_directory,
            args.whitelist_type,
            args.whitelist_path,
            args.base_log_dir,
            args.rcon_host,
            args.rcon_port,
            args.rcon_password,
            args.heartbeat,
        )
    )

    if confirm_args.lower() != "y" or confirm_args.lower() != "yes":
        print("Please restart the application to try again.")
        return

    setup_logging(args.log_directory)

    heartbeat_thread = threading.Thread(
        target=heartbeat(args.heartbeat), name="HeartbeatThread"
    )
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
        logging.exception("Unexpected error occurred in main process: %s" % e)


if __name__ == "__main__":
    main()
