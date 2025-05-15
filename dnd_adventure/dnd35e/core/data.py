import json
from pathlib import Path
from typing import Dict, Any, List

def load_json_file(file_name: str) -> Dict[str, Any]:
    """Load JSON data from a file in the data directory."""
    data_path = Path(__file__).parent / f"{file_name}.json"
    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{data_path}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{data_path}'.")
        return {}

def load_monsters() -> List[Dict[str, Any]]:
    """Load monster data."""
    return load_json_file("monsters")

def load_spells() -> List[Dict[str, Any]]:
    """Load spell data."""
    return load_json_file("spells")

def load_classes() -> List[Dict[str, Any]]:
    """Load class data."""
    return load_json_file("classes")

def load_races() -> List[Dict[str, Any]]:
    """Load race data."""
    return load_json_file("races")

def load_feats() -> List[Dict[str, Any]]:
    """Load feat data."""
    return load_json_file("feats")

def load_items() -> List[Dict[str, Any]]:
    """Load item data."""
    return load_json_file("items")

def load_locations() -> List[Dict[str, Any]]:
    """Load location data."""
    return load_json_file("locations")

# Load all data files
MONSTERS = load_monsters()
SPELLS = load_spells()
CLASSES = load_classes()
RACES = load_races()
FEATS = load_feats()
ITEMS = load_items()
LOCATIONS = load_locations()

__all__ = ['MONSTERS', 'SPELLS', 'CLASSES', 'RACES', 'FEATS', 'ITEMS', 'LOCATIONS']
# The __all__ variable is used to define the public interface of the module.