from typing import List, Dict, Optional

class RacialTrait:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class Race:
    def __init__(
        self,
        name: str,
        description: str,
        ability_modifiers: Dict[str, int],
        size: str,
        speed: int,
        racial_traits: List[Dict[str, str]],  # Changed for JSON compatibility
        favored_class: str,
        languages: List[str],
        subraces: Dict[str, Dict] = None
    ):
        self.name = name
        self.description = description
        self.ability_modifiers = ability_modifiers
        self.size = size
        self.speed = speed
        self.racial_traits = [RacialTrait(t['name'], t['description']) for t in racial_traits]
        self.favored_class = favored_class
        self.languages = languages
        self.subraces = subraces or {}
        self.subrace = None

    def apply_modifiers(self, character: 'Character') -> None:
        """
        Apply racial and subrace ability modifiers to the character's stats.
        Stats are ordered: [Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma]
        """
        stat_indices = {
            'Strength': 0,
            'Dexterity': 1,
            'Constitution': 2,
            'Intelligence': 3,
            'Wisdom': 4,
            'Charisma': 5
        }
        # Apply base race modifiers
        for stat, modifier in self.ability_modifiers.items():
            if stat in stat_indices:
                character.stats[stat_indices[stat]] += modifier
        # Apply subrace modifiers if selected
        if self.subrace and self.subraces and self.subrace in self.subraces:
            subrace_modifiers = self.subraces[self.subrace].get('ability_modifiers', {})
            for stat, modifier in subrace_modifiers.items():
                if stat in stat_indices:
                    character.stats[stat_indices[stat]] += modifier

def get_race_by_name(name: str) -> Optional[Race]:
    return RACES.get(name)

def get_races() -> List[Race]:
    return list(RACES.values())

RACES = {
    "Human": Race(
        name="Human",
        description="Versatile and adaptable, humans excel in any profession.",
        ability_modifiers={},
        size="Medium",
        speed=30,
        racial_traits=[
            {"name": "Bonus Feat", "description": "Gain one extra feat at 1st level"},
            {"name": "Extra Skills", "description": "Gain 4 extra skill points at 1st level and 1 extra skill point at each additional level"}
        ],
        favored_class="Any",
        languages=["Common"],
        subraces={}
    ),
    "Elf": Race(
        name="Elf",
        description="Graceful and magical, elves are attuned to nature and arcane arts.",
        ability_modifiers={"Dexterity": 2, "Constitution": -2},
        size="Medium",
        speed=30,
        racial_traits=[
            {"name": "Low-Light Vision", "description": "Can see twice as far as a human in dim light"},
            {"name": "Keen Senses", "description": "+2 bonus on Listen, Search, and Spot checks"},
            {"name": "Immunity to Sleep", "description": "Immune to magical sleep effects"},
            {"name": "Elven Weapon Proficiency", "description": "Proficient with longsword, rapier, longbow, shortbow"}
        ],
        favored_class="Wizard",
        languages=["Common", "Elven"],
        subraces={
            "High Elf": {
                "description": "Skilled in arcane magic, with a knack for wizardry.",
                "ability_modifiers": {"Intelligence": 1},
                "racial_traits": [
                    {"name": "Arcane Focus", "description": "+2 bonus on Spellcraft checks"}
                ]
            },
            "Wood Elf": {
                "description": "Swift and stealthy, at home in forests.",
                "ability_modifiers": {"Wisdom": 1},
                "racial_traits": [
                    {"name": "Forest Stride", "description": "Move through natural undergrowth at normal speed"}
                ]
            },
            "Dark Elf (Drow)": {
                "description": "Cunning and shadowy, with innate magical abilities.",
                "ability_modifiers": {"Charisma": 1},
                "racial_traits": [
                    {"name": "Spell Resistance", "description": "Spell Resistance equal to 11 + class levels"},
                    {"name": "Darkvision (120 ft)", "description": "Can see in the dark up to 120 feet"}
                ]
            }
        }
    ),
    "Dwarf": Race(
        name="Dwarf",
        description="Sturdy and resilient, dwarves are masters of stone and metal.",
        ability_modifiers={"Constitution": 2, "Charisma": -2},
        size="Medium",
        speed=20,
        racial_traits=[
            {"name": "Darkvision (60 ft)", "description": "Can see in the dark up to 60 feet"},
            {"name": "Stability", "description": "+4 bonus against bull rush or trip attempts when standing on the ground"},
            {"name": "Stonecunning", "description": "+2 bonus on Search checks related to stonework"},
            {"name": "Poison Resistance", "description": "+2 bonus on saving throws against poison"}
        ],
        favored_class="Fighter",
        languages=["Common", "Dwarven"],
        subraces={
            "Hill Dwarf": {
                "description": "Hardy and wise, with strong community ties.",
                "ability_modifiers": {"Wisdom": 1},
                "racial_traits": [
                    {"name": "Resilient", "description": "+2 bonus on saving throws against poison and spells"}
                ]
            },
            "Mountain Dwarf": {
                "description": "Tough and martial, skilled in combat.",
                "ability_modifiers": {"Strength": 1},
                "racial_traits": [
                    {"name": "Armor Training", "description": "Proficient with light and medium armor"}
                ]
            }
        }
    )
}

def get_default_race() -> Race:
    return RACES["Human"]