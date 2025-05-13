from dataclasses import dataclass
from typing import Dict, List, Union
import logging
from .items import Item
from .races import Race, get_race_by_name
from .classes import DnDClass, get_class_by_name
from .spells import Spell
import random

logger = logging.getLogger(__name__)

@dataclass
class AbilityScores:
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    def get_modifier(self, ability: str) -> int:
        score = getattr(self, ability.lower())
        return (score - 10) // 2

    def __str__(self):
        return (f"STR: {self.strength} ({self.get_modifier('strength'):+d}), "
                f"DEX: {self.dexterity} ({self.get_modifier('dexterity'):+d}), "
                f"CON: {self.constitution} ({self.get_modifier('constitution'):+d}), "
                f"INT: {self.intelligence} ({self.get_modifier('intelligence'):+d}), "
                f"WIS: {self.wisdom} ({self.get_modifier('wisdom'):+d}), "
                f"CHA: {self.charisma} ({self.get_modifier('charisma'):+d})")

class Character:
    def __init__(self, name: str, race: Union[str, Race], dnd_class: Union[str, DnDClass], level: int = 1, **kwargs):
        logger.debug(f"Character.__init__ called with: name={name}, race={race}, dnd_class={dnd_class}, level={level}, kwargs={kwargs}")
        if kwargs:
            logger.warning(f"Unexpected keyword arguments in Character.__init__: {kwargs}")
        self.name = name
        self.race: Race = get_race_by_name(race) if isinstance(race, str) else race
        if not isinstance(self.race, Race):
            raise ValueError(f"Invalid race: {race}. Must be a Race object or valid race name.")
        self.dnd_class: DnDClass = get_class_by_name(dnd_class) if isinstance(dnd_class, str) else dnd_class
        if not isinstance(self.dnd_class, DnDClass):
            raise ValueError(f"Invalid dnd_class: {dnd_class}. Must be a DnDClass object or valid class name.")
        self.level = max(1, level)
        self.xp = 0
        self.next_level_xp = 1000
        self.ability_scores = AbilityScores()
        self.skills: Dict[str, int] = {}
        self.feats: List[str] = []
        self.spells_known: List[Spell] = []
        self.equipment: Dict[str, Item] = {}
        self.status_effects: List[str] = []
        self.hit_points: int = 0
        self.race.apply_modifiers(self.ability_scores)
        self.hit_points = self.calculate_hit_points()

    def calculate_hit_points(self) -> int:
        con_mod = self.ability_scores.get_modifier('constitution')
        base = self.dnd_class.hit_die + con_mod
        additional = sum(max(1, (self.dnd_class.hit_die // 2 + 1 + con_mod)) for _ in range(self.level - 1))
        return base + additional

    def armor_class(self) -> int:
        base = 10
        dex_mod = self.ability_scores.get_modifier('dexterity')
        armor_bonus = self.equipment.get('armor', Item()).ac_bonus if 'armor' in self.equipment else 0
        shield_bonus = self.equipment.get('shield', Item()).ac_bonus if 'shield' in self.equipment else 0
        return base + dex_mod + armor_bonus + shield_bonus

    def attack_bonus(self, attack_type: str = 'melee') -> int:
        bab = self.dnd_class.bab_at_level(self.level)
        if attack_type == 'melee':
            return bab + self.ability_scores.get_modifier('strength')
        return bab + self.ability_scores.get_modifier('dexterity')

    def gain_xp(self, amount: int):
        logger.info(f"{self.name} gains {amount} XP.")
        self.xp += amount
        if self.xp >= self.next_level_xp:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp = 0
        self.next_level_xp *= 2
        hp_gain = max(1, (self.dnd_class.hit_die // 2 + 1 + self.ability_scores.get_modifier('constitution')))
        self.hit_points += hp_gain
        logger.info(f"{self.name} has reached level {self.level} and gained {hp_gain} HP!")

    def skill_check(self, skill: str, difficulty: int) -> bool:
        roll = random.randint(1, 20)
        bonus = self.skills.get(skill, 0)
        result = roll + bonus
        logger.info(f"{self.name} attempts {skill}: {roll} + {bonus} = {result} vs DC {difficulty}")
        return result >= difficulty

    def apply_status(self, effect: str):
        if effect not in self.status_effects:
            self.status_effects.append(effect)
            logger.info(f"{self.name} is now {effect}")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "race": self.race.name,
            "dnd_class": self.dnd_class.name,
            "level": self.level,
            "xp": self.xp,
            "next_level_xp": self.next_level_xp,
            "ability_scores": self.ability_scores.__dict__,
            "skills": self.skills,
            "feats": self.feats,
            "status_effects": self.status_effects,
            "hit_points": self.hit_points
        }

    @staticmethod
    def from_dict(data: dict) -> 'Character':
        init_args = {
            "name": data.get("name", "Unknown"),
            "race": data.get("race", "Human"),
            "dnd_class": data.get("dnd_class", "Fighter"),
            "level": data.get("level", 1)
        }
        char = Character(**init_args)
        char.xp = data.get("xp", 0)
        char.next_level_xp = data.get("next_level_xp", 1000)
        char.ability_scores = AbilityScores(**data.get("ability_scores", {}))
        char.skills = data.get("skills", {})
        char.feats = data.get("feats", [])
        char.status_effects = data.get("status_effects", [])
        char.hit_points = data.get("hit_points", char.calculate_hit_points())
        char.hit_points = char.calculate_hit_points()
        return char

    def __str__(self):
        return (f"{self.name} - Level {self.level} {self.race.name} {self.dnd_class.name}\n"
                f"HP: {self.hit_points} | AC: {self.armor_class()} | XP: {self.xp}/{self.next_level_xp}\n"
                f"Status: {', '.join(self.status_effects) or 'Normal'}\n"
                f"Abilities: {self.ability_scores}")

# Debug logging after class definition
logger.debug(f"Using Character class from: {Character.__module__}")