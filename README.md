# Reforger Whitelist

Reforger Whitelist is a Python script designed to monitor log files of a game server and kick unwhitelisted players automatically. It supports two types of whitelists: a SQLite database and a JSON file. When a player connects to the server, the script checks if the player is whitelisted in either the database or the JSON file. If the player is not whitelisted, the script executes a kick command via RCON (Remote Console) to remove the player from the server.

## Features

- Monitors log files of the game server in real-time.
- Supports both SQLite database and JSON file whitelists.
- Automatically kicks unwhitelisted players upon connection.
- Provides detailed logging for monitoring and debugging.

## Requirements

- Python 3.x
- BERCon (RCON tool for executing commands on the game server)
- SQLite (if using a database whitelist)

## Usage

1. Install the required dependencies:

   ```bash
   pip install argparse
   ```

2. Ensure BERCon is installed and accessible in the system PATH.

3. Configure the script by providing command-line arguments:

   ```bash
   python reforgewhitelist.py --whitelist-type [database/json] --whitelist-path [path_to_whitelist_file] --base-log-dir [base_directory_of_log_files] --rcon-host [rcon_host_address] --rcon-port [rcon_port_number] --rcon-password [rcon_password]
   ```

   - `whitelist-type`: Type of whitelist to use (database or JSON).
   - `whitelist-path`: Path to the whitelist file (database or JSON).
   - `base-log-dir`: Base directory to look for log files.
   - `rcon-host`: RCON host address.
   - `rcon-port`: RCON port number.
   - `rcon-password`: RCON password.

4. Run the script:

   ```bash
   python reforgewhitelist.py
   ```

5. Sit back and let the script automatically monitor and manage player whitelisting on your game server!

## Customization

- You can customize the logging behavior by modifying the `setup_logging()` function in the script.
- For advanced customization, you can extend the script to support additional whitelist types or integrate with other server management tools.

## License

This script is provided under the [MIT License](LICENSE).

## Disclaimer

This script is provided as-is, without any warranties or guarantees. Use it at your own risk. Always ensure compliance with the terms of service of your game server provider.
