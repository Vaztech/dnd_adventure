import logging
import time
from typing import Optional, List
from colorama import Fore, Style
from player_manager.player_manager import PlayerManager
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
    def __init__(self, player_name: str, player_manager: PlayerManager, save_file: Optional[str] = None):
        logger.debug(f"Initializing Game object for player: {player_name}")
        print("DEBUG: Initializing Game...")
        self.player_name = player_name
        self.graphics = load_graphics()
        self.world = World(seed=None, graphics=self.graphics)
        self.game_world = GameWorld(self.world)
        self.quest_manager = QuestManager(self.world)
        self.player_manager = player_manager
        self.races = self.player_manager.race_manager.races
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
        self.movement_handler = MovementHandler(self)
        self.combat_manager = CombatManager(self)
        lore_path = os.path.join(os.path.dirname(__file__), 'data', 'lore.json')
        self.lore_manager = LoreManager(lore_path)
        self.save_manager = SaveManager()
        self.ui_manager = UIManager(self)
        self.player, self.starting_room = self.player_manager.initialize_player(self, save_file)
        if self.player is None:
            logger.error("Game cannot start without a player")
            self.running = False
            print(f"{Fore.YELLOW}Game cannot start without a character. Returning to main menu.{Style.RESET_ALL}")
            return
        self.lore_manager.print_lore()
        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        self.current_room = self.starting_room
        self.player_pos = self.player_manager.find_starting_position(self)
        self.running = True
        self.mode = "movement"
        self.debug_mode = False
        self.previous_menu = None
        self.commands = [
            "look", "lore", "attack", "cast", "rest", "talk",
            "quest list", "quest start", "quest complete", "save", "quit", "exit", "character"
        ]
        self.current_map = None
        self.last_world_pos = self.player_pos
        self.message = ""
        self.last_enter_time = 0
        self.last_key_time = 0.0  # Added for input debouncing
        tile_key = f"{self.player_pos[0]},{self.player_pos[1]}"
        x, y = map(int, tile_key.split(","))
        tile = self.world.map["locations"][y][x] if 0 <= y < self.world.map["height"] and 0 <= x < self.world.map["width"] else {"type": "plains"}
        if tile["type"] in self.graphics["maps"]:
            self.current_map = tile["type"]
            self.player_pos = (2, 2)
        self.current_room = tile_key if tile["type"] in ["dungeon", "castle"] else None
        logger.debug(f"Game initialized: map={self.current_map}, room={self.current_room}, pos={self.player_pos}")

    @staticmethod
    def list_save_files() -> List[str]:
        """Return a list of save files in the saves directory."""
        saves_dir = os.path.join(os.path.dirname(__file__), '..', 'saves')
        try:
            if not os.path.exists(saves_dir):
                os.makedirs(saves_dir)
            save_files = [f for f in os.listdir(saves_dir) if f.endswith('.save')]
            logger.debug(f"Found save files: {save_files}")
            return save_files
        except Exception as e:
            logger.error(f"Error listing save files: {e}")
            return []

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
            tile_key = "101,96"
            self.world.map["locations"][tile_key] = {"type": "forest"}
            print("Path cleared at (101, 96)")
        elif cmd == "character":
            player_data = self.player.to_dict()
            stats = player_data["stats"]
            modifiers = {
                "Strength": (stats["Strength"] - 10) // 2,
                "Dexterity": (stats["Dexterity"] - 10) // 2,
                "Constitution": (stats["Constitution"] - 10) // 2,
                "Intelligence": (stats["Intelligence"] - 10) // 2,
                "Wisdom": (stats["Wisdom"] - 10) // 2,
                "Charisma": (stats["Charisma"] - 10) // 2,
            }
            hp = 6 + modifiers["Constitution"]  # Rogue hit die 6
            mp = 0  # Rogue has no MP
            spells = ", ".join(player_data["spells"].get(0, []) + player_data["spells"].get(1, [])) or "None"
            features = ", ".join(player_data["features"]) or "None"
            print(f"{Fore.CYAN}Character: {player_data['name']}{Style.RESET_ALL}")
            print(f"Race: {player_data['race']} ({player_data['subrace']})")
            print(f"Class: {player_data['class']} (Level {player_data['level']})")
            print(f"HP: {hp}/{hp}")
            print(f"MP: {mp}/{mp}")
            print(
                f"Stats: Strength {stats['Strength']} ({modifiers['Strength']:+d}), "
                f"Dexterity {stats['Dexterity']} ({modifiers['Dexterity']:+d}), "
                f"Constitution {stats['Constitution']} ({modifiers['Constitution']:+d}), "
                f"Intelligence {stats['Intelligence']} ({modifiers['Intelligence']:+d}), "
                f"Wisdom {stats['Wisdom']} ({modifiers['Wisdom']:+d}), "
                f"Charisma {stats['Charisma']} ({modifiers['Charisma']:+d})"
            )
            print(f"Features: {features}")
            print(f"Spells: {spells}")
            logger.debug(f"Displayed character sheet for {player_data['name']}")
        elif cmd:
            print(f"{Fore.RED}Unknown command '{cmd}'. Try: {', '.join(self.commands)}{Style.RESET_ALL}")
            logger.warning(f"Unknown command: {cmd}")