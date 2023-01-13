import re
import time
from itertools import combinations

# Predefined
SKILL_COEFF_MAX_MAGICKA = 0.1
SKILL_COEFF_SPELL_DAMAGE = 1.05

# User defined for High Elf
PLAYER_SUM_PERC_DAMAGE_AMP = 0.0 # Minor Berserk for a player dealing 5% more damage
TARGET_SUM_PERC_DAMAGE_TAKEN = 0.0 # Minor Vulnerability for a target taking 5% more damage
SUM_TARGET_DEBUFFS = 0 # Minor Breach for target resistance decreased by 2974
PLAYER_PERC_PEN = 0 # Mace ignores 20% of targets resistance

# BreakDown Stats
BASE_MAGICKA = 12000 # Magicka
ATTR_MAGICKA = 7104
ARMOUR_MAGICKA_ENCHANTS = 4008
HIGH_ELF_MAGICKA_BONUS = 2000
CHAMPION_POINT_MAGICKA = 520
SIPHONING_MAGICKA_PASSIVE = 0.08
UNDAUNTED_MAGICKA_PASSIVE = 0.02

WITCH_MOTHER_MAGICKA = 2856 # Food
GHASTLY_EYE_BOWL_MAGICKA = 4592
SOLITUDE_SALMON_MILLET_SOUP_MAGICKA = 4936

BASE_SPELL_DAMAGE = 1000 # Spell Damage
LEGENDARY_FLAME_STAFF_SPELL_DAMAGE = 1335
JEWELRY_SPELL_DAMAGE_ENCHANTS = 522
FLAME_STAFF_DAMAGE_ENCHANT_WITH_INFUSED = 452
HIGH_ELF_SPELL_DAMAGE_BONUS = 258
MEDIUM_ARMOR_PASSIVE_SPELL_DAMAGE_PER_PIECE = 0.02

BASE_SPELL_CRITICAL_CHANCE = 0.1 # Spell Crit Chance
CHAMPION_POINT_CRITICAL_CHANCE = 0.014
LEGENDARY_FLAME_STAFF_CRITICAL_CHANCE = 0.072
LIGHT_ARMOR_PASSIVE_CRITICAL_CHANCE_PER_PIECE = 0.01

BASE_SPELL_CRITICAL_DAMAGE = 0.5 # Spell Crit Damage
ASSASSIN_CRITICAL_DAMAGE_PASSIVE = 0.1
MEDIUM_ARMOR_PASSIVE_CRITICAL_DAMAGE_PER_PIECE = 0.02

ASSASSIN_PENETRATION_PASSIVE = 2974 # Flat Penetration
CHAMPION_POINT_PENETRATION = 700
LIGHT_ARMOR_PASSIVE_PENETRATION_PER_PIECE = 939

# Buffs
MAJOR_BERSERK = 0.1 # DM
MAJOR_COURAGE = 430 # D
MAJOR_FORCE = 0.2 # CD
MAJOR_PROPHECY = 0.12 # C | Potion / Inner Light
MAJOR_SLAYER = 0.1 # DM
MAJOR_SORCERY = 0.2 # SDM | Potion / Entropy
MINOR_BERSERK = 0.05 # DM
MINOR_COURAGE = 215 # D
MINOR_FORCE = 0.1 # CD | Channeled Acceleraton / Barbed Trap
MINOR_PROPHECY = 0.06 # C
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
MAGICKA = BASE_MAGICKA + ATTR_MAGICKA + ARMOUR_MAGICKA_ENCHANTS + HIGH_ELF_MAGICKA_BONUS + CHAMPION_POINT_MAGICKA
SPELL_DAMAGE = BASE_SPELL_DAMAGE + LEGENDARY_FLAME_STAFF_SPELL_DAMAGE + JEWELRY_SPELL_DAMAGE_ENCHANTS + HIGH_ELF_SPELL_DAMAGE_BONUS + FLAME_STAFF_DAMAGE_ENCHANT_WITH_INFUSED
PENETRATION = CHAMPION_POINT_PENETRATION
CRITICAL_CHANCE = BASE_SPELL_CRITICAL_CHANCE + CHAMPION_POINT_CRITICAL_CHANCE + LEGENDARY_FLAME_STAFF_CRITICAL_CHANCE
CRITICAL_DAMAGE = BASE_SPELL_CRITICAL_DAMAGE + ASSASSIN_CRITICAL_DAMAGE_PASSIVE

# User Settings
SOLO = False
DUMMY = True
ENEMY_RESISTANCE = 1170 # 18200 max enemy resistance | Dummy resistance is 1170
NUMBER_OF_CHAMPION_POINTS = 4
HIGHEST = 10

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

def user_settings():
    if SOLO:
        print('\nSolo Build\n')
    elif DUMMY:
        print('\nDummy Parse\n')

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
    mundus = {'M': [3309], 'D': [389], 'C': [0.09894977168949772], 'CD': [0.17], 'P': [4489]} # Values with 7 pieces of Divines
    champion = {'ARCANE M': [1300], 'UNTAMED D': [150], 'WRATHFUL D': [205], 'BACKSTAB CD': [0.1], 'FIGHT CD': [0.08], 'SINGLE DM': [0.03], 'DIRECT DM': [0.02]}
    champion_solo = {'ARCANE M': [1300], 'UNTAMED D': [150], 'WRATHFUL D': [205], 'FIGHT CD': [0.08], 'SINGLE DM': [0.03], 'DIRECT DM': [0.02]}
    
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

def monster_armor_test(light_pieces, medium_pieces, sets_dict):
    magicka_from_undaunted_passive = UNDAUNTED_MAGICKA_PASSIVE
    if light_pieces > 0 and medium_pieces > 0:
        magicka_from_undaunted_passive += 0.02

    maximum_magicka = (sets_dict['M']) * (1 + SIPHONING_MAGICKA_PASSIVE + magicka_from_undaunted_passive + sets_dict['MM'])

    spell_damage = (sets_dict['D']) * (1 + sets_dict['SDM'] + (medium_pieces * MEDIUM_ARMOR_PASSIVE_SPELL_DAMAGE_PER_PIECE))

    player_flat_penetration = (sets_dict['P'] + (light_pieces * LIGHT_ARMOR_PASSIVE_PENETRATION_PER_PIECE))

    if player_flat_penetration > ENEMY_RESISTANCE: # Penetration Cap
        player_flat_penetration = ENEMY_RESISTANCE

    spell_critical_chance = (sets_dict['C'] + (light_pieces * LIGHT_ARMOR_PASSIVE_CRITICAL_CHANCE_PER_PIECE))

    if spell_critical_chance > 1.0: # Crit Chance Cap
        spell_critical_chance = 1.0                        

    spell_critical_damage = (sets_dict['CD'] + (medium_pieces * MEDIUM_ARMOR_PASSIVE_CRITICAL_DAMAGE_PER_PIECE))

    if spell_critical_damage > 1.25: # Crit Damage Cap
        spell_critical_damage = 1.25

    armor_mitigation = 1 - ((((ENEMY_RESISTANCE - SUM_TARGET_DEBUFFS) * (1 - PLAYER_PERC_PEN) - player_flat_penetration) / 50000))

    average_damage_done = (SKILL_COEFF_MAX_MAGICKA * maximum_magicka + SKILL_COEFF_SPELL_DAMAGE * spell_damage + sets_dict['F']) * (1 + spell_critical_chance * spell_critical_damage) * (1 + sets_dict['DM']) * (armor_mitigation) * (1 + TARGET_SUM_PERC_DAMAGE_TAKEN)

    stats = {'M': int(maximum_magicka), 'D': int(spell_damage), 'P': int(player_flat_penetration), 'C': round(spell_critical_chance, 4), 'CD': round(spell_critical_damage, 4)}
    
    return (average_damage_done, stats)

if __name__ == '__main__':
    t1 = time.time()

    lst = []
    lowest_acceptable_damage = 0.0

    buff_debuff_dict = { \
        'M_BERSERK': 'DM', 'M_BREACH': 'P', 'M_BRITTLE': 'CD', 'M_COURAGE': 'D', 'M_FORCE': 'CD', 'M_PROPHECY': 'C', 'M_SLAYER': 'DM', 'M_SORCERY': 'SDM', 'M_VULNERABILITY': 'DM', \
        'm_BERSERK': 'DM', 'm_BREACH': 'P', 'm_BRITTLE': 'CD', 'm_COURAGE': 'D', 'm_FORCE': 'CD', 'm_PROPHECY': 'C', 'm_SLAYER': 'DM', 'm_SORCERY': 'SDM', 'm_VULNERABILITY': 'DM', \
        'Aggressive Warhorn': 'MM', 'Elemental Catalyst': 'CD'}

    user_settings()
    monster_sets, regular_sets = setCollector()
    mundus, champion_combinations, regular_combinations = combinationBuilder(regular_sets)

    mundus_iter = mundus.items()

    for champion_set in champion_combinations:

        champion_key_dict = {'ARCANE M': 'M', 'UNTAMED D': 'D', 'WRATHFUL D': 'D', 'BACKSTAB CD': 'CD', 'FIGHT CD': 'CD', 'SINGLE DM': 'DM', 'DIRECT DM': 'DM'}
        champion_value_dict = {'M': MAGICKA, 'D': SPELL_DAMAGE, 'P': PENETRATION, 'C': CRITICAL_CHANCE, 'CD': CRITICAL_DAMAGE, 'F': 0.0, 'DM': 0.0, 'MM': 0.0, 'SDM': 0.0}

        if SOLO:
            champion_value_dict['M'] += WITCH_MOTHER_MAGICKA
        elif DUMMY:
            champion_value_dict['M'] += SOLITUDE_SALMON_MILLET_SOUP_MAGICKA
            champion_value_dict['P'] += ASSASSIN_PENETRATION_PASSIVE

        for k, v in champion_set:
            champion_value_dict[champion_key_dict[k]] += v

        for mundus_key, mundus_value in mundus_iter:

            mundus_dict = champion_value_dict.copy()
            mundus_dict[mundus_key] += mundus_value[0]

            for set_M in monster_sets:

                m1 = set_M.general.items()

                dict_1 = mundus_dict.copy()
                keys = dict_1.keys()

                if SOLO:
                    active_buffs_debuffs = {'M_PROPHECY', 'M_SORCERY', 'M_BREACH', 'm_FORCE'}
                    dict_2 = {'M': 0.0, 'D': 0.0, 'P': 5948.0, 'C': 0.12, 'CD': 0.1, 'F': 0.0, 'DM': 0.0, 'MM': 0.0, 'SDM': 0.2}
                elif DUMMY:
                    active_buffs_debuffs = {'Aggressive Warhorn', 'Elemental Catalyst', 'M_FORCE', 'm_FORCE', 'M_COURAGE', 'm_COURAGE', 'M_SLAYER', \
                        'M_PROPHECY', 'm_PROPHECY', 'M_SORCERY', 'm_SORCERY', 'm_BERSERK', 'M_BREACH', 'm_BREACH', 'M_VULNERABILITY', 'm_VULNERABILITY', 'm_BRITTLE'}
                    dict_2 = {'M': 0.0, 'D': 645.0, 'P': 0.0, 'C': 0.18, 'CD': 0.55, 'F': 0.0, 'DM': 0.3, 'MM': 0.1, 'SDM': 0.3} # P is 0.0 bc after debuffs remaining res is 1170
                
                monster_dict = {k: dict_1[k] + dict_2[k] for k in keys}

                for k, v in m1:
                    if k in monster_dict:
                        monster_dict[k] += sum(v)
                    elif k in buff_debuff_dict and k not in active_buffs_debuffs:
                        monster_dict[buff_debuff_dict[k]] += v[0]
                        active_buffs_debuffs.add(k)

                for set_pair in regular_combinations:
                    set_1, set_2 = set_pair

                    s1 = set_1.general.items()
                    s2 = set_2.general.items()

                    current_buffs_debuffs = active_buffs_debuffs.copy()

                    sets_dict = monster_dict.copy()

                    for d in (s1, s2):
                        for k, v in d:
                            if k in sets_dict:
                                sets_dict[k] += sum(v)
                            elif k in buff_debuff_dict and k not in current_buffs_debuffs:
                                sets_dict[buff_debuff_dict[k]] += v[0]
                                current_buffs_debuffs.add(k)

                    if 'Dragonguard Elite M' in set_1.name or 'Dragonguard Elite M' in set_2.name:
                        sets_dict['P'] -= ASSASSIN_PENETRATION_PASSIVE
                        skip = False
                        for k, v in champion_set:
                            if 'BACKSTAB CD' in k:
                                skip = True
                                break
                        if skip:
                            break

                    if set_1.name.endswith('B') or set_2.name.endswith('B') or (set_1.name.endswith('L') and set_2.name.endswith('M')) or (set_1.name.endswith('M') and set_2.name.endswith('L')):
                        
                        average_damage_done_lst = [monster_armor_test(a, b, sets_dict) for a, b in [(2, 5), (1, 6), (0, 7), (7, 0), (6, 1), (5, 2)]]

                        for (damage, stats), (a, b) in zip(average_damage_done_lst, [(2, 5), (1, 6), (0, 7), (7, 0), (6, 1), (5, 2)]):
                            if 'Molag Kena &' in set_M.name:
                                damage -= (damage/6)
                            if damage >= lowest_acceptable_damage:
                                build = (damage, set_1, set_2, set_M, mundus_key, champion_set, a, b, stats)
                                lst, lowest_acceptable_damage = manage_list(build, lst)

                    elif set_1.name.endswith('L') and set_2.name.endswith('L'):

                        average_damage_done_lst = [monster_armor_test(a, b, sets_dict) for a, b in [(7, 0), (6, 1), (5, 2)]]

                        for (damage, stats), (a, b) in zip(average_damage_done_lst, [(7, 0), (6, 1), (5, 2)]):
                            if 'Molag Kena &' in set_M.name:
                                damage -= (damage/6)
                            if damage >= lowest_acceptable_damage:
                                build = (damage, set_1, set_2, set_M, mundus_key, champion_set, a, b, stats)
                                lst, lowest_acceptable_damage = manage_list(build, lst)

                    elif set_1.name.endswith('M') and set_2.name.endswith('M'):

                        average_damage_done_lst = [monster_armor_test(a, b, sets_dict) for a, b in [(2, 5), (1, 6), (0, 7)]]

                        for (damage, stats), (a, b) in zip(average_damage_done_lst, [(2, 5), (1, 6), (0, 7)]):
                            if 'Molag Kena &' in set_M.name:
                                damage -= (damage/6)
                            if damage >= lowest_acceptable_damage:
                                build = (damage, set_1, set_2, set_M, mundus_key, champion_set, a, b, stats)
                                lst, lowest_acceptable_damage = manage_list(build, lst)

    rank = 1
    for item in lst:
        print('#' + str(rank))
        print('DPS: ' + str(item[0]))
        print(item[3].name) # Monster Set
        print(item[3].general)
        print(item[1].name) # Sets
        print(item[1].general)
        print(item[2].name)
        print(item[2].general)
        print('Mundus: ' + item[4])
        print('Champion: ' + str(item[5]))
        print('Light Armor Pieces: ' + str(item[6]))
        print('Medium Armor Pieces: ' + str(item[7]))
        print('Stats: ' + str(item[8]) + '\n')
        rank += 1

    t2 = time.time()
    print('Time (seconds): ' + str(t2-t1))