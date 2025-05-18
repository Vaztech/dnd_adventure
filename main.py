import logging
import time
from dnd_adventure.game import Game
from dnd_adventure.msvcrt_input import handle_input
from dnd_adventure.ui_manager import UIManager
from player_manager.player_manager import PlayerManager
from colorama import init, Fore, Style
from dnd_adventure.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def display_start_menu():
    print(f"{Fore.CYAN}=== D&D Adventure ==={Style.RESET_ALL}")
    print(f"{Fore.CYAN}1. New Game{Style.RESET_ALL}")
    print(f"{Fore.CYAN}2. Continue Game{Style.RESET_ALL}")
    print(f"{Fore.CYAN}3. Select Character{Style.RESET_ALL}")
    print(f"{Fore.CYAN}4. Delete Character{Style.RESET_ALL}")
    print(f"{Fore.CYAN}5. Exit{Style.RESET_ALL}")
    choice = input(f"{Fore.YELLOW}Select an option (1-5): {Style.RESET_ALL}").strip()
    return choice

def main():
    init()  # Initialize colorama for Windows console
    logger.info("Starting D&D Adventure")
    
    player_manager = PlayerManager()
    
    while True:
        choice = display_start_menu()
        
        if choice == "1":  # New Game
            player_name = input(f"{Fore.YELLOW}Enter your character name: {Style.RESET_ALL}").strip()
            if not player_name:
                print(f"{Fore.RED}Name cannot be empty!{Style.RESET_ALL}")
                continue
            game = Game(player_name, player_manager, None)
            if not game.running:
                print(f"{Fore.RED}Failed to start new game!{Style.RESET_ALL}")
                continue
            break
        
        elif choice == "2":  # Continue Game
            save_files = Game.list_save_files()
            if not save_files:
                print(f"{Fore.RED}No save files found!{Style.RESET_ALL}")
                continue
            print(f"{Fore.YELLOW}Available save files: {', '.join(save_files)}{Style.RESET_ALL}")
            save_file = input(f"{Fore.YELLOW}Enter save file name: {Style.RESET_ALL}").strip()
            if save_file not in save_files:
                print(f"{Fore.RED}Save file not found!{Style.RESET_ALL}")
                continue
            game = Game(None, player_manager, save_file)
            if not game.running:
                print(f"{Fore.RED}Failed to load game!{Style.RESET_ALL}")
                continue
            break
        
        elif choice == "3":  # Select Character
            save_files = Game.list_save_files()
            if not save_files:
                print(f"{Fore.RED}No characters found!{Style.RESET_ALL}")
                continue
            print(f"{Fore.YELLOW}Available characters: {', '.join(save_files)}{Style.RESET_ALL}")
            save_file = input(f"{Fore.YELLOW}Enter character save file name: {Style.RESET_ALL}").strip()
            if save_file not in save_files:
                print(f"{Fore.RED}Character not found!{Style.RESET_ALL}")
                continue
            game = Game(None, player_manager, save_file)
            if not game.running:
                print(f"{Fore.RED}Failed to load character!{Style.RESET_ALL}")
                continue
            break
        
        elif choice == "4":  # Delete Character
            save_files = Game.list_save_files()
            if not save_files:
                print(f"{Fore.RED}No characters to delete!{Style.RESET_ALL}")
                continue
            print(f"{Fore.YELLOW}Available characters: {', '.join(save_files)}{Style.RESET_ALL}")
            save_file = input(f"{Fore.YELLOW}Enter character save file name to delete: {Style.RESET_ALL}").strip()
            if save_file not in save_files:
                print(f"{Fore.RED}Character not found!{Style.RESET_ALL}")
                continue
            try:
                import os
                os.remove(os.path.join("dnd_adventure", "data", "saves", save_file))
                print(f"{Fore.CYAN}Character deleted successfully!{Style.RESET_ALL}")
                logger.info(f"Deleted save file: {save_file}")
            except Exception as e:
                print(f"{Fore.RED}Failed to delete character: {e}{Style.RESET_ALL}")
                logger.error(f"Failed to delete save file {save_file}: {e}")
        
        elif choice == "5":  # Exit
            print(f"{Fore.CYAN}Exiting D&D Adventure. Goodbye!{Style.RESET_ALL}")
            return
        
        else:
            print(f"{Fore.RED}Invalid option! Please select 1-5.{Style.RESET_ALL}")

    # Main game loop
    while game.running:
        logger.debug(f"Game mode: {game.mode}")
        if game.mode == "movement":
            command = handle_input(game)
            logger.debug(f"Received command: {command}")
            if command in ["w", "s", "a", "d"]:
                logger.debug(f"Processing movement command: {command}")
                game.handle_command(command)
                game.ui_manager.display_current_map()
                from dnd_adventure.ui import display_status
                display_status(game)
                logger.debug(f"Player position after movement: {game.player_position}")
            elif command in ["enter", "help", "debug"]:
                game.handle_command(command)
                game.ui_manager.display_current_map()
                from dnd_adventure.ui import display_status
                display_status(game)
        elif game.mode == "command":
            cmd = input(f"{Fore.YELLOW}Enter command: {Style.RESET_ALL}").strip()
            logger.debug(f"Command mode input: {cmd}")
            game.handle_command(cmd)
            game.ui_manager.display_current_map()
            from dnd_adventure.ui import display_status
            display_status(game)
            game.mode = "movement"
        time.sleep(0.01)  # Reduce CPU load

if __name__ == "__main__":
    main()