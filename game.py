import os
import sys
from pathlib import Path
from .character import Character
from .world import GameWorld

class Game:
    def __init__(self):
        self.world = GameWorld.generate()
        self.player = Character("Hero", 20, 8, 4)
        # Ensure player always has a valid starting location
        self.player.location = self.world.current_room or self.get_safe_starting_location()
        
    def get_safe_starting_location(self):
        """Fallback if no room is set as current_room"""
        if self.world.rooms:
            return self.world.rooms[0]
        # Create emergency room if world is completely empty
        return {
            'id': 0,
            'name': "Void Chamber",
            'description': "You float in a featureless void.",
            'exits': {},
            'monsters': []
        }

    def start(self):
        print("\n=== Dungeon Adventure ===")
        print("Type commands like 'north', 'south', 'east', 'west', 'look', or 'quit'\n")
        self.print_location()

    def print_location(self):
        room = self.player.location
        print(f"\n{room['name']}")
        print(room['description'])
        
        if room['exits']:
            print("\nExits:", ", ".join(room['exits'].keys()))
        else:
            print("\nThere are no visible exits.")
            
        if room['monsters']:
            print("\nMonsters here:")
            for i, monster in enumerate(room['monsters'], 1):
                status = "alive" if monster.is_alive() else "defeated"
                print(f"{i}. {monster.name} (HP: {monster.hp}, Status: {status})")

    def handle_command(self, command):
        command = command.lower().strip()
        
        if command in ["north", "south", "east", "west"]:
            self.handle_movement(command)
        elif command == "look":
            self.print_location()
        elif command in ["quit", "exit"]:
            self.quit_game()
        elif command.startswith("attack"):
            self.handle_attack(command)
        else:
            print("Unknown command. Try 'north', 'south', 'east', 'west', 'look', 'attack X', or 'quit'.")

    def handle_movement(self, direction):
        current_room = self.player.location
        if direction in current_room['exits']:
            new_room_id = current_room['exits'][direction]
            new_room = self.world.get_room(new_room_id)
            if new_room:
                self.player.location = new_room
                print(f"You move {direction}.")
                self.print_location()
                return
        print(f"You can't go {direction}!")

    def handle_attack(self, command):
        if not self.player.location['monsters']:
            print("There's nothing to attack here!")
            return
            
        try:
            # Handle "attack 1" or just "attack" (target first monster)
            parts = command.split()
            target_idx = int(parts[1])-1 if len(parts) > 1 else 0
            monster = self.player.location['monsters'][target_idx]
            
            if not monster.is_alive():
                print(f"The {monster.name} is already defeated!")
                return
                
            damage = self.player.attack_target(monster)
            print(f"You attack the {monster.name} for {damage} damage!")
            
            if not monster.is_alive():
                print(f"You defeated the {monster.name}!")
            else:
                print(f"The {monster.name} has {monster.hp} HP remaining.")
                
        except (IndexError, ValueError):
            print("Invalid target. Try 'attack 1' to attack the first monster.")

    def quit_game(self):
        print("\nThanks for playing! Goodbye.")
        sys.exit()

def main():
    try:
        game = Game()
        game.start()
        
        while True:
            try:
                command = input("\nWhat would you like to do? ").lower().strip()
                game.handle_command(command)
            except KeyboardInterrupt:
                game.quit_game()
            except Exception as e:
                print(f"Error: {e}. Please try again.")
                
    except Exception as e:
        print(f"Fatal error starting game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()