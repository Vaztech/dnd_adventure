"""
dnd35e/rules.py - D&D 3.5 Edition Rule System Implementation
"""

from typing import Dict, List, Tuple, Union
import random
import math

class DnD35Rules:
    """Core 3.5 Edition Rules Implementation"""
    
    # ================
    # Core Attributes
    # ================
    ABILITY_SCORES = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    ALIGNMENTS = ['LG', 'NG', 'CG', 'LN', 'N', 'CN', 'LE', 'NE', 'CE']
    SKILLS = [
        'Appraise', 'Balance', 'Bluff', 'Climb', 'Concentration', 'Craft', 'Decipher Script',
        'Diplomacy', 'Disable Device', 'Disguise', 'Escape Artist', 'Forgery', 'Gather Information',
        'Handle Animal', 'Heal', 'Hide', 'Intimidate', 'Jump', 'Knowledge', 'Listen', 'Move Silently',
        'Open Lock', 'Perform', 'Profession', 'Ride', 'Search', 'Sense Motive', 'Sleight of Hand',
        'Spellcraft', 'Spot', 'Survival', 'Swim', 'Tumble', 'Use Magic Device', 'Use Rope'
    ]
    
    # ================
    # Ability Scores
    # ================
    @staticmethod
    def ability_modifier(score: int) -> int:
        """Calculate ability modifier from score"""
        return (score - 10) // 2
    
    @staticmethod
    def roll_ability_scores(method: str = '4d6') -> Dict[str, int]:
        """Generate ability scores using specified method"""
        methods = {
            '4d6': lambda: sum(sorted([random.randint(1, 6) for _ in range(4)], reverse=True)[1:]),  # Drop lowest
            '3d6': lambda: sum([random.randint(1, 6) for _ in range(3)]),
            'pointbuy': lambda: None  # Implement point buy system
        }
        
        if method not in methods:
            raise ValueError(f"Invalid method: {method}. Choose from '4d6', '3d6', or 'pointbuy'.")
        
        return {ab: methods[method]() for ab in DnD35Rules.ABILITY_SCORES}
    
    # ================
    # Combat Rules
    # ================
    @staticmethod
    def calculate_ac(base_ac: int, dex_mod: int, armor_bonus: int = 0, 
                    shield_bonus: int = 0, size_mod: int = 0, 
                    natural_armor: int = 0, deflection: int = 0, 
                    misc_mod: int = 0) -> int:
        """Calculate total armor class"""
        return (10 + base_ac + dex_mod + armor_bonus + shield_bonus + 
                size_mod + natural_armor + deflection + misc_mod)
    
    @staticmethod
    def attack_roll(attack_bonus: int, critical_threat: Tuple[int, int] = (20, 20)) -> Tuple[int, bool]:
        """Make an attack roll with critical threat detection"""
        roll = random.randint(1, 20)
        is_critical_threat = roll >= critical_threat[0]
        return (roll + attack_bonus, is_critical_threat)
    
    @staticmethod
    def confirm_critical(attack_bonus: int) -> bool:
        """Confirm critical hit with second attack roll"""
        return (random.randint(1, 20) + attack_bonus) >= 0  # Always succeeds against AC 0 for confirmation
    
    # ================
    # Saving Throws
    # ================
    @staticmethod
    def saving_throw(save_type: str, base_save: int, ability_mod: int, 
                    magic_mod: int = 0, misc_mod: int = 0) -> int:
        """Calculate saving throw value"""
        save_types = {'fortitude': 'CON', 'reflex': 'DEX', 'will': 'WIS'}
        return base_save + ability_mod + magic_mod + misc_mod
    
    # ================
    # Skill Checks
    # ================
    @staticmethod
    def skill_check(skill_rank: int, ability_mod: int, 
                   dc: int, armor_check_penalty: int = 0,
                   synergy_bonus: int = 0, misc_mod: int = 0) -> bool:
        """Make a skill check against difficulty class"""
        roll = random.randint(1, 20)
        total = roll + skill_rank + ability_mod - armor_check_penalty + synergy_bonus + misc_mod
        return total >= dc
    
    # ================
    # Experience & Leveling
    # ================
    XP_TABLE = [
        0, 1000, 3000, 6000, 10000, 15000, 21000, 28000, 36000, 45000,
        55000, 66000, 78000, 91000, 105000, 120000, 136000, 153000, 171000, 190000
    ]
    
    @staticmethod
    def xp_for_next_level(current_level: int) -> int:
        """Get XP needed for next level"""
        if current_level >= 20:
            return 0
        return DnD35Rules.XP_TABLE[current_level]
    
    @staticmethod
    def level_from_xp(xp: int) -> int:
        """Calculate character level from XP"""
        for level, threshold in enumerate(DnD35Rules.XP_TABLE):
            if xp < threshold:
                return level
        return 20
    
    # ================
    # Magic System
    # ================
    @staticmethod
    def calculate_spell_slots(class_type: str, level: int, 
                            ability_mod: int) -> Dict[int, int]:
        """Calculate daily spell slots by spell level"""
        # This would be expanded with actual table data
        return {1: max(0, 3 + ability_mod)}
    
    # ================
    # Damage & Healing
    # ================
    @staticmethod
    def roll_damage(dice: str, modifier: int = 0, 
                   critical_multiplier: int = 2) -> int:
        """Roll damage dice with optional critical multiplier"""
        if 'd' not in dice:
            return max(1, int(dice) + modifier)
        
        num, sides = map(int, dice.split('d'))
        damage = sum(random.randint(1, sides) for _ in range(num))
        return max(1, (damage + modifier) * critical_multiplier)
    
    @staticmethod
    def calculate_hp(hd: str, con_mod: int, level: int = 1) -> int:
        """Calculate hit points including constitution bonus"""
        if 'd' not in hd:
            return max(1, int(hd) + (con_mod * level))
        
        num, sides = map(int, hd.split('d'))
        return max(1, (sum(random.randint(1, sides) for _ in range(num))) + (con_mod * level))


# Adding the load_rules function
def load_rules():
    """Load and return the necessary game rules."""
    print("Loading rules...")  # Placeholder for actual loading logic
    return DnD35Rules  # You can return the core rules or other necessary data

'''
# Example usage
if __name__ == "__main__":
    rules = load_rules()
    print("Ability Scores:", rules.roll_ability_scores())
    print("Attack Roll:", rules.attack_roll(5))
    print("Armor Class:", rules.calculate_ac(10, 2, 3))
    print("Skill Check:", rules.skill_check(5, 2, 15))
    print("XP for Next Level:", rules.xp_for_next_level(1))
    print("Level from XP:", rules.level_from_xp(3000))
    print("Damage Roll:", rules.roll_damage('2d6+3'))
    print("Hit Points:", rules.calculate_hp('1d10', 2, 5))
 # This code is a simplified version of the D&D 3.5 ruleset and can be expanded with more features as needed.'''