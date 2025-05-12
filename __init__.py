"""
D&D 3.5e Adventure Framework
"""

from .game import Game  # Correct the name if your session class is 'Game'
from .character import PlayerCharacter
from .world import GameWorld
from .commands import CommandParser

# Core exports
__all__ = ['Game', 'PlayerCharacter', 'GameWorld', 'CommandParser']

# Version matches D&D edition
__version__ = '3.5.0'

# Initialize rule system on import
from .dnd35e import load_rules
_rules = load_rules()
# Initialize game world
from .world import GameWorld