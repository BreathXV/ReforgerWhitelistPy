import threading
import logging

from components.process_logs import find_latest_log_dir, tail_log_file, process_log_line

logger = logging.getLogger(__name__)

def initiate(
    whitelist_type: str,
    whitelist_path: str,
    base_log_dir: str,
    rcon_host: str,
    rcon_port: int,
    rcon_password: str,
    heartbeat: int,
) -> None:
    """Initiates the application with the provided arguments.

    ...

    Parameters
    ----------
        whitelist_type : str
            Type of whitelist to use (database or json).
        whitelist_path : str
            Path to the whitelist file (database or JSON).
        base_log_dir : str
            Base directory to look for log files.
        rcon_host : str
            RCON host address.
        rcon_port : int
            RCON port.
        rcon_password : str
            RCON password.
        heartbeat : int
            Interval in seconds when the application should log it's alive.
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
            logger.error("No recent log file found to process.")
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
    except Exception as e:
        logger.exception(f"Unexpected error occurred in main process: {e}")
