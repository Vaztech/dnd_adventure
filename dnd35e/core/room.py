from typing import Dict, List, Optional, Union, Callable
from enum import Enum, auto
import random
from dnd_adventure.dnd35e.core.monsters import Monster
from dnd_adventure.dnd35e.core.items import Item, Trap, Puzzle
from dnd_adventure.dnd35e.core.effects import LightSource
from dnd_adventure.dnd35e.core.npc import NPC

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
                 npcs: Optional[List[NPC]] = None,
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
        self.npcs = npcs or []
        self.on_enter = on_enter
        self.on_exit = on_exit
        self.visited = False
        self._is_lit = True

        self.update_lighting()

    @property
    def is_lit(self):
        return self._is_lit

    def update_lighting(self):
        self._is_lit = any(source.is_active for source in self.light_sources) or self.type in (RoomType.TOWN, RoomType.TEMPLE)

    def add_light_source(self, light: LightSource):
        self.light_sources.append(light)
        self.update_lighting()

    def extinguish_light(self, index: int):
        if 0 <= index < len(self.light_sources):
            self.light_sources[index].is_active = False
            self.update_lighting()

    def add_trap(self, trap: Trap):
        self.items.append(trap)

    def add_puzzle(self, puzzle: Puzzle):
        self.items.append(puzzle)

    def trigger_traps(self, character):
        for item in self.items:
            if isinstance(item, Trap) and not item.disarmed:
                item.trigger(character)

    def attempt_puzzle(self, character, solution):
        for item in self.items:
            if isinstance(item, Puzzle) and not item.solved:
                return item.attempt_solution(character, solution)
        return False

    def get_room_state(self):
        if self.is_lit:
            return self.description
        else:
            dark_desc = "Everything is pitch black. You can only see "
            if any(m for m in self.monsters if m.has_darkvision):
                dark_desc += "shadowy figures moving in the darkness!"
            else:
                dark_desc += "what's immediately in front of you."
            return dark_desc