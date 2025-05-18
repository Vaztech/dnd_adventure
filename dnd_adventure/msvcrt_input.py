import msvcrt
import time
import logging
from colorama import Fore, Style
from dnd_adventure.ui import display_current_map, display_status

logger = logging.getLogger(__name__)

# Import globals from logging_config.py
from dnd_adventure.logging_config import DEBUG_MODE, CONSOLE_HANDLER

def toggle_debug_mode():
    global DEBUG_MODE
    DEBUG_MODE = not DEBUG_MODE
    CONSOLE_HANDLER.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)
    status = "enabled" if DEBUG_MODE else "disabled"
    logger.debug(f"Debug console output {status}")
    print(f"{Fore.CYAN}Debug console output {status}{Style.RESET_ALL}")

def handle_input(game) -> str | None:
    """Handle keyboard input for movement and commands, compatible with main.py."""
    try:
        current_time = time.time()
        if msvcrt.kbhit():
            if current_time - game.last_key_time < 0.3:
                msvcrt.getwch()
                time.sleep(0.1)
                return None
            key = msvcrt.getwch()
            logger.debug(f"msvcrt key pressed: {repr(key.encode())}")
            if key in ('\xe0', '\x00'):  # Arrow key prefix
                key = msvcrt.getwch()
                logger.debug(f"Arrow key second byte: {repr(key.encode())}")
                if key == 'H':
                    game.movement_handler.handle_movement(b'w')  # Map to WASD
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Moved north via arrow key")
                    return "w"
                elif key == 'P':
                    game.movement_handler.handle_movement(b's')
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Moved south via arrow key")
                    return "s"
                elif key == 'K':
                    game.movement_handler.handle_movement(b'a')
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Moved west via arrow key")
                    return "a"
                elif key == 'M':
                    game.movement_handler.handle_movement(b'd')
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Moved east via arrow key")
                    return "d"
                else:
                    logger.debug(f"Invalid arrow key second byte: {repr(key.encode())}")
                    return None
            elif key.lower() == 'w':
                game.movement_handler.handle_movement(b'w')
                display_current_map(game)
                display_status(game)
                logger.debug("Moved north via W key")
                return "w"
            elif key.lower() == 's':
                game.movement_handler.handle_movement(b's')
                display_current_map(game)
                display_status(game)
                logger.debug("Moved south via S key")
                return "s"
            elif key.lower() == 'a':
                game.movement_handler.handle_movement(b'a')
                display_current_map(game)
                display_status(game)
                logger.debug("Moved west via A key")
                return "a"
            elif key.lower() == 'd':
                game.movement_handler.handle_movement(b'd')
                display_current_map(game)
                display_status(game)
                logger.debug("Moved east via D key")
                return "d"
            elif key == '\r':
                if current_time - game.last_enter_time > 0.3:
                    game.last_enter_time = current_time
                    game.mode = "command"
                    display_current_map(game)
                    display_status(game)
                    logger.debug("Switched to command mode via Enter")
                    return "enter"
            elif key == '\x1b':
                display_current_map(game)
                print(f"{Fore.YELLOW}Available commands: {', '.join(game.commands)}{Style.RESET_ALL}")
                display_status(game)
                logger.debug("Displayed help commands via Esc")
                return None
            elif key == '\x7f':  # F12 key
                toggle_debug_mode()
                display_current_map(game)
                display_status(game)
                logger.debug("Toggled debug mode via F12")
                return None
            else:
                logger.debug(f"Ignored key: {repr(key.encode())}")
                return None
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