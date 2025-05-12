# game.py

# Change the relative import to absolute import
from character import Player
from world import World
from commands import CommandProcessor

def main():
    # Your game logic goes here, for example:
    player = Player("Hero", 100, 10)  # Sample player creation
    world = World()  # Create a world instance
    command_processor = CommandProcessor()  # Command processor for input

    # Example of running the game logic
    print("Welcome to the D&D Adventure!")
    while True:
        command = input("What do you want to do? ")
        if command.lower() == "quit":
            print("Goodbye!")
            break
        else:
            command_processor.process_command(command, player, world)

if __name__ == "__main__":
    main()
# This is a simple main function to run the game.
# You can expand this with more game logic, such as loading a world, managing turns, etc.