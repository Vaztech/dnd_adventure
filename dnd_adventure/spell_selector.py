import os
import logging
from typing import Dict, List
from colorama import Fore, Style
from dnd_adventure.data_loader import DataLoader

logger = logging.getLogger(__name__)

def select_spells(class_name: str) -> Dict[int, List[str]]:
    spells = {0: [], 1: []}
    available_spells = get_available_spells(class_name)
    max_spells = 4 if class_name in ["Wizard", "Sorcerer"] else 3
    for level in [0, 1]:
        if level in available_spells and available_spells[level]:
            print(f"\n{Fore.CYAN}=== Select up to {max_spells} Level {level} Spells for {class_name} ==={Style.RESET_ALL}")
            selected_spells = []
            while len(selected_spells) < max_spells and available_spells[level]:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{Fore.CYAN}Level {level} Spells (Selected {len(selected_spells)}/{max_spells}){Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
                for i, spell in enumerate(available_spells[level], 1):
                    status = " [Selected]" if spell in selected_spells else ""
                    print(f"{Fore.YELLOW}{i}. {spell}{status}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}Enter the number to select/deselect a spell (or 'q' to finish):{Style.RESET_ALL}")
                choice = input().strip().lower()
                if choice == 'q':
                    break
                try:
                    spell_index = int(choice) - 1
                    if 0 <= spell_index < len(available_spells[level]):
                        spell = available_spells[level][spell_index]
                        if spell in selected_spells:
                            selected_spells.remove(spell)
                        else:
                            selected_spells.append(spell)
                        logger.debug(f"Spell {spell} {'deselected' if spell not in selected_spells else 'selected'}")
                    else:
                        print(f"{Fore.RED}Invalid choice! Please select a number between 1 and {len(available_spells[level])}.{Style.RESET_ALL}")
                        logger.warning(f"Invalid spell choice: {choice}")
                        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input! Please enter a number or 'q' to finish.{Style.RESET_ALL}")
                    logger.warning(f"Invalid spell input: {choice}")
                    input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            spells[level] = selected_spells
    logger.debug(f"Selected spells: {spells}")
    return spells

def get_available_spells(class_name: str) -> Dict[int, List[str]]:
    loader = DataLoader()
    spells_data = loader.load_spells_from_json()
    class_key = "Sorcerer/Wizard" if class_name in ["Wizard", "Sorcerer"] else class_name
    spells = {level: [spell.name for spell in spells] for level, spells in spells_data.get(class_key, {}).items() if level in [0, 1]}
    logger.debug(f"Available spells for {class_name}: {spells}")
    return spells