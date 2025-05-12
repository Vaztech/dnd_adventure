# game.py

# Import only when needed to avoid circular import issues
from .world import GameWorld  # Correct import for world-building
from .commands import CommandParser  # Corrected import

class Game:
    """Game class to encapsulate the main game logic"""
    def __init__(self):
        # Generate the world with locations and monsters
        self.world = GameWorld.generate()
        self.command_processor = CommandParser(self.world)  # CommandParser now takes the world as a parameter

    def start(self):
        """Start the game and handle the main game loop"""
        # Import PlayerCharacter inside the method to avoid circular import
        from .character import PlayerCharacter

        # Create an example player
        player = PlayerCharacter("Hero", 100, 10)  # Example player with name, health, and attack power
        
        # Set up the player's starting location in the world
        self.world.player_location = self.world.rooms.get('entrance', None)  # Assuming 'entrance' is a room in your world

        if self.world.player_location:
            print("Welcome to the D&D Adventure!")
            print(f"Your adventure begins in the {self.world.player_location.name}.")
        else:
            print("Error: Starting location 'entrance' not found!")
            return

        while True:
            # Prompt the player for a command
            command = input("What do you want to do? (Type 'quit' to exit) ").strip().lower()

            if command == "quit":
                print("Goodbye!")
                break
            else:
                # Execute the command using the command processor
                result = self.command_processor.execute(command)
                print(result if result else "Command not recognized.")

def main():
    # Instantiate the game and start it
    game = Game()
    game.start()  # Start the game loop
