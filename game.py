# game.py

# Import only when needed to avoid circular import issues
from .world import GameWorld  # Correct import for world-building
from .commands import CommandParser  # Corrected import

def main():
    # Import Player inside the main function to avoid circular import
    from .character import Player

    player = Player("Hero", 100, 10)  # Example player
    world = GameWorld()  # GameWorld instance for world-building
    command_processor = CommandParser(world)  # CommandParser now takes the world as a parameter

    print("Welcome to the D&D Adventure!")
    while True:
        command = input("What do you want to do? ")
        if command.lower() == "quit":
            print("Goodbye!")
            break
        else:
            print(command_processor.execute(command))  # Execute the command
            # Example: command_processor.execute("explore") or any other command
            # You can add more game logic here, like player actions, combat, etc.