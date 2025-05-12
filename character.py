class Character:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.inventory = []
        self.location = None

    def move(self, direction):
        if self.location and direction in self.location['exits']:
            return self.location['exits'][direction]
        return None

    def attack_target(self, target):
        damage = max(1, self.attack - target.defense)
        target.hp -= damage
        return damage