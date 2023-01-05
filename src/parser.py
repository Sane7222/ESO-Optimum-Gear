import requests
from bs4 import BeautifulSoup

# Open the HTML file
with open('../data/parsed_html.html', 'r') as f:
    html = f.read()

# Parse the HTML content
soup = BeautifulSoup(html, 'html.parser')

# Find all the `td` elements
tds = soup.find_all('td')

# Used for removing unknown sets
wasUnknown = False

# Exclude the text from the elements with the style 'padding-right: 0; vertical-align: middle'
for td in tds[:]:
    if wasUnknown: # Previous was Unknown so we remove its description
        td.decompose()
        wasUnknown = False
        continue

    if 'padding-right: 0; vertical-align: middle' in td.get('style', []): # Ignore the repeat name and type
        td.decompose()
        continue

    Medium = False
    Light = False

    # Find the anchor element that contains the URL
    anchor = td.find('a')

    if anchor:
        # Extract the URL from the anchor element
        url = anchor['href']

        if not 'sets' in url:
            continue

        print(url)

        # Send an HTTP GET request to the website's URL
        response = requests.get(url)

        # Check the response status code
        if response.status_code == 200:
            # Parse the HTML content
            new_soup = BeautifulSoup(response.text, 'html.parser')

            infos = new_soup.find_all('div')

            for info in infos:
                if 'float-right' and 'text-right' in info.get('class', []):
                    spans = info.find_all('span')
                    for span in spans:
                        if 'badge' and 'badge-info' in span.get('class', []):
                            if span.text == 'Light Armor':
                                Light = True
                            elif span.text == 'Medium Armor':
                                Medium = True

    small = td.find('small')
    if small:
        if small.string != 'Monster Set':
            if small.string == 'Unknown' or (not Light and not Medium): # Remove Unknowns
                wasUnknown = True
                td.decompose()
                continue
            if Light and Medium:
                small.string = ' B'
            elif Light:
                small.string = ' L'
            elif Medium:
                small.string = ' M'
        else: small.string = ' &'

    strongs = td.find_all('strong')
    for strong in strongs:
        strong.string = '\r\n' + strong.string

# Open the other file for reading
with open('../data/sets.txt', 'r') as other_file:
    # Read the contents of the other file into a set
    other_file_set = set(other_file.read().split('\n'))

# Open the sets.txt file for writing
with open('../data/sets.txt', 'a') as f:
    # Write the text of each element to the file, if it is not in the other file
    t = False
    for td in tds:
        string = td.text.lstrip().replace('\n', '')
        if string and string not in other_file_set and not string.startswith('(') and not t: # New Set
            t = True
            f.write(string)
        elif t and string.startswith('('):
            string = string.replace('(', '\n(')
            f.write(string + '\n')
        else:
            t = False