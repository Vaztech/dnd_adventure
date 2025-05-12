import os
import json
import random
from pathlib import Path
from .dnd35e.core.monsters import get_monster_by_name, Monster
from .dnd35e.core.races import get_default_race
from .dnd35e.core.classes import get_default_class

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
                    "features": ["strange markings on the walls", "a mysterious glow", "an unsettling silence"]
                },
                {
                    "name": ["Ruined {type}", "Abandoned {type}", "Destroyed {type}"],
                    "description": "The remains of a {adjective} {type} that {feature}.",
                    "types": ["temple", "library", "forge", "barracks"],
                    "adjectives": ["once-magnificent", "ancient", "crumbling"],
                    "features": ["has seen better days", "hints at past grandeur", "still holds secrets"]
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
            print("Warning: Could not load location templates. Using fallback.")
            self.location_templates = [{
                "name": ["Mysterious {type}"],
                "description": "A {adjective} {type} with {feature}.",
                "types": ["room"],
                "adjectives": ["plain"],
                "features": ["nothing interesting"]
            }]

    def generate_random_locations(self, num_rooms=10):
        self.rooms = []
        room_ids = list(range(1, num_rooms + 1))
        random.shuffle(room_ids)

        # Create connections
        connections = {}
        for i in range(num_rooms):
            connections[str(room_ids[i])] = {}
            if i > 0:
                direction = random.choice(["north", "south", "east", "west"])
                connections[str(room_ids[i])][direction] = room_ids[i - 1]
                opposite = {"north": "south", "south": "north", "east": "west", "west": "east"}[direction]
                connections[str(room_ids[i - 1])][opposite] = room_ids[i]

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
        available_names = ["Goblin", "Orc", "Skeleton", "Bandit", "Zombie", "Wolf", "Kobold"]
        for room in self.rooms:
            if random.random() < 0.6:  # 60% chance to spawn monsters
                num = random.randint(1, 3)
                room["monsters"] = []
                for _ in range(num):
                    name = random.choice(available_names)
                    monster = get_monster_by_name(name)
                    if monster:
                        # Clone with fresh HP
                        m = Monster(
                            name=monster.name,
                            type=monster.type,
                            armor_class=monster.armor_class,
                            hit_points=monster.hit_points,
                            speed=monster.speed,
                            challenge_rating=monster.challenge_rating,
                            abilities=monster.abilities,
                            attacks=monster.attacks,
                            spell_like_abilities=monster.spell_like_abilities,
                            abilities_list=monster.abilities_list
                        )
                        room["monsters"].append(m)

    def get_room(self, room_id):
        for room in self.rooms:
            if room["id"] == room_id:
                return room
        return None
    def get_random_room(self):
        if self.rooms:
            return random.choice(self.rooms)
        return None