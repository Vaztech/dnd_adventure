import os
import random
import logging
from colorama import Fore, Style
from dnd_adventure.character import Character

logger = logging.getLogger(__name__)

def display_character_sheet(character: Character, race_obj, dnd_class: dict) -> None:
    print(f"\n{Fore.CYAN}=== Character Sheet ==={Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Name: {Fore.WHITE}{character.name}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Health: {Fore.WHITE}{character.hit_points}/{character.max_hit_points}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Magic Points: {Fore.WHITE}{character.mp}/{character.max_mp}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Level: {Fore.WHITE}{character.level}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Experience Points: {Fore.WHITE}{character.xp}{Style.RESET_ALL}")
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
    if not character.known_spells or all(len(spells) == 0 for spells in character.known_spells.values()):
        print(f"  {Fore.WHITE}None{Style.RESET_ALL}")
    else:
        for level in sorted(character.known_spells.keys()):
            spells = character.known_spells[level]
            if spells:
                print(f"  {Fore.WHITE}Level {level}: {', '.join(spells)}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    logger.debug(f"Displayed character sheet for {character.name}")

def display_initial_lore(character: Character, world):
    random.seed(hash(character.name + world.name))
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}=== The Prophecy of {world.name} ==={Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
    era = random.choice(world.history)
    event = random.choice(era["events"])
    prophecies = [
        f"In the {era['name']}, the seers foretold that {character.name}, a {character.race_name} {character.class_name}, would rise to reclaim {event['desc'].split('discovers the ')[-1]} and restore balance.",
        f"Legends from {event['year']} speak of {character.name}, born under the stars of {world.name}, destined to confront the {random.choice(['dragon', 'lich', 'demon'])} that threatens {world.name}.",
        f"The chronicles of {era['name']} whisper of {character.name}, a {character.class_name}, who will forge a new era by fulfilling the legacy of {event['desc'].split('is founded by ')[-1]}."
    ]
    prophecy = random.choice(prophecies)
    print(f"{Fore.LIGHTYELLOW_EX}{prophecy}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Your journey begins, {character.name}. The fate of {world.name} rests in your hands.{Style.RESET_ALL}")
    input(f"\n{Fore.CYAN}Press Enter to embark on your adventure...{Style.RESET_ALL}")
    logger.debug(f"Displayed initial lore: {prophecy}")
    random.seed(None)