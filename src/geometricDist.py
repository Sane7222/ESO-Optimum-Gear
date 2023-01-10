def probabilityPerSecond(p, attacks_per_second): 
    total = 0
    for n in range(1, attacks_per_second + 1): # + 1 to include the number of attacks per second
        total += p * (1 - p) ** (n - 1)

    print(total)
    return total

def averageDamagePerSecond(probability):
    duration = 7  # The duration of the effect
    cooldown = 23  # The cooldown period
    damage_per_second = 10  # The damage dealt per second

    dps = (probability * damage_per_second * duration) / cooldown

    print(dps)


if __name__ == '__main__':
    averageDamagePerSecond(probabilityPerSecond(1.0, 1))

'''
Example: 1000 damage over 10 seconds 20 second cooldown
    duration = 10               | 1
    cooldown = 20
    damage_per_second = 100     | 1000

Example: Dealing damage has a 10% chance to activate an ability that deals 100 damage per second for 5 seconds 10 second cooldown
    duration = 5                | 1
    cooldown = 10
    damage_per_second = 100     | 500
    
    3 DoT + Light Attack + Spammable

    attacks_per_second = 5
    p = 0.1
'''