from .dnd35e.mechanics.combat import CombatSystem  # Updated class name
from .dnd35e.core.character import CharacterSheet
from .world import GameWorld

class CommandParser:
    """Bridge between player input and game systems"""
    def __init__(self, game_session):
        self.game = game_session
        self.combat = CombatSystem()  # Updated to use CombatSystem

    def execute(self, command: str):
        """Route commands to appropriate systems"""
        if not command:
            return "Please enter a command."

        # Normalize the command (lowercase and stripped)
        command = command.strip().lower()

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
        try:
            # Expect command format like "move north", "move south", etc.
            _, direction = command.split(" ", 1)
            return self.game.world.move_player(direction)
        except ValueError:
            return "Move where? Please specify a direction (e.g., 'move north')."

    def _handle_combat(self, command):
        """Use 3.5e combat rules to resolve an attack"""
        try:
            _, target_name = command.split(" ", 1)
        except ValueError:
            return "Attack what? Please specify a target (e.g., 'attack goblin')."
        
        target = self._find_target(target_name)
        if not target:
            return f"No valid target named '{target_name}' found."
        
        result = self.combat.resolve_attack(
            attacker=self.game.player.sheet,
            defender=target
        )
        return self._format_combat_result(result)

    def _format_combat_result(self, result):
        """Format combat result into a readable string"""
        if not result['hit']:
            return f"{result['attacker']} attacks {result['defender']} but misses!"

        critical = " (CRITICAL HIT!)" if result['critical'] else ""
        effects = ", ".join(result['special_effects']) if result['special_effects'] else "None"
        
        return (
            f"{result['attacker']} attacks {result['defender']} and hits!{critical}\n"
            f"Damage: {result['damage']}\n"
            f"Special Effects: {effects}"
        )

    def _find_target(self, target_name):
        """Find the target of the attack based on the command string"""
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
        search_result = self._search_room()
        return search_result

    def _search_room(self):
        """Simulate a room search for hidden items or secrets"""
        # You can expand this method to include hidden treasure, traps, or NPCs
        found_items = ["a rusty sword", "an old map", "a mysterious potion"]
        return f"You search the area and find: {', '.join(found_items)}"
    
    def _handle_use_item(self, command):
        """Handle using an item from the inventory"""
        try:
            _, item_name = command.split(" ", 1)
        except ValueError:
            return "Use what? Please specify an item (e.g., 'use potion')."
        
        item = self.game.player.inventory.get(item_name)
        if not item:
            return f"You don't have a '{item_name}' in your inventory."
        
        # Use the item (this is a placeholder; implement actual item effects)
        return f"You use the {item_name}."
