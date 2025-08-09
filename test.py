import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}

def get_team_roster_urls(league_url, season_label):
    resp = requests.get(league_url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    base_url = "https://www.eliteprospects.com"
    roster_urls = []

    # Find the heading <h2> with text "WHL Team Rosters"
    heading = soup.find("h2", string="NHL Team Rosters")
    if not heading:
        print("❌ 'WHL Team Rosters' heading not found")
        return []

    # Find the div with id="league-team-rosters" after the heading
    roster_div = heading.find_next("div", id="league-team-rosters")
    if not roster_div:
        print("❌ 'league-team-rosters' div not found")
        return []

    # Find the <ul> containing the teams
    teams_list = roster_div.find("ul", class_="TeamRoster_teamRoster__y6g5I")
    if not teams_list:
        print("❌ Teams list <ul> not found")
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

# Example usage:
league_url = "https://www.eliteprospects.com/league/nhl/2023-2024"
season = "2023-2024"
roster_urls = get_team_roster_urls(league_url, season)

print(f"Found {len(roster_urls)} team roster URLs:")
for url in roster_urls:
    print(url)

# Test for different NHL data source

headers = {"User-Agent": "Mozilla/5.0"}

def safe_int(text):
    try:
        return int(text)
    except ValueError:
        return 0

def scrape_nhl_rookie_stats(season):
    url = f"https://www.statmuse.com/nhl/ask?q=rookie+points+leaders+nhl+2024-25"
    print(f"Scraping NHL Rookie → {url}")


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

    table = tables[9]  # The detailed stats table needed on EP
    rows = table.find_all("tr")

    players = []
    for i, row in enumerate(rows):
        cols = row.find_all("td")
        if len(cols) < 7:
            continue
        try:
            player = {
                "rank": cols[0].text.strip(),
                "name": cols[2].text.strip(),
                "team": cols[4].text.strip(),
                "gp": safe_int(cols[6].text.strip()),
                "goals": safe_int(cols[8].text.strip()),
                "assists": safe_int(cols[10].text.strip()),
                "points": safe_int(cols[12].text.strip()),
                "league": 'NHL',
                "season": season
            }
            players.append(player)
        except Exception as e:
            print(f"Error, Row {i} skipped: {e}")
            continue

    print(f"Scraped {len(players)} players from NHL")
    return players

season = 26
rookie = scrape_nhl_rookie_stats(season)

for p in rookie:
    print(p)
