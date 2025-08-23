# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# from nhl_predictor.scraper_utils import get_team_roster_urls
# import time
# import random

# def safe_int(x):
#     try:
#         return int(x)
#     except:
#         return None

# def scrape_nhl_player_stats(league_id, season_label, headers=None):
#     players = []
#     page_counter = 1
    
#     while True:
#         url_stats = f"https://www.eliteprospects.com/league/{league_id}/stats/{season_label}?page={page_counter}"
#         print(f"Scraping page {page_counter}")
        
#         response = requests.get(url_stats, headers=headers)
#         if response.status_code != 200:
#             print(f"Failed to retrieve page {page_counter} (status {response.status_code})")
#             break
        
#         soup = BeautifulSoup(response.text, "html.parser")
#         tables = soup.find_all("table")
#         if len(tables) < 3:
#             print("Stats table not found")
#             break
        
#         table = tables[2]  # The detailed stats table
#         rows = table.find_all("tr")
        
#         # If no rows found or only header row, end scraping
#         if len(rows) <= 1:
#             print("No data rows found")
#             break
        
#         # Process rows
#         for i, row in enumerate(rows[1:]):  # Skip header row
#             cols = row.find_all("td")
#             if len(cols) < 7:
#                 continue
#             player = {
#                 "rank": cols[0].text.strip(),
#                 "name": cols[1].text.strip(),
#                 "team": cols[2].text.strip(),
#                 "gp": safe_int(cols[3].text.strip()),
#                 "goals": safe_int(cols[4].text.strip()),
#                 "assists": safe_int(cols[5].text.strip()),
#                 "points": safe_int(cols[6].text.strip()),
#                 "league": league_id,
#                 "season": season_label
#             }
#             players.append(player)
        
#         page_counter += 1
        
#         # Sleep to be polite to the server
#         time.sleep(random.uniform(1, 3))
    
#     df_stat = pd.DataFrame(players)
#     print(f"Scraped {len(players)} players from {league_id} {season_label}")
#     return df_stat


# def scrape_nhl_roster(rosters):
    
#     players = []
    
#     for url_roster in rosters:
#         time.sleep(random.uniform(0.5, 2.2))
#         response = requests.get(url_roster)
#         soup = BeautifulSoup(response.text, "html.parser")

#         tables = soup.find_all('table')
#         print(f"Total tables found: {len(tables)}")

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
#                     parent_table = ancestor
#                     break
#                 ancestor = ancestor.parent

#             # Extract player info (same as before)
#             player_tag = player_div.find('a', class_='TextLink_link__RhSiC')
#             if not player_tag or not parent_tr:
#                 continue
#             player_name = player_tag.text.strip()

#             tds = parent_tr.find_all('td')
#             if len(tds) < 8:
#                 continue
#             try: 
#                 number = tds[1].text.strip()
#                 nationality_img = tds[2].find('img')
#                 nationality = nationality_img['title'] if nationality_img else ''
#                 birth_year = tds[5].text.strip()
#                 birthplace_tag = tds[6].find('a')
#                 birthplace = birthplace_tag.text.strip() if birthplace_tag else ''
#                 height = tds[7].text.strip()
#                 weight = tds[8].text.strip()
#                 shoots = tds[9].text.strip()

#                 players.append({
#                     "Name": player_name,
#                     "Number": number,
#                     "Nationality": nationality,
#                     "Birth Year": birth_year,
#                     "Birthplace": birthplace,
#                     "Height": height,
#                     "Weight": weight,
#                     "Shoots": shoots,
#                 })
#             except Exception as e:
#                     print(f"Error, Player skipped: {e}")
#                     continue

#     df_roster = pd.DataFrame(players)
#     return df_roster


# season = '2023-2024'
# league = 'nhl'

# merged_df = pd.merge(scrape_nhl_roster(get_team_roster_urls(league, season)), scrape_nhl_player_stats('nhl', '2023-2024'), left_on='Name', right_on='name', how='inner')
# print(merged_df)


import pandas as pd
import os

def clean_data(input_csv="data/raw/nhl_all.csv", output_csv="data/processed/cleaned.csv"):
    print(f"Loading data from {input_csv}...")
    df = pd.read_csv(input_csv)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Ensure season is sorted properly
    df = df.sort_values(["name", "season"])

    # Shift previous season NHL games
    df['gp_prev_season'] = df.groupby('name')['gp'].shift(1).fillna(0)
    df['gp_two_seasons_ago'] = df.groupby('name')['gp'].shift(2).fillna(0)

    # Calculate cumulative NHL games prior to this season
    df['total_prev_nhl'] = df.groupby('name')['gp'].cumsum().shift(1).fillna(0)

    # Flag rookies based on new rules
    df['rookie_flag_1'] = df['gp_prev_season'] <= 25  # Not >25 games in previous season
    df['rookie_flag_2'] = ~((df['gp_prev_season'] >= 6) & (df['gp_two_seasons_ago'] >= 6))  # Not 6+ in any two preceding seasons
    df['is_rookie'] = df['rookie_flag_1'] & df['rookie_flag_2'] 

    # Fill any missing numeric values with 0
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Optional: drop rows with missing essential info
    df = df.dropna(subset=['name', 'season', 'gp'])

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Save cleaned CSV
    df.to_csv(output_csv, index=False)
    print(f"Cleaned data saved to {output_csv}")
    print(f"Total rows: {len(df)} | Total rookies flagged: {df['is_rookie'].sum()}")

if __name__ == "__main__":
    clean_data()

# import pandas as pd

# # Load CSVs
# amateur_df = pd.read_csv("data/raw/amateur_all.csv")
# nhl_df = pd.read_csv("data/raw/nhl_all.csv")


# # Convert season strings to numeric start year
# def season_to_year(season_str):
#     return int(season_str.split("-")[0])

# amateur_df['season_start'] = amateur_df['season'].apply(season_to_year)
# nhl_df['season_start'] = nhl_df['season'].apply(season_to_year)

# # Sort amateur stats by player and season
# amateur_df = amateur_df.sort_values(['name', 'season_start'])

# # Function: get most recent amateur season before NHL
# def get_last_amateur_row(player_name, nhl_season):
#     player_am_stats = amateur_df[amateur_df['name'] == player_name]
#     prev = player_am_stats[player_am_stats['season_start'] < nhl_season]
#     if prev.empty:
#         return None
#     return prev.iloc[-1]  # last amateur season

# merged_rows = []

# for _, nhl_row in nhl_df.iterrows():
#     last_am_row = get_last_amateur_row(nhl_row['name'], nhl_row['season_start'])
#     if last_am_row is None:
#         continue

#     # Build merged dict with suffixes
#     combined_dict = {}
#     for col in last_am_row.index:
#         combined_dict[f"amateur_{col}"] = last_am_row[col]
#     for col in nhl_row.index:
#         combined_dict[f"nhl_{col}"] = nhl_row[col]

#     merged_rows.append(combined_dict)

# # Create final DataFrame
# merged_df = pd.DataFrame(merged_rows)

# # Save
# merged_df.to_csv("data/processed/merged.csv", index=False)
# print(f"Merged {len(merged_df)} NHL rookies with their last amateur season")

import pandas as pd

# Load your CSVs
amateur_df = pd.read_csv("data/raw/amateur_all.csv")
nhl_df = pd.read_csv("data/raw/nhl_all.csv")

# Ensure season is sortable (string or int)
amateur_df["season"] = amateur_df["season"].astype(str)
nhl_df["season"] = nhl_df["season"].astype(str)

# Remove 2012-2013 lockout season
amateur_df = amateur_df[amateur_df["season"] != "2012-2013"]
nhl_df = nhl_df[nhl_df["season"] != "2012-2013"]

# Get last amateur season
last_amateur = (amateur_df
                .sort_values("season")
                .groupby("name")
                .tail(1))

# Get first NHL season
first_nhl = (nhl_df
             .sort_values("season")
             .groupby("name")
             .head(1))

# Ensure rookie NHL season is after last amateur season
merged = pd.merge(
    last_amateur,
    first_nhl,
    on="name",
    suffixes=("_amateur", "_nhl")
)

# Filter rows where NHL season > amateur season
merged = merged[merged["season_nhl"] > merged["season_amateur"]]

# Save merged dataset
merged.to_csv("amateur_to_rookie.csv", index=False)
print(f"Merged dataset shape (only valid rookie transitions): {merged.shape}")

