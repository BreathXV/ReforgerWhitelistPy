import sqlite3
import json
import logging

logger = logging.getLogger(__name__)


def is_player_in_database(player_name: str, identity_id: str, db_path: str) -> bool:
    """Checks if a player's identifier is in the database.

    ...

    Parameters
    ----------
    player_name : str
        The player's gamertag (Console) or name (PC).
    identity_id : str
        The player's GUID (BID).
    db_path : str
        The system path to the database file.

    Returns
    ----------
    bool
        Whether the player is in the database (True) or not (False).
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT whitelisted 
                FROM user_data 
                WHERE (LOWER(game_name) = LOWER(?) OR LOWER(game_name) = LOWER(?)) 
                AND whitelisted = 1
                """,
                (player_name, identity_id),
            )
            is_whitelisted = cur.fetchone()
            if is_whitelisted is not None:
                logger.info(
                    f"Player {player_name} or IdentityId {identity_id} found in database and is whitelisted."
                )
                return True
            else:
                logger.info(
                    f"Player {player_name} or IdentityId {identity_id} not found in database or not whitelisted."
                )
                return False
    except sqlite3.Error as database_error:
        logger.error(f"Database error: {database_error}")
        return False


def is_player_in_json(player_name: str, identity_id: str, json_path: str) -> bool:
    """Checks if the player is in the JSON.

    ...

    Parameters
    ----------
    player_name : str
        The player's gamertag (Console) or name (PC).
    identity_id : str
        The player's GUID (BID).
    json_path : str
        The system path to the JSON file.

    Returns
    ----------
    bool
        Whether the player is in the database (True) or not (False).
    """
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for player in data.get("players", []):
                if (
                    player_name.lower() == player.get("game_name", "").lower()
                    or identity_id.lower() == player.get("identity_id", "").lower()
                ):
                    if player.get("whitelisted", 0) == 1:
                        logger.info(
                            f"Player {player_name} or IdentityId {identity_id} found in JSON and is whitelisted."
                        )
                        return True
            logger.info(
                f"Player {player_name} or IdentityId {identity_id} not found in JSON or not whitelisted."
            )
            return False
    except json.JSONDecodeError as json_error:
        logger.error(f"JSON error: {json_error}")
        return False
