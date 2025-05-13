import sys
import logging
from typing import Optional

from dnd_adventure.character import Character
from dnd_adventure.dnd35e.core.world import GameWorld
from dnd_adventure.dnd35e.mechanics.combat import CombatSystem
from dnd_adventure.dnd35e.core.quest_manager import QuestManager
from dnd_adventure.dnd35e.core.save_manager import SaveManager

# Custom logging setup
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('game.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
stream_handler.setFormatter(logging.Formatter('%(message)s'))

logger.handlers = []
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        try:
            self.world = GameWorld.generate()
            if not self.world or not self.world.rooms:
                raise ValueError("World generation failed - no rooms created")

            self.player_name = input("Enter your character's name (new or existing): ").strip()
            self.player, self.starting_room = self.initialize_player()
            if not self.starting_room:
                self.starting_room = self.world.get_room(0)

            self.player.location = self.starting_room
            self.quest_log = QuestManager(self.player)
            self.quest_log.load()
            self.combat_mode = False

        except Exception as e:
            logger.critical(f"Game initialization failed: {e}")
            self.emergency_shutdown()

    def initialize_player(self) -> tuple[Character, Optional[object]]:
        try:
            player, room = SaveManager.load_player(self.world, self.player_name, self.create_player)
            if not hasattr(player, "race"):
                player.race = self.world.default_race
                player.hit_points = player.calculate_hit_points()
            return player, room or self.world.get_room(0)
        except Exception as e:
            logger.error(f"Player initialization failed: {e}")
            player = self.create_player(self.player_name)
            return player, self.world.get_room(0)

    def create_player(self, name: str) -> Character:
        try:
            print("\nChoose your race:")
            for i, race in enumerate(self.world.available_races, 1):
                print(f"{i}. {race.name}")
            race_index = input("Enter number of your race choice: ").strip()
            try:
                race_index = int(race_index) - 1
                race = self.world.available_races[race_index]
            except (ValueError, IndexError):
                print("Invalid choice. Using default race.")
                race = self.world.default_race

            print("\nChoose your class:")
            for i, cls in enumerate(self.world.available_classes, 1):
                print(f"{i}. {cls.name}")
            class_index = input("Enter number of your class choice: ").strip()
            try:
                class_index = int(class_index) - 1
                dnd_class = self.world.available_classes[class_index]
            except (ValueError, IndexError):
                print("Invalid choice. Using default class.")
                dnd_class = self.world.default_class

            return Character(
                name=name,
                race=race,
                dnd_class=dnd_class,
                level=1
            )
        except Exception as e:
            logger.critical(f"Failed to create player: {e}")
            raise RuntimeError("Could not create player character")

    def start(self):
        print("\n=== Dungeon Adventure ===")
        print("Commands: north/south/east/west, look, attack [#], quest [list/start/complete/log], save, quit")
        self.print_location()

    def print_location(self):
        room = getattr(self.player, 'location', self.starting_room)
        self.player.location = room

        print(f"\n{getattr(room, 'name', 'Unknown Location')}")
        print(getattr(room, 'description', 'You see nothing unusual.'))

        exits = getattr(room, 'exits', {})
        if exits:
            print("\nExits: " + ", ".join(exits.keys()))

        alive_monsters = [m for m in getattr(room, 'monsters', []) if getattr(m, 'hit_points', 0) > 0]

        if alive_monsters:
            print("\nMonsters here:")
            for i, monster in enumerate(alive_monsters, 1):
                print(f"{i}. {getattr(monster, 'name', 'Unknown')} (HP: {getattr(monster, 'hit_points', '?')})")
            self.combat_mode = True
        else:
            print("\nNo active threats here.")
            self.combat_mode = False

        self.check_quest_objectives(room)

    def check_quest_objectives(self, room):
        for quest in self.quest_log.active_quests:
            for objective in quest.objectives:
                if any(word in objective.lower() for word in room.name.lower().split()):
                    self.quest_log.complete_objective(quest.name, objective)

    def handle_movement(self, direction: str):
        if self.combat_mode:
            print("You can't flee from combat!")
            return

        current_room = self.player.location
        exits = getattr(current_room, 'exits', {})

        if direction not in exits:
            print(f"No exit to the {direction}.")
            return

        next_room = self.world.get_room(exits[direction])
        if not next_room:
            logger.error(f"Room {exits[direction]} doesn't exist!")
            return

        self.player.location = next_room
        print(f"You move {direction}.")
        self.print_location()

    def save_session(self):
        try:
            SaveManager.save_player(self.player, getattr(self.player.location, 'id', 0))
            self.quest_log.save()
            print("Game saved successfully.")
        except Exception as e:
            logger.error(f"Save failed: {e}")

    def emergency_shutdown(self):
        print("A critical error occurred. The game will shut down.")
        sys.exit(1)

    def handle_command(self, command: str):
        command = command.lower().strip()
        if command in ["north", "south", "east", "west"]:
            self.handle_movement(command)
        elif command == "look":
            self.print_location()
        elif command == "save":
            self.save_session()
        elif command in ["quit", "exit"]:
            self.quit_game()
        else:
            print("Unknown command. Try: north, look, save, quit")

    def quit_game(self):
        print("Thanks for playing!")
        self.save_session()
        sys.exit()

def main():
    try:
        game = Game()
        game.start()
        while True:
            try:
                command = input("\nWhat would you like to do? ").strip()
                game.handle_command(command)
            except KeyboardInterrupt:
                print("\nGame interrupted by user")
                game.quit_game()
            except Exception as e:
                logger.error(f"Command error: {e}")
                print("Type 'help' for available commands")
    except Exception as e:
        logger.critical(f"Fatal game error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()