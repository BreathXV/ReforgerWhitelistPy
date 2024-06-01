import time
import logging

logger = logging.getLogger(__name__)


def heartbeat(count: int) -> None:
    """Sends log and CLI messages every count in seconds.

    ...

    Parameters
    ----------
    count : int
        Interval between messages.
    """
    while True:
        logger.info("Whitelist is running... Use [Ctrl + C] to stop the application.")
        time.sleep(count)
