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
    description: str
    hit_die: int
    base_attack_bonus: str
    saving_throws: Dict[str, str]
    skill_points: int
    class_skills: List[str]
    spellcasting: Optional[Dict] = None
    features: Optional[List[ClassFeature]] = None
    subclasses: Optional[Dict[str, Dict]] = None

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

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "hit_die": self.hit_die,
            "base_attack_bonus": self.base_attack_bonus,
            "saving_throws": self.saving_throws,
            "skill_points": self.skill_points,
            "class_skills": self.class_skills,
            "spellcasting": self.spellcasting,
            "features": [
                {"name": f.name, "level": f.level, "description": f.description}
                for f in self.features or []
            ],
            "subclasses": self.subclasses
        }

CORE_CLASSES = {
    "Fighter": DnDClass(
        name="Fighter",
        description="A versatile combatant skilled in a wide array of weapons and tactics.",
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
        description="A scholarly arcane caster who masters magic through study and spellbooks.",
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
                1: [3, 1],
                2: [4, 2],
                3: [4, 2, 1],
            }
        },
        features=[
            ClassFeature("Arcane Bond", 1, "Choose a familiar or bonded object"),
            ClassFeature("Scribe Scroll", 1, "Can create scrolls")
        ]
    )
}

def get_default_class() -> DnDClass:
    return CORE_CLASSES["Fighter"]

def get_class_by_name(name: str) -> Optional[DnDClass]:
    return CORE_CLASSES.get(name)

def get_all_classes() -> List[DnDClass]:
    return list(CORE_CLASSES.values())