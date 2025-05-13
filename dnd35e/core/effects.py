# dnd_adventure/dnd35e/core/effects.py
from typing import Dict, List, Optional, Union, Callable, Tuple
from enum import Enum, auto
from dnd_adventure.dnd35e.core.monsters import Monster
from dnd_adventure.dnd35e.core.items import Item
from dnd_adventure.dnd35e.core.spells import Spell

class EffectType(Enum):
    LIGHT = auto()
    MAGICAL = auto()
    ENVIRONMENTAL = auto()
    CONDITION = auto()
    SPELL = auto()
    PSIONIC = auto()
    VILE = auto()
    EXALTED = auto()
    EPIC = auto()
    ITEM_PROPERTY = auto()

class DurationType(Enum):
    INSTANTANEOUS = auto()
    ROUNDS = auto()
    MINUTES = auto()
    HOURS = auto()
    DAYS = auto()
    PERMANENT = auto()
    CONCENTRATION = auto()
    DISPELLABLE = auto()
    CHARGES = auto()

class AlignmentComponent(Enum):
    GOOD = auto()
    EVIL = auto()
    LAWFUL = auto()
    CHAOTIC = auto()

class Effect:
    """Base class for all effects"""
    def __init__(self, name: str, effect_type: EffectType):
        self.name = name
        self.effect_type = effect_type
        self.duration = DurationType.INSTANTANEOUS
        self.dc = 0  # Difficulty Class
        self.saving_throw = "Will"  # Default saving throw
        self.alignment: List[AlignmentComponent] = []
        
    def apply(self, target) -> str:
        """Apply effect to target and return result description"""
        return f"{self.name} applied to {target.name}"

# ======================
# CORE EFFECT CATEGORIES
# ======================
class LightSource(Effect):
    def __init__(self, name: str, radius: int, is_active: bool = True):
        super().__init__(name, EffectType.LIGHT)
        self.radius = radius  # In feet
        self.is_active = is_active
        
    def toggle(self) -> bool:
        self.is_active = not self.is_active
        return self.is_active

class Condition(Effect):
    def __init__(self, name: str, modifiers: Dict[str, int]):
        super().__init__(name, EffectType.CONDITION)
        self.modifiers = modifiers
        
    def apply(self, target) -> str:
        for stat, mod in self.modifiers.items():
            setattr(target, stat, getattr(target, stat, 0) + mod)
        return f"{target.name} gains {self.name} condition"

# ======================
# EXPANSION EFFECTS
# ======================
class VileEffect(Effect):
    """Book of Vile Darkness effects"""
    def __init__(self, name: str, corruption_points: int):
        super().__init__(name, EffectType.VILE)
        self.corruption_points = corruption_points
        self.alignment.append(AlignmentComponent.EVIL)
        
class ExaltedEffect(Effect):
    """Book of Exalted Deeds effects"""
    def __init__(self, name: str, sanctified: bool):
        super().__init__(name, EffectType.EXALTED)
        self.sanctified = sanctified
        self.alignment.append(AlignmentComponent.GOOD)
        
class PsionicEffect(Effect):
    """Psionics Handbook effects"""
    def __init__(self, name: str, power_points: int, discipline: str):
        super().__init__(name, EffectType.PSIONIC)
        self.power_points = power_points
        self.discipline = discipline
        
class EpicEffect(Effect):
    """Epic Level Handbook effects"""
    def __init__(self, name: str, minimum_level: int):
        super().__init__(name, EffectType.EPIC)
        self.minimum_level = minimum_level
        self.dc = 30 + (minimum_level // 2)
        
class ItemProperty(Effect):
    """Magic item properties"""
    def __init__(self, name: str, activation: str):
        super().__init__(name, EffectType.ITEM_PROPERTY)
        self.activation = activation  # Command word, use-activated, etc.

# ======================
# EFFECT COLLECTIONS
# ======================
class CoreEffects:
    """PHB/DMG Core Effects"""
    @staticmethod
    def get_conditions() -> List[Condition]:
        return [
            Condition("Blinded", {"attack_rolls": -2, "ac": -4}),
            Condition("Poisoned", {"constitution": -4, "strength": -4}),
            Condition("Hasted", {"attack_rolls": 1, "ac": 1, "reflex": 1})
        ]
    
    @staticmethod
    def get_light_sources() -> List[LightSource]:
        return [
            LightSource("Torch", 20),
            LightSource("Everburning Torch", 20, True),
            LightSource("Daylight Spell", 60, True)
        ]

class VileEffects:
    """Book of Vile Darkness"""
    @staticmethod
    def get_effects() -> List[VileEffect]:
        return [
            VileEffect("Aura of Unholy Might", 3),
            VileEffect("Soul Corruption", 5),
            VileEffect("Vile Natural Attack", 2)
        ]

class ExaltedEffects:
    """Book of Exalted Deeds"""
    @staticmethod
    def get_effects() -> List[ExaltedEffect]:
        return [
            ExaltedEffect("Sacred Healing", True),
            ExaltedEffect("Holy Radiance", True),
            ExaltedEffect("Saint's Blessing", False)
        ]

class PsionicEffects:
    """Expanded Psionics Handbook"""
    @staticmethod
    def get_effects() -> List[PsionicEffect]:
        return [
            PsionicEffect("Mind Thrust", 1, "Telepathy"),
            PsionicEffect("Energy Burst", 3, "Psychokinesis"),
            PsionicEffect("Metamorphosis", 5, "Psychometabolism")
        ]

class EpicEffects:
    """Epic Level Handbook"""
    @staticmethod
    def get_effects() -> List[EpicEffect]:
        return [
            EpicEffect("Epic Spellcasting", 21),
            EpicEffect("Dragon Knight", 25),
            EpicEffect("Omniscient Whispers", 30)
        ]

class MagicItemProperties:
    """DMG Magic Item Properties"""
    @staticmethod
    def get_properties() -> List[ItemProperty]:
        return [
            ItemProperty("Flaming", "On command"),
            ItemProperty("Vorpal", "On critical hit"),
            ItemProperty("Anarchic", "Always active")
        ]

# ======================
# SPECIAL EFFECT SYSTEMS
# ======================
class EffectSystem:
    """Manager for all game effects"""
    def __init__(self):
        self.all_effects = {
            "core": CoreEffects.get_conditions() + CoreEffects.get_light_sources(),
            "vile": VileEffects.get_effects(),
            "exalted": ExaltedEffects.get_effects(),
            "psionic": PsionicEffects.get_effects(),
            "epic": EpicEffects.get_effects(),
            "item_properties": MagicItemProperties.get_properties()
        }
        
    def get_effect(self, name: str) -> Optional[Effect]:
        """Search all effect categories by name"""
        for category in self.all_effects.values():
            for effect in category:
                if effect.name.lower() == name.lower():
                    return effect
        return None
        
    def get_effects_by_type(self, effect_type: EffectType) -> List[Effect]:
        """Get all effects of specific type"""
        return [eff for cat in self.all_effects.values() 
                for eff in cat if eff.effect_type == effect_type]

# Example Usage:
if __name__ == "__main__":
    system = EffectSystem()
    haste = system.get_effect("Hasted")
    print(haste.apply(Monster("Goblin", 1)))