import json
import re

def process_actions(actions):
    """Process actions and extract relevant information."""
    action_list = []
    if isinstance(actions, str):
        action_data = actions.split('</p><p>')  # Split the actions if they are separated by paragraphs
        for action in action_data:
            action_info = {}

            # Search for action name within <strong> tags
            name_match = re.search(r'<strong>(.*?)</strong>', action)
            if name_match:
                action_info['name'] = name_match.group(1)
            else:
                action_info['name'] = "Unnamed Action"  # Default name if no match

            # Clean up HTML tags and extract the description
            description = re.sub(r'<.*?>', '', action)  # Remove all HTML tags
            action_info['description'] = description.strip()

            # Parse damage if it exists in the action description
            if "Melee Weapon Attack" in action:
                attack_match = re.search(r'(\d+) to hit.*?(\d+d\d+)', action)
                if attack_match:
                    action_info['attack_bonus'] = int(attack_match.group(1))
                    action_info['damage'] = attack_match.group(2)

            action_list.append(action_info)

    return action_list


def process_monster_data(monster_data):
    """Process the entire monster data."""
    updated_data = {}

    for category, monsters in monster_data.items():
        updated_data[category] = {}

        for monster_name, monster in monsters.items():
            monster_info = {}

            # Basic Info
            monster_info['name'] = monster.get('name', 'Unknown')
            monster_info['size'] = monster.get('size', 'Unknown')
            monster_info['meta'] = monster.get('meta', 'Unknown')
            monster_info['armor_class'] = monster.get('armor_class', 'Unknown')
            monster_info['hit_points'] = monster.get('hit_points', 'Unknown')
            monster_info['speed'] = monster.get('speed', 'Unknown')

            # Abilities
            monster_info['abilities'] = {
                'str': int(monster.get('str', 10)),
                'dex': int(monster.get('dex', 10)),
                'con': int(monster.get('con', 10)),
                'int': int(monster.get('int', 10)),
                'wis': int(monster.get('wis', 10)),
                'cha': int(monster.get('cha', 10))
            }

            # Saving Throws
            monster_info['saving_throws'] = monster.get('saving_throws', '')

            # Skills
            monster_info['skills'] = monster.get('skills', '')

            # Senses
            monster_info['senses'] = monster.get('senses', '')

            # Languages
            monster_info['languages'] = monster.get('languages', '')

            # Traits
            monster_info['traits'] = monster.get('traits', '')

            # Actions - Process the actions
            monster_info['actions'] = process_actions(monster.get('actions', ''))

            # Legendary Actions (if any)
            monster_info['legendary_actions'] = process_actions(monster.get('legendary_actions', ''))

            # Image URL
            monster_info['img_url'] = monster.get('img_url', '')

            # Challenge Rating
            monster_info['challenge_rating'] = float(monster.get('challenge_rating', 0))

            # Store processed monster
            updated_data[category][monster_name] = monster_info

    return updated_data


def main():
    # Load the SRD monster data from the JSON file
    with open('srd_monsters.json', 'r', encoding='utf-8') as f:
        monster_data = json.load(f)

    # Process the monster data
    updated_data = process_monster_data(monster_data)

    # Optionally save the updated data to a new file
    with open('updated_srd_monsters.json', 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=4)

    print("Monster data processed and saved as 'updated_srd_monsters.json'.")


if __name__ == "__main__":
    main()
