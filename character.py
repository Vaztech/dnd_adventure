from dataclasses import dataclass
from dnd_adventure.dnd35e.core.character import CharacterSheet
from dnd_adventure.world import GameWorld

# Ensure Player class is defined
class Player:
    def __init__(self, name):
        self.name = name
        # Add other attributes as needed for your game

@dataclass
class GameSession:
    """Main game controller with 3.5e integration"""
    player: CharacterSheet
    world: GameWorld
    turn: int = 0

    @classmethod
    def new_campaign(cls, character_data: dict):
        """Create new game with 3.5e character"""
        # Import GameSession inside the method to avoid circular imports
        from dnd_adventure.game import GameSession
        # Import create_character inside method to avoid circular imports
        from dnd_adventure.dnd35e.core.character import create_character
        # Create a new character and a new world for the campaign
        return cls(
            player=create_character(character_data),
            world=GameWorld.generate()
        )
    
    def save(self, filepath: str):
        """Save game state with versioning"""
        import pickle
        data = {
            'version': __version__,
            'character': self.player.serialize(),  # Save the character data
            'world': self.world.serialize(),        # Save the world state
            'turn': self.turn                       # Save the turn counter
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"Game saved to {filepath}")
    
    def load(self, filepath: str):
        """Load a previously saved game"""
        import pickle
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.player = CharacterSheet.deserialize(data['character'])
                self.world = GameWorld.deserialize(data['world'])
                self.turn = data['turn']
            print(f"Game loaded from {filepath}")
        except FileNotFoundError:
            print(f"No saved game found at {filepath}")
        except Exception as e:
            print(f"Error loading game: {e}")

    def take_turn(self):
        """Handle game logic for each turn"""
        # Example placeholder for turn-based logic
        self.turn += 1
        print(f"Turn {self.turn} for {self.player.name}")
        # Handle actions, combat, events, etc. for the player here
