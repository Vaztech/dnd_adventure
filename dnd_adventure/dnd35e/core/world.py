import os
import json
import random
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from dnd_adventure.dnd35e.core.monsters import get_monster_by_name, Monster
from dnd_adventure.races import get_default_race, Race
from dnd_adventure.classes import get_default_class, DnDClass, ClassFeature
from dnd_adventure.dnd35e.core.npc import NPC
from dnd_adventure.dnd35e.core.room import Room
from dnd_adventure.dnd35e.core.data_loader import DataLoader

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
        self.data_loader = DataLoader()

        self.race_data: Dict[str, Dict] = {}
        self.class_data: Dict[str, Dict] = {}
        self.races: List[Race] = []
        self.classes: List[DnDClass] = []

    @property
    def available_classes(self) -> List[str]:
        return [cls.name for cls in self.classes]

    def get_subraces(self, race_name: str) -> List[str]:
        race = next((r for r in self.races if r.name == race_name), None)
        if race and isinstance(race.subraces, dict):
            return list(race.subraces.keys())
        elif race and isinstance(race.subraces, list):
            return race.subraces
        return []

    def get_subclasses(self, class_name: str) -> List[str]:
        return list(self.class_data.get(class_name, {}).get("subclasses", {}).keys())

    def load_race_data(self) -> None:
        path = Path(__file__).parent.parent / "data" / "races.json"
        if path.exists():
            with open(path, 'r') as f:
                self.race_data = json.load(f)
            logger.debug(f"Loaded races: {list(self.race_data.keys())}")
        else:
            logger.warning("races.json not found")

    def load_class_data(self) -> None:
        path = Path(__file__).parent.parent / "data" / "classes.json"
        if path.exists():
            with open(path, 'r') as f:
                self.class_data = json.load(f)
            logger.debug(f"Loaded classes: {list(self.class_data.keys())}")
        else:
            logger.warning("classes.json not found")

    def load_races_from_json(self) -> List[Race]:
        self.races = self.data_loader.load_races_from_json()
        if not self.races:
            logger.warning("No races loaded from JSON, using default race")
            self.races = [get_default_race()]
        self.race_data = {race.name: race.__dict__ for race in self.races}
        logger.debug(f"Loaded races via DataLoader: {[race.name for race in self.races]}")
        return self.races

    def load_classes_from_json(self) -> List[DnDClass]:
        class_data = self.data_loader.load_classes_from_json()
        self.classes = []
        for cls_name, cls_info in class_data.items():
            try:
                if 'name' not in cls_info:
                    logger.error(f"Class {cls_name} missing 'name' field")
                    continue
                features = [
                    ClassFeature(f['name'], f['level'], f['description'])
                    for f in cls_info.get('features', [])
                ]
                required_fields = ['hit_die', 'base_attack_bonus', 'saving_throws', 'skill_points', 'class_skills']
                for field in required_fields:
                    if field not in cls_info:
                        logger.error(f"Class {cls_name} missing required field: {field}")
                        continue
                dnd_class = DnDClass(
                    name=cls_info['name'],
                    description=cls_info.get('description', 'No description available.'),
                    hit_die=cls_info['hit_die'],
                    base_attack_bonus=cls_info['base_attack_bonus'],
                    saving_throws=cls_info['saving_throws'],
                    skill_points=cls_info['skill_points'],
                    class_skills=cls_info['class_skills'],
                    spellcasting=cls_info.get('spellcasting'),
                    features=features,
                    subclasses=cls_info.get('subclasses')
                )
                self.classes.append(dnd_class)
            except Exception as e:
                logger.error(f"Failed to create DnDClass for {cls_name}: {e}")
        self.class_data = class_data
        if not self.classes:
            logger.warning("No classes loaded, using default class")
            self.classes = [get_default_class()]
            self.class_data = {cls.name: cls.to_dict() for cls in self.classes}
        logger.debug(f"Loaded classes: {[cls.name for cls in self.classes]}")
        return self.classes

    @classmethod
    def generate(cls, random_seed: Optional[int] = None) -> 'GameWorld':
        world = cls()
        if random_seed:
            random.seed(random_seed)
        try:
            world.ensure_data_directory_exists()
            world.load_templates()
            world.load_races_from_json()
            world.load_classes_from_json()
            # Temporarily disabled due to missing method
            # world.monster_pool = world.data_loader.load_monsters_from_json()
            world.generate_random_locations()
            if not world.rooms:
                world.create_fallback_rooms()
            world.generate_random_monsters()
            world.current_room = world.get_room(world.starting_room_id) or world.rooms[0]
            logger.debug(f"Generated world with {len(world.rooms)} rooms")
            return world
        except Exception as e:
            logger.error(f"World generation failed: {e}", exc_info=True)
            return cls().create_minimal_world()

    def create_minimal_world(self) -> 'GameWorld':
        fallback_world = GameWorld()
        rooms = [
            Room(
                room_id=0,
                name="Safe Room",
                description="A plain stone chamber with torches on the walls.",
                exits={'north': 1, 'east': 2, 'south': 3, 'west': 4}
            ),
            Room(
                room_id=1,
                name="North Room",
                description="A cold chamber with icy walls.",
                exits={'south': 0}
            ),
            Room(
                room_id=2,
                name="East Room",
                description="A dusty room filled with cobwebs.",
                exits={'west': 0}
            ),
            Room(
                room_id=3,
                name="South Room",
                description="A warm chamber with glowing embers.",
                exits={'north': 0}
            ),
            Room(
                room_id=4,
                name="West Room",
                description="A dark room with flickering shadows.",
                exits={'east': 0}
            )
        ]
        fallback_world.rooms = rooms
        fallback_world.default_race = get_default_race()
        fallback_world.default_class = get_default_class()
        fallback_world.current_room = rooms[0]
        logger.debug(f"Created minimal world with {len(rooms)} rooms: {[r.name for r in rooms]}")
        return fallback_world

    def create_fallback_rooms(self) -> None:
        basic_rooms = [
            Room(0, "Town Square", "The heart of the town with a central fountain.", exits={'north': 1, 'east': 2}),
            Room(1, "Market Street", "Vendors sell their wares along the road.", exits={'south': 0}),
            Room(2, "Blacksmith", "The clang of hammer on anvil fills the air.", exits={'west': 0})
        ]
        self.rooms.extend(basic_rooms)
        logger.debug(f"Created {len(basic_rooms)} fallback rooms: {[r.name for r in basic_rooms]}")

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

    def generate_random_locations(self, num_rooms: int = 5) -> None:
        self.rooms = []
        room_ids = list(range(num_rooms))
        random.shuffle(room_ids)
        connections = {i: {} for i in room_ids}

        for i in range(num_rooms):
            current = room_ids[i]
            if i > 0:
                prev = room_ids[i - 1]
                direction = random.choice(["north", "south", "east", "west"])
                opposite = {"north": "south", "south": "north", "east": "west", "west": "east"}[direction]
                connections[current][direction] = prev
                connections[prev][opposite] = current

        for room_id in room_ids:
            template = random.choice(self.location_templates)
            room_type = random.choice(template["types"])
            name_template = random.choice(template["name"])
            try:
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
                    exits=connections[room_id]
                )
            except KeyError as e:
                logger.error(f"Template formatting error for room {room_id}: {e}")
                room = Room(
                    room_id=room_id,
                    name=f"Room {room_id}",
                    description="A generic room.",
                    exits=connections[room_id]
                )
            if random.random() < 0.25:
                room.npcs.append(
                    NPC(
                        name=random.choice(["Elder Bran", "Mysterious Stranger", "Wounded Guard"]),
                        quest_offer=("Adventure_Types", "Dungeon_Crawl", "The_Sunken_Citadel")
                    )
                )
            self.rooms.append(room)
        logger.debug(f"Generated {num_rooms} random locations: {[r.name for r in self.rooms]}")

    def generate_random_monsters(self) -> None:
        if not self.monster_pool:
            logger.debug("Monster pool empty, using default Goblin")
            self.monster_pool = [Monster(
                name="Goblin",
                type="Humanoid",
                armor_class=15,
                hit_points=7,
                speed="30 ft.",
                challenge_rating=0.33,
                abilities={"STR": 8, "DEX": 14, "CON": 10, "INT": 10, "WIS": 8, "CHA": 8},
                attacks=[{"name": "Scimitar", "damage": "1d6+2", "attack_bonus": 4}]
            )]

        for room in self.rooms:
            if random.random() < 0.9:
                room.monsters = []
                num_monsters = random.randint(1, 3)
                logger.debug(f"Adding {num_monsters} monsters to room: {room.name}")
                for _ in range(num_monsters):
                    monster = random.choice(self.monster_pool)
                    room.monsters.append(Monster(**monster.__dict__))
                    logger.debug(f"Added monster: {monster.name} to room: {room.name}")

    def get_room(self, room_id: int) -> Optional[Room]:
        try:
            room = next(r for r in self.rooms if r.id == room_id)
            logger.debug(f"Retrieved room {room_id}: {room.name}, exits={room.exits}")
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