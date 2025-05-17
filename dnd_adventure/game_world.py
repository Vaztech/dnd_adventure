from typing import Dict
from dnd_adventure.room import Room, RoomType
from dnd_adventure.world import World

class GameWorld:
    def __init__(self, world: World):
        self.world = world
        self.rooms: Dict[str, Room] = {}
        self.generate_dungeons_and_castles()

    def generate_dungeons_and_castles(self):
        map_data = self.world.map
        width, height = map_data["width"], map_data["height"]
        for y in range(height):
            for x in range(width):
                tile = self.world.get_location(x, y)
                if tile["type"] in ["dungeon", "castle"]:
                    room_id = f"{x},{y}"
                    description = f"A dark {tile['type']} room at ({x},{y}) in {tile['name']}"
                    exits = {}
                    for direction, (dx, dy) in [("north", (0, 1)), ("south", (0, -1)), ("east", (1, 0)), ("west", (-1, 0))]:
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < width and 0 <= new_y < height:
                            new_tile = self.world.get_location(new_x, new_y)
                            if new_tile["type"] == tile["type"]:
                                exits[direction] = f"{new_x},{new_y}"
                    # Use Room with RoomType enum
                    self.rooms[room_id] = Room(
                        room_id=int(room_id.replace(",", "")),
                        name=tile["name"],
                        description=description,
                        room_type=RoomType.DUNGEON if tile["type"] == "dungeon" else RoomType.CASTLE,
                        exits=exits
                    )