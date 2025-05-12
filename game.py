import sys
from .character import Character
from .world import GameWorld

class Game:
    def __init__(self):
        self.world = GameWorld.generate()
        self.player = Character("Hero", 20, 8, 4)
        self.player.location = self.world.current_room or self.world.rooms[0]
        self.combat_mode = False
        self.current_enemy = None

    def start(self):
        print("\n=== Dungeon Adventure ===")
        print("Commands: move [north/south/east/west], look, attack, inventory, quit\n")
        self.print_location()

    def print_location(self):
        room = self.player.location
        print(f"\n{room['name']}")
        print(room['description'])
        
        if room['exits']:
            print("\nExits:", ", ".join(room['exits'].keys()))
        
        if room['monsters']:
            alive_monsters = [m for m in room['monsters'] if m.is_alive()]
            if alive_monsters:
                print("\nMonsters here:")
                for i, monster in enumerate(alive_monsters, 1):
                    print(f"{i}. {monster.name} (HP: {monster.hp})")
                self.combat_mode = True
            else:
                print("\nDefeated monsters lie scattered about.")
                self.combat_mode = False

    def handle_command(self, command):
        command = command.lower().strip()
        
        if self.combat_mode and command.isdigit():
            self.handle_attack(int(command))
        elif command in ["north", "south", "east", "west"]:
            self.handle_movement(command)
        elif command == "look":
            self.print_location()
        elif command.startswith("attack"):
            self.handle_attack_command(command)
        elif command in ["quit", "exit"]:
            self.quit_game()
        else:
            print("Valid commands:")
            if self.combat_mode:
                print("- [number] (to attack that monster)")
            print("- north/south/east/west")
            print("- look")
            print("- attack [number]")
            print("- quit")

    def handle_movement(self, direction):
        if self.combat_mode:
            print("You can't move while in combat!")
            return
            
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

    def handle_attack_command(self, command):
        if not self.combat_mode:
            print("There's nothing to attack here!")
            return
            
        try:
            target = int(command.split()[1]) if len(command.split()) > 1 else 1
            self.handle_attack(target)
        except (ValueError, IndexError):
            print("Specify which monster to attack (e.g. 'attack 1')")

    def handle_attack(self, target_index):
        alive_monsters = [m for m in self.player.location['monsters'] if m.is_alive()]
        
        try:
            monster = alive_monsters[target_index - 1]
            damage = self.player.attack_target(monster)
            print(f"You attack the {monster.name} for {damage} damage!")
            
            if not monster.is_alive():
                print(f"You defeated the {monster.name}!")
                alive_monsters.remove(monster)
                if not alive_monsters:
                    self.combat_mode = False
                    print("All enemies defeated! You can now move freely.")
            else:
                # Monster counterattack
                monster_damage = max(1, monster.attack - self.player.defense)
                self.player.hp -= monster_damage
                print(f"The {monster.name} attacks you back for {monster_damage} damage!")
                print(f"Your HP: {self.player.hp}/{20}")
                
                if self.player.hp <= 0:
                    print("\nYou have been defeated...")
                    self.quit_game()
                    
        except IndexError:
            print(f"Invalid target. There {'is' if len(alive_monsters) == 1 else 'are'} only {len(alive_monsters)} monster{'s' if len(alive_monsters) != 1 else ''} here.")

    def quit_game(self):
        print("\nThanks for playing! Goodbye.")
        sys.exit()

def main():
    try:
        game = Game()
        game.start()
        
        while True:
            try:
                command = input("\nWhat would you like to do? ").strip()
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