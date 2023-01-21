import re
import time
from itertools import combinations

# Predefined
SKILL_COEFF_MAX_MAG = 0.1
SKILL_COEFF_SD = 1.05

# User defined for High Elf
PLAYER_PERC_DM = 0.0 # Minor Berserk for a player dealing 5% more damage
ENEMY_PERC_DM = 0.0 # Minor Vulnerability for a target taking 5% more damage
ENEMY_RESISTANCE_DEBUFF = 0 # Minor Breach for target resistance decreased by 2974
PLAYER_PERC_PEN = 0 # Mace ignores 20% of targets resistance

# BreakDown Stats
BASE_MAG = 12000 # Magicka
ATTR_MAG = 7104
ARMOUR_MAG_ENCHANTS = 4008
HIGH_ELF_MAG = 2000
CHAMPION_POINT_MAG = 520
SIPHONING_MAG_PASSIVE = 0.08
UNDAUNTED_MAG_PASSIVE = 0.02

WITCH_MOTHER_MAG = 2856 # Food
TOMATO_SOUP_MAG = 6048

BASE_SD = 1000 # Spell Damage
FLAME_STAFF_SD = 1335
JEWELRY_SD_ENCHANTS = 522
FLAME_STAFF_SD_ENCHANT_INFUSED = 452
HIGH_ELF_SD = 258
MEDIUM_ARMOR_PASSIVE_SD_PER_PIECE = 0.02

BASE_SPELL_CC = 0.1 # Spell Crit Chance
CHAMPION_POINT_CC = 0.014
FLAME_STAFF_CC = 0.072
LIGHT_ARMOR_PASSIVE_CC_PER_PIECE = 0.01

BASE_SPELL_CD = 0.5 # Spell Crit Damage
ASSASSIN_CD_PASSIVE = 0.1
MEDIUM_ARMOR_PASSIVE_CD_PER_PIECE = 0.02

ASSASSIN_PEN_PASSIVE = 2974 # Flat Penetration
CHAMPION_POINT_PEN = 700
LIGHT_ARMOR_PASSIVE_PEN_PER_PIECE = 939

# Buffs
MAJOR_BERSERK = 0.1 # DM
MAJOR_COURAGE = 430 # SD
MAJOR_FORCE = 0.2 # CD
MAJOR_PROPHECY = 0.12 # CC | Potion / Inner Light
MAJOR_SLAYER = 0.1 # DM
MAJOR_SORCERY = 0.2 # SDM | Potion / Entropy
MINOR_BERSERK = 0.05 # DM
MINOR_COURAGE = 215 # SD
MINOR_FORCE = 0.1 # CD | Channeled Acceleraton / Barbed Trap
MINOR_PROPHECY = 0.06 # CC
MINOR_SLAYER = 0.05 # DM
MINOR_SORCERY = 0.1 # SDM

# Debuffs
MAJOR_BREACH = 5948 # P | Elemental Drain / Tank
MAJOR_BRITTLE = 0.2 # CD
MAJOR_VULNERABILITY = 0.1 # DM
MINOR_BREACH = 2974 # P
MINOR_BRITTLE = 0.1 # CD
MINOR_VULNERABILITY = 0.05 # DM

# Pre-computational values
MAGICKA = BASE_MAG + ATTR_MAG + ARMOUR_MAG_ENCHANTS + HIGH_ELF_MAG + CHAMPION_POINT_MAG
SPELL_DAMAGE = BASE_SD + FLAME_STAFF_SD + JEWELRY_SD_ENCHANTS + HIGH_ELF_SD + FLAME_STAFF_SD_ENCHANT_INFUSED
PENETRATION = CHAMPION_POINT_PEN
CRITICAL_CHANCE = BASE_SPELL_CC + CHAMPION_POINT_CC + FLAME_STAFF_CC
CRITICAL_DAMAGE = BASE_SPELL_CD + ASSASSIN_CD_PASSIVE

# User Settings
SOLO = True
DUMMY = False
ENEMY_RESISTANCE = 18200 # 18200 max enemy resistance | Dummy resistance is 1170
NUMBER_OF_CHAMPION_POINTS = 2
HIGHEST = 5

# Define the Set class
class Set:
    def __init__(self, name):
        self.name = name
        self.general = {}

    def add_general(self, key, value):
        if key in self.general:
            self.general[key].append(value)
        else:
            self.general[key] = [value]

def setCollector():
    with open("/home/sane7222/eso/data/final_sets.txt", "r") as f:
        data = f.read()

    lines = data.strip().split("\n") # Split the data into individual lines

    monster_sets = []
    regular_sets = []

    current_set = None # Initialize a variable to store the current set
    parsing_general = False # Initialize a variable to track whether we are currently parsing general information for a set

    for line in lines:
        if not line: # If the line is empty, set parsing_general to False
            parsing_general = False
        elif not parsing_general:
            current_set = Set(line) # If we are not parsing general information and the line is not empty, create a new Set object with the line as its name

            if current_set.name.endswith("&"): # If the name of the set ends with an ampersand (&), add it to the monster_sets list
                monster_sets.append(current_set)
            else: # Otherwise, add it to the regular_sets list
                regular_sets.append(current_set)

        else:
            key, value = line.split(": ") # If we are parsing general information and the line is not empty, split the line into the key and value
            numbers = re.findall(r"\[([\d., ]+)\]", value) # Use a regular expression to match the pattern "[number]" or "[number, number]" and extract the numbers
            numbers = [int(x) if '.' not in x else float(x) for x in numbers[0].split(", ")] # Split the numbers on the comma and convert them to integers or floats

            for x in numbers:
                current_set.add_general(key, x)

        parsing_general = line.endswith(tuple("]&BLM")) # Set parsing_general to True if the line ends with any of ], &, B, L, M

    return monster_sets, regular_sets

def combinationBuilder(regular_sets):
    mundus = {'M': [3309], 'SD': [389], 'CC': [0.09894977168949772], 'CD': [0.17], 'P': [4489]} # Values with 7 pieces of Divines
    champion = {'ARCANE M': [1300], 'UNTAMED SD': [150], 'WRATHFUL SD': [205], 'BACKSTAB CD': [0.1], 'FIGHT CD': [0.08], 'SINGLE DM': [0.03], 'DIRECT DM': [0.02]}
    champion_solo = {'ARCANE M': [1300], 'UNTAMED SD': [150], 'WRATHFUL SD': [205], 'FIGHT CD': [0.08], 'SINGLE DM': [0.03], 'DIRECT DM': [0.02]}
    
    if SOLO:
        champion_sets = list(combinations(champion_solo.items(), NUMBER_OF_CHAMPION_POINTS)) # Get all possible combinations of items from the champion set
    elif DUMMY:
        champion_sets = list(combinations(champion.items(), NUMBER_OF_CHAMPION_POINTS)) # Get all possible combinations of items from the champion set

    champion_combinations = set() # Create a set with all the combinations

    for champion_set in champion_sets:
        champion_combinations.add(tuple((key, value[0]) for key, value in champion_set))

    regular_combinations = list(combinations(regular_sets, 2))

    return mundus, champion_combinations, regular_combinations

def manage_list(build, lst):
    lst.append(build)
    lst.sort(key=lambda x: x[0], reverse=True)

    seen = set()
    result = []
    for setup in lst:
        comparator = setup[1:4]
        if comparator not in seen:
            seen.add(comparator)
            result.append(setup)
        elif comparator in seen:
            result = [x if x[1:4] != comparator or x[0] > setup[0] else setup for x in result]

    return result[:HIGHEST], result[len(result)-1][0]

def calculate(light_pieces, medium_pieces, sets_dict):
    magicka_from_undaunted_passive = UNDAUNTED_MAG_PASSIVE
    if light_pieces > 0 and medium_pieces > 0:
        magicka_from_undaunted_passive += 0.02

    max_magicka = (sets_dict['M']) * (1 + SIPHONING_MAG_PASSIVE + magicka_from_undaunted_passive + sets_dict['MM'])

    spell_damage = (sets_dict['SD']) * (1 + sets_dict['SDM'] + (medium_pieces * MEDIUM_ARMOR_PASSIVE_SD_PER_PIECE))

    player_flat_penetration = (sets_dict['P'] + (light_pieces * LIGHT_ARMOR_PASSIVE_PEN_PER_PIECE))

    if player_flat_penetration > ENEMY_RESISTANCE: # Penetration Cap
        player_flat_penetration = ENEMY_RESISTANCE

    spell_critical_chance = (sets_dict['CC'] + (light_pieces * LIGHT_ARMOR_PASSIVE_CC_PER_PIECE))

    if spell_critical_chance > 1.0: # Crit Chance Cap
        spell_critical_chance = 1.0                        

    spell_critical_damage = (sets_dict['CD'] + (medium_pieces * MEDIUM_ARMOR_PASSIVE_CD_PER_PIECE))

    if spell_critical_damage > 1.25: # Crit Damage Cap
        spell_critical_damage = 1.25

    armor_mitigation = 1 - ((((ENEMY_RESISTANCE - ENEMY_RESISTANCE_DEBUFF) * (1 - PLAYER_PERC_PEN) - player_flat_penetration) / 50000))

    if SOLO:
        average_damage_done = (SKILL_COEFF_MAX_MAG * max_magicka + SKILL_COEFF_SD * spell_damage + sets_dict['F']) * (1 + spell_critical_chance * spell_critical_damage) * (1 + sets_dict['DM']) * (armor_mitigation) * (1 + ENEMY_PERC_DM)
    elif DUMMY: # Elemental Catalyst & Minor Brittle
        average_damage_done = (SKILL_COEFF_MAX_MAG * max_magicka + SKILL_COEFF_SD * spell_damage + sets_dict['F']) * (1 + spell_critical_chance * spell_critical_damage * (1.25)) * (1 + sets_dict['DM']) * (armor_mitigation) * (1 + ENEMY_PERC_DM)

    stats = {'M': int(max_magicka), 'SD': int(spell_damage), 'P': int(player_flat_penetration), 'CC': round(spell_critical_chance, 4), 'CD': round(spell_critical_damage, 4)}
    
    return (average_damage_done, stats)

if __name__ == '__main__':
    t1 = time.time()

    lst = []
    lowest_acceptable_damage = 0.0

    monster_sets, regular_sets = setCollector()
    mundus, champion_combinations, regular_combinations = combinationBuilder(regular_sets)

    buff_debuff_dict = { \
        'M_BERSERK': 'DM', 'M_BREACH': 'P', 'M_BRITTLE': 'CD', 'M_COURAGE': 'SD', 'M_FORCE': 'CD', 'M_PROPHECY': 'CC', 'M_SLAYER': 'DM', 'M_SORCERY': 'SDM', 'M_VULNERABILITY': 'DM', \
        'm_BERSERK': 'DM', 'm_BREACH': 'P', 'm_BRITTLE': 'CD', 'm_COURAGE': 'SD', 'm_FORCE': 'CD', 'm_PROPHECY': 'CC', 'm_SLAYER': 'DM', 'm_SORCERY': 'SDM', 'm_VULNERABILITY': 'DM', \
        'Aggressive Warhorn': 'MM', 'Elemental Catalyst': 'CD'}

    champion_key_dict = {'ARCANE M': 'M', 'UNTAMED SD': 'SD', 'WRATHFUL SD': 'SD', 'BACKSTAB CD': 'CD', 'FIGHT CD': 'CD', 'SINGLE DM': 'DM', 'DIRECT DM': 'DM'}

    # mythic_key_dict = {'Thrassian': [1150.0], 'Mora': [0.0697716895], 'Kilt': [0.0502283105, 0.1]}
    mythic_key_dict = {'Thrassian': [1150.0]}

    default_dict = {'M': MAGICKA, 'SD': SPELL_DAMAGE, 'P': PENETRATION, 'CC': CRITICAL_CHANCE, 'CD': CRITICAL_DAMAGE, 'F': 0.0, 'DM': 0.0, 'MM': 0.0, 'SDM': 0.0}

    if SOLO:
        default_dict['M'] += WITCH_MOTHER_MAG
        active_buffs_debuffs = {'M_PROPHECY', 'M_SORCERY', 'M_BREACH', 'm_FORCE'}
        dict_2 = {'M': 0.0, 'SD': 0.0, 'P': 5948.0, 'CC': 0.12, 'CD': 0.1, 'F': 0.0, 'DM': 0.0, 'MM': 0.0, 'SDM': 0.2}
        mythic_key_dict = {'None': [0.0]}
    elif DUMMY:
        default_dict['M'] += TOMATO_SOUP_MAG
        default_dict['P'] += ASSASSIN_PEN_PASSIVE
        active_buffs_debuffs = {'Aggressive Warhorn', 'Elemental Catalyst', 'M_FORCE', 'm_FORCE', 'M_COURAGE', 'm_COURAGE', 'M_SLAYER', 'M_PROPHECY', 'm_PROPHECY', 'M_SORCERY', 'm_SORCERY', 'm_BERSERK', 'M_BREACH', 'm_BREACH', 'M_VULNERABILITY', 'm_VULNERABILITY', 'm_BRITTLE'}
        dict_2 = {'M': 0.0, 'SD': 645.0, 'P': 0.0, 'CC': 0.18, 'CD': 0.3, 'F': 0.0, 'DM': 0.3, 'MM': 0.1, 'SDM': 0.3} # P is 0.0 bc after debuffs remaining res is 1170 

    base_dict = {k: default_dict[k] + dict_2[k] for k in default_dict.keys()}

    mythic_iter = mythic_key_dict.items()
    mundus_iter = mundus.items()

    for mythic_set, mythic_values in mythic_iter:

        mythic_dict = base_dict.copy()
    
        if mythic_set == 'Thrassian':
            mythic_dict['SD'] += mythic_values[0]
        elif mythic_set == 'Mora':
            mythic_dict['CC'] += mythic_values[0]
        elif mythic_set == 'Kilt':
            mythic_dict['CC'] += mythic_values[0]
            mythic_dict['CD'] += mythic_values[1]

        for champion_set in champion_combinations:

            champion_value_dict = mythic_dict.copy()

            for k, v in champion_set:
                champion_value_dict[champion_key_dict[k]] += v

            for mundus_key, mundus_value in mundus_iter:

                mundus_dict = champion_value_dict.copy()
                mundus_dict[mundus_key] += mundus_value[0]

                for set_M in monster_sets:

                    m1 = set_M.general.items()
                    monster_dict = mundus_dict.copy()

                    for k, v in m1:
                        if k in monster_dict:
                            monster_dict[k] += sum(v)
                        elif k not in active_buffs_debuffs:
                            monster_dict[buff_debuff_dict[k]] += v[0]
                            active_buffs_debuffs.add(k)

                    for set_pair in regular_combinations:
                        
                        s1 = set_pair[0].general.items()
                        s2 = set_pair[1].general.items()
                        s1_name = set_pair[0].name
                        s2_name = set_pair[1].name

                        if 'Dragonguard Elite M' in (s1_name, s2_name):
                            if any('BACKSTAB CD' in k for k, v in champion_set):
                                continue
                            if DUMMY:
                                sets_dict['P'] -= ASSASSIN_PEN_PASSIVE

                        current_buffs_debuffs = active_buffs_debuffs.copy()
                        sets_dict = monster_dict.copy()

                        for d in (s1, s2):
                            for k, v in d:
                                if k in sets_dict:
                                    sets_dict[k] += sum(v)
                                elif k not in current_buffs_debuffs:
                                    sets_dict[buff_debuff_dict[k]] += v[0]
                                    current_buffs_debuffs.add(k)

                        if s1_name[-1] == 'B' or s2_name[-1] == 'B' or (s1_name[-1] != s2_name[-1]):
                            for (damage, stats), (a, b) in zip([calculate(a, b, sets_dict) for a, b in [(2, 5), (1, 6), (0, 7), (7, 0), (6, 1), (5, 2)]], [(2, 5), (1, 6), (0, 7), (7, 0), (6, 1), (5, 2)]):
                                if damage >= lowest_acceptable_damage:
                                    build = (damage, set_pair[0], set_pair[1], set_M, mundus_key, champion_set, a, b, stats, mythic_set)
                                    lst, lowest_acceptable_damage = manage_list(build, lst)

                        elif s1_name[-1] == 'L':
                            for (damage, stats), (a, b) in zip([calculate(a, b, sets_dict) for a, b in [(7, 0), (6, 1), (5, 2)]], [(7, 0), (6, 1), (5, 2)]):
                                if damage >= lowest_acceptable_damage:
                                    build = (damage, set_pair[0], set_pair[1], set_M, mundus_key, champion_set, a, b, stats, mythic_set)
                                    lst, lowest_acceptable_damage = manage_list(build, lst)

                        elif s1_name[-1] == 'M':
                            for (damage, stats), (a, b) in zip([calculate(a, b, sets_dict) for a, b in [(2, 5), (1, 6), (0, 7)]], [(2, 5), (1, 6), (0, 7)]):
                                if damage >= lowest_acceptable_damage:
                                    build = (damage, set_pair[0], set_pair[1], set_M, mundus_key, champion_set, a, b, stats, mythic_set)
                                    lst, lowest_acceptable_damage = manage_list(build, lst)

    rank = 1
    for item in lst:
        print('#' + str(rank))
        print('DPS: ' + str(item[0]))
        print('Mythic: ' + str(item[9]))
        print(str(item[3].name) + ' --> ' + str(item[3].general)) # Monster Set
        print(str(item[1].name) + ' --> ' + str(item[1].general)) # Sets
        print(str(item[2].name) + ' --> ' + str(item[2].general)) # Sets
        print('Mundus: ' + item[4])
        print('Champion: ' + str(item[5]))
        print('Light Armor Pieces: ' + str(item[6]))
        print('Medium Armor Pieces: ' + str(item[7]))
        print('Stats: ' + str(item[8]) + '\n')
        rank += 1

    t2 = time.time()
    print('Time (seconds): ' + str(t2-t1))