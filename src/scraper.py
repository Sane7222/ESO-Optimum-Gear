import requests
from bs4 import BeautifulSoup

def scrape(url):
    # Make a request to the website
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Write the parsed HTML content to a file
    with open('../data/parsed_html.html', 'w') as f:
        f.write(str(soup))

def main():
    scrape("https://eso-hub.com/en/sets/all")

if __name__=="__main__":
    main()