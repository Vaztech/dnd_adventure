import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

from dnd_adventure.races import Race, RacialTrait
from dnd_adventure.character import DnDClass
from dnd_adventure.dnd35e.core.monsters import Monster

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        # Use absolute path to ensure correct data directory
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = self.data_dir.resolve()
        logger.debug(f"Data directory resolved to: {self.data_dir}")
        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist")

    def load_races_from_json(self) -> List[Race]:
        path = self.data_dir / "races.json"
        logger.debug(f"Attempting to load races from {path}")
        try:
            if not path.exists():
                logger.warning(f"Races file {path} not found")
                return []
            logger.debug(f"File {path} exists, size: {path.stat().st_size} bytes")
            with open(path, 'r', encoding='utf-8') as f:
                race_data = json.load(f)
            races = []
            for data in race_data:
                racial_traits = [RacialTrait(t["name"], t["description"]) for t in data.get("racial_traits", [])]
                subraces = data.get("subraces", {})
                for subrace in subraces.values():
                    subrace["racial_traits"] = [
                        {"name": t["name"], "description": t["description"]} for t in subrace.get("racial_traits", [])
                    ]
                races.append(Race(
                    name=data.get("name", "Unknown"),
                    description=data.get("description", ""),
                    ability_modifiers=data.get("ability_modifiers", {}),
                    size=data.get("size", "Medium"),
                    speed=data.get("speed", 30),
                    racial_traits=racial_traits,
                    favored_class=data.get("favored_class", "Any"),
                    languages=data.get("languages", ["Common"]),
                    subraces=subraces
                ))
            logger.debug(f"Loaded {len(races)} races: {[r.name for r in races]}")
            return races
        except Exception as e:
            logger.error(f"Failed to load races from {path}: {e}")
            return []

    def load_classes_from_json(self) -> List[Dict[str, Any]]:
        path = self.data_dir / "classes.json"
        logger.debug(f"Attempting to load classes from {path}")
        try:
            if not path.exists():
                logger.warning(f"Classes file {path} not found")
                return []
            logger.debug(f"File {path} exists, size: {path.stat().st_size} bytes")
            with open(path, 'r', encoding='utf-8') as f:
                class_data = json.load(f)
            logger.debug(f"Loaded classes from {path}: {[c.get('name') for c in class_data]}")
            return class_data
        except Exception as e:
            logger.error(f"Failed to load classes from {path}: {e}")
            return []

    def load_monsters_from_json(self) -> List[Monster]:
        path = self.data_dir / "monsters.json"
        logger.debug(f"Attempting to load monsters from {path}")
        try:
            if not path.exists():
                logger.warning(f"Monsters file {path} not found")
                return []
            logger.debug(f"File {path} exists, size: {path.stat().st_size} bytes")
            with open(path, 'r', encoding='utf-8') as f:
                monster_data = json.load(f)
            monsters = []
            valid_fields = {'name', 'type', 'armor_class', 'hit_points', 'speed', 'challenge_rating', 'abilities', 'attacks', 'size'}
            for data in monster_data:
                filtered_data = {k: v for k, v in data.items() if k in valid_fields}
                try:
                    monster = Monster(**filtered_data)
                    monsters.append(monster)
                except TypeError as e:
                    logger.warning(f"Failed to create monster {data.get('name', 'unknown')}: {e}")
            logger.debug(f"Loaded {len(monsters)} monsters from {path}: {[m.name for m in monsters]}")
            return monsters
        except Exception as e:
            logger.error(f"Failed to load monsters from {path}: {e}")
            return []

    def load_spells_from_json(self) -> List[Dict[str, Any]]:
        path = self.data_dir / "spells.json"
        logger.debug(f"Attempting to load spells from {path}")
        try:
            if not path.exists():
                logger.warning(f"Spells file {path} not found")
                return []
            logger.debug(f"File {path} exists, size: {path.stat().st_size} bytes")
            with open(path, 'r', encoding='utf-8') as f:
                spell_data = json.load(f)
            # Flatten spell data from class-based structure
            flattened_spells = []
            for class_name, levels in spell_data.items():
                for level, spells in levels.items():
                    for spell in spells:
                        spell['class'] = class_name
                        spell['level'] = level
                        flattened_spells.append(spell)
            logger.debug(f"Loaded {len(flattened_spells)} spells from {path}: {[s.get('name') for s in flattened_spells]}")
            return flattened_spells
        except Exception as e:
            logger.error(f"Failed to load spells from {path}: {e}")
            return []