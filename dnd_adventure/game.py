import sys
import random
import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from colorama import Fore, Style
from dnd_adventure.character import Character
from dnd_adventure.world import World
from dnd_adventure.room import Room
from dnd_adventure.game_world import GameWorld
from dnd_adventure.dnd35e.core.monsters import Monster, Attack
from dnd_adventure.quest_manager import QuestManager
from dnd_adventure.save_manager import SaveManager
from dnd_adventure.utils import load_graphics

logger = logging.getLogger(__name__)

class Game:
    def __init__(self, player_name: str, save_file: Optional[str] = None):
        logger.debug(f"Initializing Game object for player: {player_name}")
        print("DEBUG: Initializing Game...")
        self.player_name = player_name
        logger.debug("Loading graphics...")
        self.graphics = load_graphics()
        logger.debug("Creating World...")
        self.world = World(seed=None, graphics=self.graphics)
        logger.debug("Creating GameWorld...")
        self.game_world = GameWorld(self.world)
        logger.debug("Creating QuestManager...")
        self.quest_manager = QuestManager(self.world)
        logger.debug("Creating SaveManager...")
        self.save_manager = SaveManager()
        logger.debug("Initializing player...")
        self.player, self.starting_room = self.initialize_player(save_file)
        logger.debug("Setting current room...")
        self.current_room = self.starting_room
        logger.debug("Finding starting position...")
        self.player_pos = self.find_starting_position()
        logger.debug("Setting game state...")
        self.running = True
        self.mode = "movement"
        self.debug_mode = False  # Added for trap testing
        self.previous_menu = None
        self.commands = [
            "look", "lore", "attack", "cast", "rest",
            "quest list", "quest start", "quest complete", "save", "quit", "exit"
        ]
        self.current_map = None
        self.last_world_pos = self.player_pos
        self.message = ""
        self.last_enter_time = 0
        logger.debug("Setting initial map and room...")
        tile = self.world.get_location(*self.player_pos)
        if tile["type"] in self.graphics["maps"]:
            self.current_map = tile["type"]
            self.player_pos = (2, 2)
        self.current_room = f"{self.last_world_pos[0]},{self.last_world_pos[1]}" if tile["type"] in ["dungeon", "castle"] else None
        logger.debug(f"Game initialized: map={self.current_map}, room={self.current_room}, pos={self.player_pos}")

    def get_xp_for_level(self, level: int) -> int:
        if level <= 1:
            return 0
        inoculated_level = level - 2
        if level == 2:
            return 300
        return 300 * (3 ** inoculated_level)

    def check_level_up(self):
        current_level = self.player.level
        next_level = current_level + 1
        xp_required = self.get_xp_for_level(next_level)
        while self.player.xp >= xp_required and next_level <= 20:
            self.player.level = next_level
            self.player.max_hit_points += 5
            self.player.hit_points = self.player.max_hit_points
            self.player.max_mp += 3
            self.player.mp = self.player.max_mp
            print(f"{Fore.GREEN}Congratulations! {self.player.name} has reached level {self.player.level}!{Style.RESET_ALL}")
            print(f"HP increased to {self.player.max_hit_points}, MP increased to {self.player.max_mp}.")
            logger.info(f"Player {self.player.name} leveled up to {self.player.level}")
            next_level += 1
            xp_required = self.get_xp_for_level(next_level)

    def calculate_monster_difficulty(self, monster: Monster) -> float:
        hp_score = monster.hit_points
        ac_score = monster.armor_class * 2
        damage_score = 0
        if monster.attacks:
            for attack in monster.attacks:
                damage_str = attack.damage
                parts = damage_str.split('+')
                dice_part = parts[0]
                bonus = int(parts[1]) if len(parts) > 1 else 0
                num_dice, die_size = map(int, dice_part.split('d'))
                avg_damage_per_die = (1 + die_size) / 2
                avg_damage = (num_dice * avg_damage_per_die) + bonus
                damage_score += avg_damage
            damage_score *= 2
        difficulty = hp_score + ac_score + damage_score
        return max(1, difficulty)

    def calculate_xp_reward(self, monster: Monster) -> int:
        difficulty = self.calculate_monster_difficulty(monster)
        scaling_factor = 50 / 33
        xp = int(difficulty * scaling_factor)
        return max(10, xp)

    def find_starting_position(self) -> Tuple[int, int]:
        x, y = 96, 96
        max_distance = 30
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for distance in range(max_distance):
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < self.world.map["width"] and 
                        0 <= new_y < self.world.map["height"]):
                        tile = self.world.get_location(new_x, new_y)
                        if tile["type"] == "plains":
                            has_exit = False
                            for dir_dx, dir_dy in directions:
                                adj_x, adj_y = new_x + dir_dx, new_y + dir_dy
                                if (0 <= adj_x < self.world.map["width"] and 
                                    0 <= adj_y < self.world.map["height"]):
                                    adj_tile = self.world.get_location(adj_x, adj_y)
                                    if adj_tile["type"] in ["plains", "forest"]:
                                        has_exit = True
                                        break
                            if has_exit:
                                logger.debug(f"Starting position found: ({new_x}, {new_y})")
                                return (new_x, new_y)
        logger.debug(f"Fallback starting position: ({x}, {y})")
        return (x, y)

    def initialize_player(self, save_file: Optional[str]) -> Tuple[Character, Optional[str]]:
        from dnd_adventure.character_creator import create_player, display_initial_lore
        logger.debug(f"Initializing player, save_file={save_file}")
        if save_file:
            try:
                player_data = self.save_manager.load_game(save_file)
                player = Character(**player_data)
                starting_room = player_data.get("current_room")
                self.player_pos = tuple(player_data.get("player_pos", (0, 0)))
                logger.info(f"Loaded character {self.player_name} from {save_file}")
                return player, starting_room
            except Exception as e:
                logger.error(f"Failed to load save file {save_file}: {e}")
                print(f"{Fore.RED}Failed to load save: {e}. Starting new game.{Style.RESET_ALL}")
        logger.debug("Creating new player")
        player = create_player(self.player_name, self)
        logger.debug("Finding starting room")
        starting_room = next((room_id for room_id in self.game_world.rooms if self.game_world.world.get_location(*map(int, room_id.split(',')))["type"] == "dungeon"), None)
        if starting_room:
            self.player_pos = tuple(map(int, starting_room.split(",")))
        logger.debug("Displaying initial lore")
        display_initial_lore(player, self.world)
        logger.debug("Player initialization complete")
        return player, starting_room

    def handle_command(self, cmd: str):
        self.message = ""
        logger.debug(f"Handling command: {cmd}")
        cmd = cmd.lower().strip()
        if cmd == "look":
            from dnd_adventure.ui import display_current_map
            display_current_map(self)
        elif cmd == "lore":
            self.print_lore()
        elif cmd == "attack":
            self.handle_attack_command()
        elif cmd.startswith("cast "):
            self.handle_cast_command(cmd)
        elif cmd == "cast list":
            self.print_spell_list()
        elif cmd == "rest":
            self.handle_rest_command()
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
            self.save_game()
        elif cmd in ["quit", "exit"]:
            self.running = False
            logger.info("Game quit by user")
        elif cmd in ["north", "south", "east", "west", "n", "s", "e", "w"]:
            print(f"{Fore.RED}Movement is controlled with arrow keys or WASD only.{Style.RESET_ALL}")
            logger.debug(f"Attempted movement command: {cmd}")
        elif cmd == "help":
            print(f"{Fore.YELLOW}Available commands: {', '.join(self.commands)}{Style.RESET_ALL}")
            logger.debug("Displayed help commands")
        elif cmd:
            print(f"{Fore.RED}Unknown command '{cmd}'. Try: {', '.join(self.commands)}{Style.RESET_ALL}")
            logger.warning(f"Unknown command: {cmd}")

    def handle_movement(self, direction: str):
        self.message = ""
        logger.debug(f"Handling movement: {direction}")
        if self.current_map:
            x, y = self.player_pos
            dx, dy = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}[direction]
            new_pos = (x + dx, y + dy)
            map_data = self.graphics["maps"][self.current_map]
            new_x, new_y = new_pos
            adjusted_y = len(map_data["layout"]) - 1 - new_y
            if (new_x < 0 or new_x >= len(map_data["layout"][0]) or
                new_y < 0 or new_y >= len(map_data["layout"])):
                self.current_map = None
                self.player_pos = self.last_world_pos
                self.current_room = None
                self.message = f"You exit the {self.current_map} and return to the world map."
                logger.debug(f"Exited mini-map to world map at {self.last_world_pos}")
            else:
                char = map_data["layout"][adjusted_y][new_x]
                symbol_type = map_data["symbols"].get(char, {"type": "unknown"})["type"]
                if symbol_type in ["wall", "building", "house", "tree"]:
                    self.message = f"You can't move {direction}! A {symbol_type} blocks your path."
                    logger.debug(f"Blocked movement {direction}: {symbol_type}")
                elif symbol_type == "door":
                    if self.current_map in ["castle", "dungeon"]:
                        room_id = f"{self.last_world_pos[0]},{self.last_world_pos[1]}"
                        room = self.game_world.rooms.get(room_id)
                        if room and direction in room.exits:
                            self.current_room = room.exits[direction]
                            self.last_world_pos = tuple(map(int, self.current_room.split(",")))
                            self.player_pos = (2, 2)
                            self.message = f"You pass through the door {direction} into a new {self.current_map} room."
                            logger.debug(f"Transitioned to room {self.current_room} via door {direction}")
                        else:
                            self.current_map = None
                            self.current_room = None
                            self.player_pos = self.last_world_pos
                            self.message = f"You exit the {self.current_map} through the door to the world map."
                            logger.debug(f"Exited {self.current_map} to world map via door")
                    else:
                        self.current_map = None
                        self.current_room = None
                        self.player_pos = self.last_world_pos
                        self.message = f"You exit the {self.current_map} through the door to the world map."
                        logger.debug(f"Exited house to world map")
                else:
                    self.player_pos = new_pos
                    self.message = f"You move {direction}."
                    logger.debug(f"Moved {direction} to {new_pos}")
        else:
            x, y = self.last_world_pos
            dx, dy = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}[direction]
            new_x, new_y = x + dx, y + dy
            if not (0 <= new_x < self.world.map["width"] and 0 <= new_y < self.world.map["height"]):
                self.message = "You cannot move beyond the edge of the world!"
                logger.debug("Blocked movement: World edge")
                return
            new_pos = (new_x, new_y)
            if self.current_room:
                room = self.game_world.rooms.get(self.current_room)
                if not room:
                    self.message = f"Error: Current room {self.current_room} does not exist. Resetting room."
                    logger.error(f"Room not found: {self.current_room}")
                    self.current_room = None
                    return
                if direction in room.exits:
                    self.current_room = room.exits[direction]
                    self.last_world_pos = tuple(map(int, self.current_room.split(",")))
                    self.player_pos = (2, 2)
                    self.message = f"You move {direction} to a new room."
                    logger.debug(f"Moved to room {self.current_room}")
                else:
                    self.message = "You can't go that way!"
                    logger.debug(f"Blocked movement: No exit {direction}")
            else:
                tile = self.world.get_location(*new_pos)
                if tile["type"] == "mountain":
                    self.message = "The mountains are too steep to climb!"
                    logger.debug("Blocked movement: Mountain")
                    return
                elif tile["type"] in ["river", "lake", "ocean"]:
                    self.message = f"You need a boat to cross the {tile['type']}!"
                    logger.debug(f"Blocked movement: {tile['type']}")
                    return
                self.last_world_pos = new_pos
                self.player_pos = new_pos
                self.message = f"You move {direction} to {tile['name']}."
                logger.debug(f"Moved {direction} to {tile['name']} at {new_pos}")
                if self.current_room and "temp_" in self.current_room:
                    del self.game_world.rooms[self.current_room]
                    self.current_room = None
                    logger.debug(f"Cleared temporary room: {self.current_room}")
                self.current_room = f"{self.last_world_pos[0]},{self.last_world_pos[1]}" if tile["type"] in ["dungeon", "castle"] else None
                if tile["type"] in self.graphics["maps"]:
                    self.current_map = tile["type"]
                    self.player_pos = (2, 2)
                    self.message = self.graphics["maps"][self.current_map]["description"]
                    logger.debug(f"Entered mini-map: {self.current_map}")
                elif tile["type"] in ["plains", "forest"] and random.random() < 0.1:
                    self.message = f"A wild Goblin ambushes you!"
                    temp_room_id = f"temp_{new_pos[0]},{new_pos[1]}"
                    self.game_world.rooms[temp_room_id] = Room(
                        description="A sudden encounter in the wild!",
                        exits={},
                        monsters=[Monster(
                            name="Goblin",
                            type="humanoid",
                            armor_class=15,
                            hit_points=6,
                            speed=30,
                            challenge_rating=0.25,
                            attacks=[Attack(name="Scimitar", damage="1d4+1", attack_bonus=3)]
                        )]
                    )
                    self.current_room = temp_room_id
                    logger.debug(f"Triggered ambush at {temp_room_id}")

    def handle_attack_command(self):
        self.message = ""
        logger.debug("Handling attack command")
        if not self.current_room:
            print("There's nothing to attack here!")
            logger.debug("No attack target: No current room")
            return
        room = self.game_world.rooms.get(self.current_room)
        if not room:
            print(f"{Fore.RED}Error: Current room {self.current_room} does not exist. Resetting room.{Style.RESET_ALL}")
            logger.error(f"Room not found: {self.current_room}")
            self.current_room = None
            return
        if not room.monsters:
            print("No monsters to attack!")
            logger.debug("No attack target: No monsters")
            return
        monster = room.monsters[0]
        bab = self.player.bab
        str_mod = self.player.get_stat_modifier(0)
        attack_roll = random.randint(1, 20) + bab + str_mod
        print(f"{self.player.name} attacks {monster.name} (Roll: {attack_roll})")
        logger.debug(f"Attack roll: {attack_roll} vs {monster.armor_class}")
        if attack_roll >= monster.armor_class:
            damage = max(1, random.randint(1, 8) + str_mod)
            monster.hit_points -= damage
            print(f"Hit! {monster.name} takes {damage} damage (HP: {monster.hit_points})")
            logger.debug(f"Hit: {monster.name} takes {damage} damage, HP now {monster.hit_points}")
            if monster.hit_points <= 0:
                print(f"{monster.name} is defeated!")
                xp_reward = self.calculate_xp_reward(monster)
                room.monsters.remove(monster)
                self.player.gain_xp(xp_reward)
                self.check_level_up()
                logger.info(f"Defeated {monster.name}, gained {xp_reward} XP")
                if "temp_" in self.current_room:
                    del self.game_world.rooms[self.current_room]
                    self.current_room = None
                    logger.debug(f"Cleared temporary room: {self.current_room}")
        else:
            print("Miss!")
            logger.debug("Attack missed")
        if room.monsters:
            self.handle_monster_attack(monster)

    def handle_monster_attack(self, monster: Monster):
        if not monster.attacks:
            print(f"{monster.name} has no attacks!")
            logger.debug(f"No attacks for {monster.name}")
            return
        attack = random.choice(monster.attacks)
        attack_roll = random.randint(1, 20) + attack.attack_bonus
        print(f"{monster.name} attacks {self.player.name} (Roll: {attack_roll})")
        logger.debug(f"Monster attack roll: {attack_roll} vs {self.player.armor_class}")
        if attack_roll >= self.player.armor_class:
            damage_parts = attack.damage.split('+')
            dice_part = damage_parts[0]
            bonus = int(damage_parts[1]) if len(damage_parts) > 1 else 0
            num_dice, die_size = map(int, dice_part.split('d'))
            damage = sum(random.randint(1, die_size) for _ in range(num_dice)) + bonus
            damage = max(1, damage)
            self.player.hit_points -= damage
            print(f"Hit! {self.player.name} takes {damage} damage (HP: {self.player.hit_points})")
            logger.debug(f"Monster hit: {self.player.name} takes {damage} damage, HP now {self.player.hit_points}")
            if self.player.hit_points <= 0:
                print(f"{self.player.name} has been defeated!")
                logger.info(f"Player {self.player.name} defeated")
                self.running = False
        else:
            print("Miss!")
            logger.debug("Monster attack missed")

    def handle_cast_command(self, cmd: str):
        self.message = ""
        logger.debug(f"Handling cast command: {cmd}")
        if not self.current_room:
            print("There's nothing to cast spells on here!")
            logger.debug("No cast target: No current room")
            return
        room = self.game_world.rooms.get(self.current_room)
        if not room:
            print(f"{Fore.RED}Error: Current room {self.current_room} does not exist. Resetting room.{Style.RESET_ALL}")
            logger.error(f"Room not found: {self.current_room}")
            self.current_room = None
            return
        if not room.monsters:
            print("No monsters to cast spells on!")
            logger.debug("No cast target: No monsters")
            return
        try:
            spell_index = int(cmd.split()[-1]) - 1
            spell_list = []
            for level in sorted(self.player.known_spells.keys()):
                spell_list.extend(self.player.known_spells[level])
            if 0 <= spell_index < len(spell_list):
                spell_name = spell_list[spell_index]
                result = self.player.cast_spell(spell_name, room.monsters[0] if room.monsters else None)
                print(result)
                logger.debug(f"Cast spell: {spell_name}, Result: {result}")
                if "dealing" in result and room.monsters and room.monsters[0].hit_points <= 0:
                    print(f"{room.monsters[0].name} is defeated!")
                    xp_reward = self.calculate_xp_reward(room.monsters[0])
                    room.monsters.pop(0)
                    self.player.gain_xp(xp_reward)
                    self.check_level_up()
                    logger.info(f"Defeated {room.monsters[0].name} with spell, gained {xp_reward} XP")
                    if self.current_room and "temp_" in self.current_room:
                        del self.game_world.rooms[self.current_room]
                        self.current_room = None
                        logger.debug(f"Cleared temporary room: {self.current_room}")
                if room.monsters:
                    self.handle_monster_attack(room.monsters[0])
            else:
                print("Invalid spell number!")
                logger.warning("Invalid spell number")
        except (ValueError, IndexError) as e:
            print(f"{Fore.RED}Invalid cast command. Use 'cast <number>' or 'cast list'.{Style.RESET_ALL}")
            logger.error(f"Invalid cast command: {cmd}, Error: {e}")

    def print_spell_list(self):
        self.message = ""
        logger.debug("Printing spell list")
        if not self.player.known_spells or all(len(spells) == 0 for spells in self.player.known_spells.values()):
            print("You don't know any spells!")
            logger.debug("No known spells")
            return
        print("\nKnown Spells:")
        spell_index = 1
        for level in sorted(self.player.known_spells.keys()):
            for spell in self.player.known_spells[level]:
                print(f"{spell_index}. Level {level}: {spell}")
                spell_index += 1
        logger.debug(f"Displayed spell list: {self.player.known_spells}")

    def handle_rest_command(self):
        self.message = ""
        logger.debug("Handling rest command")
        self.player.hit_points = min(self.player.hit_points + 10, self.player.max_hit_points)
        self.player.mp = min(self.player.mp + 5, self.player.max_mp)
        print(f"{self.player.name} rests, recovering to {self.player.hit_points} HP and {self.player.mp} MP.")
        logger.debug(f"Player rested: HP {self.player.hit_points}, MP {self.player.mp}")

    def print_lore(self):
        self.message = ""
        logger.debug("Printing lore")
        try:
            logger.debug(f"World name: {self.world.name}, History: {self.world.history}")
            if not hasattr(self.world, 'history') or not self.world.history:
                print(f"{Fore.YELLOW}No history available for {self.world.name}.{Style.RESET_ALL}")
                logger.debug("No history available")
                return
            print(f"\n{Fore.YELLOW}History of {self.world.name}:{Style.RESET_ALL}")
            for era in self.world.history:
                print(f"\n{Fore.LIGHTYELLOW_EX}{era['name']}:{Style.RESET_ALL}")
                for event in era["events"]:
                    print(f"  {Fore.WHITE}{event['year']}: {event['desc']}{Style.RESET_ALL}")
            logger.debug("Lore displayed")
        except Exception as e:
            logger.error(f"Error printing lore: {e}")
            print(f"{Fore.RED}An error occurred while displaying the lore: {e}{Style.RESET_ALL}")

    def save_game(self):
        self.message = ""
        logger.debug("Saving game")
        try:
            save_data = self.player.to_dict()
            save_data["current_room"] = self.current_room
            save_data["player_pos"] = list(self.last_world_pos)
            save_data["world_seed"] = None
            filename = f"{self.player_name.lower().replace(' ', '_')}_{int(time.time())}.save"
            self.save_manager.save_game(save_data, filename)
            print(f"{Fore.GREEN}Game saved as {filename}{Style.RESET_ALL}")
            logger.info(f"Game saved as {filename}")
        except Exception as e:
            print(f"{Fore.RED}Failed to save game: {e}{Style.RESET_ALL}")
            logger.error(f"Failed to save game: {e}")

    @staticmethod
    def list_save_files() -> List[str]:
        saves_dir = os.path.join("dnd_adventure", "saves")
        os.makedirs(saves_dir, exist_ok=True)
        save_files = [f for f in os.listdir(saves_dir) if f.endswith(".save")]
        logger.debug(f"Save files found: {save_files}")
        return save_files

    @staticmethod
    def delete_save_file(save_file: str) -> bool:
        save_path = os.path.join("dnd_adventure", "saves", save_file)
        try:
            os.remove(save_path)
            print(f"{Fore.GREEN}Deleted save file: {save_file}{Style.RESET_ALL}")
            logger.info(f"Deleted save file: {save_file}")
            return True
        except Exception as e:
            print(f"{Fore.RED}Failed to delete {save_file}: {e}{Style.RESET_ALL}")
            logger.error(f"Failed to delete {save_file}: {e}")
            return False

if __name__ == "__main__":
    from dnd_adventure.ui import display_start_menu
    player_name, save_file = display_start_menu()
    if player_name:
        game = Game(player_name, save_file)
        from dnd_adventure.input_handler import handle_input
        last_refresh_time = time.time()
        last_key_time = last_refresh_time
        while game.running:
            game.running, last_refresh_time, last_key_time = handle_input(game, last_refresh_time, last_key_time)