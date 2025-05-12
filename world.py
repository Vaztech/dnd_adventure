from random import choice, randint
from .dnd35e.core.monsters import MonsterTemplate, get_monsters_by_cr, get_monsters_by_type

class GameWorld:
    """World state container"""
    def __init__(self):
        self.rooms = {}
        self.current_time = 0
        self.player_location = None  # Tracks the player's current room

    @classmethod
    def generate(cls):
        """Create new world with 3.5e content"""
        from .dnd35e.data import load_monsters, load_locations
        world = cls()
        world.rooms = load_locations()  # Load predefined locations (dungeon rooms)
        world.populate_monsters(load_monsters())  # Populate rooms with monsters
        return world

    def populate_monsters(self, monster_data):
        """Add 3.5e monsters to world"""
        for room in self.rooms.values():
            room.monsters = [
                MonsterTemplate(**data) 
                for data in monster_data.get(room.id, [])
            ]

    def describe_current_location(self):
        """Describe the player's current location"""
        if self.player_location:
            return self.player_location.describe()
        return "You're lost in the void."

    def move_player(self, direction):
        """Move the player to another room"""
        if self.player_location and hasattr(self.player_location, direction):
            new_room = getattr(self.player_location, direction)
            if new_room:
                self.player_location = new_room
                return f"You move to the {new_room.name}."
        return "You can't move in that direction."

    def serialize(self):
        """Serialize the world state for saving"""
        return {
            'rooms': {room_id: room.serialize() for room_id, room in self.rooms.items()},
            'current_time': self.current_time,
            'player_location': self.player_location.name if self.player_location else None
        }

    @classmethod
    def deserialize(cls, data):
        """Deserialize the world state from saved data"""
        world = cls()
        world.current_time = data['current_time']
        world.player_location = world.rooms.get(data['player_location'])
        world.rooms = {room_id: DnDRoom.deserialize(room_data) for room_id, room_data in data['rooms'].items()}
        return world

class DnDRoom:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.monsters = []
        self.xp_reward = 0
        self.connections = {}
        
    def describe(self):
        """Describe the room and any creatures in it"""
        monster_list = ", ".join([monster.name for monster in self.monsters])
        return f"{self.description}\nMonsters here: {monster_list if monster_list else 'None'}"

    def populate_monsters(self, cr_range=(1, 3), monster_type=None):
        """Populate room with appropriate monsters"""
        self.monsters = []
        possible_monsters = get_monsters_by_cr(cr_range[1])

        if monster_type:
            possible_monsters = {k: v for k, v in possible_monsters.items() 
                                 if v.type.lower() == monster_type.lower()}

        if possible_monsters:
            num_monsters = randint(1, 4)
            self.monsters = [choice(list(possible_monsters.keys())) 
                             for _ in range(num_monsters)]

            # Set XP reward based on total CR
            total_cr = sum(possible_monsters[m].challenge_rating 
                           for m in self.monsters)
            self.xp_reward = int(total_cr * 100)

    def connect(self, direction, room):
        """Connect two rooms together in a specific direction"""
        self.connections[direction] = room
        room.connections[self.opposite_direction(direction)] = self

    def opposite_direction(self, direction):
        """Return the opposite direction (for bi-directional connections)"""
        opposites = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east', 'up': 'down', 'down': 'up'}
        return opposites.get(direction)

    def serialize(self):
        """Serialize room data for saving"""
        return {
            'name': self.name,
            'description': self.description,
            'monsters': [monster.serialize() for monster in self.monsters],
            'connections': self.connections,
            'xp_reward': self.xp_reward
        }

    @classmethod
    def deserialize(cls, data):
        """Deserialize room data from saved data"""
        room = cls(data['name'], data['description'])
        room.monsters = [MonsterTemplate.deserialize(monster_data) for monster_data in data['monsters']]
        room.xp_reward = data['xp_reward']
        room.connections = data['connections']
        return room

def create_world():
    """Example dungeon with themed areas"""
    rooms = {}
    
    # Entrance (low CR)
    entrance = DnDRoom(
        "Cave Entrance",
        "A damp cave mouth leading into darkness. Water drips from the ceiling."
    )
    entrance.populate_monsters((1, 2))
    
    # Goblin Warrens
    goblin_cavern = DnDRoom(
        "Goblin Cavern",
        "A foul-smelling chamber littered with bones and crude weapons."
    )
    goblin_cavern.populate_monsters((2, 4), "Humanoid")
    
    # Dragon's Lair (high CR)
    dragon_lair = DnDRoom(
        "Dragon's Lair",
        "A vast chamber filled with treasure. The air smells of sulfur."
    )
    dragon_lair.populate_monsters((10, 15), "Dragon")
    
    # Connect rooms
    entrance.connect('east', goblin_cavern)
    goblin_cavern.connect('west', entrance)
    goblin_cavern.connect('down', dragon_lair)
    dragon_lair.connect('up', goblin_cavern)

    # Return the entrance room as starting point
    return entrance
