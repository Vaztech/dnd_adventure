from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ClassFeature:
    name: str
    level: int
    description: str

@dataclass
class DnDClass:
    name: str
    hit_die: int
    base_attack_bonus: str  # 'good', 'average', 'poor'
    saving_throws: Dict[str, str]  # 'good' or 'poor' for Fort/Ref/Will
    skill_points: int
    class_skills: List[str]
    spellcasting: Optional[Dict] = None
    features: Optional[List[ClassFeature]] = None
    
    def bab_at_level(self, level: int) -> int:
        if self.base_attack_bonus == 'good':
            return level
        elif self.base_attack_bonus == 'average':
            return level * 3 // 4
        else:
            return level // 2
    
    def save_at_level(self, save_type: str, level: int) -> int:
        if self.saving_throws[save_type] == 'good':
            return 2 + level // 2
        else:
            return level // 3

CORE_CLASSES = {
    "Fighter": DnDClass(
        name="Fighter",
        hit_die=10,
        base_attack_bonus="good",
        saving_throws={"Fort": "good", "Ref": "poor", "Will": "poor"},
        skill_points=2,
        class_skills=["Climb", "Craft", "Handle Animal", "Intimidate", "Jump", "Ride", "Swim"],
        features=[
            ClassFeature("Bonus Feat", 1, "Gain a bonus combat feat at 1st level and every even level")
        ]
    ),
    "Wizard": DnDClass(
        name="Wizard",
        hit_die=4,
        base_attack_bonus="poor",
        saving_throws={"Fort": "poor", "Ref": "poor", "Will": "good"},
        skill_points=2,
        class_skills=["Concentration", "Craft", "Decipher Script", "Knowledge (all)", "Profession", "Spellcraft"],
        spellcasting={
            "type": "arcane",
            "ability": "Intelligence",
            "spells_known": "learned",
            "spells_per_day": {
                1: [3, 1],   # [1st-level, 2nd-level]
                2: [4, 2],
                3: [4, 2, 1],  # [1st, 2nd, 3rd]
            }
        },
        features=[
            ClassFeature("Arcane Bond", 1, "Choose a familiar or bonded object"),
            ClassFeature("Scribe Scroll", 1, "Can create scrolls")
        ]
    )
}