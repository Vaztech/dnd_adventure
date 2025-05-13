import sys
import logging

from dnd_adventure.character import Character
from dnd_adventure.dnd35e.core.world import GameWorld
from dnd_adventure.dnd35e.mechanics.combat import CombatSystem
from dnd_adventure.dnd35e.core.quest_manager import QuestManager
from dnd_adventure.dnd35e.core.save_manager import SaveManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        logger.info("Initializing Game")
        self.world = GameWorld.generate()

        try:
            self.player, self.starting_room = SaveManager.load_player(
                self.world, self.create_player
            )
            if not hasattr(self.player, "race"):
                self.player.race = self.world.default_race
                self.player.hit_points = self.player.calculate_hit_points()
        except Exception as e:
            logger.error(f"Failed to load player: {e}")
            self.player = self.create_player()
            self.starting_room = self.world.get_room(0)

        self.player.location = self.starting_room
        self.quest_log = QuestManager(self.player)
        self.quest_log.load()
        self.combat_mode = False

    def create_player(self, name: str = "Hero") -> Character:
        return Character(
            name=name,
            race=self.world.default_race,
            dnd_class=self.world.default_class,
            level=1
        )

    def start(self):
        logger.info("\n=== Dungeon Adventure ===")
        logger.info("Commands: north/south/east/west, look, attack [#], quest [list/start/complete/log], save, quit")
        self.print_location()

    def print_location(self):
        room = self.player.location
        logger.info(f"\n{room.name}")
        logger.info(room.description)

        if room.exits:
            logger.info("\nExits: %s", ", ".join(room.exits.keys()))

        alive_monsters = [m for m in room.monsters if m.hit_points > 0]
        if alive_monsters:
            logger.info("\nMonsters here:")
            for i, monster in enumerate(alive_monsters, 1):
                logger.info(f"{i}. {monster.name} (HP: {monster.hit_points})")
            self.combat_mode = True
        else:
            logger.info("\nThere are no living monsters here.")
            self.combat_mode = False

        self.check_quest_objectives(room)

    def check_quest_objectives(self, room):
        for quest in self.quest_log.active_quests:
            for objective in quest.objectives:
                if any(word in objective.lower() for word in room.name.lower().split()):
                    self.quest_log.complete_objective(quest.name, objective)

    def handle_command(self, command: str):
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
        logger.info("Available commands:")
        logger.info("- Movement: north/south/east/west")
        logger.info("- Combat: attack [number]")
        logger.info("- Quests: quest [list/start/complete/log]")
        logger.info("- Other: look, save, quit")

    def handle_movement(self, direction: str):
        if self.combat_mode:
            logger.info("You can't move while monsters are attacking!")
            return

        current_room = self.player.location
        if direction in current_room.exits:
            next_id = current_room.exits[direction]
            next_room = self.world.get_room(next_id)
            if next_room:
                self.player.location = next_room
                logger.info(f"You move {direction}.")
                self.print_location()
                return

        logger.info(f"You can't go {direction}.")

    def handle_attack_command(self, command: str):
        if not self.combat_mode:
            logger.info("There's nothing to attack here.")
            return

        try:
            target = int(command.split()[1]) if len(command.split()) > 1 else 1
            self.handle_attack(target)
        except (ValueError, IndexError):
            logger.info("Specify which monster to attack. Example: 'attack 1'")

    def handle_attack(self, target_index: int):
        room = self.player.location
        alive_monsters = [m for m in room.monsters if m.hit_points > 0]

        try:
            target = alive_monsters[target_index - 1]
        except IndexError:
            logger.info(f"Invalid target number. Only {len(alive_monsters)} monster(s) here.")
            return

        logger.info(f"\nYou engage the {target.name} in combat!")
        self.execute_combat_round(target)

    def execute_combat_round(self, target):
        turn_order = CombatSystem.determine_initiative([self.player, target])

        for combatant in turn_order:
            if combatant.hit_points <= 0:
                continue

            if combatant == self.player:
                result = CombatSystem.resolve_attack(self.player, target)
            else:
                result = CombatSystem.resolve_attack(target, self.player)

            self.display_combat_result(result)

            if self.check_combat_end(target):
                break

    def check_combat_end(self, target) -> bool:
        if self.player.hit_points <= 0:
            logger.info("\nYou have fallen in battle...")
            self.quit_game()
            return True
        elif target.hit_points <= 0:
            self.handle_victory(target)
            return True
        return False

    def handle_victory(self, target):
        logger.info(f"\nYou defeated the {target.name}!")
        xp_gain = int(target.challenge_rating * 100)
        self.player.gain_xp(xp_gain)

        for quest in self.quest_log.active_quests:
            for objective in quest.objectives:
                if target.name.lower() in objective.lower():
                    self.quest_log.complete_objective(quest.name, objective)

        self.combat_mode = False

    def display_combat_result(self, result: dict):
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
        try:
            _, _, category, subcategory, quest_id = parts
            self.quest_log.assign_quest(category, subcategory, quest_id)
        except ValueError:
            logger.info("Usage: quest start <category> <subcategory> <quest_id>")

    def handle_quest_completion(self):
        try:
            quest_name = input("Enter quest name: ")
            objective = input("Enter completed objective: ")
            self.quest_log.complete_objective(quest_name, objective)
        except Exception as e:
            logger.error(f"Error completing objective: {e}")

    def save_session(self):
        SaveManager.save_player(self.player, self.player.location.id)
        self.quest_log.save()
        logger.info("\U0001F4BE Game saved.")

    def quit_game(self):
        logger.info("\nSaving progress...")
        self.save_session()
        logger.info("Thanks for playing!")
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
                game.quit_game()
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    except Exception as e:
        logger.error(f"Fatal error starting game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()