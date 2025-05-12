from dataclasses import dataclass
from .world import GameWorld  # Updated to relative import

# Consolidated PlayerCharacter class
class PlayerCharacter:
    def __init__(self, name, health=100, attack_power=10):
        self.name = name
        self.health = health
        self.attack_power = attack_power

    def attack(self, target):
        """Simple attack method (placeholder)"""
        return f"{self.name} attacks {target} with power {self.attack_power}!"

    def serialize(self):
        """Serialize player data"""
        return {
            "name": self.name,
            "health": self.health,
            "attack_power": self.attack_power,
        }

    @classmethod
    def deserialize(cls, data):
        """Deserialize player data"""
        return cls(name=data["name"], health=data["health"], attack_power=data["attack_power"])

# Creating the character using the new create_character method
def create_character(data):
    """Factory function to create a player character"""
    return PlayerCharacter(
        name=data.get("name", "Hero"),
        health=data.get("health", 100),
        attack_power=data.get("attack_power", 10)
    )

@dataclass
class GameSession:
    """Main game controller with 3.5e integration"""
    player: PlayerCharacter
    world: GameWorld
    turn: int = 0

    @classmethod
    def new_campaign(cls, character_data: dict):
        """Create a new game with a 3.5e character"""
        # Create a new player character and world
        player = create_character(character_data)
        world = GameWorld.generate()
        return cls(player=player, world=world)

    def save(self, filepath: str):
        """Save game state with versioning"""
        import pickle
        data = {
            'version': '1.0',
            'character': self.player.serialize(),
            'world': self.world.serialize(),
            'turn': self.turn
        }
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            print(f"Game saved to {filepath}")
        except Exception as e:
            print(f"Error saving game: {e}")

    def load(self, filepath: str):
        """Load a previously saved game"""
        import pickle
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.player = PlayerCharacter.deserialize(data['character'])
                self.world = GameWorld.deserialize(data['world'])
                self.turn = data['turn']
            print(f"Game loaded from {filepath}")
        except FileNotFoundError:
            print(f"No saved game found at {filepath}")
        except Exception as e:
            print(f"Error loading game: {e}")

    def take_turn(self):
        """Handle game logic for each turn"""
        self.turn += 1
        print(f"Turn {self.turn} for {self.player.name}")
