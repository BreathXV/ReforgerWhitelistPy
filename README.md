# Reforger Whitelist

Reforger Whitelist is a Python script designed to monitor log files of a game server and kick unwhitelisted players automatically. It supports two types of whitelists: a SQLite database and a JSON file. When a player connects to the server, the script checks if the player is whitelisted in either the database or the JSON file. If the player is not whitelisted, the script executes a kick command via RCON (Remote Console) to remove the player from the server.

## Installation and Configuration

Find all the installation instructions [here](https://github.com/BreathXV/ReforgerWhitelistPy/blob/dev/docs/SETUP.md).
Once you have installed the application, find all of the configuration options [here](https://github.com/BreathXV/ReforgerWhitelistPy/blob/dev/docs/CONFIGURATION.md).

## Features

- Monitors log files of the game server in real-time.
- Supports both SQLite database and JSON file whitelists.
- Automatically kicks unwhitelisted players upon connection.
- Provides detailed logging for monitoring and debugging.

## Customization

- You can customize the logging behavior by modifying the `setup_logging()` function in the script.
- For advanced customization, you can extend the script to support additional whitelist types or integrate with other server management tools.

## License

This script is provided under the [MIT License](LICENSE).

## Disclaimer

This script is provided as-is, without any warranties or guarantees. Use it at your own risk. Always ensure compliance with the terms of service of your game server provider.
