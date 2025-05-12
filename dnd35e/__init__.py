# Import necessary modules from core
from .core.character import Character
from .core.classes import DnDClass, CORE_CLASSES
from .core.races import Race, RACES
from .core.spells import Spell, CORE_SPELLS
from .core.monsters import Monster, SRD_MONSTERS  # Corrected import from core.monsters
from .core.items import Item, CORE_ITEMS
from .core.feats import Feat, CORE_FEATS
from .core.skills import Skill, CORE_SKILLS

# Import load_rules from the appropriate module
try:
    from .core.rules import load_rules  # Ensure the path is correct
except ImportError:
    print("Warning: load_rules function not found in core.rules")

# Import combat from mechanics
from .mechanics import Combat

# Import necessary data loading functions
from .core.data import load_monsters, load_locations, load_spells, load_classes, load_races, load_feats, load_items

__all__ = [
    'Character', 'DnDClass', 'Race', 'Spell', 'Monster', 'Item', 'Feat', 'Skill',
    'CORE_CLASSES', 'RACES', 'CORE_SPELLS', 'SRD_MONSTERS', 'CORE_ITEMS', 'CORE_FEATS', 'CORE_SKILLS',
    'Combat', 'load_rules', 'load_monsters', 'load_locations', 'load_spells', 'load_classes', 'load_races', 'load_feats', 'load_items'
]
