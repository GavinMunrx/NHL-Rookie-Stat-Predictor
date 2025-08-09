from nhl_predictor.scraper_utils import scrape_amateur_eliteprospects_league_season
from nhl_predictor.scraper_utils import scrape_nhl_rookie_stats
import os
import pandas as pd

def run_scraping():
    leagues = ["ohl","whl"]
    seasons = ["2023-2024"]

    all_amateur = []
    all_nhl = []

    os.makedirs("data/raw", exist_ok=True)

    # for season in seasons:
    for league in leagues:
        for season in seasons:
            try:
                players = scrape_amateur_eliteprospects_league_season(league, str(season))
                all_amateur.extend(players)
            except Exception as e:
                print(f"Error scraping {league} {season}: {e}")

    try:
        season_start = seasons[0] 
        numerical_season_start = int(season_start[2:4])
        rookies = scrape_nhl_rookie_stats(numerical_season_start)
        all_nhl.extend(rookies)
    except Exception as e:
        print(f"Error scraping NHL rookies {season}: {e}")

    pd.DataFrame(all_amateur).to_csv("data/raw/amateur_all_test.csv", index=False)
    pd.DataFrame(all_nhl).to_csv("data/raw/nhl_rookies_all.csv", index=False)
    print(f"Saved {len(all_amateur)} amateur players, {len(all_nhl)} NHL rookies.")
