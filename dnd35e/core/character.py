from dataclasses import dataclass
from typing import Dict, List, Optional

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
        self.ability_scores = AbilityScores()
        self.skills: Dict[str, int] = {}
        self.feats: List[str] = []
        self.spells_known: List['Spell'] = []
        self.equipment: Dict[str, 'Item'] = {}
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
    
    def __str__(self):
        return (f"{self.name} - Level {self.level} {self.race.name} {self.dnd_class.name}\n"
                f"HP: {self.hit_points}, AC: {self.armor_class()}\n"
                f"Ability Scores: {self.ability_scores}")