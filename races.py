from dataclasses import dataclass
from typing import Dict, List

@dataclass
class RacialTrait:
    name: str
    description: str

@dataclass
class Race:
    name: str
    ability_modifiers: Dict[str, int]
    size: str  # 'Small', 'Medium', 'Large'
    speed: int  # base movement speed in feet
    racial_traits: List[RacialTrait]
    favored_class: str
    languages: List[str]

    def apply_modifiers(self, ability_scores: 'AbilityScores'):
        for ability, modifier in self.ability_modifiers.items():
            setattr(ability_scores, ability.lower(), 
                    getattr(ability_scores, ability.lower()) + modifier)

RACES = {
    "Human": Race(
        name="Human",
        ability_modifiers={},
        size="Medium",
        speed=30,
        racial_traits=[
            RacialTrait("Bonus Feat", "Gain one extra feat at 1st level"),
            RacialTrait("Extra Skills", "Gain 4 extra skill points at 1st level and 1 extra skill point at each additional level")
        ],
        favored_class="Any",
        languages=["Common"]
    ),
    "Elf": Race(
        name="Elf",
        ability_modifiers={"dexterity": 2, "constitution": -2},
        size="Medium",
        speed=30,
        racial_traits=[
            RacialTrait("Immunity to Sleep", "Immune to magic sleep effects"),
            RacialTrait("Low-Light Vision", "See twice as far as humans in low-light conditions")
        ],
        favored_class="Wizard",
        languages=["Common", "Elven"]
    )
}

def get_default_race() -> Race:
    return RACES["Human"]

def get_race_by_name(name: str) -> Race:
    return RACES.get(name, get_default_race())

def get_all_races() -> List[Race]:
    return list(RACES.values())