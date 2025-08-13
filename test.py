import requests
from bs4 import BeautifulSoup
import pandas as pd
from nhl_predictor.scraper_utils import get_team_roster_urls
import time
import random

def safe_int(x):
    try:
        return int(x)
    except:
        return None

def scrape_nhl_player_stats(league_id, season_label, headers=None):
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
        
        page_counter += 1
        
        # Sleep to be polite to the server
        time.sleep(random.uniform(1, 3))
    
    df_stat = pd.DataFrame(players)
    print(f"Scraped {len(players)} players from {league_id} {season_label}")
    return df_stat


def scrape_nhl_roster(rosters):
    
    players = []
    
    for url_roster in rosters:
        time.sleep(random.uniform(0.5, 2.2))
        response = requests.get(url_roster)
        soup = BeautifulSoup(response.text, "html.parser")

        tables = soup.find_all('table')
        print(f"Total tables found: {len(tables)}")

        # Find all player divs
        player_divs = soup.find_all('div', class_='Roster_player__e6EbP')

        for player_div in player_divs:
            # Climb up to the <tr> and then to the <table>
            parent_td = player_div.parent
            parent_tr = parent_td.parent if parent_td else None

            # Climb up parents to find <table>
            ancestor = parent_tr
            while ancestor:
                if ancestor.name == 'table':
                    parent_table = ancestor
                    break
                ancestor = ancestor.parent

            # Extract player info (same as before)
            player_tag = player_div.find('a', class_='TextLink_link__RhSiC')
            if not player_tag or not parent_tr:
                continue
            player_name = player_tag.text.strip()

            tds = parent_tr.find_all('td')
            if len(tds) < 8:
                continue
            try: 
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
                    "Number": number,
                    "Nationality": nationality,
                    "Birth Year": birth_year,
                    "Birthplace": birthplace,
                    "Height": height,
                    "Weight": weight,
                    "Shoots": shoots,
                })
            except Exception as e:
                    print(f"Error, Player skipped: {e}")
                    continue

    df_roster = pd.DataFrame(players)
    return df_roster


season = '2023-2024'
league = 'nhl'

merged_df = pd.merge(scrape_nhl_roster(get_team_roster_urls(league, season)), scrape_nhl_player_stats('nhl', '2023-2024'), left_on='Name', right_on='name', how='inner')
print(merged_df)
