import sys
import random
from typing import Optional

from .character import Character
from .dnd35e.core.world import GameWorld
from .dnd35e.mechanics.combat import CombatSystem
from .dnd35e.core.quest_manager import QuestManager
from .dnd35e.core.save_manager import SaveManager

class Game:
    def __init__(self):
        """Initialize the game world and player character"""
        self.world = GameWorld.generate()
        self.player, self.starting_room = SaveManager.load_player(
            self.world, 
            self.create_player
        )
        self.player.location = self.starting_room
        self.quest_log = QuestManager(self.player)
        self.quest_log.load()
        self.combat_mode = False

    def create_player(self, name: str = "Hero") -> Character:
        return Character(
            name=name,
            race_name=self.world.default_race.name,
            class_name=self.world.default_class.name,
            level=1
        )

    def start(self):
        print("\n=== Dungeon Adventure ===")
        print("Commands: north/south/east/west, look, attack [#], quest [list/start/complete/log], save, quit\n")
        self.print_location()

    def print_location(self):
        room = self.player.location
        print(f"\n{room['name']}")
        print(room['description'])

        if room['exits']:
            print("\nExits:", ", ".join(room['exits'].keys()))

        alive_monsters = [m for m in room['monsters'] if m.hit_points > 0]
        if alive_monsters:
            print("\nMonsters here:")
            for i, monster in enumerate(alive_monsters, 1):
                print(f"{i}. {monster.name} (HP: {monster.hit_points})")
            self.combat_mode = True
        else:
            print("\nThere are no living monsters here.")
            self.combat_mode = False

        self.check_quest_objectives(room)

    def check_quest_objectives(self, room: dict):
        room_name = room["name"].lower()
        for quest in self.quest_log.active_quests:
            for objective in quest.objectives:
                if any(word in objective.lower() for word in room_name.split()):
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
        print("Available commands:")
        print("- Movement: north/south/east/west")
        print("- Combat: attack [number]")
        print("- Quests: quest [list/start/complete/log]")
        print("- Other: look, save, quit")

    def handle_movement(self, direction: str):
        if self.combat_mode:
            print("You can't move while monsters are attacking!")
            return

        current_room = self.player.location
        if direction in current_room['exits']:
            next_id = current_room['exits'][direction]
            next_room = self.world.get_room(next_id)
            if next_room:
                self.player.location = next_room
                print(f"You move {direction}.")
                self.print_location()
                return

        print(f"You can't go {direction}.")

    def handle_attack_command(self, command: str):
        if not self.combat_mode:
            print("There's nothing to attack here.")
            return

        try:
            target = int(command.split()[1]) if len(command.split()) > 1 else 1
            self.handle_attack(target)
        except (ValueError, IndexError):
            print("Specify which monster to attack. Example: 'attack 1'")

    def handle_attack(self, target_index: int):
        alive_monsters = [m for m in self.player.location['monsters'] if m.hit_points > 0]

        try:
            target = alive_monsters[target_index - 1]
        except IndexError:
            print(f"Invalid target number. Only {len(alive_monsters)} monster(s) here.")
            return

        print(f"\nYou engage the {target.name} in combat!")
        self.execute_combat_round(target)

    def execute_combat_round(self, target):
        turn_order = CombatSystem.determine_initiative([self.player, target])

        for combatant in turn_order:
            if combatant.hit_points <= 0:
                continue

            result = CombatSystem.resolve_attack(combatant, target if combatant == self.player else self.player)
            self.display_combat_result(result)

            if self.check_combat_end(target, result):
                break

    def check_combat_end(self, target, result) -> bool:
        if self.player.hit_points <= 0:
            print("\nYou have fallen in battle...")
            self.quit_game()
            return True
        elif target.hit_points <= 0:
            self.handle_victory(target)
            return True
        return False

    def handle_victory(self, target):
        print(f"\nYou defeated the {target.name}!")
        xp_gain = int(target.challenge_rating * 100)
        self.player.gain_xp(xp_gain)

        for quest in self.quest_log.active_quests:
            for objective in quest.objectives:
                if target.name.lower() in objective.lower():
                    self.quest_log.complete_objective(quest.name, objective)

        self.combat_mode = False

    def display_combat_result(self, result: dict):
        print(f"\n{result['attacker']} attacks {result['defender']}!")
        print(f"Roll: {result['attack_roll']} + {result['attack_bonus']} vs AC")
        if result['hit']:
            print(f"HIT{' (CRITICAL!)' if result['critical'] else ''} for {result['damage']} damage!")
            print(f"{result['defender']} suffers damage.")
            if result['special_effects']:
                print(f"Special effect(s): {', '.join(result['special_effects'])}")
        else:
            print("MISS!")

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
            print("Quest command options: list | log | start <category> <subcategory> <id> | complete")

    def handle_quest_start(self, parts: list):
        try:
            _, _, category, subcategory, quest_id = parts
            self.quest_log.assign_quest(category, subcategory, quest_id)
        except ValueError:
            print("Usage: quest start <category> <subcategory> <quest_id>")

    def handle_quest_completion(self):
        try:
            quest_name = input("Enter quest name: ")
            objective = input("Enter completed objective: ")
            self.quest_log.complete_objective(quest_name, objective)
        except Exception as e:
            print(f"Error completing objective: {e}")

    def save_session(self):
        SaveManager.save_player(self.player, self.player.location["id"])
        self.quest_log.save()
        print("💾 Game saved.")

    def quit_game(self):
        print("\nSaving progress...")
        self.save_session()
        print("Thanks for playing!")
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
                print(f"Error: {e}")
    except Exception as e:
        print(f"Fatal error starting game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
