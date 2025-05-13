import os
import json
import random
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from dnd_adventure.dnd35e.core.monsters import get_monster_by_name, Monster
from dnd_adventure.races import get_default_race
from dnd_adventure.classes import get_default_class
from dnd_adventure.dnd35e.core.npc import NPC
from dnd_adventure.dnd35e.core.room import Room

logger = logging.getLogger(__name__)

class GameWorld:
    def __init__(self):
        self.rooms: List[Room] = []
        self.current_room: Optional[Room] = None
        self.monster_pool: List[Monster] = []
        self.location_templates: List[Dict] = []
        self.default_race = get_default_race()
        self.default_class = get_default_class()
        self.starting_room_id = 0

    @classmethod
    def generate(cls, random_seed: Optional[int] = None) -> 'GameWorld':
        world = cls()
        if random_seed:
            random.seed(random_seed)
        try:
            world.ensure_data_directory_exists()
            world.load_templates()
            world.generate_random_locations()
            world.generate_random_monsters()
            if not world.rooms:
                world.create_fallback_rooms()
            world.current_room = world.get_room(world.starting_room_id) or world.rooms[0]
            logger.debug(f"Generated world with {len(world.rooms)} rooms")
            return world
        except Exception as e:
            logger.error(f"World generation failed: {e}")
            return cls().create_minimal_world()

    def create_minimal_world(self) -> 'GameWorld':
        fallback_world = GameWorld()
        fallback_room = Room(
            room_id=0,
            name="Safe Room",
            description="A plain stone chamber with torches on the walls.",
            exits={'north': 1, 'east': 2, 'south': 3, 'west': 4}
        )
        fallback_world.rooms = [fallback_room]
        fallback_world.default_race = get_default_race()
        fallback_world.default_class = get_default_class()
        fallback_world.current_room = fallback_room
        logger.debug("Created minimal world with Safe Room")
        return fallback_world

    def create_fallback_rooms(self) -> None:
        basic_rooms = [
            Room(0, "Town Square", "The heart of the town with a central fountain.", exits={'north': 1, 'east': 2}),
            Room(1, "Market Street", "Vendors sell their wares along the road.", exits={'south': 0}),
            Room(2, "Blacksmith", "The clang of hammer on anvil fills the air.", exits={'west': 0})
        ]
        self.rooms.extend(basic_rooms)
        logger.debug("Created fallback rooms")

    def ensure_data_directory_exists(self) -> None:
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        template_path = data_dir / "location_templates.json"
        if not template_path.exists():
            default_templates = [{
                "name": ["{adjective} {type}", "The {feature} of {type}"],
                "description": "This {type} has {feature}. The air smells {adjective}.",
                "types": ["room", "chamber", "hall", "cave"],
                "adjectives": ["damp", "cold", "stale", "musty"],
                "features": ["cracked walls", "a strange glow", "unusual carvings"]
            }]
            with open(template_path, 'w') as f:
                json.dump(default_templates, f, indent=2)
            logger.debug("Created default location_templates.json")

    def load_templates(self) -> None:
        try:
            base_dir = Path(__file__).parent.parent
            with open(base_dir / "data" / "location_templates.json") as f:
                self.location_templates = json.load(f)
            logger.debug(f"Loaded {len(self.location_templates)} location templates")
        except Exception as e:
            logger.warning(f"Failed to load templates: {e}")
            self.location_templates = [{
                "name": ["Basic {type}"],
                "description": "A simple {type} with {feature}.",
                "types": ["room"],
                "adjectives": ["plain"],
                "features": ["nothing unusual"]
            }]
            logger.debug("Loaded fallback location templates")

    def generate_random_locations(self, num_rooms: int = 10) -> None:
        self.rooms = []
        room_ids = list(range(num_rooms))
        random.shuffle(room_ids)
        connections = {str(i): {} for i in room_ids}

        for i in range(num_rooms):
            current = str(room_ids[i])
            if i > 0:
                prev = str(room_ids[i-1])
                direction = random.choice(["north", "south", "east", "west"])
                opposite = {"north": "south", "south": "north", "east": "west", "west": "east"}[direction]
                connections[current][direction] = int(prev)
                connections[prev][opposite] = int(current)

        for room_id in room_ids:
            template = random.choice(self.location_templates)
            room_type = random.choice(template["types"])
            name_template = random.choice(template["name"])
            room = Room(
                room_id=room_id,
                name=name_template.format(
                    adjective=random.choice(template["adjectives"]),
                    type=room_type,
                    feature=random.choice(template["features"])
                ),
                description=template["description"].format(
                    type=room_type,
                    feature=random.choice(template["features"]),
                    adjective=random.choice(template["adjectives"])
                ),
                exits=connections.get(str(room_id), {})
            )
            if random.random() < 0.25:
                room.npcs.append(
                    NPC(
                        name=random.choice(["Elder Bran", "Mysterious Stranger", "Wounded Guard"]),
                        quest_offer=("Adventure_Types", "Dungeon_Crawl", "The_Sunken_Citadel")
                    )
                )
            self.rooms.append(room)
        logger.debug(f"Generated {num_rooms} random locations")

    def generate_random_monsters(self) -> None:
        monster_names = ["Goblin", "Orc", "Skeleton", "Zombie", "Wolf"]
        for room in self.rooms:
            if random.random() < 0.6:
                room.monsters = []
                for _ in range(random.randint(1, 3)):
                    base = get_monster_by_name(random.choice(monster_names))
                    if base:
                        room.monsters.append(Monster(**base.__dict__))
                logger.debug(f"Added monsters to room {room.id}: {[m.name for m in room.monsters]}")

    def get_room(self, room_id: int) -> Optional[Room]:
        try:
            room = next(r for r in self.rooms if r.id == room_id)
            logger.debug(f"Retrieved room {room_id}: {room.name}")
            return room
        except StopIteration:
            logger.warning(f"Room {room_id} not found")
            return None

    def move_player(self, direction: str) -> str:
        if not self.current_room:
            logger.error("No current room set")
            return "No current room set."
        exit_room_id = self.current_room.exits.get(direction)
        if not exit_room_id:
            logger.debug(f"No exit to {direction} from room {self.current_room.id}")
            return f"No exit to the {direction}."
        new_room = self.get_room(exit_room_id)
        if not new_room:
            logger.error(f"Destination room {exit_room_id} doesn't exist")
            return "Destination room doesn't exist."
        self.current_room = new_room
        logger.debug(f"Moved to room {new_room.id}: {new_room.name}")
        return self.describe_current_location()

    def describe_current_location(self) -> str:
        if not self.current_room:
            logger.error("No current room set")
            return "You are nowhere."
        desc = [
            f"\n{self.current_room.name}",
            self.current_room.description
        ]
        if self.current_room.exits:
            desc.append(f"\nExits: {', '.join(self.current_room.exits.keys())}")
        if self.current_room.monsters:
            desc.append(f"\nMonsters here: {', '.join(m.name for m in self.current_room.monsters)}")
        if self.current_room.npcs:
            desc.append(f"\nNPCs present: {', '.join(n.name for n in self.current_room.npcs)}")
        output = '\n'.join(desc)
        logger.debug(f"Describing room {self.current_room.id}: {output}")
        return output