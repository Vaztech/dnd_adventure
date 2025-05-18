import logging
import os
from dnd_adventure.game import Game
from player_manager.player_manager import PlayerManager
from dnd_adventure.ui import display_start_menu, display_current_map, display_status
from dnd_adventure.msvcrt_input import handle_input
from colorama import Fore, Style

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'dnd_adventure.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting D&D Adventure")
    player_manager = PlayerManager()
    
    while True:
        player_name, save_file = display_start_menu()
        if player_name is None and save_file is None:
            logger.info("Exiting game")
            return
        game = Game(player_name, player_manager, save_file)
        if not game.running:
            continue
        
        while game.running:
            display_current_map(game)
            display_status(game)
            cmd = handle_input(game)
            if cmd == "enter":
                cmd = input(f"{Fore.CYAN}Enter command: {Style.RESET_ALL}").strip()
            if cmd:
                game.handle_command(cmd)

if __name__ == "__main__":
    from colorama import init
    init()
    main()