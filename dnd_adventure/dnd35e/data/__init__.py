import json
from pathlib import Path
from typing import Dict, Any, List

def load_data(file_name: str) -> Dict[str, Any]:
    """Load JSON data from the data directory."""
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
    return load_data("monsters")

def load_locations() -> List[Dict[str, Any]]:
    """Load location data."""
    return load_data("locations")

def load_spells() -> List[Dict[str, Any]]:
    """Load spell data."""
    return load_data("spells")

def load_classes() -> List[Dict[str, Any]]:
    """Load class data."""
    return load_data("classes")

def load_races() -> List[Dict[str, Any]]:
    """Load race data."""
    return load_data("races")

def load_feats() -> List[Dict[str, Any]]:
    """Load feat data."""
    return load_data("feats")

def load_items() -> List[Dict[str, Any]]:
    """Load item data."""
    return load_data("items")

__all__ = [
    'load_monsters', 'load_locations', 'load_spells', 'load_classes',
    'load_races', 'load_feats', 'load_items'
]
