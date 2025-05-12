from typing import Optional
from adventurelib import *
from .character import Player
from .world import create_world
from .commands import *
from dnd35e.core import Race, CharacterClass
from dnd35e.data import load_races, load_classes
from dnd35e.mechanics.character import AbilityScores

class GameState:
    """Container for all game state"""
    def __init__(self):
        self.player: Optional[Player] = None
        self.world = None
        self.turn_count = 0

# Global game state
game_state = GameState()

def initialize_player() -> Player:
    """Create a new player character with 3.5e rules"""
    print("""
    ================================
    D&D 3.5e Text Adventure
    ================================
    """)
    
    # Load 3.5e content
    races = load_races()
    classes = load_classes()
    
    # Character creation
    name = input("What is your character's name? ").strip()
    
    print("\nAvailable Races:")
    for i, race in enumerate(races.values(), 1):
        print(f"{i}. {race.name}")
    race_choice = get_valid_input(
        prompt="Select race: ",
        options=range(1, len(races)+1)
    )
    selected_race: Race = list(races.values())[race_choice-1]
    
    print("\nAvailable Classes:")
    for i, cls in enumerate(classes.values(), 1):
        print(f"{i}. {cls.name} ({cls.hit_die})")
    class_choice = get_valid_input(
        prompt="Select class: ",
        options=range(1, len(classes)+1)
    )
    selected_class: CharacterClass = list(classes.values())[class_choice-1]
    
    # Generate ability scores using 3.5e rules
    print("\nGenerating ability scores...")
    ability_scores = AbilityScores.generate()
    print(f"Strength: {ability_scores.strength}")
    print(f"Dexterity: {ability_scores.dexterity}")
    print(f"Constitution: {ability_scores.constitution}")
    print(f"Intelligence: {ability_scores.intelligence}")
    print(f"Wisdom: {ability_scores.wisdom}")
    print(f"Charisma: {ability_scores.charisma}")
    
    return Player(
        name=name,
        race=selected_race,
        character_class=selected_class,
        ability_scores=ability_scores
    )

def get_valid_input(prompt: str, options: range) -> int:
    """Validate user input against available options"""
    while True:
        try:
            choice = int(input(prompt))
            if choice in options:
                return choice
            print(f"Please enter a number between {options.start} and {options.stop-1}")
        except ValueError:
            print("Please enter a valid number")

def start_game():
    """Initialize and start the game"""
    global game_state
    
    # Create player
    game_state.player = initialize_player()
    
    # Setup world
    game_state.world = create_world()
    game_state.player.location = game_state.world.start_room
    
    # Welcome message
    print(f"""
    Welcome, {game_state.player.name} the {game_state.player.race.name} {game_state.player.character_class.name}!
    
    HP: {game_state.player.hp}/{game_state.player.max_hp}
    AC: {game_state.player.armor_class}
    
    Type 'help' for commands
    """)
    
    # Initial room description
    look()
    
    # Start game loop
    start(prompt=f"[{game_state.player.name}] > ")

if __name__ == '__main__':
    start_game()