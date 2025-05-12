from dataclasses import dataclass
from typing import Dict, List, Optional
from .items import Item  # Assuming you have this defined

import random

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
    def __init__(self, name: str, race: 'Race', dnd_class: 'DnDClass', level: int = 1):
        self.name = name
        self.race = race
        self.dnd_class = dnd_class
        self.level = level
        self.xp = 0
        self.next_level_xp = 1000  # Basic D&D progression rule
        self.ability_scores = AbilityScores()
        self.skills: Dict[str, int] = {}
        self.feats: List[str] = []
        self.spells_known: List['Spell'] = []
        self.equipment: Dict[str, Item] = {}
        self.status_effects: List[str] = []
        self.hit_points: int = self.calculate_hit_points()
        
        # Apply racial modifiers
        self.race.apply_modifiers(self.ability_scores)

    def calculate_hit_points(self) -> int:
        con_mod = self.ability_scores.get_modifier('constitution')
        base = self.dnd_class.hit_die + con_mod
        additional = sum(max(1, (self.dnd_class.hit_die // 2 + 1 + con_mod)) 
                        for _ in range(self.level - 1))
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
        else:
            return bab + self.ability_scores.get_modifier('dexterity')

    def gain_xp(self, amount: int):
        print(f"{self.name} gains {amount} XP.")
        self.xp += amount
        if self.xp >= self.next_level_xp:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp = 0
        self.next_level_xp *= 2
        hp_gain = max(1, (self.dnd_class.hit_die // 2 + 1 + self.ability_scores.get_modifier('constitution')))
        self.hit_points += hp_gain
        print(f"{self.name} has reached level {self.level} and gained {hp_gain} HP!")

    def skill_check(self, skill: str, difficulty: int) -> bool:
        roll = random.randint(1, 20)
        bonus = self.skills.get(skill, 0)
        result = roll + bonus
        print(f"{self.name} attempts a {skill} check: Rolled {roll} + {bonus} = {result} vs DC {difficulty}")
        return result >= difficulty

    def apply_status(self, effect: str):
        if effect not in self.status_effects:
            self.status_effects.append(effect)
            print(f"{self.name} is now affected by: {effect}")

    def __str__(self):
        return (f"{self.name} - Level {self.level} {self.race.name} {self.dnd_class.name}\n"
                f"XP: {self.xp}/{self.next_level_xp} | HP: {self.hit_points}, AC: {self.armor_class()}\n"
                f"Status Effects: {', '.join(self.status_effects) if self.status_effects else 'None'}\n"
                f"Ability Scores: {self.ability_scores}")

class CharacterSheet:
    def __init__(self, character: Character):
        self.character = character
        self.name = character.name
        self.level = character.level
        self.race = character.race.name
        self.dnd_class = character.dnd_class.name
        self.ability_scores = character.ability_scores
        self.hit_points = character.hit_points
        self.skills = character.skills
        self.feats = character.feats
        self.spells_known = character.spells_known
        self.equipment = character.equipment

    def __str__(self):
        return (f"Character Sheet for {self.name}, Level {self.level}\n"
                f"Race: {self.race}, Class: {self.dnd_class}\n"
                f"HP: {self.hit_points}\n"
                f"Skills: {self.skills}\n"
                f"Feats: {self.feats}\n"
                f"Spells Known: {self.spells_known}\n"
                f"Equipment: {self.equipment}\n"
                f"Ability Scores: {self.ability_scores}")
