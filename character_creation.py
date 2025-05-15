from dnd35e.core.character import Character, get_class_by_name, get_all_classes
from dnd35e.core.data_loader import load_classes_from_json

def create_character_cli():
    load_classes_from_json()  # Load all classes into CORE_CLASSES

    name = input("Enter character name: ")
    race = input("Enter race: ")

    print("\nAvailable Classes:")
    for cls in get_all_classes():
        print(f"- {cls.name}")
    
    class_name = input("Choose a class: ")
    dnd_class = get_class_by_name(class_name)
    if not dnd_class:
        print("Invalid class. Aborting.")
        return

    level_input = input("Enter starting level (default 1): ").strip()
    try:
        level = int(level_input)
    except ValueError:
        level = 1

    # Initialize at level 1
    character = Character(name=name, race_name=race, class_name=class_name, level=1)

    # Simulate leveling up to desired level
    for _ in range(1, level):
        character.level_up()

    print(f\"\n✅ Created character: {character.name}, a level {character.level} {character.race_name} {character.dnd_class.name}\")
