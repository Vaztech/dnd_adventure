import os
import pickle
import logging
from dnd_adventure.character import Character  # Use absolute import based on project root

logger = logging.getLogger(__name__)

SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True)

class SaveManager:
    @staticmethod
    def save_player(player, room_id):
        """Save player and room ID to file by character name."""
        filename = f"{player.name}.save"
        filepath = os.path.join(SAVE_DIR, filename)
        try:
            with open(filepath, "wb") as f:
                pickle.dump((player, room_id), f)
        except Exception as e:
            logger.error(f"Error saving player: {e}")

    @staticmethod
    def load_player(world, name, create_player):
        """Load player and room from file by name, or create new."""
        filename = f"{name}.save"
        filepath = os.path.join(SAVE_DIR, filename)
        try:
            with open(filepath, "rb") as f:
                player, room_id = pickle.load(f)
                return player, world.get_room(room_id)
        except (FileNotFoundError, pickle.PickleError, AttributeError) as e:
            logger.warning(f"No valid save file for {name} or load error: {e}")
            return create_player(name), world.get_room(0)

    @staticmethod
    def list_saves():
        """List all saved character names."""
        try:
            return [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith(".save")]
        except Exception as e:
            logger.error(f"Error listing saves: {e}")
            return []