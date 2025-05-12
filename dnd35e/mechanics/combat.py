from typing import Dict, Union
import random

# Local import to avoid circular dependency
from ..core.character import Character
from ..core.monsters import Monster, SRD_MONSTERS

class CombatSystem:
    """Combat system for resolving attacks and monster abilities."""

    @staticmethod
    def resolve_attack(attacker: Union[Character, Monster], 
                       defender: Union[Character, Monster],
                       attack_name: str = None) -> Dict:
        """
        Resolve a combat attack with full monster capabilities.
        Returns a dictionary with the results.
        """
        result = {
            'attacker': attacker.name if hasattr(attacker, 'name') else 'Unknown Attacker',
            'defender': defender.name if hasattr(defender, 'name') else 'Unknown Defender',
            'hit': False,
            'critical': False,
            'damage': 0,
            'special_effects': [],
            'error': None  # Added for error reporting
        }

        # Determine attack bonus
        if isinstance(attacker, Character):
            attack_bonus = attacker.attack_bonus() if hasattr(attacker, 'attack_bonus') else 0
            weapon = attacker.get_equipped_weapon() if hasattr(attacker, 'get_equipped_weapon') else None
            damage_dice = weapon.dnd_item.damage if weapon else "1d3"
            damage_mod = attacker.ability_scores.get_modifier('strength') if hasattr(attacker, 'ability_scores') else 0
        else:
            # Monster attack
            attack = None
            if attack_name:
                attack = next((a for a in attacker.attacks if a.name.lower() == attack_name.lower()), None)
            if not attack:
                attack = attacker.attacks[0] if hasattr(attacker, 'attacks') and attacker.attacks else None
            
            if not attack:
                result['error'] = "No valid attack found."
                return result

            attack_bonus = attack.attack_bonus if hasattr(attack, 'attack_bonus') else 0
            damage_dice = attack.damage if hasattr(attack, 'damage') else "1d3"
            damage_mod = (attacker.abilities.get('STR', 10) - 10) // 2 if hasattr(attacker, 'abilities') else 0

        # Make attack roll
        attack_roll = random.randint(1, 20)
        is_critical = attack_roll == 20
        result['attack_roll'] = attack_roll
        result['attack_bonus'] = attack_bonus
        
        # Check for hit (ensure armor_class method exists)
        defender_ac = getattr(defender, 'armor_class', lambda: 10)()  # Default to 10 if armor_class is not found
        if is_critical or (attack_roll + attack_bonus) >= defender_ac:
            result['hit'] = True
            result['critical'] = is_critical
            
            # Calculate damage
            damage = CombatSystem.roll_dice(damage_dice) + damage_mod
            if is_critical:
                damage *= 2  # Simplified critical hit calculation
            result['damage'] = max(1, damage)  # Ensure at least 1 damage
            
            # Apply special effects if the attack has them
            if hasattr(attack, 'special') and attack.special:
                result['special_effects'].append(attack.special)

        return result

    @staticmethod
    def roll_dice(dice_str: str) -> int:
        """Improved dice rolling with support for complex expressions."""
        try:
            if '+' in dice_str:
                parts = dice_str.split('+')
                return sum(CombatSystem._roll_dice_part(p) for p in parts)
            elif '-' in dice_str:
                parts = dice_str.split('-')
                return CombatSystem._roll_dice_part(parts[0]) - sum(CombatSystem._roll_dice_part(p) for p in parts[1:])
            else:
                return CombatSystem._roll_dice_part(dice_str)
        except Exception as e:
            print(f"Error in dice rolling: {e}")  # Print out error message
            return 0  # Fallback for malformed dice strings

    @staticmethod
    def _roll_dice_part(part: str) -> int:
        """Handle individual dice parts (e.g., '2d6' or '5')."""
        part = part.strip()
        if 'd' in part:
            try:
                num, sides = map(int, part.split('d'))
                return sum(random.randint(1, sides) for _ in range(num))
            except Exception as e:
                print(f"Error in rolling dice part {part}: {e}")  # Print out error message
                return 0
        else:
            try:
                return int(part)
            except Exception as e:
                print(f"Error converting part {part} to integer: {e}")  # Print out error message
                return 0

    @staticmethod
    def resolve_monster_abilities(monster: Monster) -> Dict:
        """Resolve which special abilities a monster uses this round."""
        abilities_used = {}

        # Check spell-like abilities
        if hasattr(monster, 'spell_like_abilities') and monster.spell_like_abilities:
            for ability, uses in monster.spell_like_abilities.items():
                if uses == 'At will' or random.random() > 0.7:
                    abilities_used[ability] = {
                        'type': 'spell-like',
                        'dc': getattr(monster, 'spell_dc', 10 + monster.abilities.get('CHA', 10) // 2)
                    }

        # Check special attacks
        for ability in getattr(monster, 'abilities_list', []):
            if ability.uses == 'At will' or random.random() > 0.7:
                abilities_used[ability.name] = {
                    'type': 'special',
                    'description': ability.description,
                    'dc': getattr(ability, 'dc', 10)
                }

        return abilities_used
