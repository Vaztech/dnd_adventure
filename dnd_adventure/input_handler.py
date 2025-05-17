import time
import logging
from dnd_adventure.msvcrt_input import handle_msvcrt_input
from dnd_adventure.keyboard_input import handle_keyboard_input, failed_attempts
from dnd_adventure.command_processor import process_command
from dnd_adventure.ui import display_current_map, display_status

logger = logging.getLogger(__name__)

# Global flag to disable keyboard input after repeated failures
KEYBOARD_DISABLED = False

def handle_input(game, last_refresh_time: float, last_key_time: float) -> tuple[bool, float, float]:
    global KEYBOARD_DISABLED
    current_time = time.time()
    if current_time - last_refresh_time >= 10:
        display_current_map(game)
        display_status(game)
        last_refresh_time = current_time
        logger.debug("Periodic screen refresh")

    if game.mode == "movement":
        # Check for movement keys using msvcrt
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in [b'w', b'a', b's', b'd']:
                logger.debug(f"Handling movement key: {key}")
                game.movement_handler.handle_movement(key)  # Call MovementHandler directly
                display_current_map(game)
                display_status(game)
                return game.running, current_time, current_time

        # Try msvcrt input for other keys
        result = handle_msvcrt_input(game, current_time, last_key_time)
        if result is not None:
            game.running, last_refresh_time, last_key_time = result
            return game.running, last_refresh_time, last_key_time

        # Try keyboard input if not disabled
        if not KEYBOARD_DISABLED:
            result = handle_keyboard_input(game, current_time, last_key_time)
            if result is not None:
                game.running, last_refresh_time, last_key_time = result
                return game.running, last_refresh_time, last_key_time
            elif result is None and failed_attempts >= 3:
                logger.warning("Disabling keyboard input due to repeated failures")
                KEYBOARD_DISABLED = True

        # No input detected
        logger.debug("No input detected, idling")
        time.sleep(0.2)
    else:
        # Handle command mode
        game.running, last_refresh_time = process_command(game, current_time)
        display_current_map(game)
        display_status(game)

    return game.running, last_refresh_time, last_key_time