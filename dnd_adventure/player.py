from typing import Dict, List, Optional
from player_manager.race_manager import RaceManager

class Player:
    def __init__(
        self,
        name: str,
        race: str,
        subrace: Optional[str],
        character_class: str,
        stats: Dict[str, int],
        spells: Dict[int, List[str]],
        level: int = 1,
        features: List[str] = None,
        subclass: Optional[str] = None,
        hit_points: int = 1,
        max_hit_points: int = 1,
        mp: int = 0,
        max_mp: int = 0,
        xp: int = 0,
    ):
        self.name = name
        self.race = race
        self.subrace = subrace
        self.character_class = character_class
        self.stats = stats
        self.spells = spells
        self.level = level
        self.features = features or []
        self.subclass = subclass
        self.hit_points = hit_points
        self.max_hit_points = max_hit_points
        self.mp = mp
        self.max_mp = max_mp
        self.xp = xp
        self.race_manager = RaceManager()
        self._apply_racial_modifiers()

    def _apply_racial_modifiers(self):
        race_data = self.race_manager.get_race_data(self.race)
        subrace_data = race_data.get("subraces", {}).get(self.subrace, {}) if self.subrace else {}
        modifiers = race_data.get("ability_modifiers", {})
        subrace_modifiers = subrace_data.get("ability_modifiers", {})
        
        for stat, value in modifiers.items():
            self.stats[stat] = self.stats.get(stat, 10) + value
        for stat, value in subrace_modifiers.items():
            self.stats[stat] = self.stats.get(stat, 10) + value

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "race": self.race,
            "subrace": self.subrace,
            "class": self.character_class,
            "stats": self.stats,
            "spells": self.spells,
            "level": self.level,
            "features": self.features,
            "subclass": self.subclass,
            "hit_points": self.hit_points,
            "max_hit_points": self.max_hit_points,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "xp": self.xp,
        }