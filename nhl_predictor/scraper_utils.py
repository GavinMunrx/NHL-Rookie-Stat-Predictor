import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Safari/537.36"}

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

def scrape_nhl_debuts(year):
    url = f"https://www.hockey-reference.com/leagues/NHL_{year}_debut.html"
    print(f"Scraping {url} ...")

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    time.sleep(random.uniform(2, 5)) # preventing server overload
    
    if response.status_code != 200:
        print(f"Failed to retrieve page {year} (status {response.status_code})")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "debuts"})
    if not table:
        print("Debuts table not found")
        return pd.DataFrame()

    rows = table.find("tbody").find_all("tr")
    players = []

    for row in rows:
        cols = row.find_all("td")
        if not cols:
            continue  # skip separator/header rows

        player = {
            "name": cols[0].text.strip(),
            "debut_age": cols[1].text.strip(),
            "debut_date": cols[2].text.strip(),
            "team": cols[3].text.strip(),
            "date_of_birth": cols[4].text.strip(),
            "pos": cols[7].text.strip(),
            "season": f"{year-1}-{year}"
        }
        players.append(player)

    df = pd.DataFrame(players)
    
    df = df[df['debut_age'].notna() & (df['debut_age'].str.strip() != '')]
    
    filtered_df = df[(df['pos'] != 'G') & (df['debut_age'].str[:2].astype(int) <= 25)]
    
    print(f"Scraped {len(players)} players from NHL {year}")
    return filtered_df
