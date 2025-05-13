import pickle
import logging
from dnd_adventure.character import Character  # Use absolute import based on project root

logger = logging.getLogger(__name__)
logger.debug(f"Using Character class from: {Character.__module__}")

class SaveManager:
    SAVE_FILE = "player.save"

    @staticmethod
    def save_player(player, room_id):
        """Save player and room ID to file."""
        logger.debug(f"Saving player: name={player.name}, type={type(player)}, room_id={room_id}")
        with open(SaveManager.SAVE_FILE, "wb") as f:
            pickle.dump((player, room_id), f)

    @staticmethod
    def load_player(world, create_player):
        """Load player and room from file, or create new player if loading fails."""
        try:
            with open(SaveManager.SAVE_FILE, "rb") as f:
                player, room_id = pickle.load(f)
                logger.debug(f"Loaded player: name={player.name}, type={type(player)}, attributes={vars(player)}, room_id={room_id}")
                # Patch old player data if needed
                if not hasattr(player, "race"):
                    logger.warning("Old player data detected; creating new player")
                    return create_player(), world.get_room(0)
                return player, world.get_room(room_id)
        except (FileNotFoundError, pickle.PickleError, AttributeError) as e:
            logger.info(f"No valid save file found or error loading: {e}; creating new player")
            return create_player(), world.get_room(0)
