import json
from pathlib import Path

class Monster:
    def __init__(self, name, type, armor_class, hit_points, speed, challenge_rating):
        self.name = name
        self.type = type
        self.armor_class = armor_class
        self.hit_points = hit_points
        self.speed = speed
        self.challenge_rating = challenge_rating

    def __repr__(self):
        return f"Monster({self.name}, {self.type}, {self.armor_class}, {self.hit_points}, {self.speed}, {self.challenge_rating})"

class MonsterTemplate:
    def __init__(self, name: str, cr: float, monster_type: str, armor_class: int, hit_points: int, speed: int):
        self.name = name
        self.cr = cr  # Challenge Rating
        self.type = monster_type  # e.g., "Undead", "Beast", etc.
        self.armor_class = armor_class
        self.hit_points = hit_points
        self.speed = speed

    def __repr__(self):
        return f"MonsterTemplate({self.name}, CR: {self.cr}, Type: {self.type}, AC: {self.armor_class}, HP: {self.hit_points}, Speed: {self.speed})"

def load_monsters_from_json():
    """Load monsters from a JSON file."""
    try:
        # Get the directory of the current script and build the relative path using pathlib
        base_path = Path(__file__).resolve().parent  # Current script directory
        json_path = base_path / 'dnd35e' / 'data' / 'srd_monsters.json'
        
        # Check if the file exists before attempting to open it
        if not json_path.exists():
            print(f"Error: The file {json_path} does not exist.")
            return []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        monsters = []

        for category, category_data in data.items():
            for name, monster_data in category_data.items():
                try:
                    # Check if 'type' is missing and assign a default value
                    monster_type = monster_data.get('type', 'Unknown')
                    
                    # Now safely access 'type' without KeyError
                    monster = Monster(
                        name=name,
                        type=monster_type,  # Use default if not found
                        armor_class=monster_data.get('armor_class'),
                        hit_points=monster_data.get('hit_points'),
                        speed=monster_data.get('speed'),
                        challenge_rating=monster_data.get('challenge_rating'),
                    )
                    monsters.append(monster)
                except KeyError as e:
                    print(f"Warning: Missing required field {e} in monster '{name}'")

        return monsters

    except Exception as e:
        print(f"Error processing JSON file: {e}")
        return []

# Define SRD_MONSTERS (using the same function as CORE_MONSTERS)
SRD_MONSTERS = load_monsters_from_json()

def get_monsters_by_cr(cr):
    """Get monsters by challenge rating."""
    return [monster for monster in SRD_MONSTERS if monster.challenge_rating == cr]

def get_monsters_by_type(monster_type):
    """Get monsters by type."""
    return [monster for monster in SRD_MONSTERS if monster.type.lower() == monster_type.lower()]

def get_monster_by_name(name):
    """Get a monster by its name."""
    for monster in SRD_MONSTERS:
        if monster.name.lower() == name.lower():
            return monster
    return None

def get_monster_by_cr(cr):
    """Get a monster by its challenge rating."""
    for monster in SRD_MONSTERS:
        if monster.challenge_rating == cr:
            return monster
    return None
def get_monster_by_ac(ac):
    """Get a monster by its armor class."""
    for monster in SRD_MONSTERS:
        if monster.armor_class == ac:
            return monster
    return None