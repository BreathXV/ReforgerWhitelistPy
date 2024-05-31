import time
import re
import os
import datetime
import logging

from components.check_player import is_player_in_json, is_player_in_database

logger = logging.getLogger(__name__)

def tail_log_file(file_path: str, callback: callable) -> None:
    """Catches the latest line of the game server's console log.

    ...

    Parameters
    ----------
    file_path : str
        The system path to the console log.
    callback : callable
        Call to the process log line.
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
        logger.error("Log file not found: %s" % file_path)
    except Exception:
        logger.exception("Error reading log file")


def process_log_line(
    line: str,
    whitelist_type: str,
    whitelist_path: str,
    rcon_host: str,
    rcon_port: int,
    rcon_password: str,
) -> None:
    """Processes the log line checking for a player update/create event.

    ...

    Parameters
    ----------
        line : str
            The line of which to process.
        whitelist_type : str
            The type of whitelist procedure to use for this event.
        whitelist_path : str
            The system path to the whitelist data.
        rcon_host : str
            The host IP address of the RCON.
        rcon_port : int
            The port of the RCON.
        rcon_password : str
            The password of the RCON.
    """
    match = re.search(
        r"(Creating|Updating) player: PlayerId=(\d+), Name=([^,]+), IdentityId=([a-f0-9-]+)",
        line,
    )
    if match:
        action, player_id, player_name, identity_id = match.groups()
        player_name = player_name.strip()
        logger.info(
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
            is_whitelisted = is_player_in_json(
                player_name, identity_id, whitelist_path
            )
        else:
            logger.error("Unknown whitelist type: %s" % whitelist_type)
            return

        if not is_whitelisted:
            logger.warning(
                "Player: %s with IdentityId: %s is NOT whitelisted! Kicking..."
                % (
                    player_name,
                    identity_id,
                )
            )
            execute_kick_command(player_id, rcon_host, rcon_port, rcon_password)
        else:
            logger.info(
                "Player: %s with IdentityId: %s is whitelisted!"
                % (
                    player_name,
                    identity_id,
                )
            )
    else:
        logger.debug("Unmatched line: %s" % line)


def find_latest_log_dir(base_log_dir: str) -> str | None:
    """Used to find the latest game server log directory.

    ...

    Parameters
    ----------
    base_log_dir : str
        The directory where the game's `console.log` file is based.
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