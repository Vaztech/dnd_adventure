import logging
from typing import Dict
from colorama import Fore, Style
from dnd_adventure.character import Character
from dnd_adventure.races import Race

logger = logging.getLogger(__name__)

def display_character_sheet(character: Character, race: Race, dnd_class: Dict):
    print(f"\n{Fore.CYAN}=== Character Sheet: {character.name} ==={Style.RESET_ALL}")
    print(f"Race: {character.race_name}")
    if character.subrace_name:
        print(f"Subrace: {character.subrace_name}")
    print(f"Class: {character.class_name}")
    if character.subclass_name:
        print(f"Subclass: {character.subclass_name}")
    print(f"Level: {character.level} (XP: {character.xp})")
    print(f"Hit Points: {character.hit_points}/{character.max_hit_points}")
    print(f"Mana Points: {character.mp}/{character.max_mp}")
    stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    print("\nStats:")
    for stat_name in stat_names:
        stat_value = character.stat_dict.get(stat_name, 10)
        modifier = (stat_value - 10) // 2
        print(f"  {stat_name}: {stat_value} ({'+' if modifier >= 0 else ''}{modifier})")
    if character.class_skills:
        print("\nClass Skills:")
        print(f"  {', '.join(character.class_skills)}")
    if character.features:
        print("\nFeatures:")
        for feature in character.features:
            name = feature.get("name", "Unknown")
            desc = feature.get("description", "No description")
            print(f"  - {name}: {desc}")
    if character.known_spells and any(character.known_spells.values()):
        print("\nKnown Spells:")
        for level, spells in character.known_spells.items():
            if spells:
                print(f"  Level {level}: {', '.join(spells)}")
    print(f"\nBase Attack Bonus: {character.bab}")
    print(f"Armor Class: {character.armor_class}")
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    logger.debug(f"Displayed character sheet for {character.name}")

def display_initial_lore(character: Character, world):
    print(f"\n{Fore.YELLOW}=== Welcome to {world.name}, {character.name}! ==={Style.RESET_ALL}")
    if world.history:
        print(f"\nA brief history of {world.name}:")
        for era in world.history[:2]:
            print(f"\n{Fore.LIGHTYELLOW_EX}{era['name']}:{Style.RESET_ALL}")
            for event in era["events"][:2]:
                print(f"  {event['year']}: {event['desc']}")
    else:
        print(f"The world of {world.name} is shrouded in mystery...")
    print(f"\nYour adventure begins in {world.get_location(*world.starting_position)['name']}.")
    input(f"\n{Fore.YELLOW}Press Enter to begin your journey...{Style.RESET_ALL}")
    logger.debug(f"Displayed initial lore for {character.name} in {world.name}")