import re
from itertools import combinations
import builtins

# Open the file in read mode
with open("/home/sane7222/eso/data/sets.txt", "r") as f:
    # Read the contents of the file
    data = f.read()

# Split the data into individual lines
lines = data.strip().split("\n")

# Define the Set class
class Set:
    def __init__(self, name):
        self.name = name
        self.items = []
        self.general = {}

    def add_item(self, item):
        self.items.append(item)

    def add_general(self, key, value):
        if key in self.general:
            self.general[key].append(value)
        else:
            self.general[key] = [value]

# Initialize empty lists for the sets
monster_sets = []
other_sets = []

# Initialize a variable to store the current set
current_set = None

# Iterate through the lines
for line in lines:
    # Check if the line ends with '&'
    if line.endswith("&"):
        # If it does, create a new Set object and add it to the monster_sets list
        current_set = Set(line)
        monster_sets.append(current_set)
    elif line.startswith("("):
        # If the line starts with "(number item)", remove the prefix and add the item to the items of the current set
        item = line.strip().split(" ", 1)[1]
        item = item.strip().split(" ", 1)[1]
        current_set.add_item(item)
    else:
        # If the line is neither a set name nor an item, create a new Set object and add it to the other_sets list
        current_set = Set(line)
        other_sets.append(current_set)

for set in monster_sets:
    for item in set.items:
        if item.startswith('Adds ') and item.endswith(' Weapon and Spell Damage'): # D
            number = re.findall(r'(\d+)', item)[0]
            set.add_general('D', int(number))
        elif item.startswith('Adds ') and item.endswith(' Maximum Magicka'): # M
            number = re.findall(r'(\d+)', item)[0]
            set.add_general('M', int(number))
        elif item.startswith('Adds ') and item.endswith(' Critical Chance'): # C
            number = re.findall(r'(\d+)', item)[0]
            number = int(number)/21900
            set.add_general('C', number)
        elif item.startswith('Gain Minor Slayer at all times, increasing your damage done to Dungeon, Trial, and Arena Monsters by 5%.'): # m_SLAYER
            number = 0.05
            set.add_general('m_SLAYER', number)
        elif item.startswith('Adds ') and item.endswith(' Offensive Penetration'): # P
            number = re.findall(r'(\d+)', item)[0]
            set.add_general('P', int(number))

with open('/home/sane7222/eso/data/excluded_monster_sets.txt', 'r') as other_file:
    other_file_set = builtins.set(other_file.read().split('\n'))

filtered_sets = []
for set in monster_sets:
    if len(set.general) > 0 and set.name not in other_file_set:
        filtered_sets.append(set)

monster_sets = filtered_sets

for set in other_sets:
    for item in set.items:
        if item.startswith('Adds ') and item.endswith(' Weapon and Spell Damage'): # D
            number = re.findall(r'(\d+)', item)[0]
            set.add_general('D', int(number))
        elif item.startswith('Adds ') and item.endswith(' Maximum Magicka'): # M
            number = re.findall(r'(\d+)', item)[0]
            set.add_general('M', int(number))
        elif item.startswith('Adds ') and item.endswith(' Critical Chance'): # C
            number = re.findall(r'(\d+)', item)[0]
            number = int(number)/21900
            set.add_general('C', number)
        elif item.startswith('Gain Minor Slayer at all times, increasing your damage done to Dungeon, Trial, and Arena Monsters by 5%.'): # m_SLAYER
            number = 0.05
            set.add_general('m_SLAYER', number)
        elif item.startswith('Adds ') and item.endswith(' Offensive Penetration'): # P
            number = re.findall(r'(\d+)', item)[0]
            set.add_general('P', int(number))

with open('/home/sane7222/eso/data/excluded_regular_sets.txt', 'r') as other_file:
    other_file_set = builtins.set(other_file.read().split('\n'))

filtered_sets = []
for set in other_sets:
    if len(set.general) > 0 and set.name not in other_file_set:
        filtered_sets.append(set)

other_sets = filtered_sets

set_combos = list(combinations(other_sets, 2))

with open('/home/sane7222/eso/data/parsed_sets.txt', 'r') as other_file:
    other_file_set = builtins.set(other_file.read().split('\n'))

# Open the file in write mode
with open("/home/sane7222/eso/data/parsed_sets.txt", "a") as f:

    for set in monster_sets:
        if set.name not in other_file_set:
            f.write(set.name + '\n')
            for key, value in set.general.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

    # Iterate through the sets in other_sets
    for set in other_sets:
        if set.name not in other_file_set:
            # Write the name of the set to the file
            f.write(set.name + "\n")
            # Iterate through the general information for the set
            for key, value in set.general.items():
                # Write the key and value to the file
                f.write(f"{key}: {value}\n")
            # Write an empty line to separate the set information from the next set
            f.write("\n")
