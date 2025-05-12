from dnd35e import Character, RACES, CORE_CLASSES, CORE_SPELLS, Magic

# Create a wizard character
elf = RACES["Elf"]
wizard = CORE_CLASSES["Wizard"]
mage = Character("Eldrin", elf, wizard, level=5)

# Set ability scores
mage.ability_scores.intelligence = 18
mage.ability_scores.constitution = 12

# Learn fireball spell
fireball = CORE_SPELLS["Fireball"]
mage.spells_known.append(fireball)

# Cast spell
magic = Magic()
spell_dc = magic.calculate_spell_dc(fireball, mage.level, mage.ability_scores.get_modifier('intelligence'))
save_result = magic.apply_saving_throw("Reflex", spell_dc, 4)  # Target has +4 Reflex

print(f"{mage.name} casts {fireball.name}!")
print(f"Spell DC: {spell_dc}")
print(f"Target rolls {save_result['roll']} + {save_result['bonus']} = {save_result['total']}")
print(f"Save {'succeeds' if save_result['success'] else 'fails'}: {save_result['effect']}")

# Calculate damage
damage = magic.roll_spell_damage(fireball, mage.level)
print(f"Damage: {damage} ({'halved' if save_result['success'] else 'full'})")