import json
import logging

logger = logging.getLogger(__name__)

class Config:
    """A class to represent the configuration file and its values.

    Attributes
    ----------
    config_path : str
        The path to the configuration file.
    whitelist_type : str
        The whitelist type the user chooses (json, db).
    whitelist_path : str
        The path to the whitelist data.
    base_log_dir : str
        The path to the game's `console.log` file.
    rcon_host : str
        The IP address that the RCON is hosted on.
    rcon_port : int
        The port the RCON is hosted on.
    rcon_password : str
        The password used for connection to the RCON host.
    heartbeat : int
        The interval between whitelist status messages.

    Methods
    ----------
    check_config:
        Checks that the provided configuration file has all of the required parameters.
    get_config_value -> bool:
        Retrieves all values from the configuration file.
    """    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.whitelist_type = None
        self.whitelist_path = None
        self.base_log_dir = None
        self.rcon_host = None
        self.rcon_port = None
        self.rcon_password = None
        self.heartbeat = None
        self.param_dict = {
            "whitelist_type": "",
            "whitelist_path": "",
            "base_log_dir": "",
            "rcon_host": "",
            "rcon_port": "",
            "rcon_password": "",
            "heartbeat": ""
        }

    def check_config(self) -> bool:
        """Checks the config file to ensure it meets the application's needs.

        Returns
        ----------
        bool
            Whether the configuration file has all required parameters or not.
        """
        try:
            with open(file=self.config_path, mode="r", encoding="utf-8") as file:
                config = json.load(file)
                logger.info("Loaded configuration file")
                # Check for all params in the config
                for param in self.param_dict.keys():
                    if param not in config:
                        logger.error(f"A parameter '{param}' is missing in the configuration file!")
                        return False
                logger.info(f"All parameters are present within {self.config_path}")
                return True
        except FileNotFoundError:
            logger.error(f"Configuration file could not be found at {self.config_path}")
            return False
        except json.JSONDecodeError:
            logger.error(f"File was found but could not decode it - make sure it has 'utf-8' encoding.")
            return False
    
    def get_config_value(self) -> bool:
        """Retrieves all values from the config file.

        Returns
        ----------
        bool
            Whether all of the configuration file's values were able to be assigned.
        """        
        try:
            with open(file=self.config_path, mode="r", encoding="utf-8") as file:
                config = json.load(file)
                # Assign each config value to the corresponding class attribute
                logger.info("Assigning all config values...")
                for param in self.param_dict.keys():
                    if param in config:
                        setattr(self, param, config[param])
                        logger.info(f"{param}: {getattr(self, param)}")
                    else:
                        logger.error(f"Parameter '{param}' is missing in the configuration file!")
                        return False
                return True
        except FileNotFoundError:
            logger.error(f"Configuration file could not be found at {self.config_path}")
            return False
        except json.JSONDecodeError:
            logger.error(f"File was found but could not decode it - make sure it has 'utf-8' encoding.")
            return False
