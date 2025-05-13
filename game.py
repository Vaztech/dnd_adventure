import sys
import logging
import argparse
from typing import Optional

from dnd_adventure.character import Character
from dnd_adventure.dnd35e.core.world import GameWorld
from dnd_adventure.dnd35e.mechanics.combat import CombatSystem
from dnd_adventure.dnd35e.core.quest_manager import QuestManager
from dnd_adventure.dnd35e.core.save_manager import SaveManager

# Custom logging setup
def setup_logging(debug=False):
    """Configure logging with console and file handlers."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File handler: Log DEBUG and above to game.log
    file_handler = logging.FileHandler('game.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))

    # Console handler: Log INFO (or DEBUG if --debug) and above
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    stream_handler.setFormatter(logging.Formatter('%(message)s'))

    # Clear existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logging.getLogger(__name__)

class Game:
    def __init__(self):
        logger.info("Initializing Game")
        try:
            self.world = GameWorld.generate()
            if not self.world or not self.world.rooms:
                raise ValueError("World generation failed - no rooms created")

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
            player, room = SaveManager.load_player(self.world, self.create_player)
            if not hasattr(player, "race"):
                logger.warning("Patching legacy player data")
                player.race = self.world.default_race
                player.hit_points = player.calculate_hit_points()
            return player, room or self.world.get_room(0)
        except Exception as e:
            logger.error(f"Player initialization failed: {e}")
            player = self.create_player()
            return player, self.world.get_room(0)

    def create_player(self, name: str = "Hero") -> Character:
        try:
            return Character(
                name=name,
                race=self.world.default_race,
                dnd_class=self.world.default_class,
                level=1
            )
        except Exception as e:
            logger.critical(f"Failed to create player: {e}")
            raise RuntimeError("Could not create player character")

    def start(self):
        if not hasattr(self, 'player') or not self.player:
            logger.critical("No player character exists")
            self.emergency_shutdown()
        logger.info("\n=== Dungeon Adventure ===")
        logger.info("Commands: north/south/east/west, look, attack [#], quest [list/start/complete/log], save, quit")
        self.print_location()

    def print_location(self):
        if not hasattr(self.player, 'location'):
            logger.error("Player has no location attribute!")
            self.player.location = self.starting_room

        room = self.player.location
        if not room:
            logger.error("Current room is None! Resetting to start.")
            self.player.location = self.starting_room
            room = self.starting_room

        logger.info(f"\n{getattr(room, 'name', 'Unknown Location')}")
        logger.info(getattr(room, 'description', 'You see nothing unusual.'))

        exits = getattr(room, 'exits', {})
        if exits:
            logger.info("\nExits: %s", ", ".join(exits.keys()))

        alive_monsters = []
        if hasattr(room, 'monsters'):
            alive_monsters = [m for m in room.monsters if hasattr(m, 'hit_points') and m.hit_points > 0]

        if alive_monsters:
            logger.info("\nMonsters here:")
            for i, monster in enumerate(alive_monsters, 1):
                logger.info(f"{i}. {getattr(monster, 'name', 'Unknown')} (HP: {getattr(monster, 'hit_points', '?')})")
            self.combat_mode = True
        else:
            logger.info("\nNo active threats here.")
            self.combat_mode = False

        self.check_quest_objectives(room)

    def check_quest_objectives(self, room):
        for quest in self.quest_log.active_quests:
            for objective in quest.objectives:
                if any(word in objective.lower() for word in room.name.lower().split()):
                    self.quest_log.complete_objective(quest.name, objective)

    def handle_movement(self, direction: str):
        if not hasattr(self.player, 'location'):
            logger.error("Player location missing!")
            return
        if self.combat_mode:
            logger.info("You can't flee from combat!")
            return

        current_room = self.player.location
        exits = getattr(current_room, 'exits', {})

        if direction not in exits:
            logger.info(f"No exit to the {direction}.")
            return

        next_room = self.world.get_room(exits[direction])
        if not next_room:
            logger.error(f"Room {exits[direction]} doesn't exist!")
            return

        self.player.location = next_room
        logger.info(f"You move {direction}.")
        self.print_location()

    def save_session(self):
        try:
            if not hasattr(self.player, 'location'):
                logger.error("Cannot save - player has no location")
                return
            SaveManager.save_player(
                self.player,
                getattr(self.player.location, 'id', 0)
            )
            self.quest_log.save()
            logger.info("Game saved successfully.")
        except Exception as e:
            logger.error(f"Save failed: {e}")

    def emergency_shutdown(self):
        logger.critical("EMERGENCY SHUTDOWN INITIATED")
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
            logger.info("Unknown command. Try: north, look, save, quit")

    def quit_game(self):
        logger.info("Thanks for playing!")
        self.save_session()
        sys.exit()

def main():
    parser = argparse.ArgumentParser(description="D&D 3.5e Text Adventure")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging in console")
    args = parser.parse_args()

    global logger
    logger = setup_logging(debug=args.debug)

    try:
        game = Game()
        game.start()
        while True:
            try:
                command = input("\nWhat would you like to do? ").strip()
                game.handle_command(command)
            except KeyboardInterrupt:
                logger.info("\nGame interrupted by user")
                game.quit_game()
            except Exception as e:
                logger.error(f"Command error: {e}")
                logger.info("Type 'help' for available commands")
    except Exception as e:
        logger.critical(f"Fatal game error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()