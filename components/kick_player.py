import threading
import logging

from rcon.battleye import Client

from components import logging as dev

logger = logging.getLogger(__name__)


def execute_kick_command(
    player_id: str, rcon_host: str, rcon_port: int, rcon_password: str
) -> None:
    """Starts the thread to establish the RCON connection and execute the kick command.

    ...

    Parameters
    ----------
    player_id : str
        The ID of the player, typically assigned by the server upon join.
    rcon_host : str
        The host IP address of the RCON.
    rcon_port : int
        The port of the RCON.
    rcon_password : str
        The password of the RCON.
    """

    def kick_player() -> None:
        """Nested function that establishes a connection with BERCon and executes the kick command."""
        command = f"#kick {player_id}"
        dev.debugLine(f"Command values assigned: {command}")

        try:
            with Client(host=rcon_host, port=rcon_port, passwd=rcon_password) as client:
                rsp = client.run(command=command)
                if rsp == "":
                    logger.error(f"Failed to execute kick command for player ID {player_id}")
                    dev.debugLine(
                        f"""
                        Response: {rsp}\n
                        Command: {command}\n 
                        Host: {rcon_host}\n
                        Port: {rcon_port}\n
                        Password: {rcon_password}
                        """
                    )
                # TODO: Add additional error handling for other rsp
                client.close()
            logger.info(
                "Successfully executed kick command for player ID %s" % player_id
            )
        except Exception as e:
            logger.error(
                "Unexpected error executing kick command for player ID %s: %s"
                % (player_id, e)
            )

    kick_thread = threading.Thread(target=kick_player, name=f"KickThread-{player_id}")
    dev.debugLine("Created kick thread.")
    kick_thread.start()
    dev.debugLine("Started kick thread.")
