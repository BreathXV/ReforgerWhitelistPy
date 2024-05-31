import logging, logging.handlers
import os   # TODO: Change to pathlib

def setup_logging(log_directory: str) -> None:
    """Set up the logging for the application. Will also print to the CLI.

    ...

    Parameters
    ----------
    log_directory : str
        The system path in which the log should be printed.
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