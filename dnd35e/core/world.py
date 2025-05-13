# dnd_adventure/dnd35e/core/world.py
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
from dnd_adventure.dnd35e.core.room import Room  # Using Room class instead of dict

logger = logging.getLogger(__name__)

class GameWorld:
    def __init__(self):
        self.rooms: List[Room] = []
        self.current_room: Optional[Room] = None
        self.monster_pool: List[Monster] = []
        self.location_templates: List[Dict] = []
        self.default_race = get_default_race()
        self.default_class = get_default_class()
        self.starting_room_id = 0  # Explicit starting point

    @classmethod
    def generate(cls, random_seed: Optional[int] = None) -> Dict:
        """Generate a world with guaranteed valid starting room"""
        world = cls()
        if random_seed:
            random.seed(random_seed)
            
        try:
            world.ensure_data_directory_exists()
            world.load_templates()
            world.generate_random_locations()
            world.generate_random_monsters()
            
            # Ensure at least one room exists
            if not world.rooms:
                world.create_fallback_rooms()
                
            world.current_room = world.get_room(world.starting_room_id) or world.rooms[0]
            
            return {
                'rooms': {room.id: room for room in world.rooms},
                'default_race': world.default_race,
                'default_class': world.default_class,
                'starting_room_id': world.starting_room_id
            }
        except Exception as e:
            logger.error(f"World generation failed: {e}")
            return world.create_minimal_world()

    def create_minimal_world(self) -> Dict:
        """Create a barebones world when generation fails"""
        fallback_room = Room(
            room_id=0,
            name="Safe Room",
            description="A plain stone chamber with torches on the walls.",
            exits={'north': 1, 'east': 2, 'south': 3, 'west': 4}
        )
        return {
            'rooms': {0: fallback_room},
            'default_race': get_default_race(),
            'default_class': get_default_class(),
            'starting_room_id': 0
        }

    def create_fallback_rooms(self) -> None:
        """Generate emergency rooms if normal generation fails"""
        basic_rooms = [
            Room(0, "Town Square", "The heart of the town with a central fountain.",
                exits={'north': 1, 'east': 2}),
            Room(1, "Market Street", "Vendors sell their wares along the road.",
                exits={'south': 0}),
            Room(2, "Blacksmith", "The clang of hammer on anvil fills the air.",
                exits={'west': 0})
        ]
        self.rooms.extend(basic_rooms)

    def ensure_data_directory_exists(self) -> None:
        """Create data directory with default templates if missing"""
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        template_path = data_dir / "location_templates.json"
        if not template_path.exists():
            default_templates = [
                {
                    "name": ["{adjective} {type}", "The {feature} of {type}"],
                    "description": "This {type} has {feature}. The air smells {adjective}.",
                    "types": ["room", "chamber", "hall", "cave"],
                    "adjectives": ["damp", "cold", "stale", "musty"],
                    "features": ["cracked walls", "a strange glow", "unusual carvings"]
                }
            ]
            with open(template_path, 'w') as f:
                json.dump(default_templates, f, indent=2)

    def load_templates(self) -> None:
        """Load location templates with error handling"""
        try:
            base_dir = Path(__file__).parent.parent
            with open(base_dir / "data" / "location_templates.json") as f:
                self.location_templates = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load templates: {e}")
            self.location_templates = [{
                "name": ["Basic {type}"],
                "description": "A simple {type} with {feature}.",
                "types": ["room"],
                "adjectives": ["plain"],
                "features": ["nothing unusual"]
            }]

    def generate_random_locations(self, num_rooms: int = 10) -> None:
        """Generate interconnected rooms using templates"""
        self.rooms = []
        room_ids = list(range(num_rooms))
        random.shuffle(room_ids)
        connections = {str(i): {} for i in room_ids}

        # Create circular path guarantee
        for i in range(num_rooms):
            current = str(room_ids[i])
            if i > 0:
                prev = str(room_ids[i-1])
                direction = random.choice(["north", "south", "east", "west"])
                opposite = {"north": "south", "south": "north", 
                           "east": "west", "west": "east"}[direction]
                connections[current][direction] = int(prev)
                connections[prev][opposite] = int(current)

        # Generate each room
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

            # 25% chance for NPC
            if random.random() < 0.25:
                room.npcs.append(
                    NPC(name=random.choice(["Elder Bran", "Mysterious Stranger", "Wounded Guard"]),
                    quest_offer=("Adventure_Types", "Dungeon_Crawl", "The_Sunken_Citadel")
                )

            self.rooms.append(room)

    def generate_random_monsters(self) -> None:
        """Populate rooms with monsters safely"""
        monster_names = ["Goblin", "Orc", "Skeleton", "Zombie", "Wolf"]
        for room in self.rooms:
            if random.random() < 0.6:  # 60% chance for monsters
                monster_count = random.randint(1, 3)
                room.monsters = []
                for _ in range(monster_count):
                    base = get_monster_by_name(random.choice(monster_names))
                    if base:
                        room.monsters.append(Monster(**base.__dict__))

    def get_room(self, room_id: int) -> Optional[Room]:
        """Safely get room by ID"""
        try:
            return next(room for room in self.rooms if room.id == room_id)
        except StopIteration:
            logger.warning(f"Room {room_id} not found")
            return None

    def move_player(self, direction: str) -> str:
        """Safely move player between rooms"""
        if not self.current_room:
            return "No current room set."
            
        exit_room_id = self.current_room.exits.get(direction)
        if not exit_room_id:
            return f"No exit to the {direction}."
            
        new_room = self.get_room(exit_room_id)
        if not new_room:
            return "Destination room doesn't exist."
            
        self.current_room = new_room
        return self.describe_current_location()

    def describe_current_location(self) -> str:
        """Generate safe room description"""
        if not self.current_room:
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
            
        return '\n'.join(desc)