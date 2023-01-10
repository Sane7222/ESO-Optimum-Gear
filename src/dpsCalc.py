import re
from itertools import combinations
import builtins

# Predefined
DUMMY_HEALTH = 2002944
SKILL_COEFF_MAX_MAGICKA = 0.1
SKILL_COEFF_SPELL_DAMAGE = 1.05
ENEMY_RESISTANCE = 18200 # 18200 max enemy resistance | Dummy resistance is 1170

# User defined for High Elf
PLAYER_SUM_PERC_DAMAGE_AMP = 0.0 # Minor Berserk for a player dealing 5% more damage
TARGET_SUM_PERC_DAMAGE_TAKEN = 0.0 # Minor Vulnerability for a target taking 5% more damage
SUM_TARGET_DEBUFFS = 0 # Minor Breach for target resistance decreased by 2974
PLAYER_PERC_PEN = 0 # Mace ignores 20% of targets resistance

# BreakDown Stats
BASE_MAGICKA = 12000 # Magicka
ATTR_MAGICKA = 7104
ARMOUR_MAGICKA_ENCHANTS = 4008
WITCH_MOTHER_MAGICKA = 2856
HIGH_ELF_MAGICKA_BONUS = 2000
CHAMPION_POINT_MAGICKA = 520
SIPHONING_MAGICKA_PASSIVE = 0.08
UNDAUNTED_MAGICKA_PASSIVE = 0.02

BASE_SPELL_DAMAGE = 1000 # Spell Damage
LEGENDARY_FLAME_STAFF_SPELL_DAMAGE = 1335
JEWELRY_SPELL_DAMAGE_ENCHANTS = 522
FLAME_STAFF_DAMAGE_ENCHANT_WITH_INFUSED = 452
HIGH_ELF_SPELL_DAMAGE_BONUS = 258
MAJOR_SORCERY = 0.2 # Potion or Entropy
MEDIUM_ARMOR_PASSIVE_SPELL_DAMAGE_PER_PIECE = 0.02

BASE_SPELL_CRITICAL_CHANCE = 0.1 # Spell Crit Chance
CHAMPION_POINT_CRITICAL_CHANCE = 0.014
LEGENDARY_FLAME_STAFF_CRITICAL_CHANCE = 0.072
MAJOR_PROPHECY = 0.12 # Potion or Inner Light
LIGHT_ARMOR_PASSIVE_CRITICAL_CHANCE_PER_PIECE = 0.01

BASE_SPELL_CRITICAL_DAMAGE = 0.5 # Spell Crit Damage
ASSASSIN_CRITICAL_DAMAGE_PASSIVE = 0.1
MINOR_FORCE = 0.1 # Barb Trap or Channeled Acceleration
MEDIUM_ARMOR_PASSIVE_CRITICAL_DAMAGE_PER_PIECE = 0.02

ASSASSIN_PENETRATION_PASSIVE = 2974 # Flat Penetration
CHAMPION_POINT_PENETRATION = 700
LIGHT_ARMOR_PASSIVE_PENETRATION_PER_PIECE = 939

# Pre-computational values
MAGICKA = BASE_MAGICKA + ATTR_MAGICKA + ARMOUR_MAGICKA_ENCHANTS + WITCH_MOTHER_MAGICKA + HIGH_ELF_MAGICKA_BONUS + CHAMPION_POINT_MAGICKA
SPELL_DAMAGE = BASE_SPELL_DAMAGE + LEGENDARY_FLAME_STAFF_SPELL_DAMAGE + JEWELRY_SPELL_DAMAGE_ENCHANTS + HIGH_ELF_SPELL_DAMAGE_BONUS + FLAME_STAFF_DAMAGE_ENCHANT_WITH_INFUSED
PENETRATION = ASSASSIN_PENETRATION_PASSIVE + CHAMPION_POINT_PENETRATION
CRITICAL_CHANCE = BASE_SPELL_CRITICAL_CHANCE + CHAMPION_POINT_CRITICAL_CHANCE + LEGENDARY_FLAME_STAFF_CRITICAL_CHANCE + MAJOR_PROPHECY
CRITICAL_DAMAGE = BASE_SPELL_CRITICAL_DAMAGE + ASSASSIN_CRITICAL_DAMAGE_PASSIVE + MINOR_FORCE

# User Settings
TIME_COMPLEXITY_INFORMATION = True
NUMBER_OF_CHAMPION_POINTS = 2
SOLO = True

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
    other_sets = []

    current_set = None # Initialize a variable to store the current set
    parsing_general = False # Initialize a variable to track whether we are currently parsing general information for a set

    for line in lines:
        if not line: # If the line is empty, set parsing_general to False
            parsing_general = False
        elif not parsing_general:
            current_set = Set(line) # If we are not parsing general information and the line is not empty, create a new Set object with the line as its name

            if current_set.name.endswith("&"): # If the name of the set ends with an ampersand (&), add it to the monster_sets list
                monster_sets.append(current_set)
            else: # Otherwise, add it to the other_sets list
                other_sets.append(current_set)

        else:
            key, value = line.split(": ") # If we are parsing general information and the line is not empty, split the line into the key and value
            numbers = re.findall(r"\[([\d., ]+)\]", value) # Use a regular expression to match the pattern "[number]" or "[number, number]" and extract the numbers
            numbers = [int(x) if '.' not in x else float(x) for x in numbers[0].split(", ")] # Split the numbers on the comma and convert them to integers or floats

            for x in numbers:
                current_set.add_general(key, x)

        parsing_general = line.endswith(tuple("]&BLM")) # Set parsing_general to True if the line ends with any of ], &, B, L, M

    return monster_sets, other_sets

def combinationBuilder(other_sets):
    mundus = {'M': [3309], 'D': [389], 'C': [0.09894977168949772], 'CD': [0.17], 'P': [4489]} # Values with 7 pieces of Divines
    champion = {'ARCANE M': [1300], 'UNTAMED D': [150], 'WRATHFUL D': [205], 'BACKSTAB CD': [0.1], 'FIGHT CD': [0.08], 'SINGLE S': [0.03], 'DIRECT S': [0.02]}
    champion_solo = {'ARCANE M': [1300], 'UNTAMED D': [150], 'WRATHFUL D': [205], 'FIGHT CD': [0.08], 'SINGLE S': [0.03], 'DIRECT S': [0.02]}
    
    if SOLO:
        combos = list(combinations(champion_solo.items(), NUMBER_OF_CHAMPION_POINTS)) # Get all possible combinations of items from the champion set
    else:
        combos = list(combinations(champion.items(), NUMBER_OF_CHAMPION_POINTS)) # Get all possible combinations of items from the champion set

    champion_combos = builtins.set() # Create a set with all the combinations

    for combo in combos:
        champion_combos.add(tuple((key, value[0]) for key, value in combo))

    set_combos = list(combinations(other_sets, 2))

    return mundus, champion_combos, set_combos

def monster_armor_test(light_pieces, medium_pieces, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp):
    magicka_from_undaunted_passive = UNDAUNTED_MAGICKA_PASSIVE
    if light_pieces > 0 and medium_pieces > 0:
        magicka_from_undaunted_passive += 0.02

    maximum_magicka = (magicka_test) * (1 + SIPHONING_MAGICKA_PASSIVE + magicka_from_undaunted_passive)

    spell_damage = (spell_damage_test) * (1 + MAJOR_SORCERY + (medium_pieces * MEDIUM_ARMOR_PASSIVE_SPELL_DAMAGE_PER_PIECE))

    player_flat_penetration = (penetration_test + (light_pieces * LIGHT_ARMOR_PASSIVE_PENETRATION_PER_PIECE))

    if player_flat_penetration > ENEMY_RESISTANCE: # Penetration Cap
        player_flat_penetration = ENEMY_RESISTANCE

    spell_critical_chance = (spell_critical_chance_test + (light_pieces * LIGHT_ARMOR_PASSIVE_CRITICAL_CHANCE_PER_PIECE))

    if spell_critical_chance > 1.0: # Crit Chance Cap
        spell_critical_chance = 1.0                        

    spell_critical_damage = (spell_critical_damage_test + (medium_pieces * MEDIUM_ARMOR_PASSIVE_CRITICAL_DAMAGE_PER_PIECE))

    if spell_critical_damage > 1.25: # Crit Damage Cap
        spell_critical_damage = 1.25

    armor_mitigation = 1 - ((((ENEMY_RESISTANCE - SUM_TARGET_DEBUFFS) * (1 - PLAYER_PERC_PEN) - player_flat_penetration) / 50000))

    average_damage_done = (SKILL_COEFF_MAX_MAGICKA * maximum_magicka + SKILL_COEFF_SPELL_DAMAGE * spell_damage + flat_damage_test) * (1 + spell_critical_chance * spell_critical_damage) * (1 + sum_of_player_percent_damage_amp) * (armor_mitigation) * (1 + TARGET_SUM_PERC_DAMAGE_TAKEN)
    
    return average_damage_done

def update_best(average_damage_done, set1, set2, Mset, key, combo, light, medium):
    global highest_damage
    global setA
    global setB
    global MonsterSet
    global Mundus
    global ChampionCombo
    global LightPieces
    global MediumPieces

    highest_damage = average_damage_done
    setA = set1
    setB = set2
    MonsterSet = Mset
    Mundus = key
    ChampionCombo = combo
    LightPieces = light
    MediumPieces = medium

if __name__ == '__main__':

    highest_damage = 0
    setA = None
    setB = None
    MonsterSet = None
    Mundus = None
    ChampionCombo = None
    LightPieces = 0
    MediumPieces = 0

    monster_sets, other_sets = setCollector()
    mundus, champion_combos, set_combos = combinationBuilder(other_sets)

    if TIME_COMPLEXITY_INFORMATION:
        print('Monster Sets = ' + str(len(monster_sets)))
        print('Mundus Stones = ' + str(len(mundus)))
        print('Champion Point Combinations = ' + str(len(champion_combos)))
        print('Regular Set Combinations = ' + str(len(set_combos)))

    for combo in champion_combos:

        magicka_champion = 0
        spell_damage_champion = 0.0
        spell_crit_damage_champion = 0.0
        percent_damage_amp_champion = 0.0

        for ck, cv in combo:
            if ck == 'ARCANE M':
                magicka_champion += cv
            elif ck == 'UNTAMED D' or ck == 'WRATHFUL D':
                spell_damage_champion += cv
            elif ck == 'SINGLE S' or ck == 'DIRECT S':
                percent_damage_amp_champion += cv
            elif ck == 'BACKSTAB CD' or ck == 'FIGHT CD':
                spell_crit_damage_champion += cv

        mund = mundus.items()
        for key, value in mund:

            magicka_mundus = 0
            spell_damage_mundus = 0.0
            penetration_mundus = 0
            spell_crit_chance_mundus = 0.0
            spell_crit_damage_mundus = 0.0

            if key == 'M':
                magicka_mundus += value[0]
            elif key == 'D':
                spell_damage_mundus += value[0]
            elif key == 'P':
                penetration_mundus += value[0]
            elif key == 'C':
                spell_crit_chance_mundus += value[0]
            elif key == 'CD':
                spell_crit_damage_mundus += value[0]

            for Mset in monster_sets:

                slayer_bonus_from_sets = False
                monster_slayer_bonus = False

                magicka_monster = 0
                spell_damage_monster = 0.0
                penetration_monster = 0
                spell_crit_chance_monster = 0.0
                spell_crit_damage_monster = 0.0
                percent_damage_amp_monster = 0.0
                flat_damage_monster = 0.0
                damage_multiplier_monster = 0.0

                m1 = Mset.general.items()
                for k, v in m1:
                    if k == 'M':
                        magicka_monster += sum(v)
                    elif k == 'D':
                        spell_damage_monster += sum(v)
                    elif k == 'P':
                        penetration_monster += sum(v)
                    elif k == 'C':
                        spell_crit_chance_monster += sum(v)
                    elif k == 'CD':
                        spell_crit_damage_monster += sum(v)
                    elif k == 'S' and slayer_bonus_from_sets == False:
                        slayer_bonus_from_sets = True
                        monster_slayer_bonus = True
                        percent_damage_amp_monster += 0.05
                    elif k == 'F':
                        flat_damage_monster += sum(v)
                    elif k == 'DM':
                        damage_multiplier_monster += sum(v)

                for set_pair in set_combos:
                    set1, set2 = set_pair

                    sum_of_player_percent_damage_amp = PLAYER_SUM_PERC_DAMAGE_AMP + damage_multiplier_monster

                    if monster_slayer_bonus:
                        slayer_bonus_from_sets = True
                    else:
                        slayer_bonus_from_sets = False

                    magicka_sets = 0
                    spell_damage_sets = 0.0
                    penetration_sets = 0
                    spell_crit_chance_sets = 0.0
                    spell_crit_damage_sets = 0.0
                    flat_damage_sets = 0.0
                    damage_multiplier_sets = 0.0

                    s1 = set1.general.items()
                    s2 = set2.general.items()

                    for d in (s1, s2):
                        for k, v in d:
                            if k == 'M':
                                magicka_sets += sum(v)
                            elif k == 'D':
                                spell_damage_sets += sum(v)
                            elif k == 'P':
                                penetration_sets += sum(v)
                            elif k == 'C':
                                spell_crit_chance_sets += sum(v)
                            elif k == 'CD':
                                spell_crit_damage_sets += sum(v)
                            elif k == 'S' and slayer_bonus_from_sets == False:
                                slayer_bonus_from_sets = True
                                sum_of_player_percent_damage_amp += 0.05
                            elif k == 'F':
                                flat_damage_sets += sum(v)
                            elif k == 'DM':
                                damage_multiplier_sets += sum(v)

                    sum_of_player_percent_damage_amp += percent_damage_amp_champion
                    sum_of_player_percent_damage_amp += percent_damage_amp_monster
                    sum_of_player_percent_damage_amp += damage_multiplier_sets

                    magicka_test = MAGICKA + magicka_sets + magicka_monster + magicka_mundus + magicka_champion
                    spell_damage_test = SPELL_DAMAGE + spell_damage_sets + spell_damage_monster + spell_damage_mundus + spell_damage_champion
                    penetration_test = PENETRATION + penetration_sets + penetration_monster + penetration_mundus
                    spell_critical_chance_test = CRITICAL_CHANCE + spell_crit_chance_sets + spell_crit_chance_monster + spell_crit_chance_mundus
                    spell_critical_damage_test = CRITICAL_DAMAGE + spell_crit_damage_sets + spell_crit_damage_monster + spell_crit_damage_mundus + spell_crit_damage_champion
                    flat_damage_test = flat_damage_sets + flat_damage_monster

                    if SOLO:
                        penetration_test -= ASSASSIN_PENETRATION_PASSIVE

                    if set1.name.endswith('B') or set2.name.endswith('B') or (set1.name.endswith('L') and set2.name.endswith('M')) or (set1.name.endswith('M') and set2.name.endswith('L')):
                        average_damage_done = monster_armor_test(2, 5, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 2, 5)

                        average_damage_done = monster_armor_test(1, 6, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 1, 6)

                        average_damage_done = monster_armor_test(0, 7, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 0, 7)

                        average_damage_done = monster_armor_test(7, 0, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 7, 0)

                        average_damage_done = monster_armor_test(6, 1, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 6, 1)

                        average_damage_done = monster_armor_test(5, 2, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 5, 2)

                    elif set1.name.endswith('L') and set2.name.endswith('L'):
                        average_damage_done = monster_armor_test(7, 0, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 7, 0)

                        average_damage_done = monster_armor_test(6, 1, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 6, 1)

                        average_damage_done = monster_armor_test(5, 2, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 5, 2)

                    elif set1.name.endswith('M') and set2.name.endswith('M'):
                        average_damage_done = monster_armor_test(2, 5, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 2, 5)

                        average_damage_done = monster_armor_test(1, 6, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 1, 6)

                        average_damage_done = monster_armor_test(0, 7, magicka_test, spell_damage_test, penetration_test, spell_critical_chance_test, spell_critical_damage_test, flat_damage_test, sum_of_player_percent_damage_amp)
                        if average_damage_done >= highest_damage:
                            update_best(average_damage_done, set1, set2, Mset, key, combo, 0, 7)

    print(highest_damage)
    print(setA.name)
    print(setA.general)
    print(setB.name)
    print(setB.general)
    print(MonsterSet.name)
    print(MonsterSet.general)
    print('Mundus: ' + Mundus)
    print(ChampionCombo)
    print('Light Armor Pieces: ')
    print(LightPieces)
    print('Medium Armor Pieces: ')
    print(MediumPieces)
