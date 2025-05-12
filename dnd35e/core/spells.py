from dataclasses import dataclass
from typing import List, Dict, Optional

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