from typing import Dict, List, Optional

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
        features: Optional[List[str]] = None,
    ):
        self.name = name
        self.race = race
        self.subrace = subrace
        self.character_class = character_class
        self.stats = stats
        self.spells = spells
        self.level = level
        self.features = features or []
        # Combat attributes
        self.max_hit_points = 6 + (stats["Constitution"] - 10) // 2  # Rogue hit die 6
        self.hit_points = self.max_hit_points
        self.max_mp = 0  # Rogue has no MP
        self.mp = 0
        self.bab = 0  # Base attack bonus (Rogue level 1)
        self.armor_class = 10 + (stats["Dexterity"] - 10) // 2  # Base AC + Dex
        self.xp = 0
        self.known_spells = spells  # Alias for compatibility

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
            "hit_points": self.hit_points,
            "max_hit_points": self.max_hit_points,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "xp": self.xp,
        }

    def get_stat_modifier(self, stat_index: int) -> int:
        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        return (self.stats[stat_names[stat_index]] - 10) // 2

    def gain_xp(self, xp: int):
        self.xp += xp
        # Placeholder: Level-up check delegated to PlayerManager

    def cast_spell(self, spell_name: str, target: Optional[object]) -> str:
        if spell_name not in sum(self.known_spells.values(), []):
            return f"{self.name} does not know {spell_name}!"
        # Placeholder: Rogue has no spells
        return f"{self.name} cannot cast spells!"

    def check_level_up(self):
        # Placeholder: Level-up logic in PlayerManager
        pass