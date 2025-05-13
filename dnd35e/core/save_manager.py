import pickle
import logging
from dnd_adventure.character import Character  # Use absolute import based on project root

logger = logging.getLogger(__name__)

class SaveManager:
    SAVE_FILE = "player.save"

    @staticmethod
    def save_player(player, room_id):
        """Save player and room ID to file."""
        try:
            with open(SaveManager.SAVE_FILE, "wb") as f:
                pickle.dump((player, room_id), f)
        except Exception as e:
            logger.error(f"Error saving player: {e}")

    @staticmethod
    def load_player(world, create_player):
        """Load player and room from file, or create new player if loading fails."""
        try:
            with open(SaveManager.SAVE_FILE, "rb") as f:
                player, room_id = pickle.load(f)
                if not hasattr(player, "race"):
                    return create_player(), world.get_room(0)
                return player, world.get_room(room_id)
        except (FileNotFoundError, pickle.PickleError, AttributeError) as e:
            return create_player(), world.get_room(0)