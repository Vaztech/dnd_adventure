import random
from typing import Dict, Union

class SkillCheck:
    @staticmethod
    def make_check(skill_rank: int, ability_mod: int, dc: int, 
                  modifiers: Dict[str, int] = None) -> Dict[str, Union[bool, int]]:
        """Make a skill check against a DC"""
        if modifiers is None:
            modifiers = {}
        
        roll = random.randint(1, 20)
        total_mod = skill_rank + ability_mod + sum(modifiers.values())
        total = roll + total_mod
        
        return {
            'roll': roll,
            'skill_rank': skill_rank,
            'ability_mod': ability_mod,
            'modifiers': modifiers,
            'total_mod': total_mod,
            'total': total,
            'dc': dc,
            'success': total >= dc,
            'degree_of_success': total - dc
        }
    
    @staticmethod
    def opposed_check(active_skill: int, active_ability_mod: int,
                     passive_skill: int, passive_ability_mod: int,
                     active_modifiers: Dict[str, int] = None,
                     passive_modifiers: Dict[str, int] = None) -> Dict[str, Union[bool, int]]:
        """Make an opposed skill check"""
        if active_modifiers is None:
            active_modifiers = {}
        if passive_modifiers is None:
            passive_modifiers = {}
        
        active_roll = random.randint(1, 20)
        passive_roll = random.randint(1, 20)
        
        active_total = active_roll + active_skill + active_ability_mod + sum(active_modifiers.values())
        passive_total = passive_roll + passive_skill + passive_ability_mod + sum(passive_modifiers.values())
        
        return {
            'active_roll': active_roll,
            'passive_roll': passive_roll,
            'active_total': active_total,
            'passive_total': passive_total,
            'success': active_total > passive_total,
            'tie': active_total == passive_total,
            'degree_of_difference': active_total - passive_total
        }
