ESO DPS Calculator

Last Set in parsed_Sets.txt:
    Zen's Redress

Last Set looked at:
    Kinras's Wrath M

File Workflow:
    scraper.py
        Scrapes https://eso-hub.com/en/sets/all for their html and stores it into parsed_html.html
    parser.py
        Parses html file and stores meaningful information into sets.txt
    set_parser.py
        Organizes and parses each set. Excludes sets from excluded_sets.txt and stores parsed information into parsed_sets.txt
    dpsCalc.py
        Retrieves information from parsed_sets.txt and calculates all possible combinations of gear to find the highest damage
    
    excluded_sets.txt
        Removed anything not damage enhancing (Heroism Doesn't count as damage enhancing)
        Removed if Alchemical Poison / Maximum Health / Health based / Bash / Block / Dodge / Shield / Break / Blink / Charge / Leap / Teleport / Pull proc'd
        Removed if already grants a buff that is easy to obtain, or clearly not good

To-Do:
    Test for Light armor and/or Medium armor in Regular Sets
    Make DPS Calculator open final_sets
    Edit DPS Calculator recognize:
        F: Flat Damage Per Second, FLOAT
        B: Minor Beserk player damage +5%, FLOAT
        CD: For regular sets /100, FLOAT
        DM: Damage Multiplier, FLOAT
    Sets that need revision:
        Molag Kena &
        Dragonguard Elite M

    Add additional bonuses for each set | Get to a per second basis
    
    Example: 1000 damage over 10 seconds 20 second cooldown
        10 / 20 = 0.5
        0.5 * 1000 = 500
        500 / 10 = 50

    Example: 100 damage per second for 10 seconds 10 second cooldown
        10 / 10 = 1
        1 * 100 = 100

    Example: 70 Weapon and Spell Damage for 12 seconds 24 second cooldown
        12 / 24 = 0.5
        70 * 0.5 = 35

    Example: 10% chance to proc per second 259 damage per second for 5 seconds 10 second cooldown
        1 - 0.1 = 0.9
        10 * 1 + 0.9 = 19
        5 / 19 = 0.26
        0.26 * 259 = 68
