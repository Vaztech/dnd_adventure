import os
import json
from pathlib import Path
from .monster import Monster

class GameWorld:
    def __init__(self):
        self.rooms = []
        self.current_room = None

    @classmethod
    def generate(cls):
        world = cls()
        world.ensure_data_directory_exists()
        world.load_locations()
        world.populate_monsters(world.load_monsters())
        world.current_room = world.rooms[0] if world.rooms else None
        return world

    def ensure_data_directory_exists(self):
        """Create data directory and default files if they don't exist"""
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "dnd35e" / "core"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Default locations data
        default_locations = {
            "rooms": [
                {
                    "id": 1,
                    "name": "Entrance Hall",
                    "description": "A grand hall with torches lining the walls.",
                    "exits": {"north": 2, "east": 3},
                    "monsters": []
                },
                {
                    "id": 2,
                    "name": "Throne Room",
                    "description": "An ornate room with a golden throne.",
                    "exits": {"south": 1},
                    "monsters": []
                },
                {
                    "id": 3,
                    "name": "Dungeon",
                    "description": "A dark, damp room with chains on the walls.",
                    "exits": {"west": 1},
                    "monsters": []
                }
            ]
        }
        
        # Default monsters data
        default_monsters = {
            "1": [
                {
                    "name": "Goblin",
                    "hp": 7,
                    "attack": 4,
                    "defense": 2
                }
            ],
            "2": [
                {
                    "name": "Orc",
                    "hp": 15,
                    "attack": 8,
                    "defense": 5
                }
            ],
            "3": [
                {
                    "name": "Skeleton",
                    "hp": 12,
                    "attack": 6,
                    "defense": 3
                }
            ]
        }
        
        # Create locations.json if it doesn't exist
        locations_file = data_dir / "locations.json"
        if not locations_file.exists():
            with open(locations_file, "w") as f:
                json.dump(default_locations, f, indent=2)
        
        # Create monsters.json if it doesn't exist
        monsters_file = data_dir / "monsters.json"
        if not monsters_file.exists():
            with open(monsters_file, "w") as f:
                json.dump(default_monsters, f, indent=2)

    def load_locations(self):
        try:
            base_dir = Path(__file__).parent.parent
            path = base_dir / "dnd35e" / "core" / "locations.json"
            with open(path, "r") as f:
                data = json.load(f)
                self.rooms = data.get("rooms", [])
                
                # Ensure we have at least one room
                if not self.rooms:
                    self.rooms = [{
                        "id": 1,
                        "name": "Default Room",
                        "description": "A plain room with stone walls.",
                        "exits": {},
                        "monsters": []
                    }]
                    
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: {e}. Using default room setup.")
            self.rooms = [{
                "id": 1,
                "name": "Emergency Room",
                "description": "A featureless white room.",
                "exits": {},
                "monsters": []
            }]

    def load_monsters(self):
        try:
            base_dir = Path(__file__).parent.parent
            path = base_dir / "dnd35e" / "core" / "monsters.json"
            with open(path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: {e}. Using empty monster data.")
            return {}

    def populate_monsters(self, monster_data):
        for room in self.rooms:
            room_id = str(room['id'])
            if room_id in monster_data:
                room['monsters'] = [
                    Monster(**data) for data in monster_data[room_id]
                ]
            else:
                room['monsters'] = []

    def get_room(self, room_id):
        for room in self.rooms:
            if room['id'] == room_id:
                return room
        return None