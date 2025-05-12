@staticmethod
def load_player(game_world, character_factory):
    if not SAVE_FILE.exists():
        return character_factory(), game_world.rooms[0]

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Directly instantiate character with correct constructor args
        from .character import Character  # Import here to avoid circular issues
        player = Character(
            name=data["name"],
            race_name=data["race"],
            class_name=data["class"],
            level=data["level"]
        )

        player.xp = data.get("xp", 0)
        player.hit_points = data.get("hp", player.calculate_hit_points())

        for attr, val in data["ability_scores"].items():
            setattr(player.ability_scores, attr, val)

        player.skills = data.get("skills", {})
        player.feats = data.get("feats", [])
        player.spells_known = [CORE_SPELLS[name] for name in data.get("spells_known", []) if name in CORE_SPELLS]
        player.equipment = {
            slot: CORE_ITEMS[name] for slot, name in data.get("equipment", {}).items() if name in CORE_ITEMS
        }

        location = next((r for r in game_world.rooms if r["id"] == data["location_id"]), game_world.rooms[0])
        return player, location

    except Exception as e:
        print(f"⚠️ Failed to load player save: {e}")
        return character_factory(), game_world.rooms[0]
import json
from pathlib import Path