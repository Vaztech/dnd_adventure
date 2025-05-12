from adventurelib import Item, Bag
from dnd35e import Character as DnDCharacter, CORE_ITEMS

class Player(DnDCharacter):
    def __init__(self, name, race, dnd_class):
        super().__init__(name, race, dnd_class)
        self.inventory = Bag()
        self.equipment = {
            'weapon': None,
            'armor': None,
            'shield': None,
            'ammunition': None
        }
        self.gold = 0
        self.location = None
        self.xp = 0
        self.level = 1
        
    def equip(self, item):
        """Equip an item from inventory"""
        if item in self.inventory:
            slot = item.equip_slot
            if self.equipment[slot]:
                self.inventory.add(self.equipment[slot])
            self.equipment[slot] = item
            self.inventory.take(item.name)
            print(f"You equip {item.name}")
        else:
            print(f"You don't have {item.name} in your inventory")
    
    def get_equipped_weapon(self):
        return self.equipment['weapon'] or CORE_ITEMS["Unarmed Strike"]
    
    def add_xp(self, amount):
        self.xp += amount
        print(f"You gain {amount} XP!")
        # Simple level up - 1000 XP per level
        if self.xp >= self.level * 1000:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        new_hp = max(1, self.dnd_class.hit_die // 2 + 1 + self.ability_scores.get_modifier('constitution'))
        self.hit_points += new_hp
        print(f"\nLEVEL UP! You are now level {self.level}")
        print(f"You gain {new_hp} hit points (now {self.hit_points})")
    
    def __str__(self):
        return f"{self.name} the {self.race.name} {self.dnd_class.name} (Level {self.level})"