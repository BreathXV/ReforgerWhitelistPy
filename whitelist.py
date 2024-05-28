# whitelist.py

"""

argparse => Used for parsing command line arguments.
re => Used to check player identifiers using regex.
sqlite3 => Used for interacting with the database.
json => Used for interacting with a JSON.
time => Used for heartbeat function.
os => Used for paths and directories.
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
    """Set up the logging for the application. Will also print to the CLI.

    Args:
        log_directory (str): The system path in which the log should be printed.
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
    """Sends log and CLI messages every count in seconds.

    Args:
        count (int): Interval between messages.
    """    
    while True:
        logging.info("Whitelist is running... Use [Ctrl + C] to stop the application.")
        time.sleep(count)


def find_latest_log_dir(base_log_dir: str) -> str | None:
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
    """Checks if a player's identifier is in the database.

    Args:
        player_name (str): The player's gamertag (Console) or name (PC).
        identity_id (str): The player's GUID (BID).
        db_path (str): The system path to the database file.

    Returns:
        bool: Whether the player is in the database (True) or not (False).
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
                    "Player %s or IdentityId %s found in database and is whitelisted."
                    % (
                        player_name,
                        identity_id,
                    )
                )
                return True
            else:
                logging.info(
                    "Player %s or IdentityId %s not found in database or not whitelisted."
                    % (
                        player_name,
                        identity_id,
                    )
                )
                return False
    except sqlite3.Error as database_error:
        logging.error("Database error: %s" % database_error)
        return False


def is_player_in_json(player_name: str, identity_id: str, json_path: str) -> bool:
    """Checks if the player is in the JSON.

    Args:
        player_name (str): The player's gamertag (Console) or name (PC).
        identity_id (str): The player's GUID (BID).
        json_path (str): The system path to the JSON file.

    Returns:
        bool: Whether the player is in the database (True) or not (False).
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
                            "Player %s or IdentityId %s found in JSON and is whitelisted."
                            % (
                                player_name,
                                identity_id,
                            )
                        )
                        return True
            logging.info(
                "Player %s or IdentityId %s not found in JSON or not whitelisted."
                % (
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
    """_summary_

    Args:
        player_id (str): The ID of the player, typically assigned by the server upon join.
        rcon_host (str): The host IP address of the RCON.
        rcon_port (int): The port of the RCON.
        rcon_password (str): The password of the RCON.
    """

    def kick_player():
        """Establishes a connection with BERCon and executes the kick command.
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
                "Unexpected error executing kick command for player ID %s: %s"
                % (player_id, e)
            )

    kick_thread = threading.Thread(target=kick_player, name=f"KickThread-{player_id}")
    kick_thread.start()


def tail_log_file(file_path: str, callback: callable) -> None:
    """Catches the latest line of the game server's console log.

    Args:
        file_path (str): The system path to the console log.
        callback (callable): Call to the process log line.
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
    """Processes the log line checking for a player update/create event.

    Args:
        line (str): The line of which to process.
        whitelist_type (str): The type of whitelist procedure to use for this event.
        whitelist_path (str): The system path to the whitelist data.
        rcon_host (str): The host IP address of the RCON.
        rcon_port (int): The port of the RCON.
        rcon_password (str): The password of the RCON.
    """    
    match = re.search(
        r"(Creating|Updating) player: PlayerId=(\d+), Name=([^,]+), IdentityId=([a-f0-9-]+)",
        line,
    )
    if match:
        action, player_id, player_name, identity_id = match.groups()
        player_name = player_name.strip()
        logging.info(
            "%s Player - ID: %s, Name: %s, IdentityId: %s"
            % (
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
                "Player: %s with IdentityId: %s is NOT whitelisted! Kicking..."
                % (
                    player_name,
                    identity_id,
                )
            )
            execute_kick_command(player_id, rcon_host, rcon_port, rcon_password)
        else:
            logging.info(
                "Player: %s with IdentityId: %s is whitelisted!"
                % (
                    player_name,
                    identity_id,
                )
            )
    else:
        logging.debug("Unmatched line: %s" % line)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="Reforger Whitelist",
        description="""
                    Whitelist script to monitor logs and kick non-whitelisted players.\n
                    Reforger Whitelist is licensed under the GPL-3.0 License. This license can be found within the GitHub Repository.\n
                    https://github.com/BreathXV/ReforgerWhitelistPy
                    """,
    )
    parser.add_argument(
        "--cfg",
        "--config",
        type=str,
        required=False,
        help="Start from a config.json",
        dest="config",
    )
    parser.add_argument(
        "--wt",
        "--whitelist-type",
        type=str,
        required=False,
        choices=["database", "json"],
        help="Type of whitelist to use (database or json).",
        dest="whitelist_type",
    )
    parser.add_argument(
        "--wp",
        "--whitelist-path",
        type=str,
        required=False,
        help="Path to the whitelist file (database or JSON).",
        dest="whitelist_path",
    )
    parser.add_argument(
        "--bl",
        "--base-log-dir",
        type=str,
        required=False,
        help="Base directory to look for log files.",
        dest="base_log_dir",
    )
    parser.add_argument(
        "--rh",
        "--rcon-host",
        type=str,
        required=False,
        help="RCON host address.",
        dest="rcon_host",
    )
    parser.add_argument(
        "--rp",
        "--rcon-port",
        type=int,
        required=False,
        help="RCON port number.",
        dest="rcon_port",
    )
    parser.add_argument(
        "--rpw",
        "--rcon-password",
        type=str,
        required=False,
        help="RCON password.",
        dest="rcon_password",
    )
    parser.add_argument(
        "--hb",
        "--heartbeat",
        type=int,
        required=False,
        default=15,
        help="Interval in seconds when the application should log it's alive.",
        dest="heartbeat",
    )

    args = parser.parse_args()

    app_args = {
        "env": "",
        "whitelist_type": "",
        "whitelist_path": "",
        "base_log_dir": "",
        "rcon_host": "",
        "rcon_port": "",
        "rcon_password": "",
        "heartbeat": "",
    }

    # TODO: Invoke setup_logging() before args.config
    # NOTE: Needed for logging the progress of assigning param values in the dict! 
    # Crucial if using config.

    if args.config:
        try:
            with open(file=args.config, mode="r", encoding="utf-8") as file:
                config = json.load(file)
                logging.info("Loaded configuration file")
                # Check for all params in the config
                for param in config.get(param, ""):
                    if not param:
                        logging.error("A parameter is missing in the configuration file!")
                        return
                # Assign each args value to the dict
                logging.info("Assigning all config values...")
                for param in app_args.keys():
                    logging.info(f"Loaded {param}")
                    app_args[param] == config.get(param, "")
                # Invoke func with param values from dict
                initiate(**app_args)
        except FileNotFoundError:
            logging.error("Configuration file could not be found at path: %s" % args.config)
            print("Configuration file could not be found at path: %s" % args.config)
        except json.JSONDecodeError:
            logging.error("Error decoding the configuration file, ensure you are using 'utf-8' encoding.")
            print("Error decoding the configuration file, ensure you are using 'utf-8' encoding.")
        return
    else:
        for arg in app_args:
            print(args.app_args[arg])

    def initiate(
        whitelist_type: str = args.whitelist_type,
        whitelist_path: str = args.whitelist_path,
        base_log_dir: str = args.base_log_dir,
        rcon_host: str = args.rcon_host,
        rcon_port: int = args.rcon_port,
        rcon_password: str = args.rcon_password,
        heartbeat: int = args.heartbeat,
    ) -> None:
        """Initiates the application with the provided arguments.

        Args:
            whitelist_type (str, optional): Type of whitelist to use (database or json). Defaults to args.whitelist_type.
            whitelist_path (str, optional): Path to the whitelist file (database or JSON). Defaults to args.whitelist_path.
            base_log_dir (str, optional): Base directory to look for log files. Defaults to args.base_log_dir.
            rcon_host (str, optional): RCON host address. Defaults to args.rcon_host.
            rcon_port (int, optional): RCON port. Defaults to args.rcon_port.
            rcon_password (str, optional): RCON password. Defaults to args.rcon_password.
            heartbeat (int, optional): Interval in seconds when the application should log it's alive. Defaults to args.heartbeat.
        """

        heartbeat_thread = threading.Thread(
            target=heartbeat(heartbeat), name="HeartbeatThread"
        )
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

        latest_console_log_path = find_latest_log_dir(base_log_dir)

        try:
            if latest_console_log_path:
                tail_log_file(
                    latest_console_log_path,
                    lambda line: process_log_line(
                        line,
                        whitelist_type,
                        whitelist_path,
                        rcon_host,
                        rcon_port,
                        rcon_password,
                    ),
                )
            else:
                logging.error("No recent log file found to process.")
        except KeyboardInterrupt:
            logging.info("Script interrupted by user.")
        except Exception as e:
            logging.exception("Unexpected error occurred in main process: %s" % e)


if __name__ == "__main__":
    setup_logging("./whitelist/")
    main()
