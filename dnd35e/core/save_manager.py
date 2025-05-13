import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import asdict

from .character import Character
from .spells import CORE_SPELLS
from .items import CORE_ITEMS

SAVE_FILE = Path("dnd_adventure/dnd35e/save/player_save.json")

class SaveManager:
    @staticmethod
    def save_player(player: Character, current_room_id: str) -> None:
        """Save player data to JSON file"""
        try:
            data = {
                "name": player.name,
                "race": player.race.name,
                "class": player.dnd_class.name,
                "level": player.level,
                "xp": player.xp,
                "hp": player.hit_points,
                "ability_scores": asdict(player.ability_scores),
                "skills": player.skills,
                "feats": player.feats,
                "spells_known": [spell.name for spell in player.spells_known],
                "equipment": {slot: item.name for slot, item in player.equipment.items()},
                "location_id": current_room_id,
                "status_effects": player.status_effects
            }

            SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("💾 Player session saved.")

        except Exception as e:
            print(f"⚠️ Failed to save player data: {e}")

    @staticmethod
    def load_player(game_world: Any, character_factory: callable) -> Tuple[Character, Dict]:
        """Load player data from save file or create new character"""
        if not SAVE_FILE.exists():
            return character_factory(), game_world.rooms[0]

        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Instantiate character using correct constructor
            player = Character(
                name=data["name"],
                race_name=data["race"],
                class_name=data["class"],
                level=data["level"]
            )

            player.xp = data.get("xp", 0)
            player.hit_points = data.get("hp", player.calculate_hit_points())

            # Restore ability scores
            for attr, val in data["ability_scores"].items():
                if hasattr(player.ability_scores, attr):
                    setattr(player.ability_scores, attr, val)

            # Restore collections
            player.skills = data.get("skills", {})
            player.feats = data.get("feats", [])
            player.status_effects = data.get("status_effects", [])

            # Restore spells and equipment
            player.spells_known = [
                CORE_SPELLS[name] for name in data.get("spells_known", [])
                if name in CORE_SPELLS
            ]
            player.equipment = {
                slot: CORE_ITEMS[name] for slot, name in data.get("equipment", {}).items()
                if name in CORE_ITEMS
            }

            location = next(
                (room for room in game_world.rooms if room["id"] == data["location_id"]),
                game_world.rooms[0]
            )

            return player, location

        except Exception as e:
            print(f"⚠️ Failed to load player save: {e}")
            return character_factory(), game_world.rooms[0]

    @staticmethod
    def delete_save() -> bool:
        """Delete existing save file if it exists"""
        try:
            if SAVE_FILE.exists():
                SAVE_FILE.unlink()
                return True
            return False
        except Exception as e:
            print(f"⚠️ Failed to delete save file: {e}")
            return False
