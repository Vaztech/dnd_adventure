from adventurelib import when, set_context
from dnd35e import (
    get_monster, 
    get_monsters_by_cr,
    get_monsters_by_type,
    Combat,
    Magic,
    SkillCheck
)
from dnd35e.core.items import CORE_ITEMS
from .character import Player
from .world import DnDRoom
import random

# Game systems
combat = Combat()
magic = Magic()
skill = SkillCheck()

# Basic commands
@when("look")
def look():
    room = player.location
    if not room.visited:
        print(f"\n{room.name}\n{'-'*len(room.name)}")
        print(room.description)
        room.visited = True
    else:
        print(f"\n{room.name}")
    
    if room.monsters:
        print("\nMonsters present:")
        for monster in room.monsters:
            m = get_monster(monster)
            print(f"- {m.name} (CR {m.challenge_rating})")
    
    if room.treasure:
        print("\nYou see:")
        for item in room.treasure:
            print(f"- {item}")
    
    print("\nExits:")
    for exit in room.exits():
        print(f"- {exit}")

@when("inventory")
def show_inventory():
    if player.inventory:
        print("\nInventory:")
        for item in player.inventory:
            print(f"- {item}")
    else:
        print("\nYour inventory is empty.")
    
    print("\nEquipped:")
    for slot, item in player.equipment.items():
        if item:
            print(f"- {slot}: {item.name}")
        else:
            print(f"- {slot}: Empty")

@when("take ITEM")
def take_item(item):
    room = player.location
    for treasure in room.treasure[:]:
        if treasure.name.lower() == item.lower():
            player.inventory.add(treasure)
            room.treasure.remove(treasure)
            print(f"\nYou take the {treasure.name}.")
            return
    print(f"\nYou don't see {item} here.")

@when("drop ITEM")
def drop_item(item):
    for inv_item in player.inventory:
        if inv_item.name.lower() == item.lower():
            player.location.treasure.append(inv_item)
            player.inventory.take(inv_item.name)
            print(f"\nYou drop the {inv_item.name}.")
            return
    print(f"\nYou don't have {item} in your inventory.")

@when("equip ITEM")
def equip_item(item):
    for inv_item in player.inventory:
        if inv_item.name.lower() == item.lower():
            if hasattr(inv_item, 'equip_slot'):
                player.equip(inv_item)
                return
            else:
                print(f"\nYou can't equip {inv_item.name}.")
                return
    print(f"\nYou don't have {item} in your inventory.")

@when("unequip SLOT")
def unequip_slot(slot):
    if slot.lower() in player.equipment and player.equipment[slot.lower()]:
        item = player.equipment[slot.lower()]
        player.inventory.add(item)
        player.equipment[slot.lower()] = None
        print(f"\nYou unequip the {item.name}.")
    else:
        print(f"\nNothing equipped in {slot} slot.")

@when("stats")
def show_stats():
    print(f"\n{player.name} the {player.race.name} {player.dnd_class.name}")
    print(f"Level {player.level} | XP: {player.xp}/{player.level * 1000}")
    print(f"HP: {player.hit_points}/{player.calculate_hit_points()} | AC: {player.armor_class()}")
    
    print("\nAbility Scores:")
    print(f"STR: {player.ability_scores.strength} ({player.ability_scores.get_modifier('strength'):+d})")
    print(f"DEX: {player.ability_scores.dexterity} ({player.ability_scores.get_modifier('dexterity'):+d})")
    print(f"CON: {player.ability_scores.constitution} ({player.ability_scores.get_modifier('constitution'):+d})")
    print(f"INT: {player.ability_scores.intelligence} ({player.ability_scores.get_modifier('intelligence'):+d})")
    print(f"WIS: {player.ability_scores.wisdom} ({player.ability_scores.get_modifier('wisdom'):+d})")
    print(f"CHA: {player.ability_scores.charisma} ({player.ability_scores.get_modifier('charisma'):+d})")
    
    print("\nSaving Throws:")
    print(f"Fortitude: {player.dnd_class.save_at_level('Fort', player.level):+d}")
    print(f"Reflex: {player.dnd_class.save_at_level('Ref', player.level):+d}")
    print(f"Will: {player.dnd_class.save_at_level('Will', player.level):+d}")

# Combat commands
@when("attack MONSTER")
def attack_monster(monster_name):
    room = player.location
    target = None
    monster_key = None
    
    # Find matching monster
    for m in room.monsters:
        if monster_name.lower() in m.lower():
            target = get_monster(m)
            monster_key = m
            break
    
    if not target:
        print(f"\nYou don't see {monster_name} here.")
        return
    
    print(f"\nYou attack the {target.name}!")
    
    # Player attack
    attack_result = combat.resolve_attack(player, target)
    
    if attack_result['hit']:
        print(f"You hit for {attack_result['damage']} damage!")
        if attack_result['critical']:
            print("Critical hit!")
        
        # Check for defeat
        room.monsters.remove(monster_key)
        xp_gain = int(target.challenge_rating * 300)
        player.add_xp(xp_gain)
        print(f"{target.name} defeated! (+{xp_gain} XP)")
        
        # Check for treasure
        if target.treasure.lower() != "none" and random.random() > 0.5:
            treasure_type = target.treasure.split()[0].lower()
            if treasure_type in ["standard", "double"]:
                item = random.choice(list(CORE_ITEMS.values()))
                room.treasure.append(item)
                print(f"The {target.name} dropped {item.name.lower()}!")
        
        # Check for area clear
        if not room.monsters and hasattr(room, 'xp_reward') and room.xp_reward > 0:
            player.add_xp(room.xp_reward)
            print(f"\nArea cleared! Bonus {room.xp_reward} XP!")
            room.xp_reward = 0
    else:
        print("You miss!")
    
    # Monster counterattack if alive
    if monster_key in room.monsters:
        print(f"\nThe {target.name} retaliates!")
        
        # Use special abilities
        abilities_used = combat.resolve_monster_abilities(target)
        for ability, details in abilities_used.items():
            print(f"\n{target.name} uses {ability}!")
            print(details['description'])
            
            if details.get('dc'):
                save_type = "Will"  # Default save type
                if "poison" in ability.lower() or "disease" in ability.lower():
                    save_type = "Fort"
                elif "reflex" in details['description'].lower():
                    save_type = "Ref"
                
                save_bonus = player.dnd_class.save_at_level(save_type, player.level)
                save_roll = random.randint(1, 20) + save_bonus
                
                if save_roll >= details['dc']:
                    print(f"You resist! (Rolled {save_roll} vs DC {details['dc']})")
                else:
                    print(f"You fail to resist! (Rolled {save_roll} vs DC {details['dc']})")
                    # Apply effect
        
        # Standard attack
        attack_result = combat.resolve_attack(target, player)
        if attack_result['hit']:
            player.hit_points -= attack_result['damage']
            print(f"\n{target.name} hits you for {attack_result['damage']} damage!")
            
            if player.hit_points <= 0:
                print("\nYou have been defeated!")
                return
        else:
            print(f"\n{target.name} misses you!")

@when("cast SPELL at TARGET")
def cast_spell(spell, target):
    # Find spell in known spells
    spell_obj = None
    for s in player.spells_known:
        if s.name.lower() == spell.lower():
            spell_obj = s
            break
    
    if not spell_obj:
        print(f"\nYou don't know the spell {spell}.")
        return
    
    # Find target
    if target.lower() == "self":
        target_obj = player
    else:
        room = player.location
        target_obj = None
        for m in room.monsters:
            if target.lower() in m.lower():
                target_obj = get_monster(m)
                break
        
        if not target_obj:
            print(f"\nYou don't see {target} here.")
            return
    
    print(f"\nYou cast {spell_obj.name} at {target_obj.name}!")
    
    # Resolve spell effects
    if spell_obj.saving_throw:
        save_type = spell_obj.saving_throw.split()[0]
        save_bonus = target_obj.saves.get(save_type, 0) if isinstance(target_obj, Monster) \
                    else player.dnd_class.save_at_level(save_type, player.level)
        save_roll = random.randint(1, 20) + save_bonus
        spell_dc = 10 + spell_obj.level + player.ability_scores.get_modifier('intelligence')
        
        if save_roll >= spell_dc:
            print(f"{target_obj.name} resists the spell!")
            if "half" in spell_obj.saving_throw.lower():
                damage = magic.roll_spell_damage(spell_obj, player.level) // 2
                print(f"They take half damage: {damage}")
            else:
                return
        else:
            print(f"The spell takes full effect!")
            damage = magic.roll_spell_damage(spell_obj, player.level)
    else:
        damage = magic.roll_spell_damage(spell_obj, player.level)
    
    if damage > 0:
        if isinstance(target_obj, Monster):
            room.monsters.remove(target_obj.name)
            xp_gain = int(target_obj.challenge_rating * 300)
            player.add_xp(xp_gain)
            print(f"{target_obj.name} takes {damage} damage and is defeated! (+{xp_gain} XP)")
        else:
            player.hit_points -= damage
            print(f"You take {damage} damage from your own spell!")

# Movement commands
@when("go DIRECTION")
def go(direction):
    room = player.location
    next_room = room.exit(direction)
    
    if next_room:
        player.location = next_room
        print(f"\nYou move {direction}.")
        look()
    else:
        print(f"\nYou can't go {direction} from here.")

@when("north", direction="north")
@when("south", direction="south")
@when("east", direction="east")
@when("west", direction="west")
@when("up", direction="up")
@when("down", direction="down")
def go_direction(direction):
    go(direction)

# Monster interaction
@when("examine MONSTER")
def examine_monster(monster_name):
    monster = get_monster(monster_name)
    if not monster:
        print("\nNo such monster in your knowledge.")
        return
    
    print(f"\n{monster.name} (CR {monster.challenge_rating})")
    print(f"Type: {monster.type}{' ('+monster.subtype+')' if monster.subtype else ''}")
    print(f"Size: {monster.size} | Alignment: {monster.alignment}")
    print(f"HP: {monster.hit_dice} | AC: {monster.armor_class} (Touch: {monster.touch_ac}, Flat: {monster.flat_footed_ac})")
    print(f"Saves: Fort +{monster.saves['Fort']}, Ref +{monster.saves['Ref']}, Will +{monster.saves['Will']}")
    
    print("\nAttacks:")
    for attack in monster.attacks[:3]:  # Show first 3 attacks
        print(f"- {attack.name}: +{attack.attack_bonus} ({attack.damage} {attack.damage_type})")
    
    print("\nSpecial Abilities:")
    for ability in monster.abilities_list[:3]:  # Show first 3 abilities
        print(f"- {ability.name}: {ability.description[:60]}...")
    
    print(f"\nEnvironment: {monster.environment}")
    print(f"Treasure: {monster.treasure}")

# Help system
@when("help")
@when("help COMMAND")
def show_help(command=None):
    if not command:
        print("""
Available Commands:
------------------
Movement:
  go [direction] - Move in a direction (north, south, east, west, up, down)
  look - Examine your surroundings

Combat:
  attack [monster] - Attack a monster
  cast [spell] at [target] - Cast a spell
  examine [monster] - Examine a monster's stats

Inventory:
  inventory - Show your inventory
  take [item] - Pick up an item
  drop [item] - Drop an item
  equip [item] - Equip an item
  unequip [slot] - Unequip from a slot

Character:
  stats - Show your character sheet
  help - Show this help message

Type 'help [command]' for more info on a specific command.
""")
    elif command.lower() == "attack":
        print("""
Attack Command:
--------------
Usage: attack [monster name]

Engages in combat with the specified monster. You'll make an attack roll against
the monster's armor class. If successful, you'll deal damage based on your
equipped weapon.

Example:
  attack goblin
  attack red dragon
""")
    elif command.lower() == "cast":
        print("""
Cast Command:
------------
Usage: cast [spell name] at [target]

Attempts to cast one of your known spells at the target. The target can be
a monster name or 'self'. Spells may allow saving throws for partial effects.

Example:
  cast fireball at goblins
  cast cure light wounds at self
""")

# Debug commands (remove in production)
@when("debug addmonster MONSTER")
def debug_add_monster(monster_name):
    monster = get_monster(monster_name)
    if monster:
        player.location.monsters.append(monster_name)
        print(f"\nAdded {monster.name} to room.")
    else:
        print("\nMonster not found.")

@when("debug levelup")
def debug_level_up():
    player.add_xp(player.level * 1000)
    print("\nForced level up!")