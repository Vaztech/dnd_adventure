import os
import logging
from typing import List, Dict
from colorama import Fore, Style

logger = logging.getLogger(__name__)

def select_class(classes: List[Dict]) -> str:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== Select Your Class ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        for i, cls in enumerate(classes, 1):
            desc = cls["description"][:100] + "..." if len(cls["description"]) > 100 else cls["description"]
            print(f"{Fore.YELLOW}{i}. {cls['name']}{Style.RESET_ALL}")
            print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Enter the number of your chosen class (or 'q' to quit):{Style.RESET_ALL}")
        choice = input().strip().lower()
        if choice == 'q':
            logger.info("Game exited during class selection")
            exit()
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(classes):
                logger.debug(f"Selected class: {classes[choice_index]['name']}")
                return classes[choice_index]["name"]
            else:
                print(f"{Fore.RED}Invalid choice! Please select a number between 1 and {len(classes)}.{Style.RESET_ALL}")
                logger.warning(f"Invalid class choice: {choice}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number or 'q' to quit.{Style.RESET_ALL}")
            logger.warning(f"Invalid class input: {choice}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")