from .dnd35e.mechanics.combat import CombatSystem
from .dnd35e.core.character import CharacterSheet
from .world import GameWorld

class CommandParser:
    """Bridge between player input and game systems"""
    def __init__(self, game_session):
        self.game = game_session
        self.combat = CombatSystem()
        
    def execute(self, command: str):
        """Route commands to appropriate systems"""
        # Handle movement
        if command.startswith('move'):
            return self._handle_move(command)
        
        # Handle combat (attacking)
        elif command.startswith('attack'):
            return self._handle_combat(command)
        
        # Handle looking around
        elif command.startswith('look'):
            return self._handle_look(command)
        
        # Handle other actions (e.g., searching, using items)
        elif command.startswith('search'):
            return self._handle_search(command)
        
        return "Unknown command. Try again."

    def _handle_move(self, command):
        """Handle player movement in the world"""
        # Expect command format like "move north", "move south", etc.
        direction = command.split(" ")[1]
        return self.game.world.move_player(direction)

    def _handle_combat(self, command):
        """Use 3.5e combat rules to resolve an attack"""
        target = self._find_target(command)
        if not target:
            return "No valid target found for attack."
        
        result = self.combat.resolve_attack(
            attacker=self.game.player.sheet,
            defender=target
        )
        return result

    def _find_target(self, command):
        """Find the target of the attack (e.g., based on command string)"""
        # Here you can add logic to find a monster in the room or a player
        target_name = command.split(" ")[1]  # Example: 'attack goblin'
        
        # Check if the target exists in the current room
        for monster in self.game.world.player_location.monsters:
            if monster.name.lower() == target_name.lower():
                return monster
        return None

    def _handle_look(self, command):
        """Handle the 'look around' command to describe the current room"""
        return self.game.world.describe_current_location()

    def _handle_search(self, command):
        """Handle searching a room or object"""
        # Example: Searching the room for hidden items or secrets
        search_result = self._search_room()
        return search_result
    
    def _search_room(self):
        """Simulate a room search for hidden items or secrets"""
        # You can expand this method to include hidden treasure, traps, or NPCs
        found_items = ["a rusty sword", "an old map", "a mysterious potion"]
        return f"You found: {', '.join(found_items)}"
