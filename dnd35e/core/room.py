from typing import Dict, List, Optional, Union, Callable
from enum import Enum, auto
import random
from dnd_adventure.dnd35e.core.monsters import Monster
from dnd_adventure.dnd35e.core.items import Item, Trap, Puzzle
from dnd_adventure.dnd35e.core.effects import LightSource

class RoomType(Enum):
    TOWN = auto()
    DUNGEON = auto()
    WILDERNESS = auto()
    CASTLE = auto()
    SEWER = auto()
    TEMPLE = auto()
    CAVERN = auto()
    LABYRINTH = auto()

class Room:
    def __init__(self, room_id: int, name: str, description: str, 
                 room_type: RoomType = RoomType.DUNGEON,
                 exits: Optional[Dict[str, int]] = None,
                 monsters: Optional[List[Monster]] = None,
                 items: Optional[List[Union[Item, Trap, Puzzle]]] = None,
                 light_sources: Optional[List[LightSource]] = None,
                 on_enter: Optional[Callable] = None,
                 on_exit: Optional[Callable] = None):
        
        self.id = room_id
        self.name = name
        self.description = description
        self.type = room_type
        self.exits = exits or {}
        self.monsters = monsters or []
        self.items = items or []
        self.light_sources = light_sources or []
        self.on_enter = on_enter  # Callback when player enters
        self.on_exit = on_exit    # Callback when player exits
        self.visited = False
        self._is_lit = True  # Default state
        
        # Dynamic lighting calculation
        self.update_lighting()

    @property
    def is_lit(self):
        """Check if room has any active light sources"""
        return self._is_lit

    def update_lighting(self):
        """Recalculate lighting based on light sources"""
        self._is_lit = any(source.is_active for source in self.light_sources) or self.type in (RoomType.TOWN, RoomType.TEMPLE)

    def add_light_source(self, light: LightSource):
        """Add a light source to the room"""
        self.light_sources.append(light)
        self.update_lighting()

    def extinguish_light(self, index: int):
        """Turn off a specific light source"""
        if 0 <= index < len(self.light_sources):
            self.light_sources[index].is_active = False
            self.update_lighting()

    # ... (previous methods like add_exit, add_monster, etc.)

    def add_trap(self, trap: Trap):
        """Add a trap to the room"""
        self.items.append(trap)

    def add_puzzle(self, puzzle: Puzzle):
        """Add a puzzle to the room"""
        self.items.append(puzzle)

    def trigger_traps(self, character):
        """Check for and trigger traps in the room"""
        for item in self.items:
            if isinstance(item, Trap) and not item.disarmed:
                item.trigger(character)

    def attempt_puzzle(self, character, solution):
        """Attempt to solve a puzzle in the room"""
        for item in self.items:
            if isinstance(item, Puzzle) and not item.solved:
                return item.attempt_solution(character, solution)
        return False

    def get_room_state(self):
        """Return description based on lighting"""
        if self.is_lit:
            return self.description
        else:
            dark_desc = "Everything is pitch black. You can only see "
            if any(m for m in self.monsters if m.has_darkvision):
                dark_desc += "shadowy figures moving in the darkness!"
            else:
                dark_desc += "what's immediately in front of you."
            return dark_desc

class SampleRooms:
    @staticmethod
    def get_castle_rooms():
        """Castle locations with puzzles and traps"""
        return [
            Room(100, "Castle Courtyard",
                 "The crumbling castle walls loom above you. Weeds grow between the cobblestones.",
                 RoomType.CASTLE,
                 {'north': 101, 'east': 102},
                 [Monster("Skeletal Guard", 15)]),
            
            Room(101, "Throne Room",
                 "A massive stone throne sits atop a dais. Tattered banners hang from the walls.",
                 RoomType.CASTLE,
                 {'south': 100},
                 puzzles=[Puzzle(
                     "Throne Mechanism",
                     "The throne has strange symbols carved into its arms",
                     solution="press in order: lion, crown, sword",
                     reward=Item("Royal Signet Ring", "magic")
                 )]),
            
            Room(102, "Armory",
                 "Rusty weapons line the walls. A pressure plate is barely visible on the floor.",
                 RoomType.CASTLE,
                 {'west': 100, 'north': 103},
                 traps=[Trap(
                     "Pressure Plate",
                     "Triggers a falling portcullis",
                     dc=18,
                     damage="2d6",
                     disable_skill="Disable Device"
                 )])
        ]

    @staticmethod
    def get_sewer_rooms():
        """Sewer system with dynamic lighting"""
        return [
            Room(200, "Sewer Entrance",
                 "The stench is overwhelming. Flickering torchlight reveals slime-covered walls.",
                 RoomType.SEWER,
                 {'east': 201},
                 light_sources=[LightSource("Wall Torch", 20, True)]),
            
            Room(201, "Main Tunnel",
                 "The tunnel splits in three directions. The sound of dripping water echoes loudly.",
                 RoomType.SEWER,
                 {'west': 200, 'north': 202, 'south': 203},
                 [Monster("Giant Rat", 3)]),
            
            Room(202, "Flooded Chamber",
                 "This room is knee-deep in foul water. Something moves beneath the surface...",
                 RoomType.SEWER,
                 {'south': 201},
                 [Monster("Swarm of Rats", 6)],
                 light_sources=[LightSource("Bioluminescent Fungus", 10, True)]),
            
            Room(203, "Dark Tunnel",
                 "Complete darkness envelops this tunnel. The air smells of decay.",
                 RoomType.SEWER,
                 {'north': 201},
                 light_sources=[LightSource("Broken Torch", 0, False)])
        ]

    @staticmethod
    def get_temple_rooms():
        """Temple with interactive elements"""
        def healing_spring(character):
            if not hasattr(character, 'used_spring'):
                character.heal(character.max_hp)
                character.used_spring = True
                return "The sacred waters heal all your wounds!"
            return "The spring's power is depleted for today."

        return [
            Room(300, "Temple Sanctuary",
                 "Stained glass windows cast colorful light across marble floors.",
                 RoomType.TEMPLE,
                 {'south': 301, 'east': 302}),
            
            Room(301, "Healing Spring",
                 "A crystal-clear pool bubbles with magical energy.",
                 RoomType.TEMPLE,
                 {'north': 300},
                 on_enter=healing_spring),
            
            Room(302, "Chamber of Trials",
                 "Three statues hold out their hands as if expecting offerings.",
                 RoomType.TEMPLE,
                 {'west': 300},
                 puzzles=[Puzzle(
                     "Statue Offering",
                     "The statues require specific items",
                     solution="gold, silver, copper",
                     reward=Item("Blessed Amulet", "wondrous")
                 )])
        ]

    @staticmethod
    def get_all_rooms():
        """Combine all room types with enhanced features"""
        all_rooms = []
        all_rooms.extend(SampleRooms.get_town_rooms())
        all_rooms.extend(SampleRooms.get_dungeon_rooms())
        all_rooms.extend(SampleRooms.get_wilderness_rooms())
        all_rooms.extend(SampleRooms.get_castle_rooms())
        all_rooms.extend(SampleRooms.get_sewer_rooms())
        all_rooms.extend(SampleRooms.get_temple_rooms())
        
        # Add labyrinth rooms with special properties
        all_rooms.extend([
            Room(400, "Shifting Maze Entrance",
                 "The walls seem to move when you're not looking directly at them.",
                 RoomType.LABYRINTH,
                 {'east': 401}),
            
            Room(401, "Mirror Hall",
                 "Dozens of mirrors reflect your image infinitely in all directions.",
                 RoomType.LABYRINTH,
                 {'west': 400, 'north': 402},
                 puzzles=[Puzzle(
                     "Mirror Puzzle",
                     "One mirror shows a different reflection",
                     solution="break the true mirror",
                     reward="secret passage")]),
            
            Room(402, "Teleportation Circle",
                 "A glowing arcane circle covers the entire floor.",
                 RoomType.LABYRINTH,
                 {'south': 401},
                 on_enter=lambda c: c.change_location(random.choice([100, 200, 300])))
        ])
        
        return all_rooms