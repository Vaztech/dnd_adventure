from dataclasses import dataclass
from typing import Dict, List, Optional
from dnd_adventure.data_loader import DataLoader

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

def get_default_class() -> Dict:
    loader = DataLoader()
    classes = loader.load_classes_from_json()
    return classes.get("Fighter", {})

def get_class_by_name(name: str) -> Optional[Dict]:
    loader = DataLoader()
    classes = loader.load_classes_from_json()
    return classes.get(name)

def get_all_classes() -> List[Dict]:
    loader = DataLoader()
    classes = loader.load_classes_from_json()
    return list(classes.values())