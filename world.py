import os
import json
import random
from pathlib import Path
from .monster import Monster

class GameWorld:
    def __init__(self):
        self.rooms = []
        self.current_room = None
        self.monster_templates = []
        self.location_templates = []

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
        """Create data directory and default template files if they don't exist"""
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "dnd35e" / "core"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Monster templates
        monster_templates_file = data_dir / "monster_templates.json"
        if not monster_templates_file.exists():
            default_monsters = [
                {
                    "name": "Goblin",
                    "hp": (5, 10),
                    "attack": (3, 6),
                    "defense": (1, 3)
                },
                {
                    "name": "Orc",
                    "hp": (12, 18),
                    "attack": (6, 9),
                    "defense": (4, 6)
                },
                {
                    "name": "Skeleton",
                    "hp": (8, 14),
                    "attack": (4, 7),
                    "defense": (2, 4)
                },
                {
                    "name": "Bandit",
                    "hp": (10, 15),
                    "attack": (5, 8),
                    "defense": (3, 5)
                }
            ]
            with open(monster_templates_file, "w") as f:
                json.dump(default_monsters, f, indent=2)
        
        # Location templates
        location_templates_file = data_dir / "location_templates.json"
        if not location_templates_file.exists():
            default_locations = [
                {
                    "name": ["Dark {type}", "Forgotten {type}", "Ancient {type}"],
                    "description": "A {adjective} {type} with {feature}.",
                    "types": ["cave", "tunnel", "chamber", "hall"],
                    "adjectives": ["spooky", "damp", "cold", "eerie"],
                    "features": ["strange markings on the walls", 
                               "a mysterious glow", 
                               "an unsettling silence"]
                },
                {
                    "name": ["Ruined {type}", "Abandoned {type}", "Destroyed {type}"],
                    "description": "The remains of a {adjective} {type} that {feature}.",
                    "types": ["temple", "library", "forge", "barracks"],
                    "adjectives": ["once-magnificent", "ancient", "crumbling"],
                    "features": ["has seen better days", 
                               "hints at past grandeur", 
                               "still holds secrets"]
                }
            ]
            with open(location_templates_file, "w") as f:
                json.dump(default_locations, f, indent=2)

    def load_templates(self):
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "dnd35e" / "core"
        
        # Load monster templates
        try:
            with open(data_dir / "monster_templates.json", "r") as f:
                self.monster_templates = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Warning: Could not load monster templates. Using defaults.")
            self.monster_templates = [
                {
                    "name": "Goblin",
                    "hp": (5, 10),
                    "attack": (3, 6),
                    "defense": (1, 3)
                }
            ]
        
        # Load location templates
        try:
            with open(data_dir / "location_templates.json", "r") as f:
                self.location_templates = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Warning: Could not load location templates. Using defaults.")
            self.location_templates = [
                {
                    "name": ["Dark {type}"],
                    "description": "A {adjective} {type}.",
                    "types": ["room"],
                    "adjectives": ["plain"],
                    "features": ["nothing unusual"]
                }
            ]

    def generate_random_locations(self, num_rooms=10):
        self.rooms = []
        room_ids = list(range(1, num_rooms + 1))
        random.shuffle(room_ids)
        
        # Generate connections between rooms
        connections = {}
        for i in range(num_rooms):
            connections[str(room_ids[i])] = {}
            if i > 0:
                direction = random.choice(["north", "south", "east", "west"])
                connections[str(room_ids[i])][direction] = room_ids[i-1]
                opposite_dir = {"north": "south", "south": "north", 
                              "east": "west", "west": "east"}[direction]
                connections[str(room_ids[i-1])][opposite_dir] = room_ids[i]
        
        # Generate each room
        for room_id in room_ids:
            template = random.choice(self.location_templates)
            room_type = random.choice(template["types"])
            room_name = random.choice(template["name"]).format(type=room_type)
            room_desc = template["description"].format(
                adjective=random.choice(template["adjectives"]),
                type=room_type,
                feature=random.choice(template["features"])
            )
            
            self.rooms.append({
                "id": room_id,
                "name": room_name,
                "description": room_desc,
                "exits": connections.get(str(room_id), {}),
                "monsters": []
            })

    def generate_random_monsters(self):
        for room in self.rooms:
            # 60% chance to have monsters in a room
            if random.random() < 0.6:
                num_monsters = random.randint(1, 3)
                room['monsters'] = []
                for _ in range(num_monsters):
                    template = random.choice(self.monster_templates)
                    room['monsters'].append(Monster(
                        name=template["name"],
                        hp=random.randint(*template["hp"]),
                        attack=random.randint(*template["attack"]),
                        defense=random.randint(*template["defense"])
                    ))

    def get_room(self, room_id):
        for room in self.rooms:
            if room['id'] == room_id:
                return room
        return None