import random
import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from colorama import Fore, Style
import keyboard
from dnd_adventure.character import Character
from dnd_adventure.races import get_races
from dnd_adventure.classes import get_all_classes, get_class_by_name
from dnd_adventure.save_manager import SaveManager
from dnd_adventure.monsters import Monster
from dnd_adventure.world import World, Room, GameWorld
from dnd_adventure.quest_manager import QuestManager
from dnd_adventure.data_loader import DataLoader
from dnd_adventure.spells import Spell

logger = logging.getLogger(__name__)

def display_start_menu() -> Tuple[Optional[str], Optional[str]]:
    options = ["Start New Game", "Continue Game", "Delete Save", "Exit"]
    selected_index = 0
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== D&D Adventure Game ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        for i, option in enumerate(options):
            prefix = f"{Fore.GREEN}=> " if i == selected_index else "   "
            print(f"{prefix}{Fore.YELLOW}{option}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Use arrow keys to navigate, Enter to select.{Style.RESET_ALL}")

        event = keyboard.read_event(suppress=True)
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == "up" and selected_index > 0:
                selected_index -= 1
            elif event.name == "down" and selected_index < len(options) - 1:
                selected_index += 1
            elif event.name == "enter":
                if options[selected_index] == "Start New Game":
                    player_name = input(f"{Fore.YELLOW}Enter your character name: {Style.RESET_ALL}").strip()
                    if not player_name:
                        player_name = "Adventurer"
                    return player_name, None
                elif options[selected_index] == "Continue Game":
                    save_files = Game.list_save_files()
                    if not save_files:
                        print(f"{Fore.RED}No saved games found!{Style.RESET_ALL}")
                        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                        continue
                    selected_save = select_save_file(save_files)
                    if selected_save:
                        player_name = selected_save.replace(".save", "")
                        return player_name, os.path.join("dnd_adventure", "saves", selected_save)
                    continue
                elif options[selected_index] == "Delete Save":
                    save_files = Game.list_save_files()
                    if not save_files:
                        print(f"{Fore.RED}No saved games to delete!{Style.RESET_ALL}")
                        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                        continue
                    selected_save = select_save_file(save_files)
                    if selected_save:
                        Game.delete_save_file(selected_save)
                        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    continue
                elif options[selected_index] == "Exit":
                    return None, None

def select_save_file(save_files: List[str]) -> Optional[str]:
    selected_index = 0
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== Select Save File ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        for i, save in enumerate(save_files):
            prefix = f"{Fore.GREEN}=> " if i == selected_index else "   "
            print(f"{prefix}{Fore.YELLOW}{save}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Use arrow keys to navigate, Enter to select, Q to cancel.{Style.RESET_ALL}")

        event = keyboard.read_event(suppress=True)
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == "up" and selected_index > 0:
                selected_index -= 1
            elif event.name == "down" and selected_index < len(save_files) - 1:
                selected_index += 1
            elif event.name == "enter":
                return save_files[selected_index]
            elif event.name == "q":
                return None

class Game:
    def __init__(self, player_name: str, save_file: Optional[str] = None):
        self.player_name = player_name
        self.world = World(seed=None)
        self.game_world = GameWorld(self.world)
        self.quest_manager = QuestManager(self.world)
        self.save_manager = SaveManager()
        self.player, self.starting_room = self.initialize_player(save_file)
        self.current_room = self.starting_room
        self.player_pos = (0, 0)
        self.running = True
        self.previous_menu = None
        self.commands = [
            "north", "south", "east", "west", "look", "lore", "attack", "cast", "rest",
            "quest list", "quest start", "quest complete", "save", "quit", "exit"
        ]

    @staticmethod
    def list_save_files() -> List[str]:
        saves_dir = os.path.join("dnd_adventure", "saves")
        os.makedirs(saves_dir, exist_ok=True)
        return [f for f in os.listdir(saves_dir) if f.endswith(".save")]

    @staticmethod
    def delete_save_file(save_file: str) -> bool:
        save_path = os.path.join("dnd_adventure", "saves", save_file)
        try:
            os.remove(save_path)
            print(f"{Fore.GREEN}Deleted save file: {save_file}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}Failed to delete {save_file}: {e}{Style.RESET_ALL}")
            return False

    def initialize_player(self, save_file: Optional[str]) -> Tuple[Character, Optional[str]]:
        if save_file:
            try:
                player_data = self.save_manager.load_game(save_file)
                player = Character(**player_data)
                starting_room = player_data.get("current_room")
                self.player_pos = tuple(player_data.get("player_pos", (0, 0)))
                logger.info(f"Loaded character {self.player_name} from {save_file}.")
                return player, starting_room
            except Exception as e:
                logger.error(f"Failed to load save file {save_file}: {e}")
                print(f"{Fore.RED}Failed to load save: {e}. Starting new game.{Style.RESET_ALL}")
        player = self.create_player(self.player_name)
        starting_room = next((room_id for room_id in self.game_world.rooms if self.game_world.world.get_location(*map(int, room_id.split(',')))["type"] == "dungeon"), None)
        if starting_room:
            self.player_pos = tuple(map(int, starting_room.split(",")))
        self.display_initial_lore(player)  # Show lore for new characters
        return player, starting_room

    def display_initial_lore(self, character: Character):
        # Use hash of player_name and world.name for unique lore per save
        random.seed(hash(self.player_name + self.world.name))
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== The Prophecy of {self.world.name} ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        era = random.choice(self.world.history)
        event = random.choice(era["events"])
        prophecies = [
            f"In the {era['name']}, the seers foretold that {character.name}, a {character.race_name} {character.class_name}, would rise to reclaim {event['desc'].split('discovers the ')[-1]} and restore balance.",
            f"Legends from {event['year']} speak of {character.name}, born under the stars of {self.world.name}, destined to confront the {random.choice(['dragon', 'lich', 'demon'])} that threatens {self.world.name}.",
            f"The chronicles of {era['name']} whisper of {character.name}, a {character.class_name}, who will forge a new era by fulfilling the legacy of {event['desc'].split('is founded by ')[-1]}.",
        ]
        print(f"{Fore.LIGHTYELLOW_EX}{random.choice(prophecies)}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Your journey begins, {character.name}. The fate of {self.world.name} rests in your hands.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to embark on your adventure...{Style.RESET_ALL}")
        random.seed(None)  # Reset seed

    def create_player(self, name: str) -> Character:
        print(f"\n{Fore.CYAN}=== Creating character: {name} ==={Style.RESET_ALL}")
        selections = {}
        
        races = get_races()
        selections["race"] = self.select_race(races)
        
        selected_race = next((r for r in races if r.name == selections["race"]), None)
        if not selected_race:
            raise ValueError("Selected race not found")
        
        if selected_race.subraces:
            subrace_names = list(selected_race.subraces.keys()) + ["Base " + selections["race"]]
            selections["subrace"] = self.select_subrace(subrace_names, selected_race)
        else:
            selections["subrace"] = None
        
        classes = get_all_classes()
        selections["class"] = self.select_class(classes)
        
        selections["stats"] = self.roll_stats(selected_race, selections["subrace"], classes, selections["class"])
        
        spellcasting_classes = ["Wizard", "Sorcerer", "Cleric", "Druid", "Bard", "Paladin", "Ranger"]
        if selections["class"] in spellcasting_classes:
            selections["spells"] = self.select_spells(selections["class"])
        else:
            selections["spells"] = {0: [], 1: []}
        
        selections = self.review_selections(selections, races, classes)
        
        race = next((r for r in races if r.name == selections["race"]), None)
        if not race:
            raise ValueError("Selected race not found")
        if selections["subrace"] and selections["subrace"] != "Base " + selections["race"]:
            race.subrace = selections["subrace"]
        
        dnd_class = next((c for c in classes if c["name"] == selections["class"]), None)
        stats = selections["stats"]
        spells = selections.get("spells", {0: [], 1: []})
        
        if not race or not dnd_class:
            raise ValueError("Selected race or class not found")
        
        character = Character(
            name=name,
            race_name=selections["race"] if not selections["subrace"] or selections["subrace"] == "Base " + selections["race"] else selections["subrace"],
            class_name=selections["class"],
            stats=stats,
            known_spells=spells
        )
        race.apply_modifiers(character)
        self.display_character_sheet(character, race, dnd_class)
        return character

    def display_character_sheet(self, character: Character, race_obj: 'Race', dnd_class: Dict) -> None:
        print(f"\n{Fore.CYAN}=== Character Sheet ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Name: {Fore.WHITE}{character.name}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Health: {Fore.WHITE}{character.hit_points}/{character.max_hit_points}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Magic Points: {Fore.WHITE}{character.mp}/{character.max_mp}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Level: {Fore.WHITE}{character.level}{Style.RESET_ALL}")
        race_display = character.race_name
        print(f"{Fore.YELLOW}Race: {Fore.WHITE}{race_display}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Class: {Fore.WHITE}{character.class_name}{Style.RESET_ALL}")
        
        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        print(f"\n{Fore.YELLOW}Stats:{Style.RESET_ALL}")
        for i, stat in enumerate(character.stats):
            print(f"  {Fore.WHITE}{stat_names[i]}: {stat}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Racial Traits:{Style.RESET_ALL}")
        for trait in race_obj.racial_traits:
            print(f"  {Fore.WHITE}{trait.name}: {Fore.LIGHTYELLOW_EX}{trait.description}{Style.RESET_ALL}")
        if race_obj.subrace and race_obj.subrace in race_obj.subraces:
            subrace_traits = race_obj.subraces[race_obj.subrace].get("racial_traits", [])
            for trait in subrace_traits:
                print(f"  {Fore.WHITE}{trait['name']}: {Fore.LIGHTYELLOW_EX}{trait['description']}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Class Features:{Style.RESET_ALL}")
        for feature in dnd_class.get("features", []):
            if feature["level"] == 1:
                print(f"  {Fore.WHITE}{feature['name']}: {Fore.LIGHTYELLOW_EX}{feature['description']}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Spells:{Style.RESET_ALL}")
        if not character.known_spells or all(not spells for spells in character.known_spells.values()):
            print(f"  {Fore.WHITE}None{Style.RESET_ALL}")
        else:
            loader = DataLoader()
            spells_data = loader.load_spells_from_json()
            class_key = "Sorcerer/Wizard" if character.class_name in ["Wizard", "Sorcerer"] else character.class_name
            for level in sorted(character.known_spells.keys()):
                for spell_name in character.known_spells.get(level, []):
                    spell_obj = None
                    for spell in spells_data.get(class_key, {}).get(level, []):
                        if spell.name == spell_name:
                            spell_obj = spell
                            break
                    if spell_obj:
                        print(f"  {Fore.WHITE}Level {level} - {spell_obj.name}: {Fore.LIGHTYELLOW_EX}{spell_obj.description}{Style.RESET_ALL}")
                    else:
                        print(f"  {Fore.WHITE}Level {level} - {spell_name}: {Fore.LIGHTYELLOW_EX}(Description not found){Style.RESET_ALL}")
        
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def select_race(self, races: List) -> str:
        selected_index = 0
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}=== Select Your Race ==={Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            for i, race in enumerate(races):
                prefix = f"{Fore.GREEN}=> " if i == selected_index else "   "
                desc = race.description[:100] + "..." if len(race.description) > 100 else race.description
                print(f"{prefix}{Fore.YELLOW}{race.name}{Style.RESET_ALL}")
                print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Use arrow keys to navigate, Enter to select, Q to quit.{Style.RESET_ALL}")
            
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == "up" and selected_index > 0:
                    selected_index -= 1
                elif event.name == "down" and selected_index < len(races) - 1:
                    selected_index += 1
                elif event.name == "enter":
                    return races[selected_index].name
                elif event.name == "q":
                    exit()

    def select_subrace(self, subrace_names: List[str], race: 'Race') -> str:
        selected_index = 0
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}=== Select Subrace for {race.name} ==={Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            for i, subrace in enumerate(subrace_names):
                prefix = f"{Fore.GREEN}=> " if i == selected_index else "   "
                if subrace.startswith("Base "):
                    desc = race.description
                else:
                    desc = race.subraces[subrace]["description"]
                desc = desc[:100] + "..." if len(desc) > 100 else desc
                print(f"{prefix}{Fore.YELLOW}{subrace}{Style.RESET_ALL}")
                print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Use arrow keys to navigate, Enter to select, Q to quit.{Style.RESET_ALL}")
            
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == "up" and selected_index > 0:
                    selected_index -= 1
                elif event.name == "down" and selected_index < len(subrace_names) - 1:
                    selected_index += 1
                elif event.name == "enter":
                    return subrace_names[selected_index]
                elif event.name == "q":
                    exit()

    def select_class(self, classes: List[Dict]) -> str:
        selected_index = 0
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}=== Select Your Class ==={Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            for i, cls in enumerate(classes):
                prefix = f"{Fore.GREEN}=> " if i == selected_index else "   "
                desc = cls["description"][:100] + "..." if len(cls["description"]) > 100 else cls["description"]
                print(f"{prefix}{Fore.YELLOW}{cls['name']}{Style.RESET_ALL}")
                print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Use arrow keys to navigate, Enter to select, Q to quit.{Style.RESET_ALL}")
            
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == "up" and selected_index > 0:
                    selected_index -= 1
                elif event.name == "down" and selected_index < len(classes) - 1:
                    selected_index += 1
                elif event.name == "enter":
                    return classes[selected_index]["name"]
                elif event.name == "q":
                    exit()

    def roll_stats(self, race: 'Race', subrace: Optional[str], classes: List[Dict], class_name: str) -> List[int]:
        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        stats = []
        print(f"\n{Fore.CYAN}=== Rolling Stats (4d6, drop lowest) ==={Style.RESET_ALL}")
        for i in range(6):
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.remove(min(rolls))
            stat = sum(rolls)
            stats.append(stat)
            print(f"{stat_names[i]}: {stat}")
        
        print(f"\n{Fore.YELLOW}=== Applying Bonuses ==={Style.RESET_ALL}")
        racial_mods = race.ability_modifiers
        if racial_mods:
            print(f"{Fore.YELLOW}Racial Bonuses ({race.name}):{Style.RESET_ALL}")
            for stat, mod in racial_mods.items():
                print(f"  {stat}: {'+' if mod >= 0 else ''}{mod}")
        else:
            print(f"{Fore.YELLOW}Racial Bonuses ({race.name}): None{Style.RESET_ALL}")
        
        subrace_mods = {}
        if subrace and subrace != "Base " + race.name and race.subraces and subrace in race.subraces:
            subrace_mods = race.subraces[subrace].get("ability_modifiers", {})
            if subrace_mods:
                print(f"{Fore.YELLOW}Subrace Bonuses ({subrace}):{Style.RESET_ALL}")
                for stat, mod in subrace_mods.items():
                    print(f"  {stat}: {'+' if mod >= 0 else ''}{mod}")
            else:
                print(f"{Fore.YELLOW}Subrace Bonuses ({subrace}): None{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Subrace Bonuses: None{Style.RESET_ALL}")
        
        dnd_class = next((c for c in classes if c["name"] == class_name), None)
        if dnd_class:
            print(f"{Fore.YELLOW}Class Bonuses ({class_name}):{Style.RESET_ALL}")
            print(f"  Class Skills: {', '.join(dnd_class['class_skills'])}")
            if dnd_class["features"]:
                print(f"  Features at Level 1:")
                for feature in dnd_class["features"]:
                    if feature["level"] == 1:
                        print(f"    - {feature['name']}: {feature['description']}")
        else:
            print(f"{Fore.YELLOW}Class Bonuses: None{Style.RESET_ALL}")
        
        stat_indices = {name: i for i, name in enumerate(stat_names)}
        modified_stats = stats.copy()
        for stat, mod in racial_mods.items():
            if stat in stat_indices:
                modified_stats[stat_indices[stat]] += mod
        for stat, mod in subrace_mods.items():
            if stat in stat_indices:
                modified_stats[stat_indices[stat]] += mod
        
        print(f"\n{Fore.GREEN}=== Final Stats ==={Style.RESET_ALL}")
        for i, stat in enumerate(modified_stats):
            print(f"{stat_names[i]}: {stat}")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return modified_stats

    def select_spells(self, class_name: str) -> Dict[int, List[str]]:
        spells = {0: [], 1: []}
        available_spells = self.get_available_spells(class_name)
        max_spells = 4 if class_name in ["Wizard", "Sorcerer"] else 3
        
        for level in [0, 1]:
            if level in available_spells and available_spells[level]:
                print(f"\n{Fore.CYAN}=== Select up to {max_spells} Level {level} Spells for {class_name} ==={Style.RESET_ALL}")
                selected_index = 0
                selected_spells = []
                while len(selected_spells) < max_spells and available_spells[level]:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"{Fore.CYAN}Level {level} Spells (Selected {len(selected_spells)}/{max_spells}){Style.RESET_ALL}")
                    print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
                    for i, spell in enumerate(available_spells[level]):
                        prefix = f"{Fore.GREEN}=> " if i == selected_index else "   "
                        status = " [Selected]" if spell in selected_spells else ""
                        print(f"{prefix}{Fore.YELLOW}{spell}{status}{Style.RESET_ALL}")
                    print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
                    print(f"\n{Fore.CYAN}Use arrow keys to navigate, Enter to select/deselect, Q to finish.{Style.RESET_ALL}")
                    
                    event = keyboard.read_event(suppress=True)
                    if event.event_type == keyboard.KEY_DOWN:
                        if event.name == "up" and selected_index > 0:
                            selected_index -= 1
                        elif event.name == "down" and selected_index < len(available_spells[level]) - 1:
                            selected_index += 1
                        elif event.name == "enter":
                            spell = available_spells[level][selected_index]
                            if spell in selected_spells:
                                selected_spells.remove(spell)
                            else:
                                selected_spells.append(spell)
                        elif event.name == "q":
                            break
                spells[level] = selected_spells
        return spells

    def get_available_spells(self, class_name: str) -> Dict[int, List[str]]:
        loader = DataLoader()
        spells_data = loader.load_spells_from_json()
        class_key = "Sorcerer/Wizard" if class_name in ["Wizard", "Sorcerer"] else class_name
        return {level: [spell.name for spell in spells] for level, spells in spells_data.get(class_key, {}).items() if level in [0, 1]}

    def review_selections(self, selections: Dict, races: List, classes: List[Dict]) -> Dict:
        selections = selections or {"race": None, "subrace": None, "class": None, "stats": [], "spells": {0: [], 1: []}}
        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}=== Review Your Selections ==={Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            
            race_display = selections["race"] if not selections["subrace"] or selections["subrace"] == "Base " + selections["race"] else f"{selections['race']} ({selections['subrace']})"
            race_obj = next((r for r in races if r.name == selections["race"]), None)
            race_desc = race_obj.description if race_obj else "Not selected"
            race_desc = race_desc[:100] + "..." if len(race_desc) > 100 else race_desc
            print(f"{Fore.YELLOW}Race: {race_display or 'Not selected'}{Style.RESET_ALL}")
            print(f"  {Fore.LIGHTYELLOW_EX}{race_desc}{Style.RESET_ALL}")
            if race_obj and selections["subrace"] and selections["subrace"] != "Base " + selections["race"]:
                subrace_desc = race_obj.subraces[selections["subrace"]]["description"]
                subrace_desc = subrace_desc[:100] + "..." if len(subrace_desc) > 100 else subrace_desc
                print(f"  {Fore.LIGHTYELLOW_EX}Subrace: {subrace_desc}{Style.RESET_ALL}")
            
            class_obj = next((c for c in classes if c["name"] == selections["class"]), None)
            class_desc = class_obj["description"] if class_obj else "Not selected"
            class_desc = class_desc[:100] + "..." if len(class_desc) > 100 else class_desc
            print(f"\n{Fore.YELLOW}Class: {selections['class'] or 'Not selected'}{Style.RESET_ALL}")
            print(f"  {Fore.LIGHTYELLOW_EX}{class_desc}{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}Stats:{Style.RESET_ALL}")
            for i, stat in enumerate(selections["stats"]):
                print(f"  {stat_names[i]}: {stat}")
            
            spells_display = "None"
            if selections["spells"] and any(selections["spells"].values()):
                spells_display = ", ".join([f"Level {k}: {', '.join(v)}" for k, v in selections["spells"].items() if v])
            print(f"\n{Fore.YELLOW}Spells: {spells_display}{Style.RESET_ALL}")
            
            print(f"\n{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Options:{Style.RESET_ALL}")
            options = ["Change race", "Change class", "Reroll stats", "Change spells", "Confirm selections"]
            selected_index = 0
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{Fore.CYAN}=== Review Your Selections ==={Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Race: {race_display or 'Not selected'}{Style.RESET_ALL}")
                print(f"  {Fore.LIGHTYELLOW_EX}{race_desc}{Style.RESET_ALL}")
                if race_obj and selections["subrace"] and selections["subrace"] != "Base " + selections["race"]:
                    print(f"  {Fore.LIGHTYELLOW_EX}Subrace: {subrace_desc}{Style.RESET_ALL}")
                print(f"\n{Fore.YELLOW}Class: {selections['class'] or 'Not selected'}{Style.RESET_ALL}")
                print(f"  {Fore.LIGHTYELLOW_EX}{class_desc}{Style.RESET_ALL}")
                print(f"\n{Fore.YELLOW}Stats:{Style.RESET_ALL}")
                for i, stat in enumerate(selections["stats"]):
                    print(f"  {stat_names[i]}: {stat}")
                print(f"\n{Fore.YELLOW}Spells: {spells_display}{Style.RESET_ALL}")
                print(f"\n{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Options:{Style.RESET_ALL}")
                for i, option in enumerate(options):
                    prefix = f"{Fore.GREEN}=> " if i == selected_index else "   "
                    print(f"{prefix}{Fore.YELLOW}{option}{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}Use arrow keys to navigate, Enter to select.{Style.RESET_ALL}")
                
                event = keyboard.read_event(suppress=True)
                if event.event_type == keyboard.KEY_DOWN:
                    if event.name == "up" and selected_index > 0:
                        selected_index -= 1
                    elif event.name == "down" and selected_index < len(options) - 1:
                        selected_index += 1
                    elif event.name == "enter":
                        break
            
            if selected_index == 0:
                selections["race"] = self.select_race(races)
                selected_race = next((r for r in races if r.name == selections["race"]), None)
                if selected_race and selected_race.subraces:
                    subrace_names = list(selected_race.subraces.keys()) + ["Base " + selections["race"]]
                    selections["subrace"] = self.select_subrace(subrace_names, selected_race)
                else:
                    selections["subrace"] = None
            elif selected_index == 1:
                selections["class"] = self.select_class(classes)
            elif selected_index == 2:
                selected_race = next((r for r in races if r.name == selections["race"]), None)
                if selected_race:
                    selections["stats"] = self.roll_stats(selected_race, selections["subrace"], classes, selections["class"])
            elif selected_index == 3:
                spellcasting_classes = ["Wizard", "Sorcerer", "Cleric", "Druid", "Bard", "Paladin", "Ranger"]
                if selections["class"] in spellcasting_classes:
                    selections["spells"] = self.select_spells(selections["class"])
                else:
                    selections["spells"] = {0: [], 1: []}
            elif selected_index == 4:
                return selections

    def print_location(self):
        tile = self.world.get_location(*self.player_pos)
        print(f"\n{Fore.CYAN}You are in {tile['name']} ({tile['type'].capitalize()}){Style.RESET_ALL}")
        print(self.world.display_map(self.player_pos))
        if self.current_room:
            room = self.game_world.rooms.get(self.current_room)
            room.visited = True
            print(f"\n{room.description}")
            exits = ", ".join(room.exits.keys())
            print(f"Exits: {exits if exits else 'None'}")
            if room.monsters:
                print(f"Monsters: {', '.join(m.name for m in room.monsters)}")
            if room.items:
                print(f"Items: {', '.join(room.items)}")

    def handle_command(self, cmd: str):
        cmd = cmd.lower().strip()
        if cmd in ["north", "south", "east", "west"]:
            self.handle_movement(cmd)
        elif cmd == "look":
            self.print_location()
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
                print("Invalid quest ID.")
        elif cmd == "quest complete":
            for quest in self.quest_manager.active_quests:
                self.quest_manager.complete_quest(quest["id"], self.player, self.player_pos, self.current_room)
        elif cmd == "save":
            self.save_game()
        elif cmd in ["quit", "exit"]:
            self.running = False
        else:
            print("Unknown command. Try: north, south, east, west, look, lore, attack, cast, rest, quest list, quest start <id>, quest complete, save, quit")

    def handle_movement(self, direction: str):
        if self.current_room:
            room = self.game_world.rooms.get(self.current_room)
            if direction in room.exits:
                self.current_room = room.exits[direction]
                self.player_pos = tuple(map(int, self.current_room.split(",")))
                self.print_location()
            else:
                print("You can't go that way!")
        else:
            dx, dy = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[direction]
            new_x, new_y = self.player_pos[0] + dx, self.player_pos[1] + dy
            if 0 <= new_y < self.world.map["height"] and 0 <= new_x < self.world.map["width"]:
                tile = self.world.get_location(new_x, new_y)
                if tile["type"] == "mountain":
                    print("The mountains are too steep to climb!")
                elif tile["type"] == "river":
                    print("You need a boat to cross the river!")
                elif tile["type"] == "lake":
                    print("You need a boat to cross the lake!")
                else:
                    self.player_pos = (new_x, new_y)
                    self.current_room = f"{new_x},{new_y}" if tile["type"] in ["dungeon", "castle"] else None
                    self.print_location()
                    if tile["type"] in ["plains", "forest"] and not self.current_room and random.random() < 0.1:
                        print(f"{Fore.RED}A wild Goblin ambushes you!{Style.RESET_ALL}")
                        temp_room_id = f"temp_{new_x},{new_y}"
                        self.game_world.rooms[temp_room_id] = Room(
                            description="A sudden encounter in the wild!",
                            exits={},
                            monsters=[Monster("Goblin", 6, [{"attack_bonus": 3, "damage": "1d4+1"}])]
                        )
                        self.current_room = temp_room_id
                        self.print_location()
            else:
                print("You can't go that way!")

    def handle_attack_command(self):
        if not self.current_room:
            print("There's nothing to attack here!")
            return
        room = self.game_world.rooms.get(self.current_room)
        if not room.monsters:
            print("No monsters to attack!")
            return
        monster = room.monsters[0]
        bab = self.player.bab
        str_mod = self.player.get_stat_modifier(0)
        attack_roll = random.randint(1, 20) + bab + str_mod
        print(f"{self.player.name} attacks {monster.name} (Roll: {attack_roll})")
        if attack_roll >= monster.armor_class:
            damage = max(1, random.randint(1, 8) + str_mod)
            monster.hit_points -= damage
            print(f"Hit! {monster.name} takes {damage} damage (HP: {monster.hit_points})")
            if monster.hit_points <= 0:
                print(f"{monster.name} is defeated!")
                room.monsters.remove(monster)
                self.player.gain_xp(50)
                if "temp_" in self.current_room:
                    del self.game_world.rooms[self.current_room]
                    self.current_room = None
        else:
            print("Miss!")
        if room.monsters:
            self.handle_monster_attack(monster)

    def handle_monster_attack(self, monster: Monster):
        if not monster.attacks:
            print(f"{monster.name} has no attacks!")
            return
        attack = random.choice(monster.attacks)
        attack_roll = random.randint(1, 20) + attack.attack_bonus
        print(f"{monster.name} attacks {self.player.name} with {attack.name} (Roll: {attack_roll})")
        if attack_roll >= self.player.armor_class:
            damage_parts = attack.damage.split('+')
            dice_part = damage_parts[0]
            bonus = int(damage_parts[1]) if len(damage_parts) > 1 else 0
            num_dice, die_size = map(int, dice_part.split('d'))
            damage = sum(random.randint(1, die_size) for _ in range(num_dice)) + bonus
            damage = max(1, damage)
            self.player.hit_points -= damage
            print(f"Hit! {self.player.name} takes {damage} damage (HP: {self.player.hit_points})")
            if self.player.hit_points <= 0:
                print(f"{self.player.name} has been defeated!")
                self.running = False
        else:
            print("Miss!")

    def handle_cast_command(self, cmd: str):
        if not self.current_room:
            print("There's nothing to cast spells on here!")
            return
        room = self.game_world.rooms.get(self.current_room)
        if not room.monsters:
            print("No monsters to cast spells on!")
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
                if "dealing" in result and room.monsters and room.monsters[0].hit_points <= 0:
                    print(f"{room.monsters[0].name} is defeated!")
                    room.monsters.pop(0)
                    self.player.gain_xp(50)
                    if "temp_" in self.current_room:
                        del self.game_world.rooms[self.current_room]
                        self.current_room = None
                if room.monsters:
                    self.handle_monster_attack(room.monsters[0])
            else:
                print("Invalid spell number!")
        except (ValueError, IndexError):
            print("Invalid cast command. Use 'cast <number>' or 'cast list'.")

    def print_spell_list(self):
        if not self.player.known_spells or all(len(spells) == 0 for spells in self.player.known_spells.values()):
            print("You don't know any spells!")
            return
        print("\nKnown Spells:")
        spell_index = 1
        for level in sorted(self.player.known_spells.keys()):
            for spell in self.player.known_spells[level]:
                print(f"{spell_index}. Level {level}: {spell}")
                spell_index += 1

    def handle_rest_command(self):
        self.player.hit_points = min(self.player.hit_points + 10, self.player.max_hit_points)
        self.player.mp = min(self.player.mp + 5, self.player.max_mp)
        print(f"{self.player.name} rests, recovering to {self.player.hit_points} HP and {self.player.mp} MP.")

    def print_lore(self):
        print(f"\n{Fore.YELLOW}History of {self.world.name}:{Style.RESET_ALL}")
        for era in self.world.history:
            print(f"\n{Fore.LIGHTYELLOW_EX}{era['name']}:{Style.RESET_ALL}")
            for event in era["events"]:
                print(f"  {Fore.LIGHTBLACK_EX}{event['year']}{Style.RESET_ALL}: {event['desc']}")

    def save_game(self):
        save_data = {
            "name": self.player.name,
            "race_name": self.player.race_name,
            "class_name": self.player.class_name,
            "level": self.player.level,
            "xp": self.player.xp,
            "stats": self.player.stats,
            "skills": self.player.skills,
            "feats": self.player.feats,
            "equipment": self.player.equipment,
            "hit_points": self.player.hit_points,
            "armor_class": self.player.armor_class,
            "known_spells": self.player.known_spells,
            "mp": self.player.mp,
            "max_mp": self.player.max_mp,
            "current_room": self.current_room,
            "player_pos": list(self.player_pos)
        }
        save_file = os.path.join("dnd_adventure", "saves", f"{self.player_name}.save")
        self.save_manager.save_game(save_data, save_file)
        print(f"Game saved for {self.player_name}.")

def main():
    import colorama
    colorama.init()
    player_name, save_file = display_start_menu()
    if not player_name:
        print(f"{Fore.CYAN}Exiting game. Farewell!{Style.RESET_ALL}")
        return
    
    game = Game(player_name, save_file)
    print(f"\n{Fore.CYAN}Type 'help' for commands or start exploring!{Style.RESET_ALL}")
    game.print_location()
    
    command = ""
    while game.running:
        event = keyboard.read_event(suppress=True)
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == "enter":
                if command:
                    game.handle_command(command)
                    command = ""
            elif event.name == "backspace":
                command = command[:-1]
                os.system('cls' if os.name == 'nt' else 'clear')
                game.print_location()
                print(f"> {command}", end="", flush=True)
            elif event.name.isalnum() or event.name in ["space", "-", "_"]:
                command += event.name
                os.system('cls' if os.name == 'nt' else 'clear')
                game.print_location()
                print(f"> {command}", end="", flush=True)

if __name__ == "__main__":
    main()