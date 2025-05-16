import os
import json
import logging
from typing import Optional, Tuple, Callable, Dict
from dnd_adventure.character import Character
from dnd_adventure.world import GameWorld
from dnd_adventure.races import Race
from dnd_adventure.classes import DnDClass

logger = logging.getLogger(__name__)

SAVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'saves')
os.makedirs(SAVE_DIR, exist_ok=True)

class SaveManager:
    @staticmethod
    def save_game(game_data: Dict, save_file: str) -> bool:
        """
        Saves the game data to a file.
        Args:
            game_data: Dictionary containing game state.
            save_file: Path to the save file.
        Returns:
            bool: True if save was successful, False otherwise.
        """
        try:
            with open(save_file, 'w', encoding="utf-8") as f:
                json.dump(game_data, f, indent=4)
            logger.debug(f"Saved game to {save_file}: {game_data}")
            return True
        except Exception as e:
            logger.error(f"Failed to save game to {save_file}: {e}")
            return False

    @staticmethod
    def load_game(save_file: str) -> Dict:
        """
        Loads the game data from a file.
        Args:
            save_file: Path to the save file.
        Returns:
            dict: Game data loaded from the file.
        Raises:
            FileNotFoundError: If the save file does not exist.
            json.JSONDecodeError: If the save file is corrupted.
        """
        save_path = os.path.join(SAVE_DIR, f"{save_file}.save" if not save_file.endswith('.save') else save_file)
        if not os.path.exists(save_path):
            logger.debug(f"No save file found at {save_path}")
            raise FileNotFoundError(f"No save file found for {save_file}")

        try:
            with open(save_path, 'r', encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Loaded game from {save_path}: {data}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted save file {save_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load game from {save_path}: {e}")
            raise

    @staticmethod
    def list_saves() -> list:
        try:
            saves = [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith('.save')]
            logger.debug(f"Listed saves: {saves}")
            return saves
        except Exception as e:
            logger.error(f"Failed to list saves: {e}")
            return []