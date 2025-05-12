from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class FeatPrerequisite:
    type: str  # 'ability', 'feat', 'skill', 'base_attack_bonus'
    value: str  # e.g. "STR 13", "Power Attack", "Jump 8", "BAB +1"

@dataclass
class Feat:
    name: str
    description: str
    benefit: str
    prerequisites: List[FeatPrerequisite]
    type: str  # 'general', 'combat', 'metamagic', 'item creation'
    special: Optional[str] = None
    multiple: bool = False  # Can be taken multiple times?

CORE_FEATS = {
    "Power Attack": Feat(
        name="Power Attack",
        description="Trade attack bonus for damage bonus",
        benefit="On your action, before making attack rolls for a round, you may choose to subtract a number from all melee attack rolls and add the same number to all melee damage rolls. This number may not exceed your base attack bonus.",
        prerequisites=[
            FeatPrerequisite(type="ability", value="STR 13"),
            FeatPrerequisite(type="base_attack_bonus", value="+1")
        ],
        type="combat"
    ),
    "Improved Initiative": Feat(
        name="Improved Initiative",
        description="You get a +4 bonus on initiative checks",
        benefit="You get a +4 bonus on initiative checks.",
        prerequisites=[],
        type="general"
    )
}