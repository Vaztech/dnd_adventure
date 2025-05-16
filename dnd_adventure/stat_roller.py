import random
import logging
from typing import List, Dict, Optional
from colorama import Fore, Style

logger = logging.getLogger(__name__)

def roll_stats(race, subrace: Optional[str], classes: List[Dict], class_name: str) -> List[int]:
    stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    stats = []
    print(f"\n{Fore.CYAN}=== Rolling Stats (4d6, drop lowest) ==={Style.RESET_ALL}")
    logger.debug("Rolling stats")
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
    logger.debug(f"Stats rolled: {modified_stats}")
    return modified_stats