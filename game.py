import sys
import random
from typing import Optional
import logging

from .character import Character
from .dnd35e.core.world import GameWorld
from .dnd35e.mechanics.combat import CombatSystem
from .dnd35e.core.quest_manager import QuestManager
from .dnd35e.core.save_manager import SaveManager

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed output
logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        """Initialize the game world and player character"""
        logger.info("Initializing Game")
        logger.debug(f"Using Character class from: {Character.__module__}")
        self.world = GameWorld.generate()
        try:
            self.player, self.starting_room = SaveManager.load_player(
                self.world,
                self.create_player
            )
            # Patch old save data if needed
            if not hasattr(self.player, "race"):
                logger.warning("Old save data detected; assigning default race")
                self.player.race = self.world.default_race
                self.player.hit_points = self.player.calculate_hit_points()
        except TypeError as e:
            logger.error(f"Error loading player: {e}. Creating new player.")
            self.player = self.create_player()
            self.starting_room = self.world.get_room(0)  # Default to first room
        except Exception as e:
            logger.error(f"Failed to load player: {e}. Creating new player.")
            self.player = self.create_player()
            self.starting_room = self.world.get_room(0)
        self.player.location = self.starting_room
        self.quest_log = QuestManager(self.player)
        self.quest_log.load()
        self.combat_mode = False

    def create_player(self, name: str = "Hero") -> Character:
        """
        Create a new player character with default race and class

        Args:
            name: The character's name (default "Hero")

        Returns:
            Character: The newly created player character
        """
        logger.debug(f"Creating player with: name={name}, race={self.world.default_race}, type={type(self.world.default_race)}, dnd_class={self.world.default_class}, type={type(self.world.default_class)}")
        try:
            return Character(
                name=name,
                race=self.world.default_race,
                dnd_class=self.world.default_class,
                level=1
            )
        except TypeError as e:
            logger.error(f"Failed to create player: {e}")
            raise

    def start(self):
        """Begin the game and print starting information"""
        logger.info("\n=== Dungeon Adventure ===")
        logger.info("Commands: north/south/east/west, look, attack [#], quest [list/start/complete/log], save, quit")
        self.print_location()

    def print_location(self):
        """Display current room information including exits and monsters"""
        room = self.player.location
        logger.info(f"\n{room['name']}")
        logger.info(room['description'])

        if room['exits']:
            logger.info("\nExits: %s", ", ".join(room['exits'].keys()))

        alive_monsters = [m for m in room['monsters'] if m.hit_points > 0]
        if alive_monsters:
            logger.info("\nMonsters here:")
            for i, monster in enumerate(alive_monsters, 1):
                logger.info(f"{i}. {monster.name} (HP: {monster.hit_points})")
            self.combat_mode = True
        else:
            logger.info("\nThere are no living monsters here.")
            self.combat_mode = False

        # Check for quest objectives in this location
        self.check_quest_objectives(room)

    def check_quest_objectives(self, room: dict):
        """Check if current location completes any quest objectives"""
        room_name = room["name"].lower()
        for quest in self.quest_log.active_quests:
            for objective in quest.objectives:
                if any(word in objective.lower() for word in room_name.split()):
                    self.quest_log.complete_objective(quest.name, objective)

    def handle_command(self, command: str):
        """Process player input commands"""
        command = command.lower().strip()

        if self.combat_mode and command.isdigit():
            self.handle_attack(int(command))
        elif command in ["north", "south", "east", "west"]:
            self.handle_movement(command)
        elif command == "look":
            self.print_location()
        elif command.startswith("attack"):
            self.handle_attack_command(command)
        elif command.startswith("quest"):
            self.handle_quest_command(command)
        elif command == "save":
            self.save_session()
        elif command in ["quit", "exit"]:
            self.quit_game()
        else:
            self.display_help()

    def display_help(self):
        """Show available commands"""
        logger.info("Available commands:")
        logger.info("- Movement: north/south/east/west")
        logger.info("- Combat: attack [number]")
        logger.info("- Quests: quest [list/start/complete/log]")
        logger.info("- Other: look, save, quit")

    def handle_movement(self, direction: str):
        """Handle player movement between rooms"""
        if self.combat_mode:
            logger.info("You can't move while monsters are attacking!")
            return

        current_room = self.player.location
        if direction in current_room['exits']:
            next_id = current_room['exits'][direction]
            next_room = self.world.get_room(next_id)
            if next_room:
                self.player.location = next_room
                logger.info(f"You move {direction}.")
                self.print_location()
                return

        logger.info(f"You can't go {direction}.")

    def handle_attack_command(self, command: str):
        """Process attack commands"""
        if not self.combat_mode:
            logger.info("There's nothing to attack here.")
            return

        try:
            target = int(command.split()[1]) if len(command.split()) > 1 else 1
            self.handle_attack(target)
        except (ValueError, IndexError):
            logger.info("Specify which monster to attack. Example: 'attack 1'")

    def handle_attack(self, target_index: int):
        """Execute combat round against specified target"""
        room = self.player.location
        alive_monsters = [m for m in room['monsters'] if m.hit_points > 0]

        try:
            target = alive_monsters[target_index - 1]
        except IndexError:
            logger.info(f"Invalid target number. Only {len(alive_monsters)} monster(s) here.")
            return

        logger.info(f"\nYou engage the {target.name} in combat!")

        # Combat sequence
        self.execute_combat_round(target)

    def execute_combat_round(self, target):
        """Run a full combat round between player and target"""
        turn_order = CombatSystem.determine_initiative([self.player, target])

        for combatant in turn_order:
            if combatant.hit_points <= 0:
                continue

            if combatant == self.player:
                result = CombatSystem.resolve_attack(self.player, target)
            else:
                result = CombatSystem.resolve_attack(target, self.player)

            self.display_combat_result(result)

            # Check for combat conclusion
            if self.check_combat_end(target):
                break

    def check_combat_end(self, target) -> bool:
        """Determine if combat should end and handle results"""
        if self.player.hit_points <= 0:
            logger.info("\nYou have fallen in battle...")
            self.quit_game()
            return True
        elif target.hit_points <= 0:
            self.handle_victory(target)
            return True
        return False

    def handle_victory(self, target):
        """Process victory over a defeated monster"""
        logger.info(f"\nYou defeated the {target.name}!")
        xp_gain = int(target.challenge_rating * 100)
        self.player.gain_xp(xp_gain)

        # Check for quest completion
        for quest in self.quest_log.active_quests:
            for objective in quest.objectives:
                if target.name.lower() in objective.lower():
                    self.quest_log.complete_objective(quest.name, objective)

        self.combat_mode = False

    def display_combat_result(self, result: dict):
        """Show results of a combat action"""
        logger.info(f"\n{result['attacker']} attacks {result['defender']}!")
        logger.info(f"Roll: {result['attack_roll']} + {result['attack_bonus']} vs AC")
        if result['hit']:
            logger.info(f"HIT{' (CRITICAL!)' if result['critical'] else ''} for {result['damage']} damage!")
            logger.info(f"{result['defender']} suffers damage.")
            if result['special_effects']:
                logger.info(f"Special effect(s): {', '.join(result['special_effects'])}")
        else:
            logger.info("MISS!")

    def handle_quest_command(self, command: str):
        """Process quest-related commands"""
        parts = command.split()
        if len(parts) == 1 or parts[1] == "list":
            self.quest_log.list_quests()
        elif parts[1] == "log":
            self.quest_log.display_hud()
        elif parts[1] == "start":
            self.handle_quest_start(parts)
        elif parts[1] == "complete":
            self.handle_quest_completion()
        else:
            logger.info("Quest command options: list | log | start <category> <subcategory> <id> | complete")

    def handle_quest_start(self, parts: list):
        """Process quest start command"""
        try:
            _, _, category, subcategory, quest_id = parts
            self.quest_log.assign_quest(category, subcategory, quest_id)
        except ValueError:
            logger.info("Usage: quest start <category> <subcategory> <quest_id>")

    def handle_quest_completion(self):
        """Process quest completion command"""
        try:
            quest_name = input("Enter quest name: ")
            objective = input("Enter completed objective: ")
            self.quest_log.complete_objective(quest_name, objective)
        except Exception as e:
            logger.error(f"Error completing objective: {e}")

    def save_session(self):
        """Save game state"""
        SaveManager.save_player(self.player, self.player.location["id"])
        self.quest_log.save()
        logger.info("\U0001F4BE Game saved.")

    def quit_game(self):
        """Cleanly exit the game"""
        logger.info("\nSaving progress...")
        self.save_session()
        logger.info("Thanks for playing!")
        sys.exit()

def main():
    """Entry point for the game"""
    try:
        game = Game()
        game.start()
        while True:
            try:
                command = input("\nWhat would you like to do? ").strip()
                game.handle_command(command)
            except KeyboardInterrupt:
                game.quit_game()
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    except Exception as e:
        logger.error(f"Fatal error starting game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()