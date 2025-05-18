import logging
import os

# Global variables for debug mode toggle
DEBUG_MODE = False  # Default: console debug output off
CONSOLE_HANDLER = None  # Store console handler for level changes

def setup_logging():
    global CONSOLE_HANDLER
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels

    # File handler: logs DEBUG and above to file with UTF-8 encoding
    log_file = os.path.join("C:\\Users\\Vaz\\Desktop\\dnd_adventure", "dnd_adventure.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s,%(msecs)03d %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)

    # Console handler: starts at INFO to hide debug messages
    CONSOLE_HANDLER = logging.StreamHandler()
    CONSOLE_HANDLER.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    CONSOLE_HANDLER.setFormatter(console_formatter)

    # Clear existing handlers and add new ones
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(CONSOLE_HANDLER)