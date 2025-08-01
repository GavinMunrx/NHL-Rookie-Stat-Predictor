from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import time
import csv

headers = {"User-Agent": "Mozilla/5.0"}

def safe_int(text):
    try:
        return int(text)
    except ValueError:
        return 0

def scrape_eliteprospects_league_season(league_id, season_label):
    url = f"https://www.eliteprospects.com/league/{league_id}/stats/{season_label}"
    print(f"Scraping {league_id} {season_label} → {url}")


    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to load page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Found {len(tables)} tables on page")

    if len(tables) < 3:
        print("❌ Not enough tables found!")
        return []

    table = tables[2]  # The detailed stats table
    rows = table.find_all("tr")

    players = []
    for i, row in enumerate(rows):
        cols = row.find_all("td")
        if len(cols) < 7:
            continue
        try:
            player = {
                "rank": cols[0].text.strip(),
                "name": cols[1].text.strip(),
                "team": cols[2].text.strip(),
                "gp": safe_int(cols[3].text.strip()),
                "goals": safe_int(cols[4].text.strip()),
                "assists": safe_int(cols[5].text.strip()),
                "points": safe_int(cols[6].text.strip()),
                "league": league_id,
                "season": season_label
            }
            players.append(player)
        except Exception as e:
            print(f"⚠️ Row {i} skipped: {e}")
            continue

    print(f"✅ Scraped {len(players)} players from {league_id} {season_label}")
    return players

def write_players_to_csv(players, filename):
    fieldnames = ["rank", "name", "team", "gp", "goals", "assists", "points", "league", "season"]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for player in players:
            writer.writerow(player)
    print(f"✅ Wrote {len(players)} players to {filename}")

if __name__ == "__main__":
    players = scrape_eliteprospects_league_season("ohl", "2023-2024")
    if players:
        write_players_to_csv(players, "data/raw/ohl_2023_2024_stats.csv")
