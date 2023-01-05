def probabilityPerSecond(p, attacks_per_second): 
    total = 0
    for n in range(1, attacks_per_second + 1): # + 1 to include the number of attacks per second
        total += p * (1 - p) ** (n - 1)

    print(total)
    return total

def averageDamagePerSecond(probability):
    duration = 1  # The duration of the effect is 5 seconds
    cooldown = 1  # The cooldown period is 10 seconds
    damage_per_second = 400  # The average damage dealt per second is 259

    dps = (probability * damage_per_second * duration) / cooldown

    print(dps)


if __name__ == '__main__':
    averageDamagePerSecond(probabilityPerSecond(0.4, 1))