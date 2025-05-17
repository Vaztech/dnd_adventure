import random
import logging
from typing import Dict, List, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .dnd35e.core.monsters import Monster

from dnd_adventure.data_loaders.spell_loader import SpellLoader
from dnd_adventure.spells import Spell

logger = logging.getLogger(__name__)

class Character:
    def __init__(self, name: str, race_name: str, class_name: str, stats: List[int], known_spells: Dict[int, List[str]], subrace_name: Optional[str] = None, class_data: Dict = None):
        self.name = name
        self.race_name = race_name
        self.subrace_name = subrace_name
        self.class_name = class_name
        self.class_data = class_data or {}
        self.level = 1
        self.xp = 0
        self.stats = stats  # [Str, Dex, Con, Int, Wis, Cha]
        self.known_spells = known_spells
        self.hit_points = self.calculate_hit_points()
        self.max_hit_points = self.hit_points
        self.mp = 10 if self.class_data.get("spellcasting", False) else 0
        self.max_mp = self.mp
        self.skills = {}
        self.feats = []
        self.equipment = {}
        self.armor_class = self.calculate_armor_class()
        self.bab = self.calculate_bab()

    def calculate_hit_points(self) -> int:
        con_mod = (self.stats[2] - 10) // 2
        hit_die = self.class_data.get("hit_die", 8)  # Default to 8
        return hit_die + con_mod

    def calculate_armor_class(self) -> int:
        dex_mod = (self.stats[1] - 10) // 2
        return 10 + dex_mod

    def calculate_bab(self) -> int:
        bab_progression = self.class_data.get("bab_progression", "slow")
        return 1 if bab_progression == "fast" else 0

    def get_stat_modifier(self, stat_index: int) -> int:
        return (self.stats[stat_index] - 10) // 2

    def get_spellcasting_stat_index(self) -> int:
        stat_map = {
            "Intelligence": 3,
            "Wisdom": 4,
            "Charisma": 5
        }
        spellcasting_stat = self.class_data.get("spellcasting_stat")
        return stat_map.get(spellcasting_stat, 3)  # Default to Intelligence

    def gain_xp(self, amount: int):
        self.xp += amount
        logger.info(f"{self.name} gains {amount} XP.")

    def cast_spell(self, spell_name: str, target: Optional['Monster']) -> str:
        spell_level = None
        for level, spells in self.known_spells.items():
            if spell_name in spells:
                spell_level = level
                break
        if spell_level is None:
            return f"{self.name} does not know {spell_name}!"
        mp_cost = 1 if spell_level == 0 else 2
        if self.mp < mp_cost:
            return f"{self.name} is out of magic points! (Need {mp_cost} MP, have {self.mp})"
        loader = SpellLoader()
        spell_obj = loader.get_spell_by_name(spell_name, self.class_name)
        if not spell_obj:
            return f"Spell data for {spell_name} not found!"
        stat_index = self.get_spellcasting_stat_index()
        if not spell_obj.can_cast(self.level, self.stats[stat_index]):
            return f"{self.name} lacks the ability score to cast {spell_name}!"
        self.mp -= mp_cost
        stat_modifier = self.get_stat_modifier(stat_index)
        if target and spell_obj.damage:
            damage_str = spell_obj.damage.split()[0]
            total_damage = 0
            if "d" in damage_str:
                num_dice, rest = damage_str.split("d")
                num_dice = int(num_dice) if num_dice else 1
                if "+" in rest:
                    die_size, bonus = rest.split("+")
                    bonus = int(bonus)
                else:
                    die_size, bonus = rest, 0
                die_size = int(die_size)
                total_damage = sum(random.randint(1, die_size) for _ in range(num_dice)) + bonus + stat_modifier
            else:
                total_damage = int(damage_str) + stat_modifier
            total_damage = max(1, total_damage)
            target.hit_points -= total_damage
            return f"{self.name} casts {spell_name}, dealing {total_damage} damage to {target.name}! (Base: {spell_obj.damage}, +{stat_modifier} from stat)"
        elif spell_obj.healing:
            healing_str = spell_obj.healing.split()[0]
            total_healing = 0
            if "d" in healing_str:
                num_dice, die_size = map(int, healing_str.split("d"))
                bonus = min(self.level, 5)
                total_healing = sum(random.randint(1, die_size) for _ in range(num_dice)) + bonus + stat_modifier
            else:
                total_healing = int(healing_str) + stat_modifier
            total_healing = max(1, total_healing)
            self.hit_points = min(self.max_hit_points, self.hit_points + total_healing)
            return f"{self.name} casts {spell_name}, healing {total_healing} HP! (Base: {spell_obj.healing}, +{stat_modifier} from stat)"
        else:
            return f"{self.name} casts {spell_name}: {spell_obj.description}"

    def __str__(self):
        return f"{self.name}, Level {self.level} {self.race_name} {self.class_name}"