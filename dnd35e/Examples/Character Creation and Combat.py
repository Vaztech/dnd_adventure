from dnd35e import Character, RACES, CORE_CLASSES, Combat
from dnd35e.core.items import Item

# Create a fighter character
human = RACES["Human"]
fighter = CORE_CLASSES["Fighter"]
hero = Character("Sir Gallant", human, fighter, level=1)

# Set ability scores
hero.ability_scores.strength = 16
hero.ability_scores.dexterity = 14
hero.ability_scores.constitution = 14

# Equip a longsword
longsword = Item(
    name="Longsword",
    category="weapon",
    damage="1d8",
    critical="19-20/x2",
    properties=[ItemProperty("Martial Weapon", "Proficiency required")]
)
hero.equipment['weapon'] = longsword

# Simulate combat
combat = Combat()
attack = combat.attack_roll(hero, 15)  # Attack AC 15
damage = combat.calculate_damage(hero, longsword, attack['is_critical'])

print(f"{hero.name} attacks!")
print(f"Roll: {attack['roll']} + {attack['attack_bonus']} = {attack['total']} vs AC 15")
print(f"Hit: {'Yes' if attack['is_hit'] else 'No'}")
if attack['is_hit']:
    print(f"Damage: {damage} {'(CRITICAL!)' if attack['is_critical'] else ''}")