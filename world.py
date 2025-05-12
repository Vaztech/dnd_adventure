from random import choice
from dnd35e.core.monsters import get_monsters_by_cr, get_monsters_by_type

class DnDRoom(Room):
    def populate_monsters(self, cr_range=(1, 3), monster_type=None):
        """Populate room with appropriate monsters"""
        self.monsters = []
        possible_monsters = get_monsters_by_cr(cr_range[1])
        
        if monster_type:
            possible_monsters = {k: v for k, v in possible_monsters.items() 
                               if v.type.lower() == monster_type.lower()}
        
        if possible_monsters:
            num_monsters = random.randint(1, 4)
            self.monsters = [choice(list(possible_monsters.keys())) 
                           for _ in range(num_monsters)]
            
            # Set XP reward based on total CR
            total_cr = sum(possible_monsters[m].challenge_rating 
                          for m in self.monsters)
            self.xp_reward = int(total_cr * 100)

def create_world():
    # Example dungeon with themed areas
    rooms = {}
    
    # Entrance (low CR)
    rooms['entrance'] = DnDRoom(
        "Cave Entrance",
        "A damp cave mouth leading into darkness. Water drips from the ceiling."
    )
    rooms['entrance'].populate_monsters((1, 2))
    
    # Goblin Warrens
    rooms['goblin_cavern'] = DnDRoom(
        "Goblin Cavern",
        "A foul-smelling chamber littered with bones and crude weapons."
    )
    rooms['goblin_cavern'].populate_monsters((2, 4), "Humanoid")
    
    # Dragon's Lair (high CR)
    rooms['dragon_lair'] = DnDRoom(
        "Dragon's Lair",
        "A vast chamber filled with treasure. The air smells of sulfur."
    )
    rooms['dragon_lair'].populate_monsters((10, 15), "Dragon")
    
    # Connect rooms
    rooms['entrance'].east = rooms['goblin_cavern']
    rooms['goblin_cavern'].west = rooms['entrance']
    rooms['goblin_cavern'].down = rooms['dragon_lair']
    rooms['dragon_lair'].up = rooms['goblin_cavern']
    
    return rooms['entrance']