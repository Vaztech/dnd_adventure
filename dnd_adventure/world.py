import random
from typing import Dict, List, Tuple, Optional
from colorama import Fore, Style

class Monster:
    def __init__(self, name: str, hp: int, attacks: List[Dict]):
        self.name = name
        self.hp = hp
        self.attacks = attacks

class Room:
    def __init__(self, description: str, exits: Dict[str, str], monsters: List['Monster'] = None, items: List[str] = None):
        self.description = description
        self.exits = exits
        self.monsters = monsters or []
        self.items = items or []
        self.visited = False

class World:
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.name = self._generate_name()
        self.map = {"width": 20, "height": 20, "tiles": {}}
        self.history = self._generate_history()
        self._generate_map()

    def _generate_name(self) -> str:
        prefixes = ["Eryn", "Thal", "Vor", "Syl", "Kor"]
        suffixes = ["dia", "vania", "thar", "mor", "land"]
        return f"{random.choice(prefixes)}{random.choice(suffixes)}"

    def _generate_history(self) -> List[Dict]:
        eras = [
            {"name": "Age of Creation", "start_year": -1500, "events": []},
            {"name": "Age of Empires", "start_year": -500, "events": []},
            {"name": "Age of Heroes", "start_year": 0, "events": []}
        ]
        countries = ["Stormhold", "Silverlake", "Ironwood", "Duskmoor"]
        for era in eras:
            num_events = random.randint(3, 5)
            for _ in range(num_events):
                year = era["start_year"] + random.randint(0, 1000)
                country = random.choice(countries)
                events = [
                    f"{country} is founded by {self._generate_hero()}",
                    f"{country} defeats {random.choice(countries)} in the {self._generate_war()}",
                    f"A {random.choice(['dragon', 'demon', 'lich'])} threatens {country}",
                    f"{country} discovers the {self._generate_artifact()}"
                ]
                era["events"].append({"year": year, "desc": random.choice(events)})
            era["events"].sort(key=lambda x: x["year"])
        return eras

    def _generate_hero(self) -> str:
        names = ["Aric", "Elara", "Thane", "Liora", "Kael"]
        titles = ["Ironfoot", "Starblade", "Duskborn", "Lightbringer"]
        return f"{random.choice(names)} {random.choice(titles)}"

    def _generate_war(self) -> str:
        return f"{random.choice(['Battle', 'War', 'Siege'])} of {random.choice(['Dawn', 'Dusk', 'Iron', 'Shadow'])}"

    def _generate_artifact(self) -> str:
        return f"{random.choice(['Sword', 'Crown', 'Orb', 'Tome'])} of {random.choice(['Eternity', 'Flame', 'Void'])}"

    def _find_empty_spot(self, max_attempts: int = 100) -> Optional[Tuple[int, int]]:
        attempts = 0
        while attempts < max_attempts:
            x = random.randint(0, self.map["width"] - 1)
            y = random.randint(0, self.map["height"] - 1)
            if (x, y) not in self.map["tiles"]:
                return x, y
            attempts += 1
        # Fallback: Find any empty spot
        for x in range(self.map["width"]):
            for y in range(self.map["height"]):
                if (x, y) not in self.map["tiles"]:
                    return x, y
        return None

    def _generate_map(self):
        # Initialize empty map with plains tiles
        for x in range(self.map["width"]):
            for y in range(self.map["height"]):
                self.map["tiles"][(x, y)] = {
                    "type": "plains",
                    "name": f"Plains {x},{y}",
                    "symbol": ".",
                    "color": Fore.GREEN
                }

        # Place features
        features = [
            ("city", 2, "C", Fore.YELLOW),
            ("town", 3, "T", Fore.YELLOW),
            ("dungeon", 2, "D", Fore.MAGENTA),
            ("castle", 1, "K", Fore.MAGENTA),
            ("mountain", 10, "^", Fore.WHITE),
            ("river", 8, "~", Fore.BLUE),
            ("lake", 5, "L", Fore.CYAN),
            ("forest", 15, "F", Fore.GREEN)
        ]
        for feature, count, symbol, color in features:
            for _ in range(count):
                pos = self._find_empty_spot()
                if pos:
                    x, y = pos
                    self.map["tiles"][(x, y)] = {
                        "type": feature,
                        "name": f"{feature.capitalize()} {x},{y}",
                        "symbol": symbol,
                        "color": color
                    }
                if feature == "river":
                    # Extend river
                    for i in range(1, 3):
                        if pos and random.random() < 0.8:
                            new_x = x + random.choice([-1, 0, 1])
                            new_y = y + i
                            if 0 <= new_x < self.map["width"] and 0 <= new_y < self.map["height"] and (new_x, new_y) not in self.map["tiles"]:
                                self.map["tiles"][(new_x, new_y)] = {
                                    "type": "river",
                                    "name": f"River {new_x},{new_y}",
                                    "symbol": "~",
                                    "color": Fore.BLUE
                                }
                elif feature == "lake":
                    # Expand lake
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if pos and random.random() < 0.3:
                                new_x, new_y = x + dx, y + dy
                                if 0 <= new_x < self.map["width"] and 0 <= new_y < self.map["height"] and (new_x, new_y) not in self.map["tiles"]:
                                    self.map["tiles"][(new_x, new_y)] = {
                                        "type": "lake",
                                        "name": f"Lake {new_x},{new_y}",
                                        "symbol": "L",
                                        "color": Fore.CYAN
                                    }
                elif feature == "forest":
                    # Expand forest
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if pos and random.random() < 0.4:
                                new_x, new_y = x + dx, y + dy
                                if 0 <= new_x < self.map["width"] and 0 <= new_y < self.map["height"] and (new_x, new_y) not in self.map["tiles"]:
                                    self.map["tiles"][(new_x, new_y)] = {
                                        "type": "forest",
                                        "name": f"Forest {new_x},{new_y}",
                                        "symbol": "F",
                                        "color": Fore.GREEN
                                    }

        # Add roads
        cities_towns = [(x, y) for (x, y), tile in self.map["tiles"].items() if tile["type"] in ["city", "town"]]
        for i, (x1, y1) in enumerate(cities_towns):
            for x2, y2 in cities_towns[i+1:]:
                if random.random() < 0.7:
                    # Simple road path (horizontal then vertical)
                    for x in range(min(x1, x2), max(x1, x2) + 1):
                        if (x, y1) not in self.map["tiles"] or self.map["tiles"][(x, y1)]["type"] == "plains":
                            self.map["tiles"][(x, y1)] = {
                                "type": "road",
                                "name": f"Road {x},{y1}",
                                "symbol": "-",
                                "color": Fore.BLACK
                            }
                    for y in range(min(y1, y2), max(y1, y2) + 1):
                        if (x2, y) not in self.map["tiles"] or self.map["tiles"][(x2, y)]["type"] == "plains":
                            self.map["tiles"][(x2, y)] = {
                                "type": "road",
                                "name": f"Road {x2},{y}",
                                "symbol": "|",
                                "color": Fore.BLACK
                            }

    def get_location(self, x: int, y: int) -> Dict:
        return self.map["tiles"].get((x, y), {"type": "plains", "name": f"Plains {x},{y}", "symbol": ".", "color": Fore.GREEN})

    def display_map(self, player_pos: Tuple[int, int], radius: int = 7) -> str:
        output = []
        px, py = player_pos
        for y in range(max(0, py - radius), min(self.map["height"], py + radius + 1)):
            row = []
            for x in range(max(0, px - radius), min(self.map["width"], px + radius + 1)):
                if (x, y) == player_pos:
                    row.append(f"{Fore.RED}P{Style.RESET_ALL}")
                else:
                    tile = self.get_location(x, y)
                    row.append(f"{tile['color']}{tile['symbol']}{Style.RESET_ALL}")
            output.append(" ".join(row))
        return "\n".join(output)

class GameWorld:
    def __init__(self, world: World):
        self.world = world
        self.rooms = self._generate_rooms()

    def _generate_rooms(self) -> Dict[str, Room]:
        rooms = {}
        for (x, y), tile in self.world.map["tiles"].items():
            if tile["type"] in ["dungeon", "castle"]:
                room_id = f"{x},{y}"
                description = f"A {tile['type']} room with {random.choice(['stone walls', 'ancient runes', 'flickering torches'])}."
                exits = {}
                for direction, (dx, dy) in [("north", (0, -1)), ("south", (0, 1)), ("east", (1, 0)), ("west", (-1, 0))]:
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < self.world.map["width"] and 0 <= new_y < self.world.map["height"]:
                        new_tile = self.world.get_location(new_x, new_y)
                        if new_tile["type"] in ["dungeon", "castle"]:
                            exits[direction] = f"{new_x},{new_y}"
                monsters = [Monster(f"Goblin {i+1}", 6, [{"attack_bonus": 3, "damage": "1d4+1"}]) for i in range(random.randint(0, 2))] if tile["type"] == "dungeon" else []
                items = [random.choice(["Potion", "Scroll", "Gem"])] if random.random() < 0.3 else []
                rooms[room_id] = Room(description, exits, monsters, items)
        return rooms