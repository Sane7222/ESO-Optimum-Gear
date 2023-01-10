ESO DPS Calculator

File Workflow:
    scraper.py
        Scrapes https://eso-hub.com/en/sets/all for their html
        Parses html and stores meaningful information into sets.txt
    set_parser.py
        Organizes and parses each set. Excludes sets from excluded_sets.txt and stores parsed information into parsed_sets.txt
    dpsCalc.py
        Retrieves information from parsed_sets.txt and calculates all possible combinations of gear to find the highest damage
    
    excluded_sets.txt
        Removed if:
            Not damage enhancing
            Alchemical Poison / Maximum Health / Health based / Bash / Block / Dodge / Shield / Break / Blink / Charge / Leap / Teleport / Pull proc'd
            Grants a buff that is easy to obtain, or not as good as another set in terms of stats
