import os
import json
import logging
from typing import Optional, Tuple, Callable
from dnd_adventure.character import Character
from dnd_adventure.world import GameWorld
from dnd_adventure.races import Race
from dnd_adventure.classes import DnDClass

logger = logging.getLogger(__name__)

SAVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'saves')
os.makedirs(SAVE_DIR, exist_ok=True)

class SaveManager:
    @staticmethod
    def save_player(player: Character, room_id: int):
        save_data = {
            'name': player.name,
            'race_name': player.race_name,
            'class_name': player.class_name,
            'level': player.level,
            'stats': player.stats,
            'hit_points': player.hit_points,
            'skill_points': player.skill_points,
            'known_spells': player.known_spells,
            'mp': player.mp,
            'max_mp': player.max_mp,
            'equipment': player.equipment,
            'armor_class': player.armor_class,
            'room_id': room_id
        }
        save_path = os.path.join(SAVE_DIR, f"{player.name}.save")
        try:
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=4)
            logger.debug(f"Saving player {player.name}: hit_points={player.hit_points}, skill_points={player.skill_points}, level={player.level}, stats={player.stats}")
        except Exception as e:
            logger.error(f"Failed to save player {player.name}: {e}")
            raise

    @staticmethod
    def load_player(world: GameWorld, name: str, create_player: Callable[[str], Character]) -> Tuple[Optional[Character], Optional[object]]:
        save_path = os.path.join(SAVE_DIR, f"{name}.save")
        if not os.path.exists(save_path):
            logger.debug(f"No save file found for {name}")
            return None, None

        try:
            with open(save_path, 'r') as f:
                data = json.load(f)

            race_name = data.get('race_name', 'Human')
            race = None
            for r in world.races:
                if r.name in race_name or race_name.startswith(r.name):
                    race = r
                    break
            if not race:
                logger.warning(f"Race {race_name} not found, using default Human")
                race = next((r for r in world.races if r.name == "Human"), world.races[0])

            class_name = data.get('class_name', 'Fighter')
            dnd_class = None
            for c in world.classes:
                if c.name == class_name:
                    dnd_class = c
                    break
            if not dnd_class:
                logger.warning(f"Class {class_name} not found, using default class")
                dnd_class = world.classes[0]

            player = Character(
                name=name,
                race=race,
                dnd_class=dnd_class,
                race_name=race_name,
                class_name=class_name,
                level=data.get('level', 1),
                stats=data.get('stats', [8, 8, 8, 8, 8, 8]),
                hit_points=data.get('hit_points', 1),
                skill_points=data.get('skill_points', 0),
                known_spells=data.get('known_spells', {0: [], 1: []})
            )
            player.mp = data.get('mp', 0)
            player.max_mp = data.get('max_mp', 0)
            player.equipment = data.get('equipment', [])
            player.armor_class = data.get('armor_class', 10)
            if class_name in ["Wizard", "Sorcerer", "Cleric", "Druid", "Bard"] and not player.known_spells:
                logger.debug(f"Initializing empty spells for {class_name}")
                player.known_spells = {0: [], 1: []}
            player.calculate_mp()

            room_id = data.get('room_id', 0)
            room = world.get_room(room_id)
            if not room:
                logger.warning(f"Room {room_id} not found, using default room 0")
                room = world.get_room(0)

            logger.debug(f"Loaded player {name}: hit_points={player.hit_points}, skill_points={player.skill_points}, level={player.level}, stats={player.stats}")
            return player, room
        except Exception as e:
            logger.error(f"Failed to load player {name}: {e}")
            return None, None

    @staticmethod
    def list_saves() -> list:
        try:
            saves = [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith('.save')]
            logger.debug(f"Listed saves: {saves}")
            return saves
        except Exception as e:
            logger.error(f"Failed to list saves: {e}")
            return []