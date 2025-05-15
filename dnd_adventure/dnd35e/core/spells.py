from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
from dnd_adventure.spells import Spell

logger = logging.getLogger(__name__)

@dataclass
class Spell:
    name: str
    level: int
    school: str
    subschool: Optional[str]
    descriptor: Optional[List[str]]
    casting_time: str
    components: Dict[str, bool]  # verbal, somatic, material, focus, divine_focus
    spell_range: str
    area: Optional[str]
    target: Optional[str]
    duration: str
    saving_throw: Optional[str]
    spell_resistance: Optional[bool]
    description: str
    classes: Dict[str, int]  # {"Wizard": 3, "Sorcerer": 3}
    
    def can_cast(self, caster_level: int, ability_score: int) -> bool:
        """Check if a spell can be cast based on caster level and ability score"""
        min_level = self.level * 2 - 1
        return caster_level >= min_level and ability_score >= 10 + self.level
    
    def __str__(self) -> str:
        return f"{self.name} (Level {self.level} {self.school})"
    
    def get_full_description(self) -> str:
        """Return a formatted description of the spell."""
        descriptors = ", ".join(self.descriptor) if self.descriptor else "None"
        return f"""
{self.name}
Level: {self.level}
School: {self.school}
Descriptor: {descriptors}
Casting Time: {self.casting_time}
Range: {self.spell_range}
Target: {self.target or 'N/A'}
Area: {self.area or 'N/A'}
Duration: {self.duration}
Saving Throw: {self.saving_throw or 'None'}
Spell Resistance: {'Yes' if self.spell_resistance else 'No'}
Description: {self.description}
"""

CORE_SPELLS = {
    "Magic Missile": Spell(
        name="Magic Missile",
        level=1,
        school="Evocation",
        subschool=None,
        descriptor=["Force"],
        casting_time="1 standard action",
        components={"verbal": True, "somatic": True, "material": False, "focus": False, "divine_focus": False},
        spell_range="Medium (100 ft. + 10 ft./level)",
        area=None,
        target="Up to five creatures, no two of which can be more than 15 ft. apart",
        duration="Instantaneous",
        saving_throw="None",
        spell_resistance=True,
        description="A missile of magical energy darts forth and strikes its target.",
        classes={"Wizard": 1, "Sorcerer": 1}
    ),
    "Fireball": Spell(
        name="Fireball",
        level=3,
        school="Evocation",
        subschool=None,
        descriptor=["Fire"],
        casting_time="1 standard action",
        components={"verbal": True, "somatic": True, "material": True, "focus": False, "divine_focus": False},
        spell_range="Long (400 ft. + 40 ft./level)",
        area="20-ft.-radius spread",
        target=None,
        duration="Instantaneous",
        saving_throw="Reflex half",
        spell_resistance=True,
        description="A fireball spell generates a searing explosion of flame.",
        classes={"Wizard": 3, "Sorcerer": 3}
    )
}

# Utility functions for spell retrieval
def get_spell_by_name(name: str) -> Optional[Spell]:
    """
    Get a spell by name.
    
    Args:
        name: Name of the spell to retrieve
        
    Returns:
        Spell object if found, None otherwise
    """
    return CORE_SPELLS.get(name)

def get_spells_by_level(level: int) -> List[Spell]:
    """
    Get all spells of a specified level.
    
    Args:
        level: Spell level to retrieve
        
    Returns:
        List of spell objects of the requested level
    """
    return [spell for spell in CORE_SPELLS.values() if spell.level == level]

def get_spells_by_school(school: str) -> List[Spell]:
    """
    Get all spells from a specific school of magic.
    
    Args:
        school: School of magic (e.g., "Evocation")
        
    Returns:
        List of spell objects from the requested school
    """
    return [spell for spell in CORE_SPELLS.values() if spell.school.lower() == school.lower()]

def get_spells_for_class(class_name: str, max_level: Optional[int] = None) -> List[Spell]:
    """
    Get all spells available to a specific class.
    
    Args:
        class_name: Class name (e.g., "Wizard")
        max_level: Maximum spell level to include (optional)
        
    Returns:
        List of spell objects available to the class
    """
    spells = [
        spell for spell in CORE_SPELLS.values() 
        if class_name in spell.classes
    ]
    
    if max_level is not None:
        spells = [spell for spell in spells if spell.classes.get(class_name, 99) <= max_level]
        
    return spells