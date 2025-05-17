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
                        subclass=player_data.get("subclass", None),
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
            stats=player_data["stats"],
            spells=player_data["spells"],
            level=player_data.get("level", 1),
            features=player_data["features"],
            subclass=player_data.get("subclass", None),
        )
        starting_room = self.find_starting_position(game)
        logger.debug("Player initialization complete")
        logger.info(
            f"Character created: {player.name}, {player.race}, {player.subrace}, {player.character_class}, level {player.level}, subclass {player.subclass}"
        )
        return player, f"{starting_room[0]},{starting_room[1]}"

    def _create_character(self, game: Any) -> Optional[Dict[str, Any]]:
        """Create a character with the locked-in summary format.
        Note: On level-up, stats are rebalanced with +2 points/level (e.g., 68 points at level 20 for auto-rolled, 63 for manual).
        Max stat increases: 14 at level 5, 16 at level 10, 18 at level 15, 20 at level 20. Requires future `rebalance_stats` method."""
        logger.debug("Starting character creation")
        race = None
        subrace = None
        character_class = None
        subclass = None
        stats = None
        spells = {0: [], 1: []}
        features = []
        level = 1

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
                subclass = self._select_subclass(game, character_class, level)
            
            if not stats:
                stats = self._choose_stats(race, subrace, character_class)
            
            race_dict = next((r for r in self.races if r["name"].lower() == race.lower()), {})
            subrace_dict = race_dict.get("subraces", {}).get(subrace, {}) if subrace else {}
            race_modifiers = race_dict.get("ability_modifiers", {})
            subrace_modifiers = subrace_dict.get("ability_modifiers", {})
            
            combined_modifiers = {}
            for stat, value in race_modifiers.items():
                combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
            for stat, value in subrace_modifiers.items():
                combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
            
            stat_dict = {
                "Strength": stats[0],
                "Dexterity": stats[1],
                "Constitution": stats[2],
                "Intelligence": stats[3],
                "Wisdom": stats[4],
                "Charisma": stats[5],
            }
            for stat, value in combined_modifiers.items():
                stat_dict[stat] = stat_dict.get(stat, 6) + value
            final_stats = [
                stat_dict["Strength"], stat_dict["Dexterity"], stat_dict["Constitution"],
                stat_dict["Intelligence"], stat_dict["Wisdom"], stat_dict["Charisma"]
            ]
            
            class_data = game.classes.get(character_class, {})
            
            spells = {0: [], 1: []}
            if class_data.get("spellcasting"):
                spells = self._select_spells(game, character_class, level, stat_dict)
            
            if not features:
                features = self._get_class_features(game, character_class)
            
            max_hp = self._calculate_hp(class_data, stat_dict)
            current_hp = max_hp
            max_mp = self._calculate_mp(class_data, stat_dict)
            current_mp = max_mp
            attack = self._calculate_attack(class_data, stat_dict)
            defense = self._calculate_defense(stat_dict)
            
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
                print(f"{Fore.CYAN}Class: {character_class}{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}=== Rolling Stats ==={Style.RESET_ALL}")
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
                    racial_mod = combined_modifiers.get(stat, 0)
                    mod_str = f" ({'+' if racial_mod >= 0 else ''}{racial_mod})" if racial_mod != 0 else ""
                    print(f"{Fore.CYAN}{stat}: {value}{mod_str}{Style.RESET_ALL}")
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
                print(f"Class: {character_class}")
                print("\n=== Rolling Stats ===")
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
                        prereqs = data.get("prerequisites", {})
                        level_req = prereqs.get("level", 1)
                        stat_reqs = prereqs.get("stats", {})
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
                    racial_mod = combined_modifiers.get(stat, 0)
                    mod_str = f" ({'+' if racial_mod >= 0 else ''}{racial_mod})" if racial_mod != 0 else ""
                    print(f"{stat}: {value}{mod_str}")
                print("\n=== Spells ===")
                if spells[0] or spells[1]:
                    print(f"Level 0: {', '.join(spells[0]) or 'None'}")
                    print(f"Level 1: {', '.join(spells[1]) or 'None'}")
                else:
                    print(f"None")
            
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
                subclass = None
                spells = {0: [], 1: []}
                features = []
                continue
            elif choice == '3':
                if class_data.get("spellcasting"):
                    spells = self._select_spells(game, character_class, level, stat_dict)
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
                    f"'subclass': '{subclass}', 'stats': {stats}, 'final_stats': {final_stats}, 'spells': {spells}, 'features': {features}, 'level': {level}}}"
                )
                return {
                    "race": race,
                    "subrace": subrace,
                    "class": character_class,
                    "subclass": subclass,
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
        hit_die = class_data.get("hit_die", 6)
        con_modifier = (stat_dict.get("Constitution", 10) - 10) // 2
        max_hp = hit_die + con_modifier
        return max(max_hp, 1)

    def _calculate_mp(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        if not class_data.get("spellcasting"):
            return 0
        primary_stat = class_data.get("spellcasting_stat", "Intelligence")
        stat_modifier = (stat_dict.get(primary_stat, 10) - 10) // 2
        return max(2 + stat_modifier, 0)

    def _calculate_attack(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        bab = 0
        if class_data.get("bab_progression") == "fast":
            bab = 1
        elif class_data.get("bab_progression") == "medium":
            bab = 0
        dex_modifier = (stat_dict.get("Dexterity", 10) - 10) // 2
        str_modifier = (stat_dict.get("Strength", 10) - 10) // 2
        return max(bab + max(dex_modifier, str_modifier), 0)

    def _calculate_defense(self, stat_dict: Dict[str, int]) -> int:
        dex_modifier = (stat_dict.get("Dexterity", 10) - 10) // 2
        return 10 + dex_modifier

    def _select_subclass(self, game: Any, character_class: str, level: int) -> Optional[str]:
        logger.debug(f"Selecting subclass for {character_class}")
        class_data = game.classes.get(character_class, {})
        subclasses = class_data.get("subclasses", {})
        if not subclasses:
            logger.debug(f"No subclasses available for {character_class}")
            return None
        
        unlocked_subclasses = []
        for subclass_name, data in subclasses.items():
            prereqs = data.get("prerequisites", {})
            level_req = prereqs.get("level", 1)
            stat_reqs = prereqs.get("stats", {})
            if level >= level_req:
                unlocked_subclasses.append((subclass_name, data))
        
        if not unlocked_subclasses:
            logger.debug(f"No unlocked subclasses for {character_class} at level {level}")
            return None
        
        while True:
            try:
                print(f"{Fore.CYAN}=== Select Your Subclass (or None) ==={Style.RESET_ALL}")
                for i, (subclass_name, data) in enumerate(unlocked_subclasses, 1):
                    print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{i}. {subclass_name}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {data.get('description', '')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{len(unlocked_subclasses) + 1}. None{Style.RESET_ALL}")
                selection = input(f"{Fore.YELLOW}Select subclass (1-{len(unlocked_subclasses) + 1}): {Style.RESET_ALL}").strip()
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print("=== Select Your Subclass (or None) ===")
                for i, (subclass_name, data) in enumerate(unlocked_subclasses, 1):
                    print("----------------------------------------")
                    print(f"{i}. {subclass_name}")
                    print(f"     {data.get('description', '')}")
                print("----------------------------------------")
                print(f"{len(unlocked_subclasses) + 1}. None")
                selection = input(f"Select subclass (1-{len(unlocked_subclasses) + 1}): ").strip()
            
            logger.debug(f"Selected subclass: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(unlocked_subclasses):
                    return unlocked_subclasses[index][0]
                elif index == len(unlocked_subclasses):
                    return None
            try:
                print(f"{Fore.RED}Invalid selection. Please enter a number (1-{len(unlocked_subclasses) + 1}).{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"Invalid selection. Please enter a number (1-{len(unlocked_subclasses) + 1}).")

    def _choose_stats(self, race: str, subrace: Optional[str], character_class: str) -> List[int]:
        while True:
            try:
                print(f"{Fore.CYAN}=== Select Stat Allocation Method ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}1. Random Allocation{Style.RESET_ALL}")
                print(f"{Fore.CYAN}     Randomly allocate 30 points (min 1, max 12 before modifiers).{Style.RESET_ALL}")
                print(f"{Fore.CYAN}2. Allocate Points Manually{Style.RESET_ALL}")
                print(f"{Fore.CYAN}     Distribute 25 points (start at 6, min 4, max 15 before modifiers).{Style.RESET_ALL}")
                if character_class == "Wizard":
                    print(f"{Fore.YELLOW}Note: Wizards benefit from high Intelligence (12+ recommended for level 1 spells).{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                choice = input(f"{Fore.YELLOW}Select method (1-2): {Style.RESET_ALL}").strip()
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print("=== Select Stat Allocation Method ===")
                print("1. Random Allocation")
                print("     Randomly allocate 30 points (min 1, max 12 before modifiers).")
                print("2. Allocate Points Manually")
                print("     Distribute 25 points (start at 6, min 4, max 15 before modifiers).")
                if character_class == "Wizard":
                    print("Note: Wizards benefit from high Intelligence (12+ recommended for level 1 spells).")
                print("----------------------------------------")
                choice = input("Select method (1-2): ").strip()
            
            logger.debug(f"Selected stat method: {choice}")
            if choice == "1":
                while True:
                    stats = self._allocate_stats(race, subrace, character_class, point_pool=30, random_allocation=True)
                    try:
                        print(f"{Fore.CYAN}Generated Stats:{Style.RESET_ALL}")
                        for stat, value in zip(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"], stats):
                            print(f"{Fore.CYAN}{stat}: {value}{Style.RESET_ALL}")
                        accept = input(f"{Fore.YELLOW}Accept stats? (yes/no): {Style.RESET_ALL}").strip().lower()
                    except OSError as e:
                        logger.error(f"Console output error: {e}")
                        print("Generated Stats:")
                        for stat, value in zip(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"], stats):
                            print(f"{stat}: {value}")
                        accept = input("Accept stats? (yes/no): ").strip().lower()
                    if accept == "yes":
                        return stats
                    elif accept != "no":
                        try:
                            print(f"{Fore.RED}Please enter 'yes' or 'no'.{Style.RESET_ALL}")
                        except OSError as e:
                            logger.error(f"Console output error: {e}")
                            print("Please enter 'yes' or 'no'.")
            elif choice == "2":
                return self._allocate_stats(race, subrace, character_class, point_pool=25, random_allocation=False)
            try:
                print(f"{Fore.RED}Invalid choice. Please select 1 or 2.{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print("Invalid choice. Please select 1 or 2.")

    def _allocate_stats(self, race: str, subrace: Optional[str], character_class: str, point_pool: int, random_allocation: bool) -> List[int]:
        point_buy_costs = {
            4: -2, 5: -1, 6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 6,
            13: 8, 14: 10, 15: 12, 16: 15, 17: 18, 18: 21
        }
        min_stat = 1 if random_allocation else 4
        max_stat = 12 if random_allocation else 15
        base_stat = 1 if random_allocation else 6
        stats = [base_stat] * 6
        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        stat_descriptions = [
            "Affects melee attack and damage, carrying capacity.",
            "Affects AC, ranged attacks, Reflex saves, Stealth.",
            "Affects HP, Fortitude saves, endurance.",
            "Affects Wizard spells, skill points, Knowledge.",
            "Affects Cleric/Druid spells, Will saves, Perception.",
            "Affects Sorcerer/Bard spells, social skills, leadership."
        ]
        unallocated_points = point_pool
        
        race_dict = next((r for r in self.races if r["name"].lower() == race.lower()), {})
        subrace_dict = race_dict.get("subraces", {}).get(subrace, {}) if subrace else {}
        race_modifiers = race_dict.get("ability_modifiers", {})
        subrace_modifiers = subrace_dict.get("ability_modifiers", {})
        combined_modifiers = {}
        for stat, value in race_modifiers.items():
            combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
        for stat, value in subrace_modifiers.items():
            combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
        
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
        preferred_stat = preferred_stats.get(character_class, "Intelligence")
        preferred_stat_idx = stat_names.index(preferred_stat)
        
        if random_allocation:
            preferred_value = min(12, max(10, random.randint(8, 12)))
            stats[preferred_stat_idx] = preferred_value
            unallocated_points -= point_buy_costs.get(preferred_value, 0)
            possible_values = [v for v in point_buy_costs.keys() if min_stat <= v <= max_stat]
            weights = [1 if v < 8 else 3 for v in possible_values]
            while unallocated_points > 0:
                stat_idx = random.randint(0, 5)
                if stats[stat_idx] >= max_stat:
                    continue
                next_values = [v for v in possible_values if v > stats[stat_idx] and point_buy_costs[v] - point_buy_costs.get(stats[stat_idx], 0) <= unallocated_points]
                if not next_values:
                    continue
                new_value = random.choices(next_values, weights[:len(next_values)], k=1)[0]
                cost = point_buy_costs[new_value] - point_buy_costs.get(stats[stat_idx], 0)
                stats[stat_idx] = new_value
                unallocated_points -= cost
            logger.debug(f"Randomly allocated stats: {stats}, remaining points: {unallocated_points}")
            return stats
        
        def get_cost_to_increment(current_value: int) -> Optional[int]:
            if current_value >= max_stat:
                return None
            next_value = current_value + 1
            return point_buy_costs.get(next_value, float('inf')) - point_buy_costs.get(current_value, 0)
        
        while True:
            try:
                print(f"{Fore.CYAN}=== Manual Stat Allocation ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}Unallocated points: {unallocated_points}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Racial Modifiers: {self._format_modifiers(combined_modifiers) or 'None'}{Style.RESET_ALL}")
                for i, (stat_name, value, desc) in enumerate(zip(stat_names, stats, stat_descriptions), 1):
                    base_modifier = (value - 10) // 2
                    racial_mod = combined_modifiers.get(stat_name, 0)
                    final_value = value + racial_mod
                    final_modifier = (final_value - 10) // 2
                    cost_to_next = get_cost_to_increment(value)
                    cost_str = f"To increase to {value + 1}: {cost_to_next} point{'s' if cost_to_next != 1 else ''}" if cost_to_next is not None else "Maxed out"
                    print(f"{Fore.CYAN}{i}. {stat_name}: {value} ({'+' if base_modifier >= 0 else ''}{base_modifier}){Style.RESET_ALL}")
                    if racial_mod:
                        print(f"{Fore.CYAN}     With racial ({'+' if racial_mod > 0 else ''}{racial_mod}): {final_value} ({'+' if final_modifier >= 0 else ''}{final_modifier}){Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {desc}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {cost_str}{Style.RESET_ALL}")
                selection = input(f"{Fore.YELLOW}Select stat (1-6) or 'done' to finalize: {Style.RESET_ALL}").strip().lower()
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print("=== Manual Stat Allocation ===")
                print(f"Unallocated points: {unallocated_points}")
                print(f"Racial Modifiers: {self._format_modifiers(combined_modifiers) or 'None'}")
                for i, (stat_name, value, desc) in enumerate(zip(stat_names, stats, stat_descriptions), 1):
                    base_modifier = (value - 10) // 2
                    racial_mod = combined_modifiers.get(stat_name, 0)
                    final_value = value + racial_mod
                    final_modifier = (final_value - 10) // 2
                    cost_to_next = get_cost_to_increment(value)
                    cost_str = f"To increase to {value + 1}: {cost_to_next} point{'s' if cost_to_next != 1 else ''}" if cost_to_next is not None else "Maxed out"
                    print(f"{i}. {stat_name}: {value} ({'+' if base_modifier >= 0 else ''}{base_modifier})")
                    if racial_mod:
                        print(f"     With racial ({'+' if racial_mod > 0 else ''}{racial_mod}): {final_value} ({'+' if final_modifier >= 0 else ''}{final_modifier})")
                    print(f"     {desc}")
                    print(f"     {cost_str}")
                selection = input("Select stat (1-6) or 'done' to finalize: ").strip().lower()
            
            if selection == "done":
                if unallocated_points > 0:
                    try:
                        print(f"{Fore.RED}Cannot finalize: {unallocated_points} points remain unallocated. Spend them or lose them.{Style.RESET_ALL}")
                        finalize = input(f"{Fore.YELLOW}Finalize anyway? (yes/no): {Style.RESET_ALL}").strip().lower()
                    except OSError as e:
                        logger.error(f"Console output error: {e}")
                        print(f"Cannot finalize: {unallocated_points} points remain unallocated. Spend them or lose them.")
                        finalize = input("Finalize anyway? (yes/no): ").strip().lower()
                    if finalize == "yes":
                        logger.debug(f"Finalized stats: {stats}, unused points: {unallocated_points}")
                        return stats
                    elif finalize != "no":
                        try:
                            print(f"{Fore.RED}Please enter 'yes' or 'no'.{Style.RESET_ALL}")
                        except OSError as e:
                            logger.error(f"Console output error: {e}")
                            print("Please enter 'yes' or 'no'.")
                    continue
                try:
                    finalize = input(f"{Fore.YELLOW}Finalize stats? (yes/no): {Style.RESET_ALL}").strip().lower()
                except OSError as e:
                    logger.error(f"Console output error: {e}")
                    finalize = input("Finalize stats? (yes/no): ").strip().lower()
                if finalize == "yes":
                    logger.debug(f"Finalized stats: {stats}")
                    return stats
                elif finalize != "no":
                    try:
                        print(f"{Fore.RED}Please enter 'yes' or 'no'.{Style.RESET_ALL}")
                    except OSError as e:
                        logger.error(f"Console output error: {e}")
                        print("Please enter 'yes' or 'no'.")
                continue
            
            if not selection.isdigit() or not 1 <= int(selection) <= 6:
                try:
                    print(f"{Fore.RED}Invalid input. Please select a number (2-6) or 'done'.{Style.RESET_ALL}")
                except OSError as e:
                    logger.error(f"Console output error: {e}")
                    print("Invalid input. Please select a number (1-6) or 'done'.")
                continue
            
            stat_idx = int(selection) - 1
            try:
                prompt = f"{Fore.YELLOW}Enter target value for {stat_names[stat_idx]} ({min_stat}-{max_stat}) or '+n'/'-n' to adjust (e.g., '+2', '-1'): {Style.RESET_ALL}"
                input_str = input(prompt).strip()
                
                if input_str.startswith('+') or input_str.startswith('-'):
                    points = int(input_str)
                    target_value = stats[stat_idx] + points
                else:
                    target_value = int(input_str)
                
                if target_value < min_stat or target_value > max_stat:
                    try:
                        print(f"{Fore.RED}Value must be between {min_stat} and {max_stat}.{Style.RESET_ALL}")
                    except OSError as e:
                        logger.error(f"Console output error: {e}")
                        print(f"Value must be between {min_stat} and {max_stat}.")
                    continue
                
                cost = point_buy_costs.get(target_value, float('inf'))
                current_cost = point_buy_costs.get(stats[stat_idx], 0)
                cost_difference = cost - current_cost
                
                if cost_difference > unallocated_points:
                    try:
                        print(f"{Fore.RED}Not enough points ({unallocated_points} available, need {cost_difference}).{Style.RESET_ALL}")
                    except OSError as e:
                        logger.error(f"Console output error: {e}")
                        print(f"Not enough points ({unallocated_points} available, need {cost_difference}).")
                    continue
                if cost_difference < 0 and abs(cost_difference) > point_pool - unallocated_points:
                    try:
                        print(f"{Fore.RED}Cannot remove more points than allocated.{Style.RESET_ALL}")
                    except OSError as e:
                        logger.error(f"Console output error: {e}")
                        print("Cannot remove more points than allocated.")
                    continue
                
                stats[stat_idx] = target_value
                unallocated_points -= cost_difference
                logger.debug(f"Updated {stat_names[stat_idx]} to {stats[stat_idx]}, unallocated points: {unallocated_points}")
            except ValueError:
                try:
                    print(f"{Fore.RED}Invalid input. Enter a number ({min_stat}-{max_stat}) or '+n'/'-n' (e.g., '+2').{Style.RESET_ALL}")
                except OSError as e:
                    logger.error(f"Console output error: {e}")
                    print(f"Invalid input. Enter a number ({min_stat}-{max_stat}) or '+n'/'-n' (e.g., '+2').")

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
                selection = input(f"{Fore.YELLOW}Select race (1-{len(self.races)}): {Style.RESET_ALL}").strip()
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
                selection = input(f"Select race (1-{len(self.races)}): ").strip()
            
            logger.debug(f"Selected race: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(self.races):
                    return self.races[index]["name"]
            try:
                print(f"{Fore.RED}Invalid race selected. Please enter a number (1-{len(self.races)}).{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"Invalid race selected. Please enter a number (1-{len(self.races)}).")

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
                selection = input(f"{Fore.YELLOW}Select subrace (1-{len(subrace_list)}): {Style.RESET_ALL}").strip()
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
                selection = input(f"Select subrace (1-{len(subrace_list)}): ").strip()
            
            logger.debug(f"Selected subrace: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(subrace_list):
                    return subrace_list[index][0]
            try:
                print(f"{Fore.RED}Invalid subrace selected. Please enter a number (1-{len(subrace_list)}).{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"Invalid subrace selected. Please enter a number (1-{len(subrace_list)}).")

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
                selection = input(f"{Fore.YELLOW}Select class (1-{len(class_list)}): {Style.RESET_ALL}").strip()
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
                selection = input(f"Select class (1-{len(class_list)}): ").strip()
            
            logger.debug(f"Selected class: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(class_list):
                    return class_list[index][0]
            try:
                print(f"{Fore.RED}Invalid class selected. Please enter a number (1-{len(class_list)}).{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"Invalid class selected. Please enter a number (1-{len(class_list)}).")

    def _select_spells(self, game: Any, character_class: str, player_level: int, stat_dict: Dict[str, int]) -> Dict[int, List[str]]:
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
        
        default_spells = {
            "Assassin": {
                "0": [],
                "1": [
                    {"name": "Disguise Self", "description": "Changes your appearance.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Silent Image", "description": "Creates minor illusion of your design.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Ghost Sound", "description": "Creates minor sounds or music.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12}
                ]
            },
            "Wizard": {
                "0": [
                    {"name": "Prestidigitation", "description": "Performs minor tricks.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0, "min_stat": 10},
                    {"name": "Mage Hand", "description": "5-pound telekinesis.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0, "min_stat": 10},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0, "min_stat": 10},
                    {"name": "Light", "description": "Object shines like a torch.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Magic Missile", "description": "1d4+1 damage; +1 missile per two levels above 1st (max 5).", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Shield", "description": "Invisible shield gives +4 to AC, blocks magic missiles.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Charm Person", "description": "Makes one person your friend.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Burning Hands", "description": "1d4/level fire damage (max 5d4).", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12}
                ]
            },
            "Sorcerer": {
                "0": [
                    {"name": "Prestidigitation", "description": "Performs minor tricks.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10},
                    {"name": "Mage Hand", "description": "5-pound telekinesis.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10},
                    {"name": "Light", "description": "Object shines like a torch.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Magic Missile", "description": "1d4+1 damage; +1 missile per two levels above 1st (max 5).", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Shield", "description": "Invisible shield gives +4 to AC, blocks magic missiles.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Charm Person", "description": "Makes one person your friend.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Burning Hands", "description": "1d4/level fire damage (max 5d4).", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12}
                ]
            },
            "Bard": {
                "0": [
                    {"name": "Dancing Lights", "description": "Creates torches or other lights that you can move.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10},
                    {"name": "Ghost Sound", "description": "Creates minor sounds or music.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10},
                    {"name": "Mending", "description": "Makes minor repairs on an object.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 +1/level (max +5) points of damage.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Charm Person", "description": "Makes one person your friend.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Grease", "description": "Makes 10-ft. square or one object slippery.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Hideous Laughter", "description": "Subject loses actions for 1 round/level.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12}
                ]
            },
            "Cleric": {
                "0": [
                    {"name": "Create Water", "description": "Creates 2 gallons/level of pure water.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10},
                    {"name": "Guidance", "description": "+1 on one attack roll, saving throw, or skill check.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10},
                    {"name": "Light", "description": "Object shines like a torch.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Bless", "description": "Allies gain +1 on attack rolls and saves against fear.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 +1/level (max +5) points of damage.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Shield of Faith", "description": "Aura grants +2 or higher deflection bonus.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Command", "description": "One subject obeys selected command for 1 round.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12}
                ]
            },
            "Druid": {
                "0": [
                    {"name": "Create Water", "description": "Creates 2 gallons/level of pure water.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10},
                    {"name": "Flare", "description": "Dazzles one creature (-1 on attack rolls).", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10},
                    {"name": "Know Direction", "description": "You discern north.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Entangle", "description": "Plants entangle everyone in 40-ft.-radius.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 +1/level (max +5) points of damage.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Faerie Fire", "description": "Outlines subjects with light, canceling blur, concealment, etc.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Speak with Animals", "description": "You can communicate with animals.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12}
                ]
            },
            "Paladin": {
                "0": [],
                "1": [
                    {"name": "Bless", "description": "Allies gain +1 on attack rolls and saves against fear.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 +1/level (max +5) points of damage.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Detect Poison", "description": "Detects poison in one creature or object.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Divine Favor", "description": "You gain +1 per three levels on attack and damage rolls.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12}
                ]
            },
            "Ranger": {
                "0": [],
                "1": [
                    {"name": "Alarm", "description": "Wards an area for 2 hours/level.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Animal Messenger", "description": "Sends a Tiny animal to a specific place.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Detect Animals or Plants", "description": "Detects kinds of animals or plants.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Endure Elements", "description": "Exist comfortably in hot or cold environments.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12}
                ]
            }
        }
        available_spells = spell_data.get(character_class, default_spells.get(character_class, {}))
        
        if not available_spells:
            logger.warning(f"No spells defined for {character_class} in spells.json or defaults")
            try:
                print(f"{Fore.YELLOW}No spells available for {character_class} at level {player_level}.{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"No spells available for {character_class} at level {player_level}.")
            return spells
        
        for level in [0, 1]:
            level_spells = available_spells.get(str(level), [])
            if not level_spells:
                logger.debug(f"No level {level} spells available for {character_class}")
                continue
            
            max_spells = 4 if level == 0 else 2
            eligible_spells = [
                spell for spell in level_spells
                if spell.get("min_level", 0) <= player_level and
                   stat_dict.get(spell.get("primary_stat", "Intelligence"), 10) >= spell.get("min_stat", 10)
            ]
            if not eligible_spells:
                logger.debug(f"No eligible level {level} spells for {character_class} at player level {player_level}")
                try:
                    print(f"{Fore.YELLOW}No level {level} spells available (check level or stat requirements).{Style.RESET_ALL}")
                except OSError as e:
                    logger.error(f"Console output error: {e}")
                    print(f"No level {level} spells available (check level or stat requirements).")
                continue
            
            try:
                print(f"{Fore.CYAN}=== Select Level {level} Spells (Choose up to {max_spells}) ==={Style.RESET_ALL}")
                for i, spell in enumerate(eligible_spells, 1):
                    spell_name = spell.get("name", "Unknown")
                    spell_desc = spell.get("description", "No description available")
                    spell_mp = spell.get("mp_cost", "Unknown")
                    spell_min_level = spell.get("min_level", 0)
                    spell_min_stat = spell.get("min_stat", 10)
                    spell_stat = spell.get("primary_stat", "Intelligence")
                    print(f"{Fore.CYAN}{i}. {spell_name}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     Description: {spell_desc}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     MP Cost: {spell_mp}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     Min Level: {spell_min_level}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     Min {spell_stat}: {spell_min_stat}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
            except OSError as e:
                logger.error(f"Console output error: {e}")
                print(f"=== Select Level {level} Spells (Choose up to {max_spells}) ===")
                for i, spell in enumerate(eligible_spells, 1):
                    spell_name = spell.get("name", "Unknown")
                    spell_desc = spell.get("description", "No description available")
                    spell_mp = spell.get("mp_cost", "Unknown")
                    spell_min_level = spell.get("min_level", 0)
                    spell_min_stat = spell.get("min_stat", 10)
                    spell_stat = spell.get("primary_stat", "Intelligence")
                    print(f"{i}. {spell_name}")
                    print(f"     Description: {spell_desc}")
                    print(f"     MP Cost: {spell_mp}")
                    print(f"     Min Level: {spell_min_level}")
                    print(f"     Min {spell_stat}: {spell_min_stat}")
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
                    if 0 <= index < len(eligible_spells):
                        spell_name = eligible_spells[index]["name"]
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
                    for spell in eligible_spells:
                        spell_name = spell["name"]
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