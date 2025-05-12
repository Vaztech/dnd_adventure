from typing import Dict, Union
from ..core.character import Character
from ..core.monsters import Monster, SRD_MONSTERS
import random

class Combat:
    @staticmethod
    def resolve_attack(attacker: Union[Character, Monster], 
                      defender: Union[Character, Monster],
                      attack_name: str = None) -> Dict:
        """
        Resolve a combat attack with full monster capabilities
        Returns dictionary with results
        """
        result = {
            'attacker': attacker.name,
            'defender': defender.name,
            'hit': False,
            'critical': False,
            'damage': 0,
            'special_effects': []
        }

        # Determine attack bonus
        if isinstance(attacker, Character):
            attack_bonus = attacker.attack_bonus()
            weapon = attacker.get_equipped_weapon()
            damage_dice = weapon.dnd_item.damage if weapon else "1d3"
            damage_mod = attacker.ability_scores.get_modifier('strength')
        else:
            # Monster attack
            if attack_name:
                attack = next((a for a in attacker.attacks 
                             if a.name.lower() == attack_name.lower()), None)
                if not attack:
                    attack = attacker.attacks[0]
            else:
                attack = attacker.attacks[0]
                
            attack_bonus = attack.attack_bonus
            damage_dice = attack.damage
            damage_mod = (attacker.abilities['STR'] - 10) // 2

        # Make attack roll
        attack_roll = random.randint(1, 20)
        is_critical = attack_roll == 20
        result['attack_roll'] = attack_roll
        result['attack_bonus'] = attack_bonus
        
        # Check for hit
        if is_critical or (attack_roll + attack_bonus) >= defender.armor_class():
            result['hit'] = True
            result['critical'] = is_critical
            
            # Calculate damage
            damage = Combat.roll_dice(damage_dice) + damage_mod
            if is_critical:
                damage *= 2  # Simplified critical - some weapons have higher multipliers
            result['damage'] = max(1, damage)
            
            # Apply special effects
            if isinstance(attacker, Monster) and hasattr(attack, 'special'):
                result['special_effects'].append(attack.special)
                
        return result

    @staticmethod
    def roll_dice(dice_str: str) -> int:
        """Improved dice rolling with support for complex expressions"""
        try:
            if '+' in dice_str:
                parts = dice_str.split('+')
                return sum(Combat._roll_dice_part(p) for p in parts)
            elif '-' in dice_str:
                parts = dice_str.split('-')
                return Combat._roll_dice_part(parts[0]) - sum(Combat._roll_dice_part(p) for p in parts[1:])
            else:
                return Combat._roll_dice_part(dice_str)
        except:
            return 0  # Fallback for malformed dice strings

    @staticmethod
    def _roll_dice_part(part: str) -> int:
        """Handle individual dice parts (e.g., '2d6' or '5')"""
        part = part.strip()
        if 'd' in part:
            num, sides = map(int, part.split('d'))
            return sum(random.randint(1, sides) for _ in range(num))
        else:
            return int(part) if part else 0

    @staticmethod
    def resolve_monster_abilities(monster: Monster) -> Dict:
        """Resolve which special abilities a monster uses this round"""
        abilities_used = {}
        
        # Check spell-like abilities
        if monster.spell_like_abilities:
            for ability, uses in monster.spell_like_abilities.items():
                if uses == 'At will' or random.random() > 0.7:
                    abilities_used[ability] = {
                        'type': 'spell-like',
                        'dc': monster.spell_dc if hasattr(monster, 'spell_dc') else 10 + monster.abilities['CHA'] // 2
                    }
        
        # Check special attacks
        for ability in monster.abilities_list:
            if ability.uses == 'At will' or random.random() > 0.7:
                abilities_used[ability.name] = {
                    'type': 'special',
                    'description': ability.description,
                    'dc': ability.dc
                }
        
        return abilities_used