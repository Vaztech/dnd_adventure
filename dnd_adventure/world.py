import random
import json
import os
from typing import Dict, List, Tuple, Optional
from colorama import Fore, Style
import logging
import pickle
from dnd_adventure.paths import get_resource_path

logger = logging.getLogger(__name__)

class Room:
    def __init__(self, description: str, exits: Dict[str, str], monsters: List = None, items: List = None, visited: bool = False):
        self.description = description
        self.exits = exits
        self.monsters = monsters if monsters is not None else []
        self.items = items if items is not None else []
        self.visited = visited

class GameWorld:
    def __init__(self, world: 'World'):
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
                    self.rooms[room_id] = Room(description=description, exits=exits)

class Monster:
    def __init__(self, name: str, hp: int, attacks: List[Dict], armor_class: int = 10):
        self.name = name
        self.hp = hp
        self.attacks = attacks  # List of dicts with "attack_bonus" and "damage"
        self.armor_class = armor_class

class World:
    def __init__(self, seed: Optional[int] = None, graphics: Dict = None):
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        random.seed(self.seed)
        self.name = self.generate_name()
        self.graphics = graphics if graphics else {}
        self.map = self.load_or_generate_map()
        self.history = self.generate_history()

    def generate_name(self) -> str:
        prefixes = ["Eldr", "Thal", "Vyr", "Kael", "Drak", "Fyr"]
        suffixes = ["ion", "stead", "moor", "wyn", "gard", "thyr"]
        return random.choice(prefixes) + random.choice(suffixes)

    def load_or_generate_map(self) -> Dict:
        cache_path = os.path.join("dnd_adventure", "map_cache.pkl")
        try:
            with open(cache_path, "rb") as f:
                cached_map = pickle.load(f)
            logger.info("Loaded map from cache.")
            return cached_map
        except Exception as e:
            logger.error(f"Failed to load map cache from {cache_path}: {e}. Regenerating map.")
            new_map = self.generate_map()
            try:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "wb") as f:
                    pickle.dump(new_map, f)
                logger.info(f"Saved generated map to cache at {cache_path}.")
            except Exception as e:
                logger.error(f"Failed to save map cache to {cache_path}: {e}")
            return new_map

    def generate_map(self) -> Dict:
        width, height = 192, 192  # Adjusted for Dwarf Fortress scale
        map_data = {
            "width": width,
            "height": height,
            "locations": [],
            "countries": []
        }

        for y in range(height):
            row = []
            for x in range(width):
                terrain = self.generate_terrain(x, y, width, height)
                row.append({
                    "x": x,
                    "y": y,
                    "type": terrain,
                    "name": f"{terrain.capitalize()} at ({x},{y})",
                    "country": None
                })
            map_data["locations"].append(row)

        self.assign_countries(map_data)
        return map_data

    def generate_terrain(self, x: int, y: int, width: int, height: int) -> str:
        perlin = self.perlin_noise(x / 20.0, y / 20.0, self.seed)
        elevation = self.perlin_noise(x / 50.0, y / 50.0, self.seed + 1)
        if elevation > 0.7:
            return "mountain"
        elif perlin < 0.2:
            return random.choice(["river", "lake", "ocean"])
        elif perlin < 0.4:
            return "plains"
        elif perlin < 0.6:
            return "forest"
        elif perlin < 0.7:
            return "dungeon"
        else:
            return "castle"

    def perlin_noise(self, x: float, y: float, seed: int) -> float:
        random.seed(seed + int(x * 1000 + y))
        return random.random()

    def assign_countries(self, map_data: Dict):
        width, height = map_data["width"], map_data["height"]
        num_countries = random.randint(3, 6)
        countries = []
        for i in range(num_countries):
            capital_x, capital_y = random.randint(0, width - 1), random.randint(0, height - 1)
            countries.append({
                "id": i,
                "name": self.generate_name(),
                "capital": (capital_x, capital_y)
            })

        for y in range(height):
            for x in range(width):
                closest_country = min(countries, key=lambda c: (c["capital"][0] - x) ** 2 + (c["capital"][1] - y) ** 2)
                map_data["locations"][y][x]["country"] = closest_country["id"]

        map_data["countries"] = countries

    def generate_history(self) -> List[Dict]:
        history = []
        num_eras = random.randint(3, 5)
        current_year = 0
        for i in range(num_eras):
            era_length = random.randint(100, 500)
            era = {
                "name": f"Era {i + 1}",
                "start_year": current_year,
                "events": []
            }
            num_events = random.randint(2, 5)
            for j in range(num_events):
                event_year = current_year + random.randint(0, era_length)
                event_desc = random.choice([
                    f"The kingdom of {self.generate_name()} is founded by a legendary hero.",
                    f"A great war breaks out between {self.generate_name()} and {self.generate_name()}.",
                    f"An ancient artifact, the {self.generate_name()} Stone, is discovered.",
                    f"The {self.generate_name()} Plague devastates the population."
                ])
                era["events"].append({"year": event_year, "desc": event_desc})
            history.append(era)
            current_year += era_length
        return history

    def get_location(self, x: int, y: int) -> Dict:
        if 0 <= y < self.map["height"] and 0 <= x < self.map["width"]:
            return self.map["locations"][y][x]
        return {"type": "void", "name": "Void", "country": None}

    def display_map(self, player_pos: Tuple[int, int]) -> str:
        view_radius = 5
        x, y = player_pos
        map_display = []
        for dy in range(view_radius, -view_radius - 1, -1):
            row = ""
            for dx in range(-view_radius, view_radius + 1):
                map_x, map_y = x + dx, y + dy
                if 0 <= map_x < self.map["width"] and 0 <= map_y < self.map["height"]:
                    tile = self.map["locations"][map_y][map_x]
                    terrain_type = tile["type"]
                    if (map_x, map_y) == (x, y):
                        row += Fore.RED + "@" + Style.RESET_ALL
                    else:
                        symbol_data = self.graphics.get("terrains", {}).get(terrain_type, {"symbol": "?", "color": "white"})
                        symbol = symbol_data["symbol"]
                        color = symbol_data["color"]
                        if color == "gray":
                            row += Fore.LIGHTBLACK_EX + symbol + Style.RESET_ALL
                        elif color == "dark_green":
                            row += Fore.GREEN + symbol + Style.RESET_ALL
                        elif color == "green":
                            row += Fore.GREEN + symbol + Style.RESET_ALL
                        elif color == "light_green":
                            row += Fore.LIGHTGREEN_EX + symbol + Style.RESET_ALL
                        elif color == "light_green_ex":
                            row += Fore.LIGHTGREEN_EX + symbol + Style.RESET_ALL
                        elif color == "blue":
                            row += Fore.BLUE + symbol + Style.RESET_ALL
                        elif color == "light_blue_ex":
                            row += Fore.LIGHTBLUE_EX + symbol + Style.RESET_ALL
                        elif color == "cyan":
                            row += Fore.CYAN + symbol + Style.RESET_ALL
                        elif color == "light_cyan_ex":
                            row += Fore.LIGHTCYAN_EX + symbol + Style.RESET_ALL
                        elif color == "yellow":
                            row += Fore.YELLOW + symbol + Style.RESET_ALL
                        elif color == "light_yellow_ex":
                            row += Fore.LIGHTYELLOW_EX + symbol + Style.RESET_ALL
                        elif color == "red":
                            row += Fore.RED + symbol + Style.RESET_ALL
                        elif color == "light_red_ex":
                            row += Fore.LIGHTRED_EX + symbol + Style.RESET_ALL
                        elif color == "brown":
                            row += Fore.LIGHTRED_EX + symbol + Style.RESET_ALL
                        elif color == "magenta":
                            row += Fore.MAGENTA + symbol + Style.RESET_ALL
                        elif color == "light_magenta_ex":
                            row += Fore.LIGHTMAGENTA_EX + symbol + Style.RESET_ALL
                        elif color == "light_black_ex":
                            row += Fore.LIGHTBLACK_EX + symbol + Style.RESET_ALL
                        elif color == "white":
                            row += Fore.WHITE + symbol + Style.RESET_ALL
                        elif color == "light_white_ex":
                            row += Fore.LIGHTWHITE_EX + symbol + Style.RESET_ALL
                        elif color == "black":
                            row += Fore.BLACK + symbol + Style.RESET_ALL
                        else:
                            print(f"{Fore.YELLOW}Warning: Unsupported color '{color}' for symbol '{symbol}' in terrain.{Style.RESET_ALL}")
                            row += symbol  # Fallback: no color applied
                else:
                    row += " "
            map_display.append(row)
        return "\n".join(map_display)