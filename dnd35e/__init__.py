"""D&D 3.5e Rules Implementation"""
from .core.character import Character
from .core.classes import DnDClass, CORE_CLASSES
from .core.races import Race, RACES
from .core.spells import Spell, CORE_SPELLS
from .core.monsters import Monster, SRD_MONSTERS, get_monster, get_monsters_by_cr
from .core.items import Item, CORE_ITEMS
from .core.feats import Feat, CORE_FEATS
from .core.skills import Skill, CORE_SKILLS
from .mechanics.combat import Combat
from .mechanics.magic import Magic
from .mechanics.skills import SkillCheck

__version__ = "0.1.0"
__all__ = [
    'Character', 'DnDClass', 'Race', 'Spell', 'Monster', 'Item', 'Feat', 'Skill',
    'Combat', 'Magic', 'SkillCheck',
    'CORE_CLASSES', 'RACES', 'CORE_SPELLS', 'CORE_MONSTERS', 
    'CORE_ITEMS', 'CORE_FEATS', 'CORE_SKILLS'
]