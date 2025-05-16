import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

def process_command(game, current_time: float) -> tuple[bool, float]:
    print("> ", end="", flush=True)
    try:
        cmd = input().strip().lower()
        logger.debug(f"Command input: {cmd}")
        if not cmd:
            game.mode = "movement"
            logger.debug("Switched to movement mode")
        else:
            game.handle_command(cmd)
            logger.debug(f"Processed command: {cmd}")
        return game.running, current_time
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}Game interrupted. Farewell, traveler!{Style.RESET_ALL}")
        logger.info("Game interrupted by user")
        return False, current_time
    except Exception as e:
        logger.error(f"Error in command mode: {e}")
        print(f"{Fore.RED}Error processing command: {e}{Style.RESET_ALL}")
        return game.running, current_time