from typing import List, Optional
from dnd_adventure.data_loader import DataLoader
from dnd_adventure.race_models import Race

def get_race_by_name(name: str) -> Optional[Race]:
    loader = DataLoader()
    races = loader.load_races_from_json()
    for race in races:
        if race.name == name:
            return race
    return None

def get_races() -> List[Race]:
    loader = DataLoader()
    return loader.load_races_from_json()

def get_default_race() -> Race:
    loader = DataLoader()
    races = loader.load_races_from_json()
    for race in races:
        if race.name == "Human":
            return race
    return races[0] if races else None