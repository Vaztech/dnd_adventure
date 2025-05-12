"""
D&D 3.5e Adventure Framework
"""

from .game import GameSession
from .character import PlayerCharacter
from .world import GameWorld
from .commands import CommandParser

# Core exports
__all__ = ['GameSession', 'PlayerCharacter', 'GameWorld', 'CommandParser']

# Version matches D&D edition
__version__ = '3.5.0'

# Initialize rule system on import
from .dnd35e import load_rules
_rules = load_rules()