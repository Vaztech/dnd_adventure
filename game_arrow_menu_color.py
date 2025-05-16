import sys
import os
import platform
import logging
import random
from typing import Optional, Dict, Tuple, List
from colorama import init, Fore, Style
from textwrap import fill
import difflib
import msvcrt
import time

from dnd_adventure.character import Character
from dnd_adventure.dnd35e.core.world import GameWorld
from dnd_adventure.dnd35e.mechanics.combat import CombatSystem
from dnd_adventure.dnd35e.core.quest_manager import QuestManager
from dnd_adventure.dnd35e.core.save_manager import SaveManager, SAVE_DIR
from dnd_adventure.dnd35e.core.data_loader import DataLoader
from dnd_adventure.races import Race, RacialTrait
from dnd_adventure.classes import get_default_class, DnDClass, CORE_CLASSES

# Custom exception for returning to main menu
class ReturnToMenu(Exception):
    pass

def format_description_block(title, description, indent=2, wrap=80):
    lines = [f"{' ' * indent}{Fore.CYAN}{title}{Style.RESET_ALL}"]
    lines.append(fill(description, width=wrap, initial_indent=' ' * indent, subsequent_indent=' ' * indent))
    return '\n'.join(lines)

init()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("game.log")
fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s:%(name)s:%(message)s"))
logger.handlers = [fh]
logger = logging.getLogger(__name__)

class Game:
    def __init__(self, player_name: str, require_character: bool = True):
        logger.debug(f"Initializing game for player: {player_name}, require_character={require_character}")
        self.world = GameWorld.generate()
        self.player_name = player_name
        self.player = None
        self.starting_room = None
        self.quest_log = None
        self.combat_mode = False

        # Load races
        data_loader = DataLoader()
        self.world.races = data_loader.load_races_from_json()
        if not self.world.races:
            logger.warning("No races loaded, using fallback races")
            self.world.races = [
                Race(
                    name="Human",
                    description="Versatile and adaptable, humans excel in any profession.",
                    ability_modifiers={},
                    size="Medium",
                    speed=30,
                    racial_traits=[
                        {"name": "Bonus Feat", "description": "Gain one extra feat at 1st level"},
                        {"name": "Extra Skills", "description": "Gain 4 extra skill points at 1st level and 1 extra skill point at each additional level"}
                    ],
                    favored_class="Any",
                    languages=["Common"],
                    subraces={}
                ),
                Race(
                    name="Elf",
                    description="Graceful and magical, elves are attuned to nature and arcane arts.",
                    ability_modifiers={"Dexterity": 2, "Constitution": -2},
                    size="Medium",
                    speed=30,
                    racial_traits=[
                        {"name": "Low-Light Vision", "description": "Can see twice as far as a human in dim light"},
                        {"name": "Keen Senses", "description": "+2 bonus on Listen, Search, and Spot checks"},
                        {"name": "Immunity to Sleep", "description": "Immune to magical sleep effects"},
                        {"name": "Elven Weapon Proficiency", "description": "Proficient with longsword, rapier, longbow, shortbow, and composite versions"}
                    ],
                    favored_class="Wizard",
                    languages=["Common", "Elven"],
                    subraces={
                        "High Elf": {
                            "description": "Skilled in arcane magic, with a knack for wizardry.",
                            "ability_modifiers": {"Intelligence": 2},
                            "racial_traits": [
                                {"name": "Arcane Focus", "description": "+2 bonus on Spellcraft checks"}
                            ]
                        },
                        "Wood Elf": {
                            "description": "Swift and stealthy, at home in forests.",
                            "ability_modifiers": {"Wisdom": 2},
                            "racial_traits": [
                                {"name": "Camouflage", "description": "+4 Hide in natural terrain"}
                            ]
                        },
                        "Dark Elf (Drow)": {
                            "description": "Cunning and shadowy, with innate magical abilities.",
                            "ability_modifiers": {"Charisma": 2},
                            "racial_traits": [
                                {"name": "Spell Resistance", "description": "Spell Resistance equal to 11 + class levels"},
                                {"name": "Darkvision (120 ft)", "description": "Can see in the dark up to 120 feet"}
                            ]
                        }
                    }
                ),
                Race(
                    name="Dwarf",
                    description="Sturdy and resilient, dwarves are masters of stone and metal.",
                    ability_modifiers={"Constitution": 2, "Charisma": -2},
                    size="Medium",
                    speed=20,
                    racial_traits=[
                        {"name": "Darkvision (60 ft)", "description": "Can see in the dark up to 60 feet"},
                        {"name": "Stability", "description": "+4 bonus against bull rush or trip attempts when standing on the ground"},
                        {"name": "Stonecunning", "description": "+2 bonus on Search checks related to stonework"},
                        {"name": "Poison Resistance", "description": "+2 bonus on saving throws against poison"}
                    ],
                    favored_class="Fighter",
                    languages=["Common", "Dwarven"],
                    subraces={
                        "Hill Dwarf": {
                            "description": "Hardy and wise, with strong community ties.",
                            "ability_modifiers": {"Wisdom": 2},
                            "racial_traits": [
                                {"name": "Resilient", "description": "+2 bonus on saving throws against poison and spells"}
                            ]
                        },
                        "Mountain Dwarf": {
                            "description": "Tough and martial, skilled in combat.",
                            "ability_modifiers": {"Strength": 2},
                            "racial_traits": [
                                {"name": "Armor Training", "description": "Proficient with light and medium armor"}
                            ]
                        }
                    }
                ),
                Race(
                    name="Aasimar",
                    description="Celestial-touched beings with a natural inclination toward good.",
                    ability_modifiers={"Wisdom": 2, "Charisma": 2},
                    size="Medium",
                    speed=30,
                    racial_traits=[
                        {"name": "Darkvision", "description": "See 60 ft in darkness"},
                        {"name": "Celestial Resistance", "description": "+2 vs acid/cold/electricity"}
                    ],
                    favored_class="Paladin",
                    languages=["Common", "Celestial"],
                    subraces={}
                )
            ]

        # Load classes explicitly
        self.world.load_classes_from_json()
        logger.debug(f"Classes loaded in Game.__init__: {[cls.name for cls in self.world.classes]}")
        if not self.world.classes:
            logger.error("Failed to load classes, using default class")
            self.world.classes = [get_default_class()]
            self.world.class_data = {cls.name: cls.to_dict() for cls in self.world.classes}

        if require_character:
            self.player, self.starting_room = self.initialize_player()
            if self.player is None:
                print("Failed to create character. Exiting.")
                sys.exit(1)
            
            self.player.location = self.starting_room or self.world.get_room(0)
            if not self.player.location:
                logger.error("Invalid starting room, defaulting to room 0")
                self.player.location = self.world.get_room(0)
            if self.starting_room and hasattr(self.starting_room, 'monsters'):
                self.starting_room.monsters = [m for m in self.starting_room.monsters][:1]  # Limit to 1 monster
            self.quest_log = QuestManager(self.player)
            self.quest_log.load()

    def initialize_player(self) -> Tuple[Character, Optional[object]]:
        save_path = os.path.join(SAVE_DIR, f"{self.player_name}.save")
        if os.path.exists(save_path):
            try:
                player, room = SaveManager.load_player(self.world, self.player_name, self.create_player)
                if player is None:
                    player = self.create_player(self.player_name)
                    room = None
                if room and hasattr(room, 'monsters'):
                    room.monsters = [m for m in room.monsters][:1]  # Limit to 1 monster
                return player, room
            except Exception as e:
                logger.error(f"Player initialization failed: {e}")
                return self.create_player(self.player_name), None
        else:
            player, room = self.create_player(self.player_name), None
            if room and hasattr(room, 'monsters'):
                room.monsters = [m for m in room.monsters][:1]  # Limit to 1 monster
            return player, room

    def create_player(self, name: str) -> Character:
        print("\nCreate a new character")
        print("-----------------------")
        logger.debug(f"Starting character creation for {name}")

        selections = {
            'race': None,
            'subrace': None,
            'class': None,
            'stats': None,
            'spells': None,
            'points_remaining': 28
        }
        stat_order = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        point_costs = {5: 0, 6: 1, 7: 2, 8: 3, 9: 4, 10: 5, 11: 6, 12: 7, 13: 8, 14: 9, 15: 10, 16: 12, 17: 15, 18: 19}

        def select_race() -> Optional[Race]:
            print("\n=== Select Race ===")
            races = self.world.races
            if not races:
                logger.error("No races available")
                print("Error: No races available. Using default race.")
                return Race(
                    name="Human",
                    description="Versatile and adaptable",
                    ability_modifiers={},
                    size="Medium",
                    speed=30,
                    racial_traits=[
                        {"name": "Bonus Feat", "description": "Gain one extra feat at 1st level"},
                        {"name": "Extra Skills", "description": "Gain 4 extra skill points at 1st level and 1 extra skill point at each additional level"}
                    ],
                    favored_class="Any",
                    languages=["Common"],
                    subraces={}
                )
            options = [
                {"name": race.name, "description": race.description}
                for race in races
            ] + [{"name": "Cancel", "description": "Return to main menu."}]
            critical_indices = {len(options) - 1}
            choice = arrow_menu(options, critical_indices, title="Select Race")
            if choice is None or options[choice]["name"] == "Cancel":
                logger.debug("Race selection cancelled")
                return None
            logger.debug(f"Selected race: {races[choice].name}")
            return races[choice]

        def select_subrace(race: Race) -> Optional[str]:
            subraces = getattr(race, 'subraces', {})
            if not subraces:
                logger.debug(f"No subraces for {race.name}")
                return None
            print(f"\n=== Select Subrace for {race.name} ===")
            options = [
                {"name": subrace, "description": details["description"]}
                for subrace, details in subraces.items()
            ] + [{"name": "No Subrace", "description": "Proceed without selecting a subrace."},
                  {"name": "Cancel", "description": "Return to main menu."}]
            critical_indices = {len(options) - 1}
            choice = arrow_menu(options, critical_indices, title=f"Select Subrace for {race.name}")
            if choice is None or options[choice]["name"] == "Cancel":
                logger.debug("Subrace selection cancelled")
                return None
            if options[choice]["name"] == "No Subrace":
                logger.debug("Selected No Subrace")
                return None
            race.subrace = options[choice]["name"]
            logger.debug(f"Selected subrace: {race.subrace}")
            return race.subrace

        def select_class() -> Optional[DnDClass]:
            print("\n=== Select Class ===")
            classes = self.world.classes
            logger.debug(f"Available classes in select_class: {[cls.name for cls in classes]}")
            if not classes:
                logger.error("No classes available in world.classes")
                raise ValueError("No classes available. Please check classes.json or class loading logic.")
            options = [
                {"name": cls.name, "description": cls.description}
                for cls in classes
            ] + [{"name": "Cancel", "description": "Return to main menu."}]
            critical_indices = {len(options) - 1}
            choice = arrow_menu(options, critical_indices, title="Select Class")
            if choice is None or options[choice]["name"] == "Cancel":
                logger.debug("Class selection cancelled")
                return None
            logger.debug(f"Selected class: {classes[choice].name}")
            return classes[choice]

        def select_stats(race: Race) -> Optional[Dict[str, int]]:
            stats = selections['stats'] or {
                'strength': 8, 'dexterity': 8, 'constitution': 8,
                'intelligence': 8, 'wisdom': 8, 'charisma': 8
            }
            points_remaining = selections['points_remaining']
            stat_descriptions = {
                'strength': 'Affects melee damage and carrying capacity.',
                'dexterity': 'Improves agility, reflexes, and ranged accuracy.',
                'constitution': 'Boosts health and endurance.',
                'intelligence': 'Enhances arcane magic and knowledge (MP for Wizards).',
                'wisdom': 'Strengthens divine magic, perception, and willpower (MP for Clerics/Druids).',
                'charisma': 'Improves social skills and leadership (MP for Sorcerers/Bards).'
            }
            racial_modifiers = race.ability_modifiers.copy()
            if selections['subrace'] and race.subraces:
                racial_modifiers.update(race.subraces[selections['subrace']].get('ability_modifiers', {}))
            
            print("\nAllocate stat points (28 points available, costs vary, max 15 per stat):")
            while True:
                print("\nCurrent Character Sheet:")
                print(f"Name: {name}")
                print(f"Race: {selections['race'].name if selections['race'] else 'Not selected'}")
                print(f"Subrace: {selections['subrace'] if selections['subrace'] else 'None'}")
                print(f"Class: {selections['class'].name if selections['class'] else 'Not selected'}")
                print("Stats:")
                for stat in stat_order:
                    total = stats[stat] + racial_modifiers.get(stat.capitalize(), 0)
                    print(f"  {stat.capitalize()}: {total}")
                print(f"Points remaining: {points_remaining}")
                
                print("\nAvailable Stats:")
                for i, stat in enumerate(stat_order, 1):
                    value = stats[stat]
                    total = value + racial_modifiers.get(stat.capitalize(), 0)
                    description = stat_descriptions[stat]
                    if value >= 15:
                        cost_desc = "Maxed out"
                    else:
                        cost = point_costs.get(value + 1, 999) - point_costs.get(value, 0)
                        cost_desc = f"Cost to increase by 1: {cost} point{'s' if cost != 1 else ''}"
                    print(f"\n{Fore.YELLOW}{stat.capitalize()}: {total}{Style.RESET_ALL}")
                    print(format_description_block("Description", description))
                    print(format_description_block("Cost to Increase", cost_desc))
                print("\nEnter stat and change (e.g., 'charisma +3' or 'strength -2'), 'reset' to start over, 'done' to finish, or 'cancel' to exit:")
                user_input = input().lower().strip()
                if user_input == 'done':
                    selections['stats'] = stats
                    selections['points_remaining'] = points_remaining
                    logger.debug("Stats allocation completed")
                    return stats
                if user_input == 'cancel':
                    logger.debug("Stats allocation cancelled")
                    return None
                if user_input == 'reset':
                    stats = {stat: 8 for stat in stat_order}
                    points_remaining = 28
                    continue
                try:
                    parts = user_input.split()
                    if len(parts) != 2:
                        print("Invalid input. Use format: 'stat +number' or 'stat -number' (e.g., 'charisma +3').")
                        continue
                    stat, change = parts
                    if stat not in stats:
                        print("Invalid stat. Choose: strength, dexterity, constitution, intelligence, wisdom, charisma")
                        continue
                    if not (change.startswith('+') or change.startswith('-')):
                        print("Invalid change. Use '+' or '-' followed by a number (e.g., '+3' or '-2').")
                        continue
                    delta = int(change[1:]) if change[0] == '+' else -int(change[1:])
                    if delta == 0:
                        print("Change must be non-zero.")
                        continue
                    current_value = stats[stat]
                    new_value = current_value + delta
                    if new_value < 5 or new_value > 15:
                        print(f"Cannot change {stat.capitalize()} to {new_value}. Stats must be between 5 and 15.")
                        continue
                    if delta > 0:
                        cost = sum(point_costs.get(i + 1, 999) - point_costs[i] for i in range(current_value, new_value))
                    else:
                        cost = sum(point_costs[i] - point_costs.get(i - 1, 0) for i in range(new_value, current_value))
                    if cost > points_remaining:
                        print(f"Not enough points (need {cost}, have {points_remaining}).")
                        continue
                    if cost < 0 and points_remaining - cost > 28:
                        print("Cannot refund more points than available (max 28).")
                        continue
                    stats[stat] = new_value
                    points_remaining -= cost
                    print(f"{stat.capitalize()} changed to {new_value}. Points remaining: {points_remaining}")
                except ValueError:
                    print("Invalid number. Use format: 'stat +number' or 'stat -number' (e.g., 'charisma +3').")
                    continue

        def select_spells(dnd_class: DnDClass, stats: Dict[str, int]) -> Optional[Dict[int, List[str]]]:
            if not dnd_class.spellcasting and dnd_class.name != "Bard":
                logger.debug(f"No spellcasting for class: {dnd_class.name}")
                return {0: [], 1: []}
            if dnd_class.spellcasting and dnd_class.spellcasting.get('type') not in ['arcane', 'divine']:
                logger.debug(f"Invalid spellcasting type for class: {dnd_class.name}")
                return {0: [], 1: []}
            
            cleric_spells = {
                0: [
                    {"name": "Light", "description": "Illuminates an area for 10 minutes (1 MP)."},
                    {"name": "Guidance", "description": "Grants +1 to one attack roll, saving throw, or skill check (1 MP)."},
                    {"name": "Cure Minor Wounds", "description": "Heals 1 hit point (1 MP)."}
                ],
                1: [
                    {"name": "Cure Light Wounds", "description": "Heals 1d8 + caster level hit points (2 MP)."},
                    {"name": "Bless", "description": "Grants +1 to attack rolls and saves vs. fear for allies (2 MP)."}
                ]
            }
            # Optional Druid spells (uncomment to enable)
            # druid_spells = {
            #     0: [
            #         {"name": "Create Water", "description": "Creates 2 gallons of pure water (1 MP)."},
            #         {"name": "Detect Poison", "description": "Detects poison in one creature or object (1 MP)."},
            #         {"name": "Flare", "description": "Creates a burst of light, dazzling a creature (1 MP)."}
            #     ],
            #     1: [
            #         {"name": "Entangle", "description": "Plants entangle creatures in a 40-ft. radius (2 MP)."},
            #         {"name": "Charm Animal", "description": "Makes one animal friendly (2 MP)."}
            #     ]
            # }
            arcane_spells = {
                0: [
                    {"name": "Daze", "description": "Stuns a weak enemy for one round (1 MP)."},
                    {"name": "Mage Hand", "description": "Moves a small object up to 5 pounds (1 MP)."}
                ],
                1: [
                    {"name": "Magic Missile", "description": "Deals 1d4+1 force damage to one target (2 MP)."},
                    {"name": "Shield", "description": "Grants +4 to AC for 1 minute (2 MP)."}
                ]
            }
            spell_list = cleric_spells if dnd_class.name in ["Cleric", "Druid"] else arcane_spells
            if dnd_class.name == "Bard":
                spell_list = arcane_spells  # Bards use arcane spells
            # Optional: Use Druid spells (uncomment to enable)
            # spell_list = cleric_spells if dnd_class.name == "Cleric" else druid_spells if dnd_class.name == "Druid" else arcane_spells

            spells_known = {0: 0, 1: 0}
            if dnd_class.name in ["Cleric", "Druid"]:
                spells_known = {0: 3, 1: 2}
                if dnd_class.name == "Cleric":
                    spells_known[1] += 1  # Healing domain: extra Cure Light Wounds
            elif dnd_class.name in ["Wizard", "Sorcerer", "Bard"]:
                spells_known = {0: 4, 1: 2}
            
            casting_stat = {"Wizard": "Intelligence", "Sorcerer": "Charisma", "Cleric": "Wisdom", "Druid": "Wisdom", "Bard": "Charisma"}
            stat_name = casting_stat.get(dnd_class.name, "Intelligence")
            stat_mod = (stats[stat_name.lower()] - 10) // 2
            max_mp = (stat_mod * 2) + 1 + 4  # Level 1
            
            print(f"\n=== Select Spells for {dnd_class.name} ===")
            print(f"You can learn {spells_known[0]} cantrips (level 0, 1 MP each) and {spells_known[1]} 1st-level spells (2 MP each).")
            print(f"Cantrips are minor spells. Your MP is based on {stat_name} (current MP: {max_mp}).")
            print("Use arrow keys to highlight a spell, Enter to select, repeat until all slots are filled, then select Done.")
            print("You can cast any known spell as long as you have enough MP. MP recovers after resting.")
            selected_spells = {0: [], 1: []}
            
            for level in [0, 1]:
                if spells_known[level] == 0:
                    continue
                level_name = "Cantrips (Level 0)" if level == 0 else "1st-Level Spells"
                mp_cost = 1 if level == 0 else 2
                print(f"\n{level_name} (Choose {spells_known[level]}):")
                options = spell_list[level] + [{"name": "Done", "description": "Finish selecting spells for this level."}]
                critical_indices = {len(options) - 1}
                remaining = spells_known[level]
                while remaining > 0:
                    print(f"\nRemaining slots: {remaining}")
                    if selected_spells[level]:
                        print(f"Selected {level_name}: {', '.join(selected_spells[level])}")
                    choice = arrow_menu(options, critical_indices, title=f"Select {level_name}")
                    if choice is None or options[choice]["name"] == "Done":
                        if level == 1 and dnd_class.name == "Cleric" and "Cure Light Wounds" not in selected_spells[1]:
                            selected_spells[1].append("Cure Light Wounds")
                            remaining -= 1
                            print(f"\n{Fore.GREEN}Cure Light Wounds automatically added for Cleric (Healing domain).{Style.RESET_ALL}")
                            time.sleep(1)
                        break
                    spell = options[choice]["name"]
                    selected_spells[level].append(spell)
                    remaining -= 1
                    spell_type = "cantrip" if level == 0 else "1st-level spell"
                    print(f"\n{Fore.GREEN}{spell} added to your known {spell_type}s (costs {mp_cost} MP)!{Style.RESET_ALL}")
                    time.sleep(1)
                if selected_spells[level]:
                    print(f"\nFinal {level_name} selected: {', '.join(selected_spells[level])}")
                else:
                    print(f"\nNo {level_name} selected.")
            
            if dnd_class.name == "Cleric" and "Cure Light Wounds" not in selected_spells[1]:
                selected_spells[1].append("Cure Light Wounds")
                print(f"\n{Fore.GREEN}Cure Light Wounds automatically added for Cleric (Healing domain).{Style.RESET_ALL}")
            
            logger.debug(f"Selected spells for {name}: {selected_spells}")
            return selected_spells

        def review_selections():
            print("\nReview Your Character:")
            print(f"Name: {name}")
            print(f"Race: {selections['race'].name}")
            print(f"Subrace: {selections['subrace'] if selections['subrace'] else 'None'}")
            print(f"Class: {selections['class'].name}")
            print("Stats:")
            racial_modifiers = selections['race'].ability_modifiers.copy()
            if selections['subrace'] and selections['race'].subraces:
                racial_modifiers.update(selections['race'].subraces[selections['subrace']].get('ability_modifiers', {}))
            for stat in stat_order:
                total = selections['stats'][stat] + racial_modifiers.get(stat.capitalize(), 0)
                print(f"  {stat.capitalize()}: {total}")
            print(f"Points remaining: {selections['points_remaining']}")
            print("\nRacial Traits:")
            for trait in getattr(selections['race'], 'racial_traits', []):
                if isinstance(trait, RacialTrait):
                    print(f"  {trait.name}: {trait.description}")
                else:
                    print(f"  {trait['name']}: {trait['description']}")
            if selections['subrace'] and selections['race'].subraces:
                print("Subrace Traits:")
                for trait in selections['race'].subraces[selections['subrace']].get('racial_traits', []):
                    if isinstance(trait, RacialTrait):
                        print(f"  {trait.name}: {trait.description}")
                    else:
                        print(f"  {trait['name']}: {trait['description']}")
            if selections['spells']:
                print("\nKnown Spells:")
                for level, spells in selections['spells'].items():
                    level_name = "Cantrips (Level 0, 1 MP)" if level == 0 else "1st-Level Spells (2 MP)"
                    if spells:
                        print(f"  {level_name}: {', '.join(spells)}")

        selections['race'] = select_race()
        if selections['race'] is None:
            print("Character creation cancelled.")
            logger.debug("Character creation cancelled at race selection")
            return None

        selections['subrace'] = select_subrace(selections['race'])
        if selections['subrace'] is None and selections['race'].subraces:
            print("Character creation cancelled.")
            logger.debug("Character creation cancelled at subrace selection")
            return None

        selections['class'] = select_class()
        if selections['class'] is None:
            print("Character creation cancelled.")
            logger.debug("Character creation cancelled at class selection")
            return None

        selections['stats'] = select_stats(selections['race'])
        if selections['stats'] is None:
            print("Character creation cancelled.")
            logger.debug("Character creation cancelled at stats allocation")
            return None

        selections['spells'] = select_spells(selections['class'], selections['stats'])
        if selections['spells'] is None:
            print("Character creation cancelled.")
            logger.debug("Character creation cancelled at spell selection")
            return None

        review_selections()
        options = ["Confirm Character", "Cancel"]
        critical_indices = {1}
        choice = arrow_menu(options, critical_indices, title="Confirm Character")
        if choice is None or options[choice] == "Cancel":
            print("Character creation cancelled.")
            logger.debug("Character creation cancelled at confirmation")
            return None

        race_name = selections['race'].name + (f" ({selections['subrace']})" if selections['subrace'] else "")
        character = Character(
            name=name,
            race=selections['race'],
            dnd_class=selections['class'],
            race_name=race_name,
            class_name=selections['class'].name,
            level=1,
            known_spells=selections['spells']
        )
        character.stats = [selections['stats'][stat] for stat in stat_order]
        selections['race'].apply_modifiers(character)
        character.armor_class += 2  # Leather armor (+2 AC)
        character.equipment.append("Leather Armor")
        logger.debug(f"Applied racial modifiers for {race_name}: stats={character.stats}")
        character.calculate_hit_points()
        character.calculate_skill_points()
        character.calculate_mp()

        print(f"\nCharacter created:")
        print(f"Name: {character.name}")
        print(f"Health: {character.hit_points}")
        print(f"MP: {character.mp}/{character.max_mp}")
        print(f"Level: {character.level}")
        print(f"Race: {character.race_name}")
        print(f"Class: {selections['class'].name}")
        print("Stats:")
        stat_names = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
        for stat_name, stat_value in zip(stat_names, character.stats):
            print(f"  {stat_name}: {stat_value}")
        print("Racial Traits:")
        for trait in getattr(selections['race'], 'racial_traits', []):
            if isinstance(trait, RacialTrait):
                print(f"  {trait.name}: {trait.description}")
            else:
                print(f"  {trait['name']}: {trait['description']}")
        if selections['subrace'] and selections['race'].subraces:
            print("Subrace Traits:")
            for trait in selections['race'].subraces[selections['subrace']].get('racial_traits', []):
                if isinstance(trait, RacialTrait):
                    print(f"  {trait.name}: {trait.description}")
                else:
                    print(f"  {trait['name']}: {trait['description']}")
        print(f"Skill Points: {character.skill_points}")
        print(f"Equipment: {', '.join(character.equipment)}")
        if character.known_spells:
            print("Known Spells:")
            for level, spells in character.known_spells.items():
                level_name = "Cantrips (Level 0, 1 MP)" if level == 0 else "1st-Level Spells (2 MP)"
                if spells:
                    print(f"  {level_name}: {', '.join(spells)}")

        print("\nCharacter creation complete!")
        input("Press Enter to begin your adventure...")
        logger.debug(f"Character created: {character.name}, Race: {character.race_name}, Class: {character.class_name}")
        return character

    def start(self):
        print("\n=== Dungeon Adventure ===")
        print("Commands: north/south/east/west, look, attack [#], cast [#], rest, quest [list/start/complete/log], save, quit, exit")
        self.print_location()

        while True:
            try:
                command = input("\nWhat would you like to do? ").strip()
                self.handle_command(command)
            except ReturnToMenu:
                logger.debug("Returning to main menu")
                return
            except (EOFError, KeyboardInterrupt):
                print("\nUse 'quit' to exit the game properly or 'exit' to return to the main menu.")
            except Exception as e:
                logger.error(f"Game loop error: {e}", exc_info=True)
                print("An error occurred. Please try again.")

    def print_location(self):
        room = getattr(self.player, 'location', self.starting_room)
        if not room:
            logger.error("No valid room found for player location")
            print("Error: No valid location. Returning to main menu...")
            self.quit_game(return_to_menu=True)
        logger.debug(f"Room details: name={getattr(room, 'name', 'Unknown')}, "
                    f"description={getattr(room, 'description', 'None')}, "
                    f"exits={getattr(room, 'exits', {})}")
        print(f"\n{room.name}\n{room.description}")
        exits = getattr(room, 'exits', {})
        if exits:
            print("Exits:", ", ".join(exits.keys()))
        else:
            print("No exits available.")
        monsters = getattr(room, 'monsters', [])
        alive = [m for m in monsters if hasattr(m, 'hit_points') and m.hit_points > 0]
        logger.debug(f"Monsters in room: {alive}")
        if alive:
            print("Monsters here:")
            for i, m in enumerate(alive, 1):
                print(f"{i}. {m.name} (HP: {m.hit_points})")
            self.combat_mode = True
        else:
            print("No active threats here.")
            self.combat_mode = False

    def handle_command(self, command: str):
        cmd = command.lower().strip()
        logger.debug(f"Processing command: {cmd}")
        valid_commands = [
            "north", "south", "east", "west", "look", "save", "quit", "exit",
            "attack", "cast", "rest", "quest", "help"
        ]
        try:
            if cmd not in valid_commands and not (cmd.startswith("attack ") or cmd.startswith("cast ") or cmd.startswith("quest ")):
                close_matches = difflib.get_close_matches(cmd, valid_commands, n=1, cutoff=0.8)
                if close_matches:
                    suggested_cmd = close_matches[0]
                    print(f"Did you mean '{suggested_cmd}'? Please try again.")
                    logger.debug(f"Suggested correction: '{cmd}' -> '{suggested_cmd}'")
                    return

            if cmd in ["north", "south", "east", "west"]:
                self.move(cmd)
            elif cmd == "look":
                self.print_location()
            elif cmd == "save":
                self.save_session()
            elif cmd == "quit":
                self.quit_game(return_to_menu=False)
            elif cmd == "exit":
                self.quit_game(return_to_menu=True)
            elif cmd == "rest":
                print(self.player.rest())
            elif cmd == "help":
                print("Commands: north, south, east, west, look, attack [#], cast [#], rest, quest [list/start/complete/log], save, quit, exit")
            elif cmd.startswith("quest"):
                self.handle_quest_command(cmd)
            elif cmd.startswith("attack"):
                self.handle_attack_command(cmd)
            elif cmd.startswith("cast"):
                self.handle_cast_command(cmd)
            else:
                print("Unknown command. Try: north, south, east, west, look, attack [#], cast [#], rest, quest [list/start/complete/log], save, quit, exit")
        except Exception as e:
            logger.error(f"Command '{cmd}' failed: {e}", exc_info=True)
            raise

    def move(self, direction: str):
        if self.combat_mode:
            print("You can't flee from combat!")
            return
        if not hasattr(self.player, 'location') or not self.player.location:
            logger.error("Player has no valid location")
            print("Error: Invalid player location.")
            return
        exits = getattr(self.player.location, 'exits', {})
        if not exits:
            logger.error(f"No exits defined for room: {self.player.location.name}")
            print("No exits available from this room.")
            return
        if direction not in exits:
            logger.debug(f"Invalid direction '{direction}' for room {self.player.location.name}, exits: {exits}")
            print(f"No exit to the {direction}.")
            return
        new_room = self.world.get_room(exits[direction])
        if not new_room:
            logger.error(f"Room ID {exits[direction]} not found in world")
            print(f"Cannot move {direction}: destination not found.")
            return
        self.player.location = new_room
        logger.debug(f"Moved to room: name={new_room.name}, id={exits[direction]}")
        self.print_location()

    def handle_quest_command(self, command: str):
        parts = command.split()
        if len(parts) == 1:
            print("Quest commands: list, start <id>, complete <id>, log")
            return
        subcommand = parts[1].lower()
        if subcommand == "list":
            quests = self.quest_log.list_quests()
            if quests:
                print("\nAvailable Quests:")
                for i, quest in enumerate(quests, 1):
                    print(f"{i}. {quest['name']}: {quest['description']}")
            else:
                print("No quests available.")
        elif subcommand == "start" and len(parts) > 2:
            try:
                quest_id = int(parts[2])
                self.quest_log.start_quest(quest_id)
                print(f"Started quest {quest_id}.")
            except ValueError:
                print("Invalid quest ID. Use 'quest list' to see available quests.")
        elif subcommand == "complete" and len(parts) > 2:
            try:
                quest_id = int(parts[2])
                self.quest_log.complete_quest(quest_id)
                print(f"Completed quest {quest_id}.")
            except ValueError:
                print("Invalid quest ID. Use 'quest log' to see active quests.")
        elif subcommand == "log":
            active_quests = self.quest_log.get_active_quests()
            if active_quests:
                print("\nActive Quests:")
                for quest in active_quests:
                    print(f"- {quest['name']}: {quest['description']}")
            else:
                print("No active quests.")
        else:
            print("Invalid quest command. Use: list, start <id>, complete <id>, log")

    def handle_attack_command(self, command: str):
        if not self.combat_mode:
            print("No monsters to attack!")
            return
        parts = command.split()
        if len(parts) < 2:
            print("Specify a monster number to attack (e.g., 'attack 1').")
            return
        try:
            monster_idx = int(parts[1]) - 1
            room = self.player.location
            monsters = getattr(room, 'monsters', [])
            alive = [m for m in monsters if hasattr(m, 'hit_points') and m.hit_points > 0]
            if 0 <= monster_idx < len(alive):
                monster = alive[monster_idx]
                bab = self.player.dnd_class.bab_at_level(self.player.level)
                str_mod = self.player.get_stat_modifier(0)
                attack_roll = random.randint(1, 20) + bab + str_mod
                logger.debug(f"Player attack roll: d20={attack_roll - bab - str_mod}, BAB={bab}, Str mod={str_mod}, Total={attack_roll} vs. AC={monster.armor_class}")
                
                if attack_roll >= monster.armor_class:
                    weapon_die = 8 if self.player.class_name == "Cleric" else 6
                    damage = self.player.calculate_damage_output(weapon_die=weapon_die)
                    if damage <= 0:
                        damage = 1
                    monster.hit_points -= damage
                    print(f"You hit {monster.name} for {damage} damage (HP: {monster.hit_points})")
                    logger.info(f"Player hit {monster.name} for {damage} damage")
                    if monster.hit_points <= 0:
                        print(f"{monster.name} defeated!")
                        logger.info(f"{monster.name} defeated")
                else:
                    print(f"Your attack misses {monster.name}!")
                    logger.debug(f"Player attack missed: roll={attack_roll}, needed={monster.armor_class}")

                alive = [m for m in monsters if hasattr(m, 'hit_points') and m.hit_points > 0]
                self.combat_mode = len(alive) > 0

                if self.combat_mode:
                    for enemy in alive:
                        attack = enemy.attacks[0] if enemy.attacks else {'name': 'Scimitar', 'attack_bonus': 4, 'damage': '1d4+1'}
                        attack_roll = random.randint(1, 20) + attack['attack_bonus']
                        player_ac = self.player.armor_class
                        logger.debug(f"{enemy.name} attack roll: d20={attack_roll - attack['attack_bonus']}, Bonus={attack['attack_bonus']}, Total={attack_roll} vs. Player AC={player_ac}")
                        
                        if attack_roll >= player_ac:
                            damage_dice = attack['damage'].split('+')
                            base_dice = damage_dice[0]
                            bonus = int(damage_dice[1]) if len(damage_dice) > 1 else 0
                            dice_count, dice_type = map(int, base_dice.split('d'))
                            damage = sum(random.randint(1, dice_type) for _ in range(dice_count)) + bonus
                            self.player.hit_points -= damage
                            print(f"{enemy.name} hits you with {attack['name']} for {damage} damage! (Your HP: {self.player.hit_points})")
                            logger.info(f"{enemy.name} dealt {damage} damage to player")
                        else:
                            print(f"{enemy.name}'s {attack['name']} attack misses you!")
                            logger.debug(f"{enemy.name} attack missed: roll={attack_roll}, needed={player_ac}")

                        if self.player.hit_points <= 0:
                            print("\nYou have been defeated! Game Over.")
                            logger.info(f"Player {self.player.name} died (HP: {self.player.hit_points})")
                            self.save_session()
                            sys.exit()

                self.print_location()
            else:
                print(f"Invalid monster number. Choose 1 to {len(alive)}.")
        except ValueError:
            print("Invalid number. Use 'attack <number>' (e.g., 'attack 1').")
        except Exception as e:
            logger.error(f"Attack command failed: {e}", exc_info=True)
            print(f"Combat error: {str(e)}. Please try again.")

    def handle_cast_command(self, command: str):
        if not self.combat_mode:
            print("No monsters to cast spells on!")
            return
        parts = command.split()
        if len(parts) < 2:
            print("Specify a spell number to cast (e.g., 'cast 1'). Use 'cast list' to see spells.")
            return
        try:
            if parts[1].lower() == "list":
                if not hasattr(self.player, 'known_spells') or not self.player.known_spells:
                    print("You have no spells known.")
                    return
                print(f"\nKnown Spells (MP: {self.player.mp}/{self.player.max_mp}):")
                spell_list = []
                for level, spells in self.player.known_spells.items():
                    mp_cost = 1 if level == 0 else 2
                    for spell in spells:
                        spell_list.append((spell, level, mp_cost))
                for i, (spell, level, mp_cost) in enumerate(spell_list, 1):
                    level_name = "Cantrip" if level == 0 else "1st-Level"
                    print(f"{i}. {spell} ({level_name}, {mp_cost} MP)")
                return

            spell_idx = int(parts[1]) - 1
            spell_list = []
            for level, spells in self.player.known_spells.items():
                mp_cost = 1 if level == 0 else 2
                for spell in spells:
                    spell_list.append((spell, level, mp_cost))
            if 0 <= spell_idx < len(spell_list):
                spell, level, mp_cost = spell_list[spell_idx]
                room = self.player.location
                monsters = getattr(room, 'monsters', [])
                alive = [m for m in monsters if hasattr(m, 'hit_points') and m.hit_points > 0]
                
                target = None
                enemy = None
                if spell in ["Cure Light Wounds", "Cure Minor Wounds"]:
                    target = self.player
                elif spell in ["Magic Missile", "Daze"] and alive:
                    enemy = alive[0]
                elif len(parts) > 2 and spell in ["Magic Missile", "Daze"]:
                    monster_idx = int(parts[2]) - 1
                    if 0 <= monster_idx < len(alive):
                        enemy = alive[monster_idx]
                    else:
                        print(f"Invalid monster number. Choose 1 to {len(alive)}.")
                        return

                result = self.player.cast_spell(spell, target=target, enemy=enemy)
                print(result)

                alive = [m for m in monsters if hasattr(m, 'hit_points') and m.hit_points > 0]
                self.combat_mode = len(alive) > 0

                if self.combat_mode:
                    for enemy in alive:
                        attack = enemy.attacks[0] if enemy.attacks else {'name': 'Scimitar', 'attack_bonus': 4, 'damage': '1d4+1'}
                        attack_roll = random.randint(1, 20) + attack['attack_bonus']
                        player_ac = self.player.armor_class
                        logger.debug(f"{enemy.name} attack roll: d20={attack_roll - attack['attack_bonus']}, Bonus={attack['attack_bonus']}, Total={attack_roll} vs. Player AC={player_ac}")
                        
                        if attack_roll >= player_ac:
                            damage_dice = attack['damage'].split('+')
                            base_dice = damage_dice[0]
                            bonus = int(damage_dice[1]) if len(damage_dice) > 1 else 0
                            dice_count, dice_type = map(int, base_dice.split('d'))
                            damage = sum(random.randint(1, dice_type) for _ in range(dice_count)) + bonus
                            self.player.hit_points -= damage
                            print(f"{enemy.name} hits you with {attack['name']} for {damage} damage! (Your HP: {self.player.hit_points})")
                            logger.info(f"{enemy.name} dealt {damage} damage to player")
                        else:
                            print(f"{enemy.name}'s {attack['name']} attack misses you!")
                            logger.debug(f"{enemy.name} attack missed: roll={attack_roll}, needed={player_ac}")

                        if self.player.hit_points <= 0:
                            print("\nYou have been defeated! Game Over.")
                            logger.info(f"Player {self.player.name} died (HP: {self.player.hit_points})")
                            self.save_session()
                            sys.exit()

                self.print_location()
            else:
                print(f"Invalid spell number. Choose 1 to {len(spell_list)}.")
        except ValueError:
            print("Invalid number. Use 'cast <number>' (e.g., 'cast 1') or 'cast list'.")
        except Exception as e:
            logger.error(f"Cast command failed: {e}", exc_info=True)
            print(f"Spell error: {str(e)}. Please try again.")

    def save_session(self):
        try:
            room_id = getattr(self.player.location, 'id', 0)
            SaveManager.save_player(self.player, room_id)
            print("Game saved.")
            logger.info(f"Saved player {self.player.name} to {os.path.join(SAVE_DIR, f'{self.player.name}.save')}")
        except Exception as e:
            logger.error(f"Save session failed: {e}")
            print("Error: Failed to save game.")

    def quit_game(self, return_to_menu: bool = False):
        print("Thanks for playing!")
        self.save_session()
        if return_to_menu:
            logger.debug("Quit game: returning to main menu")
            raise ReturnToMenu()
        else:
            logger.debug("Quit game: exiting program")
            sys.exit()

    @staticmethod
    def list_characters():
        print("\nList Saved Characters:")
        saves = SaveManager.list_saves()
        if not saves:
            print("No characters saved.")
        else:
            for i, name in enumerate(saves, 1):
                print(f"{i}. {name}")
        options = ["Return to Main Menu"]
        critical_indices = set()
        arrow_menu(options, critical_indices, title="List Characters")
        print("Returning to main menu...")

    @staticmethod
    def delete_character():
        print("\nDelete a Character:")
        saves = SaveManager.list_saves()
        if not saves:
            print("No characters to delete.")
            options = ["Return to Main Menu"]
            arrow_menu(options, set(), title="Delete Character")
            print("Returning to main menu...")
            return
        options = [
            {"name": name, "description": f"Delete the saved character '{name}'."}
            for name in saves
        ] + [{"name": "Cancel", "description": "Return to main menu."}]
        critical_indices = set(range(len(saves)))
        choice = arrow_menu(options, critical_indices, title="Select Character to Delete")
        if choice is None or options[choice]["name"] == "Cancel":
            print("Deletion cancelled.")
            print("Returning to main menu...")
            return
        name = options[choice]["name"]
        confirm = input(f"Are you sure you want to delete {name}? (yes/no): ").lower().strip()
        if confirm == "yes":
            path = os.path.join(SAVE_DIR, f"{name}.save")
            try:
                os.remove(path)
                print(f"{name} deleted.")
            except Exception as e:
                logger.error(f"Failed to delete {name}: {e}")
                print(f"Error: Could not delete {name}.")
        else:
            print("Deletion cancelled.")
        options = ["Return to Main Menu"]
        arrow_menu(options, set(), title="Delete Character")
        print("Returning to main menu...")

def color_option(index, selected, text, critical=False):
    prefix = "> " if index == selected else "  "
    color = Fore.RED if critical else Fore.GREEN
    return f"{prefix}{color}{text}{Style.RESET_ALL}"

def arrow_menu(options, critical_indices=None, title="Menu"):
    critical_indices = critical_indices or set()
    selected = 0
    is_windows = platform.system() == "Windows"
    if not is_windows:
        print("Arrow key navigation is only supported on Windows.")
        return None

    while True:
        os.system('cls')
        print(f"=== {title} ===\nUse ↑↓ arrows to navigate, Enter to select, Esc to cancel:\n")
        for i, option in enumerate(options):
            is_critical = i in critical_indices
            name = option['name'] if isinstance(option, dict) else option
            print(color_option(i, selected, name, is_critical))
            if isinstance(option, dict) and 'description' in option:
                print(format_description_block("Description", option['description'], indent=4))
        print(f"\nSelected option: {options[selected]['name'] if isinstance(options[selected], dict) else options[selected]}")

        while msvcrt.kbhit():
            msvcrt.getch()
        
        try:
            key = msvcrt.getch()
            logger.debug(f"Key pressed: {key}")
            if key == b'\xe0':
                key2 = msvcrt.getch()
                logger.debug(f"Extended key: {key2}")
                if key2 == b'H':
                    selected = max(0, selected - 1)
                elif key2 == b'P':
                    selected = min(len(options) - 1, selected + 1)
            elif key == b'\r':
                logger.debug(f"Selected option: {options[selected]['name'] if isinstance(options[selected], dict) else options[selected]} (index {selected})")
                print(f"Confirmed: {options[selected]['name'] if isinstance(options[selected], dict) else options[selected]}")
                return selected
            elif key == b'\x1b':
                logger.debug("Esc pressed, returning None")
                print("Selection cancelled.")
                return None
        except Exception as e:
            logger.error(f"Menu input error: {e}")
            print("Error reading input. Please try again.")

def main_menu():
    options = ["Start New Game", "Continue Game", "List Characters", "Delete Character", "Exit"]
    critical_indices = {4}
    while True:
        os.system('cls')
        choice = arrow_menu(options, critical_indices, title="Main Menu")
        if choice is None:
            print("Menu cancelled. Returning to main menu...")
            continue
        logger.debug(f"Main menu selected: {options[choice]} (index {choice})")
        if choice == 0:
            name = input("Enter your character's name: ").strip()
            if name:
                game = Game(name, require_character=True)
                game.start()
        elif choice == 1:
            name = input("Enter your character's name: ").strip()
            if name:
                try:
                    game = Game(name, require_character=True)
                    game.start()
                except Exception as e:
                    print(f"Failed to load character: {e}")
        elif choice == 2:
            Game.list_characters()
        elif choice == 3:
            Game.delete_character()
        elif choice == 4:
            print("Goodbye!")
            sys.exit()

if __name__ == "__main__":
    main_menu()