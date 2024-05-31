import json
import loggi

class Config:
    """A class to represent the configuration file and its values.

    ...
    
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
    def __init__(
        self,
        config_path: str,
    ) -> bool:
        self.config_path = config_path
        self.whitelist_type = None
        self.whitelist_path = None
        self.base_log_dir = None
        self.rcon_host = None
        self.rcon_port = None
        self.rcon_password = None
        self.heartbeat = None
        self.param_dict = {
            "env": "",
            "whitelist_type": "",
            "whitelist_path": "",
            "base_log_dir": "",
            "rcon_host": "",
            "rcon_port": "",
            "rcon_password": "",
            "heartbeat": ""
        }


    def check_config(self) -> bool:
        """Checks the config file to ensure it befits the applications needs.

        ...

        Returns
        ----------
        bool
            Whether the configuration file has all required parameters or not.
        """
        try:
            with open(file=self.config_path, mode="r", encoding="utf-8") as file:
                config = json.load(file)
                logging.info("Loaded configuration file")
                # Check for all params in the config
                for param in config.get(str(self.param_dict.keys()), ""):
                    if not param:
                        logging.error("A parameter is missing in the configuration file!")
                        return False
                    else:
                        logging.info(f"All parameters are present within {self.config_path}")
                        return True
        except FileNotFoundError:
            logging.error(f"Configuration file could not be found at {self.config_path}")
        except json.JSONDecodeError:
            logging.error(f"File was found but could not decode it - make sure it has 'utf-8' encoding.")
    
    def get_config_value(self) -> bool:
        """Retrieves all values from the config file.

        ...

        Returns
        ----------
        bool
            Whether all of the configuration file's values where able to be assigned.
        """        
        with open(file=self.config_path, mode="r", encoding="utf-8") as file:
            config = json.load(file)
            # Assign each args value to the dict
            logging.info("Assigning all config values...")
            for param in self.param_dict.keys():
                logging.info(f"Loaded {param}")
                self.param_dict[param] == config.get(param, "")
                logging.info(f"{param}: {self.param_dict[param]}")
            return True