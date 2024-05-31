import argparse
import logging

from components.logging import setup_logging
from components.config import Config
from components.initiate import initiate

logger = logging.getLogger(__name__)

def main() -> None:
    """Used to invoke the initiate function. Parses any arguments provided by the user.
    """    
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
    # parser.add_argument(
    #     "--wt",
    #     "--whitelist-type",
    #     type=str,
    #     required=False,
    #     choices=["database", "json"],
    #     help="Type of whitelist to use (database or json).",
    #     dest="whitelist_type",
    # )
    parser.add_argument(
        "--json",
        action="store_true",
        required=False,
        help="Use JSON for whitelist queries.",
        dest="json",
    )
    parser.add_argument(
        "--db",
        "--database",
        action="store_true",
        required=False,
        help="Use a database for whitelist queries.",
        dest="db",
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
    
    if args.json:
        whitelist_type = "json"
    elif args.db:
        whitelist_type = "db"

    if args.config:
        logger.info("Configuration argument provided...")
        Config()
    else:
        logger.info("Using provided arguments...")
        initiate(
            whitelist_type=whitelist_type,
            whitelist_path=args.whitelist_path,
            base_log_dir=args.base_log_dir,
            rcon_host=args.rcon_host,
            rcon_port=args.rcon_port,
            rcon_password=args.rcon_password,
            heartbeat=args.heartbeat
        )


if __name__ == "__main__":
    setup_logging("./logs/")
    main()
