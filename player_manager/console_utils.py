import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

def console_print(message: str, color: str = None):
    color_map = {
        "red": Fore.RED,
        "cyan": Fore.CYAN,
        "yellow": Fore.YELLOW
    }
    try:
        if color and color in color_map:
            print(f"{color_map[color]}{message}{Style.RESET_ALL}")
        else:
            print(message)
    except OSError as e:
        logger.error(f"Console output error: {e}")
        print(message)

def console_input(prompt: str, color: str = None) -> str:
    color_map = {
        "red": Fore.RED,
        "cyan": Fore.CYAN,
        "yellow": Fore.YELLOW
    }
    try:
        if color and color in color_map:
            return input(f"{color_map[color]}{prompt}{Style.RESET_ALL}")
        return input(prompt)
    except OSError as e:
        logger.error(f"Console output error: {e}")
        return input(prompt)