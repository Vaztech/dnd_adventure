import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

class LoreManager:
    def __init__(self, game):
        self.game = game

    def print_lore(self):
        self.game.message = ""
        logger.debug("Printing lore")
        try:
            logger.debug(f"World name: {self.game.world.name}, History: {self.game.world.history}")
            if not hasattr(self.game.world, 'history') or not self.game.world.history:
                print(f"{Fore.YELLOW}No history available for {self.game.world.name}.{Style.RESET_ALL}")
                logger.debug("No history available")
                return
            print(f"\n{Fore.YELLOW}History of {self.game.world.name}:{Style.RESET_ALL}")
            for era in self.game.world.history:
                print(f"\n{Fore.LIGHTYELLOW_EX}{era['name']}:{Style.RESET_ALL}")
                for event in era["events"]:
                    print(f"  {Fore.WHITE}{event['year']}: {event['desc']}{Style.RESET_ALL}")
            logger.debug("Lore displayed")
        except Exception as e:
            logger.error(f"Error printing lore: {e}")
            print(f"{Fore.RED}An error occurred while displaying the lore: {e}{Style.RESET_ALL}")