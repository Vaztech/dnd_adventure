import msvcrt
import time
import logging

logger = logging.getLogger(__name__)

def handle_input(game):
    logger.debug("Checking for keypress with kbhit")
    if msvcrt.kbhit():
        char = msvcrt.getwch().lower()
        logger.debug(f"Key pressed: {char}")
        current_time = time.time()
        # Ensure last_key_time is initialized
        if not hasattr(game, 'last_key_time'):
            game.last_key_time = 0.0
            logger.debug("Initialized last_key_time to 0.0")
        if current_time - game.last_key_time < 0.1:  # Reduced debounce
            logger.debug("Input ignored due to debounce")
            time.sleep(0.05)
            return None
        game.last_key_time = current_time
        logger.debug(f"last_key_time updated to {current_time}")

        # Handle single-character keys
        if char == 'w':
            logger.debug("Returning command: w")
            return "w"
        elif char == 's':
            logger.debug("Returning command: s")
            return "s"
        elif char == 'a':
            logger.debug("Returning command: a")
            return "a"
        elif char == 'd':
            logger.debug("Returning command: d")
            return "d"
        elif char == '\r':
            logger.debug("Returning command: enter")
            return "enter"
        elif char == '\x1b':
            logger.debug("Returning command: help")
            return "help"
        elif char == '\x00':
            second_char = msvcrt.getwch()
            if second_char == ';':  # F12
                logger.debug("Returning command: debug")
                return "debug"
        # Handle arrow keys
        elif char == '\xe0':
            second_char = msvcrt.getwch()
            logger.debug(f"Arrow key second char: {second_char}")
            if second_char == 'H':  # Up
                logger.debug("Returning command: w")
                return "w"
            elif second_char == 'P':  # Down
                logger.debug("Returning command: s")
                return "s"
            elif second_char == 'K':  # Left
                logger.debug("Returning command: a")
                return "a"
            elif second_char == 'M':  # Right
                logger.debug("Returning command: d")
                return "d"
        else:
            logger.debug(f"Ignored key: {char}")
    else:
        logger.debug("No keypress detected")
    return None