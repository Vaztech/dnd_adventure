from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Skill:
    name: str
    key_ability: str
    armor_check_penalty: bool
    trained_only: bool
    description: str
    synergies: Optional[Dict[str, str]] = None  # {skill: "bonus description"}

CORE_SKILLS = {
    "Climb": Skill(
        name="Climb",
        key_ability="STR",
        armor_check_penalty=True,
        trained_only=False,
        description="The skill used to scale cliffs, walls, and other steep surfaces.",
        synergies={"Jump": "+2 bonus on Climb checks when making a running jump"}
    ),
    "Hide": Skill(
        name="Hide",
        key_ability="DEX",
        armor_check_penalty=True,
        trained_only=False,
        description="The skill used to conceal oneself from others.",
        synergies={"Move Silently": "Often used together when sneaking"}
    )
}