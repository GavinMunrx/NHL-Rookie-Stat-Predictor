import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


headers = {"User-Agent": "Mozilla/5.0"}

def safe_int(text):
    try:
        return int(text)
    except ValueError:
        return 0

def scrape_player_stats(league_id, season_label, headers=None):
    players = []
    page_counter = 1
    
    while True:
        url_stats = f"https://www.eliteprospects.com/league/{league_id}/stats/{season_label}?page={page_counter}"
        print(f"Scraping page {page_counter}")
        
        response = requests.get(url_stats, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_counter} (status {response.status_code})")
            break
        
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")
        if len(tables) < 3:
            print("Stats table not found")
            break
        
        table = tables[2]  # The detailed stats table
        rows = table.find_all("tr")
        
        # If no rows found or only header row, end scraping
        if len(rows) <= 1:
            print("No data rows found")
            break
        
        # Process rows
        for i, row in enumerate(rows[1:]):  # Skip header row
            cols = row.find_all("td")
            if len(cols) < 7:
                continue
            player = {
                "season_rank": cols[0].text.strip(),
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
        
        page_counter += 1
        
        time.sleep(random.uniform(1, 3)) # preventing server overload
    
    df_stat = pd.DataFrame(players)
    print(f"Scraped {len(players)} players from {league_id} {season_label}")
    return df_stat

def scrape_statistics(league, season):
    table_structure = ['name',
                       'season',
                       'season_rank',
                       "team",
                        "gp",
                        "goals",
                        "assists",
                        "points",
                        "league"]
    
    df = scrape_player_stats(league, season)
    return df[table_structure]



# Needed for Phase 2 of Scraping, which aims to inlude player weight, height, birth year and more.
# Was able to get roster URL's from league web pages, however these were only for current teams.
# No expansion teams or teams that changed location include in this so may pivot to selenium solution.

# Scrape roster data works well, issue now is getting the URLs of current and past teams.


# def get_team_roster_urls(league, season_label):
#     league_url = f"https://www.eliteprospects.com/league/{league}/{season_label}"
#     resp = requests.get(league_url, headers=headers)
#     soup = BeautifulSoup(resp.text, "html.parser")
#     base_url = "https://www.eliteprospects.com"
#     roster_urls = []

#     # Find the heading <h2> with text "WHL Team Rosters"
#     heading = soup.find("h2", string=f"{league.upper()} Team Rosters")
#     if not heading:
#         print("'XXXX Team Rosters' heading not found")
#         return []

#     # Find the div with id="league-team-rosters" after the heading
#     roster_div = heading.find_next("div", id="league-team-rosters")
#     if not roster_div:
#         print("'league-team-rosters' div not found")
#         return []

#     # Find the <ul> containing the teams
#     teams_list = roster_div.find("ul", class_="TeamRoster_teamRoster__y6g5I")
#     if not teams_list:
#         print("Teams list <ul> not found")
#         return []

#     # Extract team URLs from the <a> tags inside the <li>s
#     for li in teams_list.find_all("li"):
#         a_tag = li.find("a", href=True)
#         if a_tag:
#             href = a_tag['href']
#             team_base_url = base_url + href.split("?")[0]
#             full_roster_url = f"{team_base_url}/{season_label}#players"
#             if full_roster_url not in roster_urls:
#                 roster_urls.append(full_roster_url)

#     return roster_urls

# def scrape_roster_data(rosters):
    
#     players = []
#
#     for url_roster in rosters:
#         time.sleep(random.uniform(1, 2)) # preventing server overload
#         response = requests.get(url_roster)
#         soup = BeautifulSoup(response.text, "html.parser")

#         tables = soup.find_all('table')
#         print(f"Total tables found: {len(tables)} for {url_roster}")

#         # Find all player divs
#         player_divs = soup.find_all('div', class_='Roster_player__e6EbP')

#         for player_div in player_divs:
#             # Climb up to the <tr> and then to the <table>
#             parent_td = player_div.parent
#             parent_tr = parent_td.parent if parent_td else None

#             # Climb up parents to find <table>
#             ancestor = parent_tr
#             while ancestor:
#                 if ancestor.name == 'table':
#                     break
#                 ancestor = ancestor.parent

#             # Extract player info (same as before)
#             player_tag = player_div.find('a', class_='TextLink_link__RhSiC')
#             if not player_tag or not parent_tr:
#                 continue

#             tds = parent_tr.find_all('td')
#             if len(tds) < 8:
#                 continue
#             try: 
#                 nationality_img = tds[2].find('img')

#                 players.append({
#                     "name": player_tag.text.strip(),
#                     "nationality": nationality_img['title'] if nationality_img else '',
#                     "birth_year": tds[5].text.strip(),
#                     "height": tds[7].text.strip(),
#                     "weight": tds[8].text.strip(),
#                     "shoots": tds[9].text.strip(),
#                 })
#             except Exception as e:
#                     print(f"Error, Player skipped: {e}")
#                     continue

#     df_roster = pd.DataFrame(players)
#     return df_roster
#
# def scrape_nhl_stats(season):
#     table_structure = ['name',
#                        'season',
#                        'season_rank',
#                        "team",
#                         "gp",
#                         "goals",
#                         "assists",
#                         "points",
#                         "league",
#                         "nationality",
#                         "birth_year",
#                         "height",
#                         "weight",
#                         "shoots"]
#     merged_df = pd.merge(scrape_roster_data(get_team_roster_urls('nhl', season)), scrape_player_stats('nhl', season), on='name', how='inner')
#     return merged_df[table_structure]

# def scrape_amateur_stats(league, season):
#     table_structure = ['name',
#                        'season',
#                        'season_rank',
#                        "team",
#                         "gp",
#                         "goals",
#                         "assists",
#                         "points",
#                         "league",
#                         "nationality",
#                         "birth_year",
#                         "height",
#                         "weight",
#                         "shoots"]
    
#     merged_df = pd.merge(scrape_roster_data(get_team_roster_urls(league, season)), scrape_player_stats(league, season), on='name', how='outer')
#     return merged_df[table_structure]
