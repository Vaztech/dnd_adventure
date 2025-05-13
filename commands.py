import logging
from .dnd35e.mechanics.combat import CombatSystem
from .character import Character

logger = logging.getLogger(__name__)

class CommandParser:
    """Bridge between player input and game systems"""
    def __init__(self, game_session):
        self.game = game_session
        self.combat = CombatSystem()
        logger.debug("Initialized CommandParser")

    def execute(self, command: str):
        """Route commands to appropriate systems"""
        if not command:
            logger.debug("Empty command received")
            return "Please enter a command."

        # Normalize the command (lowercase and stripped)
        command = command.strip().lower()
        logger.debug(f"Executing command: {command}")

        # Handle movement
        if command.startswith('move'):
            return self._handle_move(command)

        # Handle combat (attacking)
        elif command.startswith('attack'):
            return self._handle_combat(command)

        # Handle looking around
        elif command.startswith('look'):
            return self._handle_look(command)

        # Handle other actions (e.g., searching)
        elif command.startswith('search'):
            return self._handle_search(command)

        logger.debug(f"Unknown command: {command}")
        return "Unknown command. Try again."

    def _handle_move(self, command):
        """Handle player movement in the world"""
        try:
            _, direction = command.split(" ", 1)
            logger.debug(f"Handling move: direction={direction}")
            return self.game.handle_movement(direction)
        except ValueError:
            logger.debug("Invalid move command format")
            return "Move where? Please specify a direction (e.g., 'move north')."

    def _handle_combat(self, command):
        """Use 3.5e combat rules to resolve an attack"""
        try:
            _, target_name = command.split(" ", 1)
            logger.debug(f"Handling combat: target={target_name}")
        except ValueError:
            logger.debug("Invalid attack command format")
            return "Attack what? Please specify a target (e.g., 'attack goblin')."

        target = self._find_target(target_name)
        if not target:
            logger.debug(f"No valid target found: {target_name}")
            return f"No valid target named '{target_name}' found."

        result = self.combat.resolve_attack(
            attacker=self.game.player,
            defender=target
        )
        combat_result = self._format_combat_result(result)
        logger.debug(f"Combat result: {combat_result}")
        return combat_result

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
        logger.debug(f"Searching for target: {target_name}")
        try:
            for monster in self.game.player.location.monsters:
                if monster.name.lower() == target_name.lower():
                    logger.debug(f"Target found: {monster.name}")
                    return monster
        except AttributeError:
            logger.error("Invalid player location or monsters attribute")
        logger.debug(f"No target found for: {target_name}")
        return None

    def _handle_look(self, command):
        """Handle the 'look around' command to describe the current room"""
        logger.debug("Handling look command")
        return self.game.print_location()

    def _handle_search(self, command):
        """Handle searching a room or object"""
        logger.debug("Handling search command")
        search_result = self._search_room()
        logger.debug(f"Search result: {search_result}")
        return search_result

    def _search_room(self):
        """Simulate a room search for hidden items or secrets"""
        found_items = ["a rusty sword", "an old map", "a mysterious potion"]
        return f"You search the area and find: {', '.join(found_items)}"