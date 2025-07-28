import requests
from bs4 import BeautifulSoup

url = "https://www.eliteprospects.com/league/ohl/stats/2023-2024"
headers = {"User-Agent": "Mozilla/5.0"}

resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")

tables = soup.find_all("table")
print(f"Found {len(tables)} tables")

# Try printing the 3rd table (usually the stats one)
if len(tables) >= 3:
    print(tables[2].prettify())
