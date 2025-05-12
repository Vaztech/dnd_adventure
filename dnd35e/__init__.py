# Import necessary modules from core
from .core.character import Character
from .core.classes import DnDClass, CORE_CLASSES
from .core.races import Race, RACES
from .core.spells import Spell, CORE_SPELLS
from .core.monsters import Monster, SRD_MONSTERS  # Correctly importing from core.monsters
from .core.items import Item, CORE_ITEMS
from .core.feats import Feat, CORE_FEATS
from .core.skills import Skill, CORE_SKILLS

__all__ = [
    'Character', 'DnDClass', 'Race', 'Spell', 'Monster', 'Item', 'Feat', 'Skill',
    'CORE_CLASSES', 'RACES', 'CORE_SPELLS', 'SRD_MONSTERS', 'CORE_ITEMS', 'CORE_FEATS', 'CORE_SKILLS'
]

# Import all core modules
from .core import *

# Import combat from mechanics (corrected import)
from .mechanics import Combat
