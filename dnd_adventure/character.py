import random
import logging
from typing import Dict, List, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .monster import Monster

from dnd_adventure.data_loader import DataLoader
from dnd_adventure.spells import Spell

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
        self.mp = 10 if class_name in ["Wizard", "Sorcerer", "Cleric", "Druid", "Bard", "Paladin", "Ranger"] else 0
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

    def get_spellcasting_stat_index(self) -> int:
        stat_map = {
            "Wizard": 3,  # Intelligence
            "Sorcerer": 5,  # Charisma
            "Cleric": 4,  # Wisdom
            "Druid": 4,  # Wisdom
            "Bard": 5,  # Charisma
            "Paladin": 4,  # Wisdom
            "Ranger": 4  # Wisdom
        }
        return stat_map.get(self.class_name, 3)  # Default to Intelligence

    def gain_xp(self, amount: int):
        self.xp += amount
        logger.info(f"{self.name} gains {amount} XP.")

    def cast_spell(self, spell_name: str, target: Optional['Monster']) -> str:
        # Check if spell is known
        spell_level = None
        for level, spells in self.known_spells.items():
            if spell_name in spells:
                spell_level = level
                break
        if spell_level is None:
            return f"{self.name} does not know {spell_name}!"

        # Calculate MP cost
        mp_cost = 1 if spell_level == 0 else 2
        if self.mp < mp_cost:
            return f"{self.name} is out of magic points! (Need {mp_cost} MP, have {self.mp})"

        # Retrieve spell data
        loader = DataLoader()
        spell_obj = loader.get_spell_by_name(spell_name, self.class_name)
        if not spell_obj:
            return f"Spell data for {spell_name} not found!"

        # Check casting requirements
        stat_index = self.get_spellcasting_stat_index()
        if not spell_obj.can_cast(self.level, self.stats[stat_index]):
            return f"{self.name} lacks the ability score to cast {spell_name}!"

        # Deduct MP
        self.mp -= mp_cost

        # Process spell effect
        stat_modifier = self.get_stat_modifier(stat_index)
        if target and spell_obj.damage:
            # Parse damage (e.g., "1d4+1 per missile (force)", "1d3 acid")
            damage_str = spell_obj.damage.split()[0]  # Get "1d4+1" or "1d3"
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
            # Parse healing (e.g., "1d8 +1/level (max +5)")
            healing_str = spell_obj.healing.split()[0]  # Get "1d8"
            total_healing = 0
            if "d" in healing_str:
                num_dice, die_size = map(int, healing_str.split("d"))
                bonus = min(self.level, 5)  # Max +5 for Cure Light Wounds
                total_healing = sum(random.randint(1, die_size) for _ in range(num_dice)) + bonus + stat_modifier
            else:
                total_healing = int(healing_str) + stat_modifier
            total_healing = max(1, total_healing)
            self.hit_points = min(self.max_hit_points, self.hit_points + total_healing)
            return f"{self.name} casts {spell_name}, healing {total_healing} HP! (Base: {spell_obj.healing}, +{stat_modifier} from stat)"

        else:
            # Non-damaging/non-healing spell
            return f"{self.name} casts {spell_name}: {spell_obj.description}"

    def __str__(self):
        return f"{self.name}, Level {self.level} {self.race_name} {self.class_name}"