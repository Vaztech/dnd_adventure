import logging
import time
from typing import Optional
from colorama import Fore, Style
from dnd_adventure.player_manager import PlayerManager
from dnd_adventure.movement_handler import MovementHandler
from dnd_adventure.combat_manager import CombatManager
from dnd_adventure.lore_manager import LoreManager
from dnd_adventure.save_manager import SaveManager
from dnd_adventure.ui_manager import UIManager
from dnd_adventure.world import World
from dnd_adventure.game_world import GameWorld
from dnd_adventure.quest_manager import QuestManager
from dnd_adventure.utils import load_graphics
import json
import os

logger = logging.getLogger(__name__)

class Game:
    def __init__(self, player_name: str, save_file: Optional[str] = None):
        logger.debug(f"Initializing Game object for player: {player_name}")
        print("DEBUG: Initializing Game...")
        self.player_name = player_name
        self.graphics = load_graphics()
        races_path = os.path.join(os.path.dirname(__file__), 'data', 'races.json')
        logger.debug(f"Loading races from {races_path}...")
        try:
            with open(races_path, 'r') as f:
                self.races = json.load(f)
            logger.debug(f"Loaded races: {self.races}")
        except FileNotFoundError:
            logger.error(f"Races file not found at {races_path}")
            self.races = []
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding races.json: {e}")
            self.races = []
        classes_path = os.path.join(os.path.dirname(__file__), 'data', 'classes.json')
        logger.debug(f"Loading classes from {classes_path}...")
        try:
            with open(classes_path, 'r') as f:
                self.classes = json.load(f)
            logger.debug(f"Loaded classes: {self.classes}")
        except FileNotFoundError:
            logger.error(f"Classes file not found at {classes_path}")
            self.classes = []
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding classes.json: {e}")
            self.classes = []
        self.world = World(seed=None, graphics=self.graphics)
        self.game_world = GameWorld(self.world)
        self.quest_manager = QuestManager(self.world)
        self.player_manager = PlayerManager(self)
        self.movement_handler = MovementHandler(self)
        self.combat_manager = CombatManager(self)
        self.lore_manager = LoreManager(self)
        self.save_manager = SaveManager()
        self.ui_manager = UIManager(self)
        self.player, self.starting_room = self.player_manager.initialize_player(save_file)
        if self.player is None:
            logger.error("Game cannot start without a player")
            self.running = False
            print(f"{Fore.YELLOW}Game cannot start without a character. Returning to main menu.{Style.RESET_ALL}")
            return
        self.current_room = self.starting_room
        self.player_pos = self.player_manager.find_starting_position()
        self.running = True
        self.mode = "movement"
        self.debug_mode = False
        self.previous_menu = None
        self.commands = [
            "look", "lore", "attack", "cast", "rest", "talk",
            "quest list", "quest start", "quest complete", "save", "quit", "exit"
        ]
        self.current_map = None
        self.last_world_pos = self.player_pos
        self.message = ""
        self.last_enter_time = 0
        tile = self.world.get_location(*self.player_pos)
        if tile["type"] in self.graphics["maps"]:
            self.current_map = tile["type"]
            self.player_pos = (2, 2)
        self.current_room = f"{self.last_world_pos[0]},{self.last_world_pos[1]}" if tile["type"] in ["dungeon", "castle"] else None
        logger.debug(f"Game initialized: map={self.current_map}, room={self.current_room}, pos={self.player_pos}")

    def handle_command(self, cmd: str):
        self.message = ""
        logger.debug(f"Handling command: {cmd}")
        cmd = cmd.lower().strip()
        if cmd == "look":
            self.ui_manager.display_current_map()
        elif cmd == "lore":
            self.lore_manager.print_lore()
        elif cmd == "attack":
            self.combat_manager.handle_attack_command()
        elif cmd.startswith("cast "):
            self.combat_manager.handle_cast_command(cmd)
        elif cmd == "cast list":
            self.combat_manager.print_spell_list()
        elif cmd == "rest":
            self.combat_manager.handle_rest_command()
        elif cmd == "talk":
            room = self.game_world.rooms.get(self.current_room)
            if room and hasattr(room, 'npcs') and room.npcs:
                print(room.npcs[0].talk())
            else:
                print(f"{Fore.YELLOW}No one to talk to here!{Style.RESET_ALL}")
        elif cmd == "quest list":
            self.quest_manager.quest_list()
        elif cmd.startswith("quest start "):
            try:
                quest_id = int(cmd.split()[-1])
                self.quest_manager.start_quest(quest_id)
            except ValueError:
                print(f"{Fore.RED}Invalid quest ID. Use 'quest start <number>'.{Style.RESET_ALL}")
                logger.warning(f"Invalid quest ID: {cmd}")
        elif cmd == "quest complete":
            for quest in self.quest_manager.active_quests:
                self.quest_manager.complete_quest(quest["id"], self.player, self.last_world_pos, self.current_room)
        elif cmd == "save":
            save_data = self.player.to_dict()
            save_data["current_room"] = self.current_room
            save_data["player_pos"] = list(self.last_world_pos)
            save_data["world_seed"] = None
            self.save_manager.save_game(save_data, f"{self.player_name.lower().replace(' ', '_')}_{int(time.time())}.save")
        elif cmd in ["quit", "exit"]:
            self.running = False
            logger.info("Game quit by user")
        elif cmd in ["north", "south", "east", "west", "n", "s", "e", "w"]:
            print(f"{Fore.RED}Movement is controlled with arrow keys or WASD only.{Style.RESET_ALL}")
            logger.debug(f"Attempted movement command: {cmd}")
        elif cmd == "help":
            print(f"{Fore.YELLOW}Available commands: {', '.join(self.commands)}{Style.RESET_ALL}")
            logger.debug("Displayed help commands")
        elif cmd == "debug":
            self.debug_mode = not self.debug_mode
            print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
        elif cmd == "clear path" and self.debug_mode:
            self.world.map["locations"][101][96]["type"] = "forest"
            print("Path cleared at (101, 96)")
        elif cmd:
            print(f"{Fore.RED}Unknown command '{cmd}'. Try: {', '.join(self.commands)}{Style.RESET_ALL}")
            logger.warning(f"Unknown command: {cmd}")