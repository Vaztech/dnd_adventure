import msvcrt
import time
import logging

logger = logging.getLogger(__name__)

def handle_input(game):
    logger.debug("Checking for keypress with kbhit")
    if msvcrt.kbhit():
        char = msvcrt.getch()
        last_key_time = time.time()
        logger.debug(f"Key pressed: {char}")
        key_map = {
            b'w': 'w',
            b's': 's',
            b'a': 'a',
            b'd': 'd',
            b'\r': 'enter',  # Enter key
            b'\x1b': 'help',  # Esc key
            b'\x00': None,  # Handle special keys
            b'\xe0': None  # Handle arrow keys
        }
        command = key_map.get(char)
        if command is None and char in [b'\x00', b'\xe0']:
            # Read the second byte for special keys
            char2 = msvcrt.getch()
            arrow_map = {
                b'H': 'w',  # Up arrow
                b'P': 's',  # Down arrow
                b'K': 'a',  # Left arrow
                b'M': 'd',  # Right arrow
                b';': 'debug'  # F12
            }
            command = arrow_map.get(char2)
        logger.debug(f"last_key_time updated to {last_key_time}")
        logger.debug(f"Returning command: {command}")
        return command
    logger.debug("No keypress detected")
    return None