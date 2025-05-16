import random
import logging
from typing import Dict, List, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .monster import Monster

logger = logging.getLogger(__name__)

class Character:
    def __init__(self, name: str, race_name: str, class_name: str, stats: List[int], known_spells: Dict[int, List[str]]):
        self.name = name
        self.race_name = race_name
        self.class_name = class_name
        self.level = 1
        self.xp = 0
        self.stats = stats  # [Str, Dex, Con, Int, Wis, Cha]
        self.known_spells = known_spells
        self.hit_points = self.calculate_hit_points()
        self.max_hit_points = self.hit_points
        self.mp = 10 if class_name in ["Wizard", "Sorcerer", "Cleric", "Druid", "Bard"] else 0
        self.max_mp = self.mp
        self.skills = {}
        self.feats = []
        self.equipment = {}
        self.armor_class = self.calculate_armor_class()
        self.bab = 1 if class_name in ["Fighter", "Barbarian", "Paladin", "Ranger"] else 0

    def calculate_hit_points(self) -> int:
        con_mod = (self.stats[2] - 10) // 2
        hit_die = 10 if self.class_name == "Fighter" else 8
        return hit_die + con_mod

    def calculate_armor_class(self) -> int:
        dex_mod = (self.stats[1] - 10) // 2
        return 10 + dex_mod

    def get_stat_modifier(self, stat_index: int) -> int:
        return (self.stats[stat_index] - 10) // 2

    def gain_xp(self, amount: int):
        self.xp += amount
        logger.info(f"{self.name} gains {amount} XP.")

    def cast_spell(self, spell_name: str, target: Optional['Monster']) -> str:
        if not any(spell_name in spells for spells in self.known_spells.values()):
            return f"{self.name} does not know {spell_name}!"
        if self.mp < 1:
            return f"{self.name} is out of magic points!"
        self.mp -= 1
        if target:
            damage = random.randint(1, 6)
            target.hit_points -= damage
            return f"{self.name} casts {spell_name}, dealing {damage} damage to {target.name}!"
        return f"{self.name} casts {spell_name}!"

    def __str__(self):
        return f"{self.name}, Level {self.level} {self.race_name} {self.class_name}"