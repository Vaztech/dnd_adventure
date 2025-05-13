import os
import json
import random
from pathlib import Path

from .monsters import get_monster_by_name, Monster
from ...races import get_default_race  # Use dnd_adventure.races
from ...classes import get_default_class  # Use dnd_adventure.classes
from .npc import NPC

class GameWorld:
    def __init__(self):
        self.rooms = []
        self.current_room = None
        self.monster_pool = []
        self.location_templates = []
        self.default_race = get_default_race()
        self.default_class = get_default_class()

    @classmethod
    def generate(cls, random_seed=None):
        world = cls()
        if random_seed:
            random.seed(random_seed)
        world.ensure_data_directory_exists()
        world.load_templates()
        world.generate_random_locations()
        world.generate_random_monsters()
        world.current_room = world.rooms[0] if world.rooms else None
        return world

    def ensure_data_directory_exists(self):
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "dnd35e" / "core"
        data_dir.mkdir(parents=True, exist_ok=True)

        # Location templates
        location_file = data_dir / "location_templates.json"
        if not location_file.exists():
            default_locations = [
                {
                    "name": ["Dark {type}", "Forgotten {type}", "Ancient {type}"],
                    "description": "A {adjective} {type} with {feature}.",
                    "types": ["cave", "tunnel", "chamber", "hall"],
                    "adjectives": ["spooky", "damp", "cold", "eerie"],
                    "features": ["strange markings", "a mysterious glow", "an unsettling silence"]
                }
            ]
            with open(location_file, "w") as f:
                json.dump(default_locations, f, indent=2)

    def load_templates(self):
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "dnd35e" / "core"

        try:
            with open(data_dir / "location_templates.json", "r") as f:
                self.location_templates = json.load(f)
        except Exception:
            print("⚠ Failed to load templates, using fallback.")
            self.location_templates = [{
                "name": ["Unknown {type}"],
                "description": "A {adjective} {type} filled with {feature}.",
                "types": ["room"],
                "adjectives": ["plain"],
                "features": ["dust and echoes"]
            }]

    def generate_random_locations(self, num_rooms=10):
        self.rooms = []
        room_ids = list(range(1, num_rooms + 1))
        random.shuffle(room_ids)
        connections = {}

        for i in range(num_rooms):
            current = str(room_ids[i])
            connections[current] = {}
            if i > 0:
                prev = str(room_ids[i - 1])
                direction = random.choice(["north", "south", "east", "west"])
                opposite = {"north": "south", "south": "north", "east": "west", "west": "east"}[direction]
                connections[current][direction] = int(prev)
                connections[prev][opposite] = int(current)

        for room_id in room_ids:
            template = random.choice(self.location_templates)
            room_type = random.choice(template["types"])
            room_name = random.choice(template["name"]).format(type=room_type)
            room_desc = template["description"].format(
                adjective=random.choice(template["adjectives"]),
                type=room_type,
                feature=random.choice(template["features"])
            )

            room = {
                "id": room_id,
                "name": room_name,
                "description": room_desc,
                "exits": connections.get(str(room_id), {}),
                "monsters": [],
                "npcs": []
            }

            if random.random() < 0.25:
                room["npcs"].append(
                    NPC(name="Elder Bran", quest_offer=("Adventure_Types", "Dungeon_Crawl", "The_Sunken_Citadel"))
                )

            self.rooms.append(room)

    def generate_random_monsters(self):
        names = ["Goblin", "Orc", "Skeleton", "Zombie", "Wolf", "Kobold"]
        for room in self.rooms:
            if random.random() < 0.6:
                room["monsters"] = []
                for _ in range(random.randint(1, 3)):
                    base = get_monster_by_name(random.choice(names))
                    if base:
                        room["monsters"].append(Monster(**base.__dict__))

    def get_room(self, room_id):
        return next((room for room in self.rooms if room["id"] == room_id), None)

    def get_random_room(self):
        return random.choice(self.rooms) if self.rooms else None

    def move_player(self, direction):
        """Move the player to a new room based on the direction."""
        if not self.current_room:
            return "No current room set."
        
        exits = self.current_room.get("exits", {})
        if direction not in exits:
            return f"No exit to the {direction}."
        
        new_room_id = exits[direction]
        new_room = self.get_room(new_room_id)
        if new_room:
            self.current_room = new_room
            return self.describe_current_location()
        return "Cannot move to that location."

    def describe_current_location(self):
        """Describe the current room, including exits, monsters, and NPCs."""
        if not self.current_room:
            return "You are nowhere."
        
        desc = f"\n{self.current_room['name']}\n{self.current_room['description']}\n"
        exits = self.current_room.get("exits", {})
        if exits:
            desc += f"Exits: {', '.join(exits.keys())}\n"
        else:
            desc += "No visible exits.\n"
        
        monsters = self.current_room.get("monsters", [])
        if monsters:
            desc += f"Monsters: {', '.join(m.name for m in monsters)}\n"
        
        npcs = self.current_room.get("npcs", [])
        if npcs:
            desc += f"NPCs: {', '.join(npc.name for npc in npcs)}\n"
        
        return desc