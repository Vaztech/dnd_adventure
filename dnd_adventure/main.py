import os
import sys
import time
import logging
import msvcrt
from colorama import init, Fore, Style
from dnd_adventure.game import Game
from dnd_adventure.ui import display_start_menu, display_current_map, display_status
from dnd_adventure.input_handler import handle_input
from dnd_adventure.logging_config import setup_logging

# Initialize colorama for colored output
init()

# Initialize logging
setup_logging()

logger = logging.getLogger(__name__)

def main():
    print("DEBUG: Starting main...")
    logger.debug(f"Starting main loop. Terminal: {os.getenv('TERM', 'Unknown')}, stdout: {sys.stdout}")
    player_name, save_file = display_start_menu()
    if not player_name:
        print(f"{Fore.CYAN}Farewell, traveler!{Style.RESET_ALL}")
        logger.info("Game exited at start menu")
        return

    game = Game(player_name, save_file)
    display_current_map(game)
    display_status(game)

    # Clear input buffer
    while msvcrt.kbhit():
        msvcrt.getwch()
    time.sleep(0.3)
    logger.debug("Initial input buffer cleared")

    last_refresh_time = time.time()
    last_key_time = 0

    while game.running:
        logger.debug(f"Main loop iteration: mode={game.mode}, pos={game.player_pos}, map={game.current_map}, kbhit={msvcrt.kbhit()}")
        game.running, last_refresh_time, last_key_time = handle_input(game, last_refresh_time, last_key_time)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Main loop crashed: {e}")
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)