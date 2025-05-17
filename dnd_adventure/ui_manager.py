import logging
from dnd_adventure.ui import display_current_map

logger = logging.getLogger(__name__)

class UIManager:
    def __init__(self, game):
        self.game = game

    def display_current_map(self):
        logger.debug("Displaying current map")
        display_current_map(self.game)