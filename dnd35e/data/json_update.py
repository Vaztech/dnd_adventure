import json
from collections import defaultdict

# Load the existing JSON file (incorrect structure)
def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Save the corrected JSON to a new file
def save_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# Transform the list of monsters into the required dictionary structure
def transform_monsters_data(monsters_data):
    transformed_data = defaultdict(dict)

    for monster in monsters_data:
        # Assuming each monster has a 'category' key, you may need to adjust this part
        category = monster.get('category', 'Uncategorized')  # Default category if none exists
        name = monster.get('name')
        
        if name:
            transformed_data[category][name] = monster

    return transformed_data

# Main function to load, transform, and save the corrected data
def main():
    # Provide the path to your incorrect JSON file
    input_file_path = r'C:\Users\Vaz\Desktop\dnd_adventure\dnd35e\data\srd_monsters.json'
    
    # Load the existing (incorrect) JSON data
    monsters_data = load_json_file(input_file_path)
    
    # Transform the data into the correct format
    corrected_data = transform_monsters_data(monsters_data)
    
    # Provide the path where you want to save the corrected file
    output_file_path = r'C:\Users\Vaz\Desktop\dnd_adventure\dnd35e\data\srd_monsters_corrected.json'
    
    # Save the corrected JSON data
    save_json_file(output_file_path, corrected_data)
    print(f"Corrected JSON saved to: {output_file_path}")

# Run the script
if __name__ == '__main__':
    main()
