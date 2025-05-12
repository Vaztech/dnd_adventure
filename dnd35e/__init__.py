# Import necessary modules from core
from .core.character import Character
from .core.classes import DnDClass, CORE_CLASSES
from .core.races import Race, RACES
from .core.spells import Spell, CORE_SPELLS
from .core.monsters import Monster, SRD_MONSTERS  # Corrected import from core.monsters
from .core.items import Item, CORE_ITEMS
from .core.feats import Feat, CORE_FEATS
from .core.skills import Skill, CORE_SKILLS
# dnd35e/__init__.py
from .core.rules import load_rules  # Correct import for load_rules function
from .core.items import Item, CORE_ITEMS
from .core.feats import Feat, CORE_FEATS

# Import load_rules from the appropriate module
try:
    from .core.rules import load_rules  # Ensure the path is correct
except ImportError:
    print("Warning: load_rules function not found in core.rules")

# Import combat from mechanics
from .mechanics import Combat

__all__ = [
    'Character', 'DnDClass', 'Race', 'Spell', 'Monster', 'Item', 'Feat', 'Skill',
    'CORE_CLASSES', 'RACES', 'CORE_SPELLS', 'SRD_MONSTERS', 'CORE_ITEMS', 'CORE_FEATS', 'CORE_SKILLS',
    'Combat', 'load_rules'  # Added Combat and load_rules to __all__
]
