import json
from pathlib import Path
from typing import Dict, Any

def load_data(file_name: str) -> Dict[str, Any]:
    """Load JSON data from the data directory"""
    # Adjust the file path to include the "srd_" prefix as needed
    data_path = Path(__file__).parent / f"srd_{file_name}.json"
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found - {data_path}")
        return {}

# Load all data files with correct names
SPELLS = load_data("spells")
MONSTERS = load_data("monsters")
CLASSES = load_data("classes")
RACES = load_data("races")
FEATS = load_data("feats")
ITEMS = load_data("items")

__all__ = ['SPELLS', 'MONSTERS', 'CLASSES', 'RACES', 'FEATS', 'ITEMS']
