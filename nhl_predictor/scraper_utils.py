# from webdriver_manager.chrome import ChromeDriverManager
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

def get_team_roster_urls(league_url, season_label):
    resp = requests.get(league_url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    base_url = "https://www.eliteprospects.com"
    roster_urls = []

    # Find the heading <h2> with text "WHL Team Rosters"
    heading = soup.find("h2", string="NHL Team Rosters")
    if not heading:
        print("'XXXX Team Rosters' heading not found")
        return []

    # Find the div with id="league-team-rosters" after the heading
    roster_div = heading.find_next("div", id="league-team-rosters")
    if not roster_div:
        print("'league-team-rosters' div not found")
        return []

    # Find the <ul> containing the teams
    teams_list = roster_div.find("ul", class_="TeamRoster_teamRoster__y6g5I")
    if not teams_list:
        print("Teams list <ul> not found")
        return []

    # Extract team URLs from the <a> tags inside the <li>s
    for li in teams_list.find_all("li"):
        a_tag = li.find("a", href=True)
        if a_tag:
            href = a_tag['href']
            team_base_url = base_url + href.split("?")[0]
            full_roster_url = f"{team_base_url}/{season_label}#players"
            if full_roster_url not in roster_urls:
                roster_urls.append(full_roster_url)

    return roster_urls

def scrape_amateur_eliteprospects_league_season(league_id, season_label):
    url = f"https://www.eliteprospects.com/league/{league_id}/stats/{season_label}"
    print(f"Scraping {league_id} {season_label} → {url}")


    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error Loading Page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Found {len(tables)} tables on page")

    if len(tables) < 3:
        print("Error Locating Tables")
        return []

    table = tables[2]  # The detailed stats table needed on EP
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
            print(f"Error, Row {i} skipped: {e}")
            continue

    print(f"Scraped {len(players)} players from {league_id} {season_label}")
    return players

def scrape_nhl_rookie_stats(season):
    return

def write_players_to_csv(players, filename):
    fieldnames = ["rank", "name", "team", "gp", "goals", "assists", "points", "league", "season"]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for player in players:
            writer.writerow(player)
    print(f"Wrote {len(players)} players data to {filename}")


