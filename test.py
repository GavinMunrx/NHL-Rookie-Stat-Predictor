import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}

def get_team_roster_urls(league_url, league, season_label):
    resp = requests.get(league_url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    base_url = "https://www.eliteprospects.com"
    roster_urls = []
    league_cap = league.upper()

    # Find the heading <h2> with text "WHL Team Rosters"
    heading = soup.find("h2", string=f"{league_cap} Team Rosters")
    if not heading:
        print(f"'{league} Team Rosters' heading not found")
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

# Example usage:
league = 'nhl'
league_url = f"https://www.eliteprospects.com/league/{league}/2023-2024"
season = "2023-2024"
roster_urls = get_team_roster_urls(league_url, league, season)

print(league_url)

print(f"Found {len(roster_urls)} team roster URLs:")
for url in roster_urls:
    print(url)
    
    headers = {"User-Agent": "Mozilla/5.0"}

def safe_int(text):
    try:
        return int(text)
    except ValueError:
        return 0

def scrape_amateur_eliteprospects_league_season(league_id, season_label):
    url = f"https://www.eliteprospects.com/team/1580/anaheim-ducks/2023-2024"
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

    table = tables[0]  # The detailed stats table needed on EP
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

league1 = 'nhl'
season1 = "2023-2024"
stats = scrape_amateur_eliteprospects_league_season( league1, season1)

print(f"Found {len(stats)} team roster URLs:")
for s in stats:
    print(s)



# Test for different NHL data source

# headers = {"User-Agent": "Mozilla/5.0"}

# def safe_int(text):
#     try:
#         return int(text)
#     except ValueError:
#         return 0

# def scrape_nhl_rookie_stats(season):
#     url = f"https://www.statmuse.com/nhl/ask?q=rookie+points+leaders+nhl+2024-25"
#     print(f"Scraping NHL Rookie → {url}")


#     response = requests.get(url, headers=headers)
#     if response.status_code != 200:
#         print(f"Error Loading Page: {response.status_code}")
#         return []

#     soup = BeautifulSoup(response.text, "html.parser")
#     tables = soup.find_all("table")
#     print(f"Found {len(tables)} tables on page")

#     if len(tables) < 3:
#         print("Error Locating Tables")
#         return []

#     table = tables[9]  # The detailed stats table needed on EP
#     rows = table.find_all("tr")

#     players = []
#     for i, row in enumerate(rows):
#         cols = row.find_all("td")
#         if len(cols) < 7:
#             continue
#         try:
#             player = {
#                 "rank": cols[0].text.strip(),
#                 "name": cols[2].text.strip(),
#                 "team": cols[4].text.strip(),
#                 "gp": safe_int(cols[6].text.strip()),
#                 "goals": safe_int(cols[8].text.strip()),
#                 "assists": safe_int(cols[10].text.strip()),
#                 "points": safe_int(cols[12].text.strip()),
#                 "league": 'NHL',
#                 "season": season
#             }
#             players.append(player)
#         except Exception as e:
#             print(f"Error, Row {i} skipped: {e}")
#             continue

#     print(f"Scraped {len(players)} players from NHL")
#     return players

# season = 26
# rookie = scrape_nhl_rookie_stats(season)

# for p in rookie:
#     print(p)
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.eliteprospects.com/team/1580/anaheim-ducks/2023-2024"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

tables = soup.find_all('table')
print(f"Total tables found: {len(tables)}")

players = []

# Map each table to an index for reference
table_to_index = {table: idx for idx, table in enumerate(tables)}

# Find all player divs
player_divs = soup.find_all('div', class_='Roster_player__e6EbP')

for player_div in player_divs:
    # Climb up to the <tr> and then to the <table>
    parent_td = player_div.parent
    parent_tr = parent_td.parent if parent_td else None
    parent_table = None

    # Climb up parents to find <table>
    ancestor = parent_tr
    while ancestor:
        if ancestor.name == 'table':
            parent_table = ancestor
            break
        ancestor = ancestor.parent

    # Identify the table index or class for this player row
    table_index = table_to_index.get(parent_table, None)

    # Extract player info (same as before)
    player_tag = player_div.find('a', class_='TextLink_link__RhSiC')
    if not player_tag or not parent_tr:
        continue
    player_name = player_tag.text.strip()
    player_url = "https://www.eliteprospects.com" + player_tag['href']

    tds = parent_tr.find_all('td')
    if len(tds) < 8:
        continue

    number = tds[1].text.strip()
    nationality_img = tds[2].find('img')
    nationality = nationality_img['title'] if nationality_img else ''
    birth_year = tds[5].text.strip()
    birthplace_tag = tds[6].find('a')
    birthplace = birthplace_tag.text.strip() if birthplace_tag else ''
    height = tds[7].text.strip()
    weight = tds[8].text.strip()
    shoots = tds[9].text.strip()

    players.append({
        "Name": player_name,
        "Profile_URL": player_url,
        "Number": number,
        "Nationality": nationality,
        "Birth Year": birth_year,
        "Birthplace": birthplace,
        "Height": height,
        "Weight": weight,
        "Shoots": shoots,
        "Table_Index": table_index  # added info about the table source
    })

df = pd.DataFrame(players)
print(df)
