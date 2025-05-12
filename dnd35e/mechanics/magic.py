import random
from typing import Dict, Union
from ..core.spells import Spell

class Magic:
    @staticmethod
    def calculate_spell_dc(spell: Spell, caster_level: int, ability_mod: int) -> int:
        """Calculate spell save DC"""
        return 10 + spell.level + ability_mod
    
    @staticmethod
    def check_spell_resistance(caster_level: int, spell_resistance: int) -> bool:
        """Determine if spell penetrates spell resistance"""
        roll = random.randint(1, 20)
        return (roll + caster_level) >= spell_resistance
    
    @staticmethod
    def apply_saving_throw(save_type: str, save_dc: int, save_bonus: int) -> Dict[str, Union[bool, str]]:
        """Determine if a saving throw succeeds"""
        roll = random.randint(1, 20)
        total = roll + save_bonus
        
        result = {
            'roll': roll,
            'bonus': save_bonus,
            'total': total,
            'dc': save_dc,
            'success': total >= save_dc,
            'effect': None
        }
        
        if save_type.lower() == 'reflex':
            result['effect'] = 'half damage' if result['success'] else 'full damage'
        elif save_type.lower() == 'will':
            result['effect'] = 'negates' if result['success'] else 'afflicted'
        elif save_type.lower() == 'fortitude':
            result['effect'] = 'partial effect' if result['success'] else 'full effect'
        
        return result
    
    @staticmethod
    def roll_spell_damage(spell: Spell, caster_level: int) -> int:
        """Calculate spell damage based on caster level"""
        if 'd' in spell.description:  # Simple heuristic to find damage dice
            # Extract dice from description (e.g., "1d6 per level (max 10d6)")
            try:
                dice_part = spell.description.split('d')[0].split()[-1]
                dice_count = int(dice_part)
                max_dice = 10  # Default max
                
                if 'max' in spell.description.lower():
                    max_part = spell.description.lower().split('max')[-1].split('d')[0].strip()
                    max_dice = int(max_part)
                
                dice_to_roll = min(dice_count * caster_level, max_dice)
                return sum(random.randint(1, 6) for _ in range(dice_to_roll))
            except (ValueError, IndexError):
                return 0
        return 0
