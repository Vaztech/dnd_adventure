import random
import logging
from typing import Tuple
from dnd_adventure.room import Room, RoomType
from dnd_adventure.dnd35e.core.monsters import Monster, Attack
from dnd_adventure.npc import NPC

logger = logging.getLogger(__name__)

class MovementHandler:
    def __init__(self, game):
        self.game = game

    def handle_movement(self, direction: str):
        self.game.message = ""
        logger.debug(f"Handling movement: {direction}")
        if self.game.current_map:
            x, y = self.game.player_pos
            dx, dy = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}[direction]
            new_pos = (x + dx, y + dy)
            map_data = self.game.graphics["maps"][self.game.current_map]
            new_x, new_y = new_pos
            adjusted_y = len(map_data["layout"]) - 1 - new_y
            if (new_x < 0 or new_x >= len(map_data["layout"][0]) or
                new_y < 0 or new_y >= len(map_data["layout"])):
                self.game.current_map = None
                self.game.player_pos = self.game.last_world_pos
                self.game.current_room = None
                self.game.message = f"You exit the {self.game.current_map} and return to the world map."
                logger.debug(f"Exited mini-map to world map at {self.game.last_world_pos}")
            else:
                char = map_data["layout"][adjusted_y][new_x]
                symbol_type = map_data["symbols"].get(char, {"type": "unknown"})["type"]
                if symbol_type in ["wall", "building", "house", "tree"]:
                    self.game.message = f"You can't move {direction}! A {symbol_type} blocks your path."
                    logger.debug(f"Blocked movement {direction}: {symbol_type}")
                elif symbol_type == "door":
                    if self.game.current_map in ["castle", "dungeon"]:
                        room_id = f"{self.game.last_world_pos[0]},{self.game.last_world_pos[1]}"
                        room = self.game.game_world.rooms.get(room_id)
                        if room and direction in room.exits:
                            self.game.current_room = room.exits[direction]
                            self.game.last_world_pos = tuple(map(int, self.game.current_room.split(",")))
                            self.game.player_pos = (2, 2)
                            self.game.message = f"You pass through the door {direction} into a new {self.game.current_map} room."
                            logger.debug(f"Transitioned to room {self.game.current_room} via door {direction}")
                        else:
                            self.game.current_map = None
                            self.game.current_room = None
                            self.game.player_pos = self.game.last_world_pos
                            self.game.message = f"You exit the {self.game.current_map} through the door to the world map."
                            logger.debug(f"Exited {self.game.current_map} to world map via door")
                    else:
                        self.game.current_map = None
                        self.game.current_room = None
                        self.game.player_pos = self.game.last_world_pos
                        self.game.message = f"You exit the {self.game.current_map} through the door to the world map."
                        logger.debug(f"Exited house to world map")
                else:
                    self.game.player_pos = new_pos
                    self.game.message = f"You move {direction}."
                    logger.debug(f"Moved {direction} to {new_pos}")
        else:
            x, y = self.game.last_world_pos
            dx, dy = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}[direction]
            new_x, new_y = x + dx, y + dy
            if not (0 <= new_x < self.game.world.map["width"] and 0 <= new_y < self.game.world.map["height"]):
                self.game.message = "You cannot move beyond the edge of the world!"
                logger.debug("Blocked movement: World edge")
                return
            new_pos = (new_x, new_y)
            if self.game.current_room:
                room = self.game.game_world.rooms.get(self.game.current_room)
                if not room:
                    self.game.message = f"Error: Current room {self.game.current_room} does not exist. Resetting room."
                    logger.error(f"Room not found: {self.game.current_room}")
                    self.game.current_room = None
                    return
                if direction in room.exits:
                    self.game.current_room = room.exits[direction]
                    self.game.last_world_pos = tuple(map(int, self.game.current_room.split(",")))
                    self.game.player_pos = (2, 2)
                    self.game.message = f"You move {direction} to a new room."
                    logger.debug(f"Moved to room {self.game.current_room}")
                else:
                    self.game.message = "You can't go that way!"
                    logger.debug(f"Blocked movement: No exit {direction}")
            else:
                tile = self.game.world.get_location(*new_pos)
                if tile["type"] == "mountain":
                    self.game.message = "The mountains are too steep to climb!"
                    logger.debug("Blocked movement: Mountain")
                    return
                elif tile["type"] in ["river", "lake", "ocean"]:
                    self.game.message = f"You need a boat to cross the {tile['type']}!"
                    logger.debug(f"Blocked movement: {tile['type']}")
                    return
                self.game.last_world_pos = new_pos
                self.game.player_pos = new_pos
                self.game.message = f"You move {direction} to {tile['name']}."
                logger.debug(f"Moved {direction} to {tile['name']} at {new_pos}")
                if self.game.current_room and "temp_" in self.game.current_room:
                    del self.game.game_world.rooms[self.game.current_room]
                    self.game.current_room = None
                    logger.debug(f"Cleared temporary room: {self.game.current_room}")
                self.current_room = f"{self.game.last_world_pos[0]},{self.game.last_world_pos[1]}" if tile["type"] in ["dungeon", "castle"] else None
                if tile["type"] in self.game.graphics["maps"]:
                    self.game.current_map = tile["type"]
                    self.game.player_pos = (2, 2)
                    self.game.message = self.game.graphics["maps"][self.game.current_map]["description"]
                    logger.debug(f"Entered mini-map: {self.game.current_map}")
                elif tile["type"] in ["plains", "forest"] and random.random() < 0.1:
                    self.game.message = f"A wild Goblin ambushes you!"
                    temp_room_id = f"temp_{new_pos[0]},{new_pos[1]}"
                    self.game.game_world.rooms[temp_room_id] = Room(
                        room_id=int(temp_room_id.replace("temp_", "").replace(",", "")),
                        name="Ambush Site",
                        description="A sudden encounter in the wild!",
                        room_type=RoomType.WILDERNESS,
                        exits={},
                        monsters=[Monster(
                            name="Goblin",
                            type="humanoid",
                            armor_class=15,
                            hit_points=6,
                            speed=30,
                            challenge_rating=0.25,
                            attacks=[Attack(name="Scimitar", damage="1d4+1", attack_bonus=3)]
                        )],
                        npcs=[NPC(name="Traveler", dialog="Help! I'm caught in this ambush!", quest_offer=("main", "explore", 1))] if random.random() < 0.2 else []
                    )
                    self.game.current_room = temp_room_id
                    logger.debug(f"Triggered ambush at {temp_room_id}")