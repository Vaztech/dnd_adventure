import os
import json
import logging
from typing import List, Optional, Tuple
from dnd_adventure.character import Character
from dnd_adventure.races import Race
from dnd_adventure.leveling import level_up, load_classes
from dnd_adventure.utils import load_json_file
from colorama import Fore, Style

logger = logging.getLogger(__name__)

class PlayerManager:
    def __init__(self, game):
        self.game = game
        self.races = self.load_races()
        self.classes = load_classes()

    def load_races(self) -> List[Race]:
        races_path = os.path.join(os.path.dirname(__file__), "data", "races.json")
        logger.debug(f"Loading races from {races_path}...")
        try:
            races_data = load_json_file(races_path)
            return [Race(**race) for race in races_data]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load races: {e}. Using fallback races.")
            return [
                Race(
                    name="Gnome",
                    subraces={
                        "Svirfneblin": {"stat_bonuses": {"Dexterity": 2, "Wisdom": 2}, "features": ["Darkvision", "Stone Camouflage"]},
                        "Forest": {"stat_bonuses": {"Intelligence": 2}, "features": ["Natural Illusionist"]}
                    },
                    features=["Gnome Cunning"]
                ),
                Race(
                    name="Aasimar",
                    subraces={
                        "Base Aasimar": {"stat_bonuses": {"Charisma": 2}, "features": ["Celestial Resistance"]}
                    },
                    features=["Darkvision"]
                )
            ]

    def get_xp_for_level(self, level: int) -> int:
        if level <= 1:
            return 0
        inoculated_level = level - 2
        if level == 2:
            return 300
        return 300 * (3 ** inoculated_level)

    def check_level_up(self):
        if level_up(self.game.player, self.classes):
            # Level-up handled in leveling.py
            pass

    def find_starting_position(self) -> Tuple[int, int]:
        x, y = 96, 96
        max_distance = 30
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for distance in range(max_distance):
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < self.game.world.map["width"] and 
                        0 <= new_y < self.game.world.map["height"]):
                        tile = self.game.world.get_location(new_x, new_y)
                        if tile["type"] == "plains":
                            has_exit = False
                            for dir_dx, dir_dy in directions:
                                adj_x, adj_y = new_x + dir_dx, new_y + dir_dy
                                if (0 <= adj_x < self.game.world.map["width"] and 
                                    0 <= adj_y < self.game.world.map["height"]):
                                    adj_tile = self.game.world.get_location(adj_x, adj_y)
                                    if adj_tile["type"] in ["plains", "forest"]:
                                        has_exit = True
                                        break
                            if has_exit:
                                logger.debug(f"Starting position found: ({new_x}, {new_y})")
                                return (new_x, new_y)
        logger.debug(f"Fallback starting position: ({x}, {y})")
        return (x, y)

    def initialize_player(self, save_file: Optional[str]) -> Tuple[Character, Optional[str]]:
        from dnd_adventure.character_creator import create_player
        logger.debug(f"Initializing player, save_file={save_file}")
        if save_file:
            try:
                player_data = self.game.save_manager.load_game(save_file)
                player = Character(**player_data)
                starting_room = player_data.get("current_room")
                self.game.player_pos = tuple(player_data.get("player_pos", (0, 0)))
                logger.info(f"Loaded character {self.game.player_name} from {save_file}")
                return player, starting_room
            except Exception as e:
                logger.error(f"Failed to load save file {save_file}: {e}")
                print(f"{Fore.RED}Failed to load save: {e}. Starting new game.{Style.RESET_ALL}")
        logger.debug("Creating new player")
        player = create_player(self.game.player_name, self.game)
        starting_room = next((room_id for room_id in self.game.game_world.rooms if self.game.game_world.world.get_location(*map(int, room_id.split(',')))["type"] == "dungeon"), None)
        if starting_room:
            self.game.player_pos = tuple(map(int, starting_room.split(",")))
        logger.debug("Player initialization complete")
        return player, starting_room