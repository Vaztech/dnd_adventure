import os
from typing import List, Optional, Tuple
from colorama import Fore, Style
import logging
from dnd_adventure.game import Game

logger = logging.getLogger(__name__)

def display_start_menu() -> Tuple[Optional[str], Optional[str]]:
    options = ["Start New Game", "Continue Game", "Delete Save", "Exit"]
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== D&D Adventure Game ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        for i, option in enumerate(options, 1):
            print(f"{Fore.YELLOW}{i}. {option}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Enter the number of your choice (or 'q' to quit):{Style.RESET_ALL}")

        choice = input().strip().lower()
        if choice == 'q':
            return None, None
        try:
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(options):
                if options[selected_index] == "Start New Game":
                    player_name = input(f"{Fore.YELLOW}Enter your character name: {Style.RESET_ALL}").strip()
                    if not player_name:
                        player_name = "Adventurer"
                    return player_name, None
                elif options[selected_index] == "Continue Game":
                    save_files = Game.list_save_files()
                    if not save_files:
                        print(f"{Fore.RED}No saved games found!{Style.RESET_ALL}")
                        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                        continue
                    selected_save = select_save_file(save_files)
                    if selected_save:
                        player_name = selected_save.split('_')[0].replace('_', ' ').title()
                        return player_name, selected_save
                    continue
                elif options[selected_index] == "Delete Save":
                    save_files = Game.list_save_files()
                    if not save_files:
                        print(f"{Fore.RED}No saved games to delete!{Style.RESET_ALL}")
                        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                        continue
                    selected_save = select_save_file(save_files)
                    if selected_save:
                        Game.delete_save_file(selected_save)
                        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    continue
                elif options[selected_index] == "Exit":
                    return None, None
            else:
                print(f"{Fore.RED}Invalid choice! Please select a number between 1 and {len(options)}.{Style.RESET_ALL}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number or 'q' to quit.{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def select_save_file(save_files: List[str]) -> Optional[str]:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== Select Save File ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        for i, save in enumerate(save_files, 1):
            print(f"{Fore.YELLOW}{i}. {save}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Enter the number of your choice (or 'q' to cancel):{Style.RESET_ALL}")

        choice = input().strip().lower()
        if choice == 'q':
            return None
        try:
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(save_files):
                return save_files[selected_index]
            else:
                print(f"{Fore.RED}Invalid choice! Please select a number between 1 and {len(save_files)}.{Style.RESET_ALL}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number or 'q' to cancel.{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def display_current_map(game: Game):
    os.system('cls' if os.name == 'nt' else 'clear')
    tile = game.world.get_location(*game.last_world_pos)
    country_id = tile.get("country")
    country_name = "Unknown Lands"
    if country_id is not None:
        country = next((c for c in game.world.map["countries"] if c["id"] == country_id), None)
        if country:
            country_name = country["name"]
    
    if game.current_map:
        map_data = game.graphics["maps"][game.current_map]
        print(f"\n{Fore.CYAN}{map_data['description']} ({tile['name']} in {country_name}){Style.RESET_ALL}")
        for y, row in enumerate(map_data["layout"]):
            line = ""
            for x, char in enumerate(row):
                if (x, len(map_data["layout"]) - 1 - y) == game.player_pos:
                    line += Fore.RED + "@" + Style.RESET_ALL
                elif char == '@':
                    line += " "
                else:
                    symbol_data = map_data["symbols"].get(char, {"symbol": char, "color": "white", "type": "unknown"})
                    symbol = symbol_data["symbol"]
                    color = symbol_data["color"]
                    if color == "gray":
                        line += Fore.LIGHTBLACK_EX + symbol + Style.RESET_ALL
                    elif color == "dark_green":
                        line += Fore.GREEN + symbol + Style.RESET_ALL
                    elif color == "green":
                        line += Fore.GREEN + symbol + Style.RESET_ALL
                    elif color == "light_green":
                        line += Fore.LIGHTGREEN_EX + symbol + Style.RESET_ALL
                    elif color == "light_green_ex":
                        line += Fore.LIGHTGREEN_EX + symbol + Style.RESET_ALL
                    elif color == "blue":
                        line += Fore.BLUE + symbol + Style.RESET_ALL
                    elif color == "light_blue_ex":
                        line += Fore.LIGHTBLUE_EX + symbol + Style.RESET_ALL
                    elif color == "cyan":
                        line += Fore.CYAN + symbol + Style.RESET_ALL
                    elif color == "light_cyan_ex":
                        line += Fore.LIGHTCYAN_EX + symbol + Style.RESET_ALL
                    elif color == "yellow":
                        line += Fore.YELLOW + symbol + Style.RESET_ALL
                    elif color == "light_yellow_ex":
                        line += Fore.LIGHTYELLOW_EX + symbol + Style.RESET_ALL
                    elif color == "red":
                        line += Fore.RED + symbol + Style.RESET_ALL
                    elif color == "light_red_ex":
                        line += Fore.LIGHTRED_EX + symbol + Style.RESET_ALL
                    elif color == "brown":
                        line += Fore.LIGHTRED_EX + symbol + Style.RESET_ALL
                    elif color == "magenta":
                        line += Fore.MAGENTA + symbol + Style.RESET_ALL
                    elif color == "light_magenta_ex":
                        line += Fore.LIGHTMAGENTA_EX + symbol + Style.RESET_ALL
                    elif color == "light_black_ex":
                        line += Fore.LIGHTBLACK_EX + symbol + Style.RESET_ALL
                    elif color == "white":
                        line += Fore.WHITE + symbol + Style.RESET_ALL
                    elif color == "light_white_ex":
                        line += Fore.LIGHTWHITE_EX + symbol + Style.RESET_ALL
                    elif color == "black":
                        line += Fore.BLACK + symbol + Style.RESET_ALL
                    else:
                        print(f"{Fore.YELLOW}Warning: Unsupported color '{color}' for symbol '{symbol}' in {game.current_map} map. Using default color.{Style.RESET_ALL}")
                        logger.warning(f"Unsupported color '{color}' for symbol '{symbol}' in {game.current_map} map")
                        line += symbol
            print(line)
    else:
        print(f"\n{Fore.CYAN}You are in {tile['name']} at ({game.last_world_pos[0]},{game.last_world_pos[1]}) ({tile['type'].capitalize()}) in {country_name}{Style.RESET_ALL}")
        print(game.world.display_map(game.last_world_pos))
    
    if game.current_room:
        expected_room = f"{game.last_world_pos[0]},{game.last_world_pos[1]}" if tile["type"] in ["dungeon", "castle"] else None
        if game.current_room != expected_room:
            print(f"{Fore.RED}Position mismatch detected! Expected room: {expected_room}, Current room: {game.current_room}. Resetting room.{Style.RESET_ALL}")
            logger.error(f"Position mismatch: Expected room {expected_room}, Current room {game.current_room}")
            game.current_room = expected_room
        if game.current_room:
            room = game.game_world.rooms.get(game.current_room)
            if room:
                room.visited = True
                print(f"\n{room.description}")
                exits = ", ".join(room.exits.keys())
                print(f"Exits: {exits if exits else 'None'}")
                if room.monsters:
                    print(f"Monsters: {', '.join(m.name for m in room.monsters)}")
                if room.items:
                    print(f"Items: {', '.join(room.items)}")
            else:
                print(f"{Fore.RED}Error: Room {game.current_room} not found! Resetting room.{Style.RESET_ALL}")
                logger.error(f"Room not found: {game.current_room}")
                game.current_room = None
    logger.debug(f"Displayed map: map={game.current_map}, room={game.current_room}, pos={game.player_pos}")

def display_status(game: Game):
    if game.player is None:
        print(f"{Fore.YELLOW}No character created. Please create a character to continue.{Style.RESET_ALL}")
        logger.warning("Attempted to display status with no player")
        return
    print(f"\n{Fore.YELLOW}HP: {game.player.hit_points}/{game.player.max_hit_points} | MP: {game.player.mp}/{game.player.max_mp} | Level: {game.player.level} | XP: {game.player.xp}{Style.RESET_ALL}")
    if game.message:
        print(f"{Fore.LIGHTYELLOW_EX}{game.message}{Style.RESET_ALL}")
    if game.mode == "movement":
        print(f"\n{Fore.CYAN}Use arrow keys or WASD to move. Press Enter for commands, Esc for help.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.CYAN}Type a command ('lore', 'save', 'quit', etc.) or press Enter to return to movement.{Style.RESET_ALL}")
    logger.debug(f"Displayed status: mode={game.mode}, message={game.message}, HP={game.player.hit_points}/{game.player.max_hit_points}, MP={game.player.mp}/{game.player.max_mp}")