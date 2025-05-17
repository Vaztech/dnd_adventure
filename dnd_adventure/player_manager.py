import json
import logging
import os
import random
from typing import Optional, Tuple, Any, Dict, List
from colorama import Fore, Style

from dnd_adventure.player import Player

logger = logging.getLogger(__name__)

class PlayerManager:
    def __init__(self):
        self.races: List[Dict[str, Any]] = []
        races_path = os.path.join(os.path.dirname(__file__), "data", "races.json")
        logger.debug(f"Loading races from {races_path}...")
        try:
            with open(races_path, "r") as f:
                self.races = json.load(f)
            logger.debug(f"Loaded races: {self.races}")
        except FileNotFoundError:
            logger.error(f"Races file not found at {races_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding races.json: {e}")

    def initialize_player(self, game: Any, save_file: Optional[str] = None) -> Tuple[Optional[Player], Optional[str]]:
        logger.debug(f"Initializing player, save_file={save_file}")
        if save_file:
            try:
                player_data = game.save_manager.load_game(save_file)
                if player_data:
                    player = Player(
                        name=player_data["name"],
                        race=player_data["race"],
                        subrace=player_data["subrace"],
                        character_class=player_data["class"],
                        stats=player_data["stats"],
                        spells=player_data.get("spells", {0: [], 1: []}),
                        level=player_data.get("level", 1),
                        features=player_data.get("features", []),
                    )
                    starting_room = player_data.get("current_room")
                    logger.debug(f"Loaded player: {player_data['name']}, room: {starting_room}")
                    return player, starting_room
            except Exception as e:
                logger.error(f"Failed to load save file {save_file}: {e}")
                try:
                    print(f"{Fore.RED}Failed to load save file. Starting new character.{Style.RESET_ALL}")
                except OSError as e:
                    logger.error(f"Console output error: {e}")
                    print("Failed to load save file. Starting new character.")
        
        logger.debug("Creating new player")
        try:
            print(f"{Fore.CYAN}Creating new character...{Style.RESET_ALL}")
        except OSError as e:
            logger.error(f"Console output error: {e}")
            print("Creating new character...")
        player_data = self._create_character(game)
        if not player_data:
            logger.error("Character creation failed")
            return None, None
        
        player = Player(
            name=game.player_name,
            race=player_data["race"],
            subrace=player_data["subrace"],
            character_class=player_data["class"],
            stats=player_data["stat_dict"],
            spells=player_data["spells"],
            level=player_data.get("level", 1),
            features=player_data["features"],
        )
        starting_room = self.find_starting_position(game)
        logger.debug("Player initialization complete")
        logger.info(
            f"Character created: {player.name}, {player.race}, {player.subrace}, {player.character_class}, level {player.level}"
        )
        return player, f"{starting_room[0]},{starting_room[1]}"

    def _create_character(self, game: Any) -> Optional[Dict[str, Any]]:
        """Create a character with the locked-in summary format:
        Name, Level, Race, Racial Stat Bonus, HP, MP, Attack Bonus, AC, Class,
        Rolling Stats, Applying Bonuses, Available Subclasses, Final Stats, Spells, Confirm Character."""
        logger.debug("Starting character creation")
        race = None
        subrace = None
        character_class = None
        stats = None
        stat_dict = None
        spells = {0: [], 1: []}
        features = []
        level = 1  # Locked to 1 for new characters

        while True:
            if not race:
                race = self._select_race()
                if not race:
                    logger.debug("Character creation cancelled during race selection")
                    return None
                subrace = self._select_subrace(race)
            
            if not character_class:
                character_class = self._select_class(game)
                if not character_class:
                    logger.debug("Character creation cancelled during class selection")
                    return None
            
            if not stats:
                stats = self._roll_stats()
            
            # Get race and subrace data
            race_dict = next((r for r in self.races if r["name"].lower() == race.lower()), {})
            subrace_dict = race_dict.get("subraces", {}).get(subrace, {}) if subrace else {}
            race_modifiers = race_dict.get("ability_modifiers", {})
            subrace_modifiers = subrace_dict.get("ability_modifiers", {})
            
            # Combine racial modifiers for Racial Stat Bonus
            combined_modifiers = {}
            for stat, value in race_modifiers.items():
                combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
            for stat, value in subrace_modifiers.items():
                combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
            
            # Apply modifiers
            stat_dict = {
                "Strength": stats[0],
                "Dexterity": stats[1],
                "Constitution": stats[2],
                "Intelligence": stats[3],
                "Wisdom": stats[4],
                "Charisma": stats[5],
            }
            for stat, value in combined_modifiers.items():
                stat_dict[stat] = stat_dict.get(stat, 10) + value
            final_stats = [
                stat_dict["Strength"], stat_dict["Dexterity"], stat_dict["Constitution"],
                stat_dict["Intelligence"], stat_dict["Wisdom"], stat_dict["Charisma"]
            ]
            
            # Get class data
            class_data = game.classes.get(character_class, {})
            
            # Select spells for spellcasting classes
            spells = {0: [], 1: []}  # Reset spells
            if class_data.get("spellcasting"):
                spells = self._select_spells(game, character_class)
            
            if not features:
                features = self._get_class_features(game, character_class)
            
            # Calculate HP, MP, Attack, Defense
            max_hp = self._calculate_hp(class_data, stat_dict)
            current_hp = max_hp
            max_mp = self._calculate_mp(class_data, stat_dict)
            current_mp = max_mp
            attack = self._calculate_attack(class_data, stat_dict)
            defense = self._calculate_defense(stat_dict)
            
            # Determine subclass
            subclass = self._get_subclass(class_data, stat_dict, level=level)
            
            # Display character summary
            try:
                print(f"{Fore.CYAN}=== Character Summary ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}Name: {game.player_name}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Level: {level}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Race: {race} ({subrace or 'None'}){Style.RESET_ALL}")
                print(f"{Fore.CYAN}Racial Stat Bonus: {self._format_modifiers(combined_modifiers) or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}HP: {current_hp}/{max_hp}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}MP: {current_mp}/{max_mp}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Attack Bonus: {attack}  # Added to your d20 roll when attacking to hit enemies{Style.RESET_ALL}")
                print(f"{Fore.CYAN}AC: {defense}  # Armor Class; enemies must roll this or higher to hit you{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Class: {character_class} ({subclass or 'None'}){Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}=== Rolling Stats (4d6, drop lowest) ==={Style.RESET_ALL}")
                for stat, value in zip(stat_dict.keys(), stats):
                    print(f"{Fore.CYAN}{stat}: {value}{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}=== Applying Bonuses ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}Racial Bonuses ({race}):{Style.RESET_ALL}")
                race_modifier_str = self._format_modifiers(race_modifiers)
                print(f"{Fore.CYAN}  {race_modifier_str or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Subrace Bonuses ({subrace or 'None'}):{Style.RESET_ALL}")
                subrace_modifier_str = self._format_modifiers(subrace_modifiers)
                print(f"{Fore.CYAN}  {subrace_modifier_str or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Class Bonuses ({character_class}):{Style.RESET_ALL}")
                print(f"{Fore.CYAN}  Class Skills: {', '.join(class_data.get('class_skills', [])) or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}  Features:{Style.RESET_ALL}")
                for feature in features:
                    feature_desc = next((f['description'] for f in class_data.get('features', []) if f['name'] == feature), '')
                    print(f"{Fore.CYAN}    - {feature}: {feature_desc}{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}Available Subclasses at Level 1:{Style.RESET_ALL}")
                subclasses = class_data.get('subclasses', {})
                if subclasses:
                    for subclass_name, data in subclasses.items():
                        prereqs = data.get('prerequisites', {})
                        level_req = prereqs.get('level', 1)
                        stat_reqs = prereqs.get('stats', {})
                        meets_stats = all(stat_dict.get(stat, 10) >= value for stat, value in stat_reqs.items())
                        status = "Unlocked" if level_req == 1 and meets_stats else "Locked"
                        print(f"{Fore.CYAN}  {subclass_name} ({status}): {data.get('description', '')}{Style.RESET_ALL}")
                        if status == "Locked":
                            print(f"{Fore.CYAN}    Requirements:{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}      - Level: {level_req}{Style.RESET_ALL}")
                            for stat, value in stat_reqs.items():
                                print(f"{Fore.CYAN}      - {stat}: {value}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}  None{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}=== Final Stats ==={Style.RESET_ALL}")
                for stat, value in stat_dict.items():
                    print(f"{Fore.CYAN}{stat}: {value}{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}=== Spells ==={Style.RESET_ALL}")
                if spells[0] or spells[1]:
                    print(f"{Fore.CYAN}Level 0: {', '.join(spells[0]) or 'None'}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Level 1: {', '.join(spells[1]) or 'None'}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}None{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print("=== Character Summary ===")
                print(f"Name: {game.player_name}")
                print(f"Level: {level}")
                print(f"Race: {race} ({subrace or 'None'})")
                print(f"Racial Stat Bonus: {self._format_modifiers(combined_modifiers) or 'None'}")
                print(f"HP: {current_hp}/{max_hp}")
                print(f"MP: {current_mp}/{max_mp}")
                print(f"Attack Bonus: {attack}  # Added to your d20 roll when attacking to hit enemies")
                print(f"AC: {defense}  # Armor Class; enemies must roll this or higher to hit you")
                print(f"Class: {character_class} ({subclass or 'None'})")
                print("\n=== Rolling Stats (4d6, drop lowest) ===")
                for stat, value in zip(stat_dict.keys(), stats):
                    print(f"{stat}: {value}")
                print("\n=== Applying Bonuses ===")
                print(f"Racial Bonuses ({race}):")
                race_modifier_str = self._format_modifiers(race_modifiers)
                print(f"  {race_modifier_str or 'None'}")
                print(f"Subrace Bonuses ({subrace or 'None'}):")
                subrace_modifier_str = self._format_modifiers(subrace_modifiers)
                print(f"  {subrace_modifier_str or 'None'}")
                print(f"Class Bonuses ({character_class}):")
                print(f"  Class Skills: {', '.join(class_data.get('class_skills', [])) or 'None'}")
                print(f"  Features:")
                for feature in features:
                    feature_desc = next((f['description'] for f in class_data.get('features', []) if f['name'] == feature), '')
                    print(f"    - {feature}: {feature_desc}")
                print("\nAvailable Subclasses at Level 1:")
                if subclasses:
                    for subclass_name, data in subclasses.items():
                        prereqs = data.get('prerequisites', {})
                        level_req = prereqs.get('level', 1)
                        stat_reqs = prereqs.get('stats', {})
                        meets_stats = all(stat_dict.get(stat, 10) >= value for stat, value in stat_reqs.items())
                        status = "Unlocked" if level_req == 1 and meets_stats else "Locked"
                        print(f"  {subclass_name} ({status}): {data.get('description', '')}")
                        if status == "Locked":
                            print(f"    Requirements:")
                            print(f"      - Level: {level_req}")
                            for stat, value in stat_reqs.items():
                                print(f"      - {stat}: {value}")
                else:
                    print(f"  None")
                print("\n=== Final Stats ===")
                for stat, value in stat_dict.items():
                    print(f"{stat}: {value}")
                print("\n=== Spells ===")
                if spells[0] or spells[1]:
                    print(f"Level 0: {', '.join(spells[0]) or 'None'}")
                    print(f"Level 1: {', '.join(spells[1]) or 'None'}")
                else:
                    print(f"None")
            
            # Display confirmation menu
            try:
                print(f"\n{Fore.CYAN}=== Confirm Character ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}1. Change Race{Style.RESET_ALL}")
                print(f"{Fore.CYAN}2. Change Class{Style.RESET_ALL}")
                print(f"{Fore.CYAN}3. Change Spells{Style.RESET_ALL}")
                print(f"{Fore.CYAN}4. Reroll Stats{Style.RESET_ALL}")
                print(f"{Fore.CYAN}5. Confirm Character{Style.RESET_ALL}")
                choice = input(f"{Fore.YELLOW}Select an option (1-5): {Style.RESET_ALL}").strip().lower()
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print("\n=== Confirm Character ===")
                print("1. Change Race")
                print("2. Change Class")
                print("3. Change Spells")
                print("4. Reroll Stats")
                print("5. Confirm Character")
                choice = input("Select an option (1-5): ").strip().lower()
            
            logger.debug(f"Confirmation menu choice: {choice}")
            if choice == '1':
                race = None
                subrace = None
                spells = {0: [], 1: []}
                continue
            elif choice == '2':
                character_class = None
                spells = {0: [], 1: []}
                features = []
                continue
            elif choice == '3':
                if class_data.get("spellcasting"):
                    spells = self._select_spells(game, character_class)
                else:
                    try:
                        print(f"{Fore.RED}This class cannot cast spells.{Style.RESET_ALL}")
                    except OSError as e:
                        logger.error(f"Console output error: {e}")
                        print("This class cannot cast spells.")
                continue
            elif choice == '4':
                stats = None
                continue
            elif choice == '5':
                logger.debug(
                    f"Character confirmed: {{'race': '{race}', 'subrace': '{subrace}', 'class': '{character_class}', "
                    f"'stats': {stats}, 'final_stats': {final_stats}, 'spells': {spells}, 'features': {features}, 'level': {level}}}"
                )
                return {
                    "race": race,
                    "subrace": subrace,
                    "class": character_class,
                    "stats": final_stats,
                    "stat_dict": stat_dict,
                    "spells": spells,
                    "features": features,
                    "level": level,
                }
            else:
                try:
                    print(f"{Fore.RED}Invalid choice. Please select 1-5.{Style.RESET_ALL}")
                except OSError as e:
                    logger.error(f"Console output error: {e}")
                    print("Invalid choice. Please select 1-5.")

    def _calculate_hp(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        """Calculate max HP based on class hit die and Constitution modifier."""
        hit_die = class_data.get("hit_die", 6)  # Default to d6
        con_modifier = (stat_dict.get("Constitution", 10) - 10) // 2
        max_hp = hit_die + con_modifier  # Max hit die at level 1
        return max(max_hp, 1)  # Ensure at least 1 HP

    def _calculate_mp(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        """Calculate max MP for spellcasting classes."""
        if not class_data.get("spellcasting"):
            return 0
        primary_stat = class_data.get("spellcasting_stat", "Intelligence")
        stat_modifier = (stat_dict.get(primary_stat, 10) - 10) // 2
        return max(2 + stat_modifier, 0)  # Base 2 MP + modifier

    def _calculate_attack(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        """Calculate attack bonus based on BAB and Dexterity/Strength."""
        bab = 0
        if class_data.get("bab_progression") == "fast":
            bab = 1
        elif class_data.get("bab_progression") == "medium":
            bab = 0
        dex_modifier = (stat_dict.get("Dexterity", 10) - 10) // 2
        str_modifier = (stat_dict.get("Strength", 10) - 10) // 2
        # Use higher of DEX or STR (DEX for ranged, STR for melee)
        return bab + max(dex_modifier, str_modifier)

    def _calculate_defense(self, stat_dict: Dict[str, int]) -> int:
        """Calculate Armor Class based on Dexterity."""
        dex_modifier = (stat_dict.get("Dexterity", 10) - 10) // 2
        return 10 + dex_modifier  # Base AC 10 + DEX

    def _get_subclass(self, class_data: Dict[str, Any], stat_dict: Dict[str, int], level: int = 1) -> Optional[str]:
        """Determine if a subclass is available at the current level."""
        subclasses = class_data.get("subclasses", {})
        for subclass, data in subclasses.items():
            prereqs = data.get("prerequisites", {})
            level_req = prereqs.get("level", 1)
            stat_reqs = prereqs.get("stats", {})
            meets_stats = all(stat_dict.get(stat, 10) >= value for stat, value in stat_reqs.items())
            if level >= level_req and meets_stats:
                return subclass
        return None

    def _format_modifiers(self, modifiers: Dict[str, int]) -> str:
        return ", ".join(f"{k}: {'+' if v > 0 else ''}{v}" for k, v in modifiers.items()) if modifiers else ""

    def _select_race(self) -> Optional[str]:
        while True:
            try:
                print(f"{Fore.CYAN}=== Select Your Race ==={Style.RESET_ALL}")
                for i, race in enumerate(self.races, 1):
                    print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{i}. {race['name']}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {race['description']}{Style.RESET_ALL}")
                    modifiers = race.get("ability_modifiers", {})
                    modifier_str = self._format_modifiers(modifiers)
                    print(f"{Fore.CYAN}     Stat Modifiers: {modifier_str or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                selection = input(f"{Fore.YELLOW}Select race (number or name): {Style.RESET_ALL}").strip()
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print("=== Select Your Race ===")
                for i, race in enumerate(self.races, 1):
                    print("----------------------------------------")
                    print(f"{i}. {race['name']}")
                    print(f"     {race['description']}")
                    modifiers = race.get("ability_modifiers", {})
                    modifier_str = self._format_modifiers(modifiers)
                    print(f"     Stat Modifiers: {modifier_str or 'None'}")
                print("----------------------------------------")
                selection = input("Select race (number or name): ").strip()
            
            logger.debug(f"Selected race: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(self.races):
                    return self.races[index]["name"]
            else:
                selection = selection.capitalize()
                for race_dict in self.races:
                    if race_dict["name"].lower() == selection.lower():
                        return race_dict["name"]
            
            try:
                print(f"{Fore.RED}Invalid race selected. Please enter a number (1-{len(self.races)}) or race name.{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"Invalid race selected. Please enter a number (1-{len(self.races)}) or race name.")

    def _select_subrace(self, race: str) -> Optional[str]:
        race_dict = next((r for r in self.races if r["name"].lower() == race.lower()), None)
        subraces = race_dict.get("subraces", {}) if race_dict else {}
        if not subraces:
            return None
        
        while True:
            try:
                print(f"{Fore.CYAN}=== Select Your Subrace ==={Style.RESET_ALL}")
                subrace_list = list(subraces.items())
                for i, (subrace_name, subrace_data) in enumerate(subrace_list, 1):
                    print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{i}. {subrace_name}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {subrace_data.get('description', '')}{Style.RESET_ALL}")
                    modifiers = subrace_data.get("ability_modifiers", {})
                    modifier_str = self._format_modifiers(modifiers)
                    print(f"{Fore.CYAN}     Stat Modifiers: {modifier_str or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                selection = input(f"{Fore.YELLOW}Select subrace (number or name): {Style.RESET_ALL}").strip()
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print("=== Select Your Subrace ===")
                subrace_list = list(subraces.items())
                for i, (subrace_name, subrace_data) in enumerate(subrace_list, 1):
                    print("----------------------------------------")
                    print(f"{i}. {subrace_name}")
                    print(f"     {subrace_data.get('description', '')}")
                    modifiers = subrace_data.get("ability_modifiers", {})
                    modifier_str = self._format_modifiers(modifiers)
                    print(f"     Stat Modifiers: {modifier_str or 'None'}")
                print("----------------------------------------")
                selection = input("Select subrace (number or name): ").strip()
            
            logger.debug(f"Selected subrace: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(subrace_list):
                    return subrace_list[index][0]
            else:
                selection = selection.capitalize()
                if selection in subraces:
                    return selection
            
            try:
                print(f"{Fore.RED}Invalid subrace selected. Please enter a number (1-{len(subrace_list)}) or subrace name.{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"Invalid subrace selected. Please enter a number (1-{len(subrace_list)}) or subrace name.")

    def _select_class(self, game: Any) -> Optional[str]:
        logger.debug("Starting class selection")
        classes = game.classes
        preferred_stats = {
            "Barbarian": "Strength",
            "Bard": "Charisma",
            "Cleric": "Wisdom",
            "Druid": "Wisdom",
            "Fighter": "Strength",
            "Monk": "Dexterity",
            "Paladin": "Charisma",
            "Ranger": "Dexterity",
            "Rogue": "Dexterity",
            "Sorcerer": "Charisma",
            "Wizard": "Intelligence",
            "Assassin": "Dexterity"
        }
        
        while True:
            try:
                print(f"{Fore.CYAN}=== Select Your Class ==={Style.RESET_ALL}")
                class_list = list(classes.items())
                for i, (class_name, class_data) in enumerate(class_list, 1):
                    print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{i}. {class_name}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {class_data.get('description', '')}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     Preferred Stat: {preferred_stats.get(class_name, 'Unknown')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                selection = input(f"{Fore.YELLOW}Select class (number or name): {Style.RESET_ALL}").strip()
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print("=== Select Your Class ===")
                class_list = list(classes.items())
                for i, (class_name, class_data) in enumerate(class_list, 1):
                    print("----------------------------------------")
                    print(f"{i}. {class_name}")
                    print(f"     {class_data.get('description', '')}")
                    print(f"     Preferred Stat: {preferred_stats.get(class_name, 'Unknown')}")
                print("----------------------------------------")
                selection = input("Select class (number or name): ").strip()
            
            logger.debug(f"Selected class: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(class_list):
                    return class_list[index][0]
            else:
                selection = selection.capitalize()
                if selection in classes:
                    return selection
            
            try:
                print(f"{Fore.RED}Invalid class selected. Please enter a number (1-{len(class_list)}) or class name.{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"Invalid class selected. Please enter a number (1-{len(class_list)}) or class name.")

    def _roll_stats(self) -> List[int]:
        logger.debug("Rolling stats")
        stats = [sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]) for _ in range(6)]
        return stats

    def _select_spells(self, game: Any, character_class: str) -> Dict[int, List[str]]:
        classes = game.classes
        class_data = classes.get(character_class, {})
        spells = {0: [], 1: []}
        
        if not class_data.get("spellcasting"):
            logger.debug(f"No spells available for non-spellcasting class: {character_class}")
            return spells
        
        spells_path = os.path.join(os.path.dirname(__file__), "data", "spells.json")
        try:
            with open(spells_path, "r") as f:
                spell_data = json.load(f)
            logger.debug(f"Loaded spells.json: {spell_data}")
        except FileNotFoundError:
            logger.error(f"Spells file not found at {spells_path}")
            spell_data = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding spells.json: {e}")
            spell_data = {}
        
        # Default spells for spellcasting classes
        default_spells = {
            "Assassin": {
                "0": [],
                "1": [
                    {"name": "Disguise Self", "description": "Changes your appearance.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Silent Image", "description": "Creates minor illusion of your design.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Ghost Sound", "description": "Creates minor sounds or music.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1}
                ]
            },
            "Wizard": {
                "0": [
                    {"name": "Prestidigitation", "description": "Performs minor tricks.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0},
                    {"name": "Mage Hand", "description": "5-pound telekinesis.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0},
                    {"name": "Light", "description": "Object shines like a torch.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0}
                ],
                "1": [
                    {"name": "Magic Missile", "description": "1d4+1 damage; +1 missile per two levels above 1st (max 5).", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Shield", "description": "Invisible shield gives +4 to AC, blocks magic missiles.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Charm Person", "description": "Makes one person your friend.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Burning Hands", "description": "1d4/level fire damage (max 5d4).", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1}
                ]
            },
            "Sorcerer": {
                "0": [
                    {"name": "Prestidigitation", "description": "Performs minor tricks.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0},
                    {"name": "Mage Hand", "description": "5-pound telekinesis.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0},
                    {"name": "Light", "description": "Object shines like a torch.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0}
                ],
                "1": [
                    {"name": "Magic Missile", "description": "1d4+1 damage; +1 missile per two levels above 1st (max 5).", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1},
                    {"name": "Shield", "description": "Invisible shield gives +4 to AC, blocks magic missiles.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1},
                    {"name": "Charm Person", "description": "Makes one person your friend.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1},
                    {"name": "Burning Hands", "description": "1d4/level fire damage (max 5d4).", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1}
                ]
            },
            "Bard": {
                "0": [
                    {"name": "Dancing Lights", "description": "Creates torches or other lights that you can move.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0},
                    {"name": "Ghost Sound", "description": "Creates minor sounds or music.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0},
                    {"name": "Mending", "description": "Makes minor repairs on an object.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0}
                ],
                "1": [
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 +1/level (max +5) points of damage.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1},
                    {"name": "Charm Person", "description": "Makes one person your friend.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1},
                    {"name": "Grease", "description": "Makes 10-ft. square or one object slippery.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1},
                    {"name": "Hideous Laughter", "description": "Subject loses actions for 1 round/level.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1}
                ]
            },
            "Cleric": {
                "0": [
                    {"name": "Create Water", "description": "Creates 2 gallons/level of pure water.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                    {"name": "Guidance", "description": "+1 on one attack roll, saving throw, or skill check.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                    {"name": "Light", "description": "Object shines like a torch.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0}
                ],
                "1": [
                    {"name": "Bless", "description": "Allies gain +1 on attack rolls and saves against fear.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 +1/level (max +5) points of damage.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Shield of Faith", "description": "Aura grants +2 or higher deflection bonus.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Command", "description": "One subject obeys selected command for 1 round.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1}
                ]
            },
            "Druid": {
                "0": [
                    {"name": "Create Water", "description": "Creates 2 gallons/level of pure water.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                    {"name": "Flare", "description": "Dazzles one creature (-1 on attack rolls).", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                    {"name": "Know Direction", "description": "You discern north.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0}
                ],
                "1": [
                    {"name": "Entangle", "description": "Plants entangle everyone in 40-ft.-radius.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 +1/level (max +5) points of damage.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Faerie Fire", "description": "Outlines subjects with light, canceling blur, concealment, etc.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Speak with Animals", "description": "You can communicate with animals.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1}
                ]
            },
            "Paladin": {
                "0": [],
                "1": [
                    {"name": "Bless", "description": "Allies gain +1 on attack rolls and saves against fear.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1},
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 +1/level (max +5) points of damage.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1},
                    {"name": "Detect Poison", "description": "Detects poison in one creature or object.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1},
                    {"name": "Divine Favor", "description": "You gain +1 per three levels on attack and damage rolls.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1}
                ]
            },
            "Ranger": {
                "0": [],
                "1": [
                    {"name": "Alarm", "description": "Wards an area for 2 hours/level.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Animal Messenger", "description": "Sends a Tiny animal to a specific place.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Detect Animals or Plants", "description": "Detects kinds of animals or plants.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Endure Elements", "description": "Exist comfortably in hot or cold environments.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1}
                ]
            }
        }
        available_spells = spell_data.get(character_class, default_spells.get(character_class, {}))
        
        if not available_spells:
            logger.warning(f"No spells defined for {character_class} in spells.json or defaults")
            try:
                print(f"{Fore.YELLOW}No spells available for {character_class} at level 1.{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"No spells available for {character_class} at level 1.")
            return spells
        
        for level in [0, 1]:
            level_spells = available_spells.get(str(level), [])
            if not level_spells:
                logger.debug(f"No level {level} spells available for {character_class}")
                continue
            
            max_spells = 4 if level == 0 else 2
            try:
                print(f"{Fore.CYAN}=== Select Level {level} Spells (Choose up to {max_spells}) ==={Style.RESET_ALL}")
                for i, spell in enumerate(level_spells, 1):
                    spell_name = spell if isinstance(spell, str) else spell.get("name", "Unknown")
                    spell_desc = spell.get("description", "No description available") if isinstance(spell, dict) else "No description available"
                    spell_mp = spell.get("mp_cost", "Unknown") if isinstance(spell, dict) else "Unknown"
                    print(f"{Fore.CYAN}{i}. {spell_name}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     Description: {spell_desc}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     MP Cost: {spell_mp}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"=== Select Level {level} Spells (Choose up to {max_spells}) ===")
                for i, spell in enumerate(level_spells, 1):
                    spell_name = spell if isinstance(spell, str) else spell.get("name", "Unknown")
                    spell_desc = spell.get("description", "No description available") if isinstance(spell, dict) else "No description available"
                    spell_mp = spell.get("mp_cost", "Unknown") if isinstance(spell, dict) else "Unknown"
                    print(f"{i}. {spell_name}")
                    print(f"     Description: {spell_desc}")
                    print(f"     MP Cost: {spell_mp}")
                print("----------------------------------------")
            
            selected = []
            while len(selected) < max_spells:
                try:
                    choice = input(f"{Fore.YELLOW}Select spell {len(selected)+1}/{max_spells} (number, name, or 'done' to finish): {Style.RESET_ALL}").strip().lower()
                except OSError as e:
                    logger.error(f"Console output error: {e}")
                    choice = input(f"Select spell {len(selected)+1}/{max_spells} (number, name, or 'done' to finish): ").strip().lower()
                if choice == 'done' and selected:
                    break
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(level_spells):
                        spell_name = level_spells[index]["name"] if isinstance(level_spells[index], dict) else level_spells[index]
                        if spell_name not in selected:
                            selected.append(spell_name)
                            logger.debug(f"Selected spell: {spell_name}")
                        else:
                            try:
                                print(f"{Fore.RED}Spell already selected. Try again.{Style.RESET_ALL}")
                            except OSError as e:
                                logger.error(f"Console output error: {e}")
                                print("Spell already selected. Try again.")
                    else:
                        try:
                            print(f"{Fore.RED}Invalid number. Try again.{Style.RESET_ALL}")
                        except OSError as e:
                            logger.error(f"Console output error: {e}")
                            print("Invalid number. Try again.")
                else:
                    choice = choice.capitalize()
                    for spell in level_spells:
                        spell_name = spell["name"] if isinstance(spell, dict) else spell
                        if spell_name.lower() == choice and spell_name not in selected:
                            selected.append(spell_name)
                            logger.debug(f"Selected spell: {spell_name}")
                            break
                    else:
                        try:
                            print(f"{Fore.RED}Invalid or already selected spell. Try again.{Style.RESET_ALL}")
                        except OSError as e:
                            logger.error(f"Console output error: {e}")
                            print("Invalid or already selected spell. Try again.")
            
            spells[level] = selected
            logger.debug(f"Selected spells for level {level}: {selected}")
        
        return spells

    def _get_class_features(self, game: Any, character_class: str) -> List[str]:
        classes = game.classes
        class_data = classes.get(character_class, {})
        features = [f["name"] for f in class_data.get("features", []) if f.get("level", 1) == 1]
        logger.debug(f"Selected features for {character_class}: {features}")
        return features

    def find_starting_position(self, game: Any) -> Tuple[int, int]:
        logger.debug("Searching for starting dungeon position")
        locations = game.world.map.get("locations", {})
        for key, loc in locations.items():
            if loc.get("type") == "dungeon":
                x, y = map(int, key.split(","))
                logger.debug(f"Found dungeon at ({x}, {y}) for starting position")
                return (x, y)
        logger.warning("No dungeon found, defaulting to (0, 0)")
        return (0, 0)