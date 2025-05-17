import msvcrt
import time
import logging
from colorama import Fore, Style
from dnd_adventure.ui import display_current_map, display_status

logger = logging.getLogger(__name__)

def handle_msvcrt_input(game, current_time: float, last_key_time: float) -> tuple[bool, float, float] | None:
    try:
        if msvcrt.kbhit():
            if current_time - last_key_time < 0.3:
                msvcrt.getwch()
                time.sleep(0.1)
                return game.running, current_time, last_key_time
            key = msvcrt.getwch()
            logger.debug(f"msvcrt key pressed: {repr(key.encode())}")
            if key in ('\xe0', '\x00'):  # Arrow key prefix
                key = msvcrt.getwch()
                logger.debug(f"Arrow key second byte: {repr(key.encode())}")
                if key == 'H':
                    game.handle_movement("north")
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Moved north via arrow key")
                elif key == 'P':
                    game.handle_movement("south")
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Moved south via arrow key")
                elif key == 'K':
                    game.handle_movement("west")
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Moved west via arrow key")
                elif key == 'M':
                    game.handle_movement("east")
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Moved east via arrow key")
                else:
                    logger.debug(f"Invalid arrow key second byte: {repr(key.encode())}")
                    return None
            elif key.lower() == 'w':
                game.handle_movement("north")
                display_current_map(game)
                display_status(game)
                logger.debug("Moved north via W key")
            elif key.lower() == 's':
                game.handle_movement("south")
                display_current_map(game)
                display_status(game)
                logger.debug("Moved south via S key")
            elif key.lower() == 'a':
                game.handle_movement("west")
                display_current_map(game)
                display_status(game)
                logger.debug("Moved west via A key")
            elif key.lower() == 'd':
                game.handle_movement("east")
                display_current_map(game)
                display_status(game)
                logger.debug("Moved east via D key")
            elif key == '\r':
                if current_time - game.last_enter_time > 0.3:
                    game.last_enter_time = current_time
                    game.mode = "command"
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Switched to command mode via Enter")
            elif key == '\x1b':
                display_current_map(game)
                print(f"{Fore.YELLOW}Available commands: {', '.join(game.commands)}{Style.RESET_ALL}")
                display_status(game)
                logger.debug("Displayed help commands via Esc")
            else:
                logger.debug(f"Ignored key: {repr(key.encode())}")
                return None
            return game.running, current_time, current_time
        return None
    except UnicodeDecodeError as e:
        logger.error(f"Ignoring invalid msvcrt key input: {e}")
        return None
    except Exception as e:
        logger.error(f"Error in msvcrt input: {e}")
        print(f"{Fore.RED}Error processing msvcrt input: {e}{Style.RESET_ALL}")
        display_current_map(game)
        display_status(game)
        return None