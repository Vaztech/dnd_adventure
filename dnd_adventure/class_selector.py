import os
import logging
from typing import Dict
from colorama import Fore, Style

logger = logging.getLogger(__name__)

def select_class(classes: Dict[str, dict]) -> str:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== Select Your Class ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        class_list = list(classes.items())  # Convert dict to list of (name, data) tuples
        for i, (class_name, class_data) in enumerate(class_list, 1):
            desc = class_data.get("description", "No description available")
            desc = desc[:100] + "..." if len(desc) > 100 else desc
            print(f"{Fore.YELLOW}{i}. {class_name}{Style.RESET_ALL}")
            print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Enter the number of your chosen class (or 'q' to quit):{Style.RESET_ALL}")
        choice = input().strip().lower()
        if choice == 'q':
            logger.info("Game exited during class selection")
            raise SystemExit("Class selection cancelled")
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(class_list):
                selected_class = class_list[choice_index][0]
                logger.debug(f"Selected class: {selected_class}")
                return selected_class
            else:
                print(f"{Fore.RED}Invalid choice! Please select a number between 1 and {len(class_list)}.{Style.RESET_ALL}")
                logger.warning(f"Invalid class choice: {choice}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number or 'q' to quit.{Style.RESET_ALL}")
            logger.warning(f"Invalid class input: {choice}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")