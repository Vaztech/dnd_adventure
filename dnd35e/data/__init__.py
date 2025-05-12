import json
from pathlib import Path
from typing import Dict, Any

def load_data(file_name: str) -> Dict[str, Any]:
    """Load JSON data from the data directory"""
    data_path = Path(__file__).parent / f"{file_name}.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load all data files
SPELLS = load_data("spells")
MONSTERS = load_data("monsters")
CLASSES = load_data("classes")
RACES = load_data("races")
FEATS = load_data("feats")
ITEMS = load_data("items")

__all__ = ['SPELLS', 'MONSTERS', 'CLASSES', 'RACES', 'FEATS', 'ITEMS']